import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/wuhang-novel/scripts"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


init = load("novel_init", SCRIPTS / "init_project.py")
counter = load("novel_count", SCRIPTS / "count_chinese_words.py")
summary = load("novel_summary", SCRIPTS / "summarize.py")
builder = load("release_builder", ROOT / "tools/build_release.py")


class ProjectTests(unittest.TestCase):
    def test_reinitialization_preserves_every_existing_file(self):
        with tempfile.TemporaryDirectory(prefix="武行 中文路径 ") as directory:
            project = Path(directory) / "我的小说"
            result = init.initialize(project)
            self.assertIn("SOLOENT.md", result["created"])
            (project / "SOLOENT.md").write_text("作者进度：第205章")
            (project / "4-正文/第205章_草稿.md").write_text("作者正文")
            before = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
            second = init.initialize(project)
            after = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
            self.assertEqual(before, after)
            self.assertEqual(second["created"], [])
            self.assertTrue(second["warnings"])

    def test_symlinked_destination_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, outside = root / "novel", root / "outside"
            project.mkdir()
            outside.mkdir()
            (project / ".novelkit").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                init.initialize(project)
            self.assertEqual(list(outside.iterdir()), [])
            self.assertFalse((project / "SOLOENT.md").exists())

    def test_invalid_target_type_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "SOLOENT.md").mkdir()
            with self.assertRaises(ValueError):
                init.initialize(project)


