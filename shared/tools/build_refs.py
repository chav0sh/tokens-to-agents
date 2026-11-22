"""Builds a book's assets/book-refs.js, the data behind the "From the books" pop-ups, from its notes/refs/*.json.

Run from the repository root:
    uv run python shared/tools/build_refs.py .

Each JSON file holds one source book: per chapter, what it covers, its main ideas, when to read it, and a note on
each section this book cites. The notes were written from the books' text (see notes/refs/README.md).
"""

import html
import json
import sys
from pathlib import Path

if len(sys.argv) != 2:
    sys.exit(__doc__)
BOOK_DIR = Path(sys.argv[1])
NOTES = BOOK_DIR / "notes" / "refs"
TARGET = BOOK_DIR / "assets" / "book-refs.js"

BOOKS = {
    "AIE": {"title": "AI Engineering", "authors": "Chip Huyen (O'Reilly)"},
    "HOLLM": {
        "title": "Hands-On Large Language Models",
        "authors": "Jay Alammar and Maarten Grootendorst (O'Reilly)",
    },
    "PE": {"title": "Prompt Engineering for LLMs", "authors": "John Berryman and Albert Ziegler (O'Reilly)"},
    "DDIA": {"title": "Designing Data-Intensive Applications", "authors": "Martin Kleppmann (O'Reilly)"},
    "DMLS": {"title": "Designing Machine Learning Systems", "authors": "Chip Huyen (O'Reilly)"},
}


def clean(text: str) -> str:
    """The pages insert these strings as HTML, so escape them here, once."""
    return html.escape(" ".join(text.split()), quote=False)


def load() -> dict:
    refs: dict = {}
    for path in sorted(NOTES.glob("refs-*.json")):
        for key, chapter in json.loads(path.read_text(encoding="utf-8")).items():
            refs[key] = {
                "chapter": clean(chapter["chapter"]),
                "about": clean(chapter["about"]),
                "ideas": [clean(idea) for idea in chapter["ideas"]],
                "read_when": clean(chapter["read_when"]),
                "sections": {title: clean(note) for title, note in chapter["sections"].items()},
            }
    return refs


def main() -> None:
    refs = load()
    body = (
        "// Written by shared/tools/build_refs.py from notes/refs/*.json. Do not edit by hand.\n"
        f"const BOOKS = {json.dumps(BOOKS, ensure_ascii=False)};\n"
        f"const BOOK_REFS = {json.dumps(refs, ensure_ascii=False)};\n"
    )
    TARGET.write_text(body, encoding="utf-8")
    print(f"wrote {TARGET.name}: {len(refs)} book chapters, {sum(len(r['sections']) for r in refs.values())} sections")


if __name__ == "__main__":
    main()
