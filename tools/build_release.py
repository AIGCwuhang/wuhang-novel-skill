#!/usr/bin/env python3
"""Build deterministic preview release packages; never upload or install anything."""
import hashlib
import json
import zipfile
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/wuhang-novel"
VERSION = (ROOT / "VERSION").read_text().strip()
STAMP = (2026, 11, 5, 0, 0, 0)


def safe_files(root):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in ("__pycache__", ".DS_Store", "node_modules", ".git", "cache") for part in rel.parts):
            continue
        if path.suffix in (".pyc", ".pyo"):
            continue
        if path.name.startswith(".env") and path.name != ".env.example":
            raise ValueError(f"不打包本地密钥配置：{rel}")
        if path.is_symlink():
            raise ValueError(f"不打包符号链接：{rel}")
        if path.is_file():
            yield rel.as_posix(), path.read_bytes()


def write_archive(path, entries):
    if len({name for name, _ in entries}) != len(entries):
        raise ValueError("打包条目重复")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries):
            entry = zipfile.ZipInfo(name, STAMP)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)


def build(output=None):
    dist = Path(output) if output else ROOT / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    skill_entries = list(safe_files(SKILL))
    license_entry = [("LICENSE", (ROOT / "LICENSE").read_bytes())]
    plugin = json.loads((ROOT / "plugin.json").read_text())
    package = json.loads((ROOT / "adapters/vscode/package.json").read_text())
    if plugin["version"] != VERSION or package["version"] != VERSION:
        raise ValueError("版本号不一致")
    products = []
    def emit(name, entries):
        path = dist / name
        write_archive(path, entries)
        products.append(path)
    emit(f"wuhang-novel-skill-v{VERSION}.zip",
         [("wuhang-novel/" + name, data) for name, data in skill_entries + license_entry])
    # Root SKILL.md is a deliberate WorkBuddy import candidate layout, not a claimed host certification.
    emit(f"wuhang-novel-workbuddy-v{VERSION}.zip", skill_entries + license_entry)
    plugin_docs = [(name, (ROOT / name).read_bytes()) for name in
                   ("plugin.json", "LICENSE", "CHANGELOG.md")]
    video_guide = (SKILL / "assets/视频使用说明.md").read_text(encoding="utf-8")
    plugin_readme = "# 武行小说创作插件\n\n预览版。技能位于 skills/wuhang-novel/。许可范围待作者明确，宿主安装状态见源码项目 docs/validation.md。\n\n"
    plugin_docs.append(("README.md", (plugin_readme + video_guide.replace("# 视频使用说明", "## 视频使用说明", 1)).encode()))
    emit(f"wuhang-novel-codex-plugin-v{VERSION}.zip", plugin_docs +
         [("skills/wuhang-novel/" + name, data) for name, data in skill_entries])
    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
<Metadata><Identity Language="zh-CN" Id="wuhang-novel-skill" Version="{VERSION}" Publisher="wuhang"/>
<DisplayName>武行·网文创作 Skill</DisplayName><Description xml:space="preserve">{escape(package['description'])}</Description>
<Tags>novel,writing</Tags><Categories>Other</Categories><GalleryFlags>Public</GalleryFlags>
<Properties><Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.80.0"/>
<Property Id="Microsoft.VisualStudio.Code.ExtensionDependencies" Value=""/>
<Property Id="Microsoft.VisualStudio.Code.ExtensionPack" Value=""/>
<Property Id="Microsoft.VisualStudio.Code.ExtensionKind" Value="workspace"/>
<Property Id="Microsoft.VisualStudio.Code.LocalizedLanguages" Value=""/>
<Property Id="Microsoft.VisualStudio.Code.EnabledApiProposals" Value=""/></Properties></Metadata>
<Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation><Dependencies/>
<Assets><Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
<Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true"/>
<Asset Type="Microsoft.VisualStudio.Services.Content.License" Path="extension/LICENSE" Addressable="true"/></Assets></PackageManifest>'''
    extension_entries = [
        ("extension.vsixmanifest", xml.encode()),
        ("extension/package.json", (ROOT / "adapters/vscode/package.json").read_bytes()),
        ("extension/extension.js", (ROOT / "adapters/vscode/extension.js").read_bytes()),
        ("extension/README.md", (ROOT / "docs/install-vscode.md").read_bytes()),
        ("extension/LICENSE", (ROOT / "LICENSE").read_bytes()),
        *[("extension/assets/wuhang-novel/" + name, data) for name, data in skill_entries]]
    mime = {".json": "application/json", ".js": "application/javascript", ".md": "text/markdown",
            ".py": "text/x-python", ".yaml": "text/yaml", ".vsixmanifest": "text/xml"}
    # Explicit parts also cover extensionless LICENSE and dotfiles without an invalid empty Extension.
    parts = "".join(f'<Override PartName="{quote("/" + name)}" ContentType="{mime.get(Path(name).suffix, "text/plain")}"/>'
                    for name, _ in extension_entries)
    types = '<?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' + parts + '</Types>'
    emit(f"wuhang-novel-skill-{VERSION}.vsix", extension_entries + [("[Content_Types].xml", types.encode())])
    manifest = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in products)
    (dist / "SHA256SUMS").write_text(manifest)
    return products


if __name__ == "__main__":
    for product in build():
        print(f"{product.name}: {product.stat().st_size:,} bytes")
