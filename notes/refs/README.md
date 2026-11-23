# Notes behind the "From the books" pop-ups

One file per source book: `refs-aie.json` (*AI Engineering*, Chip Huyen), `refs-pe.json` (*Prompt Engineering for
LLMs*, John Berryman and Albert Ziegler) and `refs-hollm.json` (*Hands-On Large Language Models*, Jay Alammar and
Maarten Grootendorst). Per chapter: what it covers, its main ideas, when to read it, and a note on each section this
book cites. `uv run python shared/tools/build_refs.py .
and `shared/tools/check.py` fails if a page cites a chapter or section with no note.

**What they are.** Short summaries in our own words, not quotes, to help you decide which chapter of which book to
read next. Chapter and section titles match the books, and the numbers in the notes were checked against them. They
do not replace the books: read the originals for the full argument, the figures and the details.
