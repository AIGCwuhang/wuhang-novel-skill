#!/usr/bin/env python3
"""Create missing novel project files without replacing author content."""
import argparse
import json
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / "assets" / "project"
EMPTY_DIRS = ("2-设定", "3-大纲", "4-正文", "5-审查")


def safe_target(root, relative):
    target = root / relative
    for part in (target, *target.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError(f"项目路径包含符号链接，未写入：{part}")
    return target


def initialize(project):
    root = Path(project).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ValueError("项目路径不是文件夹")
    sources = sorted(p for p in TEMPLATES.rglob("*") if p.is_file())
    if not sources:
        raise ValueError("缺少项目模板，请重新取得完整技能包")
    # Validate all destinations before making changes.
    for rel in [*(p.relative_to(TEMPLATES) for p in sources), *EMPTY_DIRS]:
        dest = safe_target(root, rel)
        for parent in dest.parents:
            if parent == root:
                break
            if parent.exists() and not parent.is_dir():
                raise ValueError(f"父路径不是文件夹：{parent}")
        if dest.exists() and (dest.is_dir() != (str(rel) in EMPTY_DIRS)):
            raise ValueError(f"目标类型冲突：{dest}")
    root.mkdir(parents=True, exist_ok=True)
    for relative in EMPTY_DIRS:
        safe_target(root, relative).mkdir(parents=True, exist_ok=True)
    created, preserved = [], []
    for src in sources:
        rel = src.relative_to(TEMPLATES)
        dest = safe_target(root, rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with dest.open("xb") as output:
                output.write(src.read_bytes())
            created.append(rel.as_posix())
        except FileExistsError:
            preserved.append(rel.as_posix())
    warnings = []
    if ".gitignore" in preserved:
        warnings.append("保留了已有 .gitignore；请合并模板中的密钥与缓存忽略项。")
    return {"project": str(root), "created": created, "preserved": preserved, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="小说项目文件夹，可含空格或中文")
    args = parser.parse_args()
    try:
        result = initialize(args.project)
    except (OSError, ValueError) as error:
        parser.exit(1, f"初始化未完成：{error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
