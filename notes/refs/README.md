# Notes behind the "From the books" pop-ups

One file per source book. Per chapter: what it covers, its main ideas, when to read it, and a note on each section
the book cites. `notes/build_refs.py` turns these into `assets/book-refs.js`.

**How they were written (2026-11-22).** Three Sonnet 5.5 agents, one per book, read the cited sections in the
extracted book text and wrote the notes in their own words. Then a sample was checked by hand against the text:
five sections of *AI Engineering* (hybrid search and rank fusion, chunking, sampling, finetuning and RAG, caches),
two of *Prompt Engineering for LLMs* (the ideal prompt, the loop) and two of *Hands-On Large Language Models*
(chunking long texts, reranking, including its quoted benchmark numbers). All matched. The other notes were not
individually checked.

**Known limits, as reported by the agents.** The text has no figures. For *AI Engineering* ch. 8 and 9, and
*Hands-On LLMs* ch. 11, the chapter-level ideas come from the parts read plus headings, not a full read. A few
sub-sections of *Prompt Engineering for LLMs* ch. 2, 3 and 6 were not read in detail.


## Audit (2026-11-22, by hand, no agents)

Checked every note in both books against the extracted text of the five source books:

- All 52 chapter titles and all 247 cited section titles appear verbatim in their book.
- All 73 numbers in the notes appear in the book; 71 of them next to at least two of the same words the note uses
  around them, and the other two (p999, p90/p95/p99) were confirmed by reading.
- Sampled claims read against the passage they summarise, all found: Kleppmann on schemas as documentation, moving
  as little data as possible, three ways to route requests, error handling without transactions, weak isolation;
  *AI Engineering* on 95% per step over 10 steps, 56 GB for a 7B model, prompt caching up to 90%; *Designing ML
  Systems* on bandits needing less data and the build-versus-buy factors; *Hands-On LLMs* on F1 0.80 versus 0.85 and
  primacy and recency; *Prompt Engineering for LLMs* on the Valley of Meh, the sandwich and refocus, the Little Red
  Riding Hood principle, special tokens users cannot send, options sharing a first token, and evaluation written first.
- The notes are paraphrases, not quotes. Chapter-level "main ideas" for chapters only partly read rest on the
  sections read plus the headings, as noted above; their sampled claims held up.
