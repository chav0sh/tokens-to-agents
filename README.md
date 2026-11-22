# Tokens to Agents

**AI engineering for back-end developers, drawn.**

You already build APIs, queues and databases. This book adds the model: the patterns every AI product uses, the
tools that fill each slot, and how to design a whole system from them. It is a visual book of 25 short chapters,
each with a diagram, a worked example on real numbers, when to use the pattern and when to skip it, and the
tools that fill the slot. One small app, a docs assistant, runs through the whole book and gets one piece better
in every chapter.

## Read it

Open `index.html` in a browser. The book is plain HTML, CSS and JavaScript: no server, no build step, no account,
and it works offline. Start with "The whole system on one page".

## Contents

| Part | Chapter |
|---|---|
| 0. Start here | [The whole system on one page](00-start.html) |
| 1. The model | [The LLM as an API](01-llm-api.html) |
|  | [Prompts](02-prompts.html) |
|  | [Choosing a model](03-choosing-a-model.html) |
| 2. Giving it context | [RAG: the whole pattern](04-rag.html) |
|  | [Embeddings](05-embeddings.html) |
|  | [Vector databases](06-vector-databases.html) |
|  | [Keyword search: BM25](07-keyword-search.html) |
|  | [Hybrid search and reranking](08-hybrid-search.html) |
|  | [Chunking and indexing](09-chunking.html) |
|  | [Graph databases](10-graph-databases.html) |
|  | [GraphRAG](11-graphrag.html) |
| 3. Building the flow | [Tool calling](12-tool-calling.html) |
|  | [Workflows and agents](13-workflows-and-agents.html) |
|  | [LangChain](14-langchain.html) |
|  | [LangGraph](15-langgraph.html) |
|  | [Memory and MCP](16-memory-and-mcp.html) |
| 4. Keeping it reliable | [Evals](17-evals.html) |
|  | [Guardrails and prompt injection](18-guardrails.html) |
|  | [Monitoring, cost, caching](19-monitoring.html) |
|  | [Finetuning: when you need it](20-finetuning.html) |
| 5. Designing the system | [The architecture, step by step](21-architecture.html) |
|  | [Problem → pattern → tool](22-design-method.html) |
|  | [Reference architectures](23-reference-architectures.html) |
|  | [Your build plan](24-build-plan.html) |
| Compare | [Compare and combine](compare.html) |
| Extras | [Case study: the voting assistant](case-voting.html) |
|  | [Pattern cheat sheet](cheat-sheet.html) |
|  | [Interview questions](interview.html) |
|  | [Glossary](glossary.html) |
|  | [References by book](references.html) |

## The app behind the book

`app/` holds the docs assistant the chapters build. It answers employees' questions from a small company handbook
(`app/handbook.md`) and names the document it used. The numbers on the pages come from running it.

| File | What it shows | Chapters |
|---|---|---|
| `app/assistant.py` | The assistant in one file: chunking, embeddings, keyword and vector search, rank fusion, reranking, the model call | 1 to 9 |
| `app/graph.py` | An org chart in Neo4j, and GraphRAG: handbook passages plus facts from the graph | 10, 11 |
| `app/agent.py` | Tool calling, a workflow, an agent loop, and the same flow as a LangGraph graph with memory | 12 to 16 |
| `app/mcp_server.py`, `app/mcp_client.py` | A tool behind the Model Context Protocol | 16 |
| `app/reliability.py` | Evals with code checks and a model as judge, prompt-injection attacks and defences, timing and caching | 17 to 19 |
| `notes/figures.py` | The worked numbers the chapters quote (similarities, scores) | 4 to 9 |

### What you need

- Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).
- For answers from a model: an NVIDIA API key from [build.nvidia.com](https://build.nvidia.com). The app calls
  `nvidia/nemotron-3.5-lightning-30b-a3b`. The search scoreboard runs without a key.
- For the graph chapters: Docker, to run a throwaway Neo4j.

### Set up

```
git clone <this repository's URL> tokens-to-agents
cd tokens-to-agents
uv sync                          # creates .venv with the pinned dependencies
cp .env.example .env             # then paste your key after NVIDIA_API_KEY=
```

### Run

```
uv run python app/assistant.py --eval                                    # the search scoreboard (no key)
uv run python app/assistant.py --explain "When do I need FIN-140?"       # what each search found (no key)
uv run python app/assistant.py "What do I do if my computer is stolen?"  # one answer from the model
uv run python app/agent.py                                               # tools, workflow, agent, LangGraph
uv run python app/mcp_client.py                                          # starts the MCP server and calls its tool
uv run python app/reliability.py evals                                   # also: attacks, trace
uv run python notes/figures.py                                           # the worked numbers (no key)
```

The first search run downloads two small models for your CPU (`BAAI/bge-small-en-v1.5` for embeddings and
`Xenova/ms-marco-MiniLM-L-6-v2` for reranking), once. The vector store is Qdrant running in memory, so there is no
database to install for chapters 1 to 9.

For the graph chapters, start Neo4j, run the examples, then stop it:

```
docker run -d --rm --name tta-neo4j -p 127.0.0.1:7688:7687 -e NEO4J_AUTH=neo4j/tokens-to-agents-local neo4j:5.26.32
uv run python app/graph.py                                                # load the org chart, run the queries
uv run python app/graph.py "I'm Maria Lind. Who has to approve my expense claim of 800 euros?"   # needs the key
docker stop tta-neo4j
```

## Checks

```
uv run python shared/tools/check.py .         # chapter list, links, page template, references
uv run python shared/tools/build_refs.py .    # rebuild the "From the books" pop-ups from notes/refs/
uv run ruff check . && uv run pyright         # lint and type checks for the Python
uv run pre-commit install                     # optional: ruff and a secret scanner on every commit
```

## Layout

```
index.html, 00-start.html … 24-build-plan.html    the chapters
compare.html, case-voting.html, cheat-sheet.html, interview.html, glossary.html, references.html    the extras
assets/        this book's script and data (chapter list, scoreboard data, reference pop-ups)
shared/        styles, page script and the check tools
app/           the docs assistant
notes/         where the worked numbers and the reference notes come from
```

## Sources

The chapters draw on three books, credited on every page under "From the books": *AI Engineering* (Chip Huyen),
*Hands-On Large Language Models* (Jay Alammar and Maarten Grootendorst) and *Prompt Engineering for LLMs* (John
Berryman and Albert Ziegler). Those books are not included; the notes in `notes/refs/` are paraphrases. The tool
names in each chapter are general knowledge as of November 2026; check a tool's own documentation before you adopt it.

## Next

*Prototype to Production*, the companion book, takes the same docs assistant into a real company and designs the
system around it: targets, data, serving, release, monitoring and improvement.

## License

Copyright 2026. All rights reserved. No open-source licence has been chosen yet.
