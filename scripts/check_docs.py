#!/usr/bin/env python3
"""Validate local Markdown links and roadmap dependencies without downloads."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

EXCLUDED = {
    ".git",
    ".venv",
    ".superpowers",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "data",
    "models",
    "artifacts",
    "dist",
    "build",
    "coverage",
    "htmlcov",
}
STORY = re.compile(r"\bS\d{2}\.\d{2}\b")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")


def prose(text: str) -> str:
    """Exclude fenced examples when finding headings and document links."""
    return re.sub(r"^```[^\n]*\n.*?^```[ \t]*$", "", text, flags=re.M | re.S)


def anchors(text: str) -> set[str]:
    result: set[str] = set()
    counts: dict[str, int] = {}
    for heading in re.findall(r"^#{1,6}\s+(.+)$", prose(text), re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        number = counts.get(slug, 0)
        result.add(slug if number == 0 else f"{slug}-{number}")
        counts[slug] = number + 1
    return result


def validate(root: Path) -> tuple[list[str], int, int]:
    files = sorted(
        path
        for path in root.rglob("*.md")
        if not EXCLUDED.intersection(path.relative_to(root).parts)
    )
    errors: list[str] = []
    texts = {path: path.read_text(encoding="utf-8") for path in files}
    link_count = 0

    for path, text in texts.items():
        relative = path.relative_to(root)
        if not text.endswith("\n"):
            errors.append(f"{relative}: missing final newline")
        if len(re.findall(r"^```", text, re.M)) % 2:
            errors.append(f"{relative}: unbalanced code fences")
        for number, line in enumerate(text.splitlines(), 1):
            if line != line.rstrip():
                errors.append(f"{relative}:{number}: trailing whitespace")
        for target in LINK.findall(prose(text)):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            link_count += 1
            destination = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not destination.is_relative_to(root):
                errors.append(f"{relative}: link escapes repository: {target}")
            elif not destination.exists():
                errors.append(f"{relative}: missing target: {target}")
            elif parsed.fragment and destination.suffix == ".md":
                content = texts.get(destination)
                if content is None:
                    content = destination.read_text(encoding="utf-8")
                if unquote(parsed.fragment) not in anchors(content):
                    errors.append(f"{relative}: missing heading: {target}")

    roadmap = root / "docs" / "ROADMAP.md"
    if roadmap in texts:
        text = texts[roadmap]
        blocks = re.split(r"^### (S\d{2}\.\d{2}) — .+$", text, flags=re.M)
        ids = blocks[1::2]
        if len(ids) != len(set(ids)):
            errors.append("ROADMAP.md: duplicate story IDs")
        dependencies: dict[str, list[str]] = {}
        for index in range(1, len(blocks), 2):
            story_id, block = blocks[index : index + 2]
            if not re.search(r"^- \[[ x]\] As an? ", block, re.M):
                errors.append(f"{story_id}: missing user-story checkbox")
            if "**Acceptance:**" not in block:
                errors.append(f"{story_id}: missing acceptance criteria")
            line = next((line for line in block.splitlines() if "**Dependencies:**" in line), "")
            if not line:
                errors.append(f"{story_id}: missing dependencies")
            dependencies[story_id] = STORY.findall(line)
        for path, content in texts.items():
            for story_id in set(STORY.findall(content)) - set(ids):
                errors.append(f"{path.relative_to(root)}: unknown story {story_id}")

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(story_id: str) -> None:
            if story_id in visiting:
                errors.append(f"ROADMAP.md: dependency cycle at {story_id}")
                return
            if story_id in visited:
                return
            visiting.add(story_id)
            for dependency in dependencies.get(story_id, []):
                visit(dependency)
            visiting.remove(story_id)
            visited.add(story_id)

        for story_id in ids:
            visit(story_id)

    return errors, len(files), link_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors, files, links = validate(args.root.resolve())
    for error in errors:
        print(f"ERROR: {error}")
    print(f"Checked {files} Markdown files and {links} local links: {'FAIL' if errors else 'PASS'}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
