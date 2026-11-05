#!/usr/bin/env python3
"""Count body Han characters and punctuation; exclude the first chapter title."""
import argparse
import json
import re
import unicodedata
from pathlib import Path


def count_chinese_words(text):
    lines = text.lstrip("\ufeff").splitlines()
    first = next((i for i, line in enumerate(lines) if line.strip()), None)
    if first is not None:
        title = lines[first].strip()
        if title.startswith("#") or re.match(r"^第[\d零〇一二三四五六七八九十百千万]+章", title):
            lines.pop(first)
    # Remove Markdown link destinations, inline markup, and HTML tags.
    body = "\n".join(lines)
    body = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"<[^>]*>", "", body)
    body = re.sub(r"(?m)^\s*(?:#{1,6}\s+|[-*+]\s+|>\s*)", "", body)
    body = re.sub(r"[`*_~]", "", body)
    def counted(char):
        code = ord(char)
        return (0x3400 <= code <= 0x4DBF or 0x4E00 <= code <= 0x9FFF
                or 0xF900 <= code <= 0xFAFF or 0x20000 <= code <= 0x323AF
                or unicodedata.category(char).startswith("P"))
    return sum(counted(char) for char in body)


def report(paths, minimum=2300, maximum=4000):
    if minimum < 0 or maximum < minimum:
        raise ValueError("字数范围无效")
    rows = []
    for path in paths:
        count = count_chinese_words(path.read_text(encoding="utf-8-sig"))
        rows.append({"file": str(path), "words": count,
                     "status": "不足" if count < minimum else "超出建议范围" if count > maximum else "达标"})
    total = sum(row["words"] for row in rows)
    return {"metric": "正文汉字及标点，不含首行标题、英文、数字；非平台官方统计",
            "range": {"min": minimum, "max": maximum}, "chapters": rows,
            "count": len(rows), "total": total, "average": round(total / len(rows), 2) if rows else 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path)
    parser.add_argument("--project", type=Path, help="按此项目配置统计 4-正文 中的 Markdown/TXT")
    parser.add_argument("--min", dest="minimum", type=int)
    parser.add_argument("--max", dest="maximum", type=int)
    args = parser.parse_args()
    try:
        limits = {"min": 2300, "max": 4000}
        if args.project:
            config = args.project / ".novelkit/config.json"
            if config.exists():
                limits.update(json.loads(config.read_text(encoding="utf-8"))["chapter_words"])
        if args.minimum is not None:
            limits["min"] = args.minimum
        if args.maximum is not None:
            limits["max"] = args.maximum
        paths = args.files
        if not paths and args.project:
            paths = sorted(p for p in (args.project / "4-正文").glob("*")
                           if p.is_file() and p.suffix.lower() in (".md", ".txt"))
        if not paths:
            raise ValueError("未找到正文文件；请传文件路径或 --project 小说目录")
        if any(not isinstance(limits[k], int) or isinstance(limits[k], bool) for k in ("min", "max")):
            raise ValueError("字数范围必须为整数")
        result = report(paths, limits["min"], limits["max"])
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"统计失败：{error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