class CountTests(unittest.TestCase):
    def test_body_metric_does_not_include_title_or_link_url(self):
        self.assertEqual(counter.count_chinese_words("# 第205章：标题\n\n你好，世界！abc123\n[线索](https://example.com/123)"), 8)

    def test_actual_file_count_drives_average_and_chapters_over_199(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for number, body in [(1, "甲乙"), (205, "甲乙丙丁")]:
                path = Path(directory) / f"第{number}章_草稿.md"
                path.write_text(f"# 第{number}章\n{body}")
                paths.append(path)
            result = counter.report(paths, 1, 10)
            self.assertEqual((result["count"], result["total"], result["average"]), (2, 6, 3))
            self.assertEqual([r["status"] for r in result["chapters"]], ["达标", "达标"])


class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="梗概测试 ")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.novel = self.project / "参考书.txt"
        self.novel.write_text("第一章 河边\n第一章的原创材料。\n第二章 船上\n第二章的原创材料。")
        self.output = self.project / "1-边界/1.1_全书故事梗概.md"

    def invoke(self, extra=()):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            result = summary.main([str(self.novel), "--project", str(self.project), *extra])
        return result, buffer.getvalue()

    def test_preview_is_offline_and_creates_no_output_or_env(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(summary.urllib.request, "urlopen") as network:
            result, text = self.invoke(["--limit", "1"])
        self.assertEqual(result, 0)
        network.assert_not_called()
        self.assertIn('"chapters": 1', text)
        self.assertFalse(self.output.exists())
        self.assertFalse((self.project / ".env").exists())
        self.assertFalse((self.project / ".novelkit").exists())

    def test_cache_isolates_content_and_model(self):
        chapters = summary.extract_chapters(self.novel)
        self.assertEqual(len(chapters), 2)
        a = summary.cache_key(chapters, "https://example.test/v1", "model-a")
        self.assertNotEqual(a, summary.cache_key(chapters, "https://example.test/v1", "model-b"))
        chapters[0]["content"] = "另一本书相同章号的内容"
        self.assertNotEqual(a, summary.cache_key(chapters, "https://example.test/v1", "model-a"))

    def test_failed_batch_never_claims_a_complete_summary(self):
        env = {"NOVEL_API_KEY": "test-secret-not-real", "NOVEL_API_MODEL": "test-model"}
        with patch.dict(os.environ, env, clear=True), patch.object(summary, "request_summary", side_effect=ValueError("模拟失败")):
            result, text = self.invoke(["--run"])
        self.assertEqual(result, 1)
        self.assertFalse(self.output.exists())
        self.assertIn("未生成最终梗概", text)
        self.assertNotIn(env["NOVEL_API_KEY"], text)

    def test_existing_output_is_preserved_without_overwrite(self):
        self.output.parent.mkdir()
        self.output.write_text("作者已有梗概")
        with patch.dict(os.environ, {"NOVEL_API_KEY": "fake", "NOVEL_API_MODEL": "fake"}, clear=True), patch.object(summary, "request_summary") as request:
            result, _ = self.invoke(["--run"])
        self.assertEqual(result, 1)
        request.assert_not_called()
        self.assertEqual(self.output.read_text(), "作者已有梗概")

    def test_mocked_http_success_and_repeated_run_reuses_cache(self):
        calls = []
        def fake_urlopen(request, timeout):
            payload = json.loads(request.data)
            calls.append(payload)
            titles = re.findall(r"^## (.+)$", payload["messages"][1]["content"], re.MULTILINE)
            content = "\n\n".join(f"## {title}\n主角核查了账册中的记录，发现一条需要进一步验证的线索。" for title in titles)
            return io.BytesIO(json.dumps({"choices": [{"message": {"content": content}}]}).encode())
        env = {"NOVEL_API_KEY": "test-secret-not-real", "NOVEL_API_MODEL": "test-model"}
        with patch.dict(os.environ, env, clear=True), patch.object(summary.urllib.request, "urlopen", side_effect=fake_urlopen):
            result, text = self.invoke(["--run", "--batch-size", "1"])
            self.assertEqual(result, 0)
            self.assertEqual(len(calls), 2)
            self.assertNotIn(env["NOVEL_API_KEY"], text)
            second, _ = self.invoke(["--run", "--batch-size", "1", "--overwrite"])
        self.assertEqual(second, 0)
        self.assertEqual(len(calls), 2)
        self.assertEqual(re.findall(r"^## (.+)$", self.output.read_text(), re.MULTILINE), ["第一章 河边", "第二章 船上"])

    def test_bad_response_and_missing_chapters_are_rejected(self):
        chapters = summary.extract_chapters(self.novel)
        with self.assertRaises(ValueError):
            summary.validate_summary("## 第一章 河边\n这份输出遗漏第二章，不能作为成功结果。", chapters)


class ReleaseTests(unittest.TestCase):
    def test_all_packages_contain_same_skill_and_are_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "one"
            second = Path(directory) / "two"
            products = builder.build(first)
            builder.build(second)
            self.assertEqual(len(products), 4)
            for product in products:
                self.assertEqual(product.read_bytes(), (second / product.name).read_bytes())
                with zipfile.ZipFile(product) as archive:
                    names = archive.namelist()
                    self.assertFalse(any("__pycache__" in n or n.endswith(".pyc") or n.endswith("/.env") for n in names))
                    self.assertFalse(any(Path(n).is_absolute() or ".." in Path(n).parts for n in names))
                    skill_name = next(n for n in names if n.endswith("SKILL.md"))
                    self.assertEqual(archive.read(skill_name), (ROOT / "skills/wuhang-novel/SKILL.md").read_bytes())
            # Test a distributable, not only source-tree imports.
            with zipfile.ZipFile(first / "wuhang-novel-workbuddy-v0.2.0.zip") as archive:
                unpacked = Path(directory) / "unpacked"
                archive.extractall(unpacked)
            project = Path(directory) / "unpacked novel"
            subprocess.run([sys.executable, str(unpacked / "scripts/init_project.py"), str(project)], check=True, capture_output=True)
            self.assertTrue((project / "SOLOENT.md").exists())
            if shutil.which("node"):
                extension_root = Path(directory) / "vsix"
                with zipfile.ZipFile(first / "wuhang-novel-skill-0.2.0.vsix") as archive:
                    archive.extractall(extension_root)
                result = subprocess.run(["node", str(ROOT / "tests/vscode-smoke.cjs"), str(extension_root / "extension"), str(Path(directory) / "editor novel")], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
