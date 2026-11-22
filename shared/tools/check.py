"""Checks one book: the chapter list, the files, the links and the chapter template agree.

Run from the repository root (no output and exit 0 means fine):
    uv run python shared/tools/check.py .
"""

import json
import re
import sys
from pathlib import Path

if len(sys.argv) != 2:
    sys.exit(__doc__)
BOOK = Path(sys.argv[1])
SECTIONS = ["problem", "picture", "how", "when", "tools", "app", "books"]  # the chapter template, in order


def main() -> int:
    problems: list[str] = []

    # The book's one chapter list lives in its assets/book.js: { file: "x.html", ..., ready: true }
    js = (BOOK / "assets" / "book.js").read_text(encoding="utf-8")
    entries = re.findall(r'file:\s*"([^"]+)".*?ready:\s*(true|false)', js)
    if not entries:
        problems.append("book.js: no chapter entries found")
    ready = {name for name, flag in entries if flag == "true"}

    on_disk = {p.name for p in BOOK.glob("*.html")} - {"index.html"}
    problems += [f"{name}: listed as ready but the file is missing" for name in sorted(ready - on_disk)]
    problems += [f"{name}: file exists but is not a ready entry in book.js" for name in sorted(on_disk - ready)]

    for page in sorted(BOOK.glob("*.html")):
        html = page.read_text(encoding="utf-8")

        # Every local link and script/style/image must resolve.
        for target in re.findall(r'(?:href|src)="([^"#]+)(?:#[^"]*)?"', html):
            if re.match(r"^(https?:|mailto:|data:)", target):
                continue
            if not (BOOK / target).exists():
                problems.append(f"{page.name}: broken link to {target}")

        # Numbered chapters follow the seven-section template.
        if re.match(r"^(0[1-9]|[12]\d)-", page.name):
            found = re.findall(r'<section[^>]*data-s="([^"]+)"', html)
            if found != SECTIONS:
                problems.append(f"{page.name}: sections are {found}, expected {SECTIONS}")
            if not re.search(r'class="(steps|figure|stack|chart|canvas|compare)', html):  # any kind of diagram
                problems.append(f"{page.name}: no diagram")
            if 'class="refs"' not in html and 'class="ref-card' not in html:
                problems.append(f"{page.name}: no book references")

    problems += _missing_lab_numbers()
    problems += _missing_book_refs()
    problems += _broken_canvases()
    print("\n".join(problems), end="\n" if problems else "")
    return 1 if problems else 0


def _missing_lab_numbers() -> list[str]:
    """Book 2 fills numbers from assets/lab-data.js (<span data-lab="latency.total.p95">); each path must exist."""
    data_file = BOOK / "assets" / "lab-data.js"
    if not data_file.exists():
        return []
    lab = json.loads(data_file.read_text(encoding="utf-8").split("const LAB = ", 1)[1].rstrip().rstrip(";"))
    problems = []
    for page in sorted(BOOK.glob("*.html")):
        for path in re.findall(r'data-(?:lab|rows)="([^"]+)"', page.read_text(encoding="utf-8")):
            value = lab
            for key in path.split("."):  # a number picks a list item: cost.rows.0.per_month
                if isinstance(value, list) and key.isdigit() and int(key) < len(value):
                    value = value[int(key)]
                else:
                    value = value.get(key) if isinstance(value, dict) else None
            if value is None:
                problems.append(f"{page.name}: no lab number at {path}")
    return problems


def _missing_book_refs() -> list[str]:
    """Every "From the books" card must point at a chapter, and at sections, that assets/book-refs.js has notes on."""
    refs_file = BOOK / "assets" / "book-refs.js"
    if not refs_file.exists():
        return []
    text = refs_file.read_text(encoding="utf-8")
    refs = json.loads(text.split("const BOOK_REFS = ", 1)[1].strip().rstrip(";"))
    problems = []
    for page in sorted(BOOK.glob("*.html")):
        cards = re.findall(r'data-ref="([^"]+)"(?:\s+data-sections="([^"]*)")?', page.read_text(encoding="utf-8"))
        for key, sections in cards:
            if key not in refs:
                problems.append(f"{page.name}: no notes for {key}")
                continue
            problems += [
                f"{page.name}: {key} has no note on section '{title}'"
                for title in filter(None, sections.split("|"))
                if title not in refs[key]["sections"]
            ]
    return problems


def _broken_canvases() -> list[str]:
    """Book 2's system canvases are JSON: it must parse, and every link and lane must name a card that exists."""
    problems = []
    for page in sorted(BOOK.glob("*.html")):
        html = page.read_text(encoding="utf-8")
        for spec_text in re.findall(
            r'<figure class="canvas"[^>]*>\s*<script type="application/json">(.*?)</script>', html, re.S
        ):
            try:
                spec = json.loads(spec_text)
            except json.JSONDecodeError as error:
                problems.append(f"{page.name}: a canvas is not valid JSON ({error})")
                continue
            ids = {node["id"] for node in spec["nodes"]}
            named = [(edge["from"], "link") for edge in spec["edges"]] + [
                (edge["to"], "link") for edge in spec["edges"]
            ]
            named += [(node_id, "lane") for lane in spec.get("lanes", []) for node_id in lane["nodes"]]
            problems += [
                f"{page.name}: a canvas {what} names a missing card '{node_id}'"
                for node_id, what in named
                if node_id not in ids
            ]
    return problems


if __name__ == "__main__":
    sys.exit(main())
