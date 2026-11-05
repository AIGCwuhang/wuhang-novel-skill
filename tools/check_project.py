#!/usr/bin/env python3
"""Check local links, metadata, source hygiene and example consistency, offline."""
import ast
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check():
    errors = []
    version = (ROOT / "VERSION").read_text().strip()
    for relative in ("plugin.json", "adapters/vscode/package.json"):
        data = json.loads((ROOT / relative).read_text())
        if data["version"] != version:
            errors.append(f"{relative}: 版本不一致")
    skill = ROOT / "skills/wuhang-novel"
    entry = (skill / "SKILL.md").read_text()
    if not entry.startswith("---\nname: wuhang-novel\ndescription:"):
        errors.append("Skill 名称或 frontmatter 无效")
    for mode in ("define", "guide", "analyze", "ideation", "outline", "write", "review", "project-contract"):
        if not (skill / "references" / (mode + ".md")).is_file():
            errors.append(f"缺少流程：{mode}")
    marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
    for plugin in marketplace["plugins"]:
        path = (ROOT / plugin["source"]["path"]).resolve()
        if not (path / "plugin.json").is_file():
            errors.append("本地市场未指向插件目录")
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if any(part in ("dist", ".git", "node_modules", "__pycache__") for part in relative.parts):
            continue
        if path.is_symlink():
            errors.append(f"不应包含符号链接：{relative}")
        if not path.is_file():
            continue
        if path.name.startswith(".env") and path.name != ".env.example":
            errors.append(f"发现本地配置：{relative}")
        if path.suffix not in (".md", ".py", ".json", ".yaml", ".js", ".cjs"):
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(relative))
            except SyntaxError as error:
                errors.append(str(error))
        if "/Users/" in text and relative.parts[0] in ("skills", "adapters"):
            errors.append(f"个人绝对路径：{relative}")
        if relative.parts[0] == "skills" and any(token in text for token in
                (".soloent/skills/", "docs/MASTER.md", "state.json", "novel-review`", "novel-outline`")):
            errors.append(f"残留旧路径或独立技能调用：{relative}")
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                target = target.strip("<>")
                parsed = urllib.parse.urlsplit(target)
                if parsed.scheme or target.startswith("#"):
                    continue
                target_path = urllib.parse.unquote(parsed.path)
                if target_path and not (path.parent / target_path).exists():
                    errors.append(f"断链：{relative} → {target}")
    sys.path.insert(0, str(skill / "scripts"))
    from count_chinese_words import count_chinese_words
    demo = ROOT / "examples/demo-novel"
    count = count_chinese_words((demo / "4-正文/第1章_草稿.md").read_text())
    if not 300 <= count <= 900:
        errors.append(f"示例字数未达演示范围：{count}")
    if f"{count}" not in (demo / "5-审查/第1章_自检与审稿.md").read_text():
        errors.append("示例自检字数与脚本不一致")
    return errors


if __name__ == "__main__":
    issues = check()
    for issue in issues:
        print(issue, file=sys.stderr)
    print(f"项目检查：{'未通过' if issues else '通过'}（{len(issues)} 个问题）")
    raise SystemExit(bool(issues))
