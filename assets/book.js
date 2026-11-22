// This book's own script: its chapter list and the "system so far" strip.
// Everything both books do (sidebar, previous/next, tabs, pop-ups, diagram colours) is in shared/book.js,
// which every page loads just before this file.

// One entry per page, in reading order. `ready: false` shows greyed, with no link.
// `lit` = how many STAGES the docs assistant has after this chapter (leave out for pages without the strip).
const CHAPTERS = [
  { file: "00-start.html", part: "0. Start here", title: "The whole system on one page", lit: 0, ready: true },
  { file: "01-llm-api.html", part: "1. The model", title: "The LLM as an API", lit: 1, ready: true },
  { file: "02-prompts.html", part: "1. The model", title: "Prompts", lit: 2, ready: true },
  { file: "03-choosing-a-model.html", part: "1. The model", title: "Choosing a model", lit: 2, ready: true },
  { file: "04-rag.html", part: "2. Giving it context", title: "RAG: the whole pattern", lit: 3, ready: true },
  { file: "05-embeddings.html", part: "2. Giving it context", title: "Embeddings", lit: 3, ready: true },
  { file: "06-vector-databases.html", part: "2. Giving it context", title: "Vector databases", lit: 3, ready: true },
  { file: "07-keyword-search.html", part: "2. Giving it context", title: "Keyword search: BM25", lit: 4, ready: true },
  { file: "08-hybrid-search.html", part: "2. Giving it context", title: "Hybrid search and reranking", lit: 5, ready: true },
  { file: "09-chunking.html", part: "2. Giving it context", title: "Chunking and indexing", lit: 5, ready: true },
  { file: "10-graph-databases.html", part: "2. Giving it context", title: "Graph databases", lit: 6, ready: true },
  { file: "11-graphrag.html", part: "2. Giving it context", title: "GraphRAG", lit: 6, ready: true },
  { file: "12-tool-calling.html", part: "3. Building the flow", title: "Tool calling", lit: 7, ready: true },
  { file: "13-workflows-and-agents.html", part: "3. Building the flow", title: "Workflows and agents", lit: 8, ready: true },
  { file: "14-langchain.html", part: "3. Building the flow", title: "LangChain", lit: 8, ready: true },
  { file: "15-langgraph.html", part: "3. Building the flow", title: "LangGraph", lit: 8, ready: true },
  { file: "16-memory-and-mcp.html", part: "3. Building the flow", title: "Memory and MCP", lit: 8, ready: true },
  { file: "17-evals.html", part: "4. Keeping it reliable", title: "Evals", lit: 9, ready: true },
  { file: "18-guardrails.html", part: "4. Keeping it reliable", title: "Guardrails and prompt injection", lit: 10, ready: true },
  { file: "19-monitoring.html", part: "4. Keeping it reliable", title: "Monitoring, cost, caching", lit: 11, ready: true },
  { file: "20-finetuning.html", part: "4. Keeping it reliable", title: "Finetuning: when you need it", lit: 11, ready: true },
  { file: "21-architecture.html", part: "5. Designing the system", title: "The architecture, step by step", lit: 11, ready: true },
  { file: "22-design-method.html", part: "5. Designing the system", title: "Problem → pattern → tool", lit: 11, ready: true },
  { file: "23-reference-architectures.html", part: "5. Designing the system", title: "Reference architectures", lit: 11, ready: true },
  { file: "24-build-plan.html", part: "5. Designing the system", title: "Your build plan", lit: 11, ready: true },
  { file: "compare.html", part: "Compare", title: "Compare and combine", ready: true },
  { file: "case-voting.html", part: "Extras", title: "Case study: the voting assistant", ready: true },
  { file: "cheat-sheet.html", part: "Extras", title: "Pattern cheat sheet", ready: true },
  { file: "interview.html", part: "Extras", title: "Interview questions", ready: true },
  { file: "glossary.html", part: "Extras", title: "Glossary", ready: true },
  { file: "references.html", part: "Extras", title: "References by book", ready: true },
];

// The docs assistant, one piece per stage, in the order the book adds them. `idea` picks the colour.
const STAGES = [
  ["Model", "model"], ["Prompt", "model"],
  ["Vectors", "retrieval"], ["Keywords", "retrieval"], ["Hybrid", "retrieval"],
  ["Graph", "graphdb"],
  ["Tools", "flow"], ["Flow", "flow"],
  ["Evals", "reliability"], ["Guardrails", "reliability"], ["Monitoring", "reliability"],
];

const IDEAS = ["model", "retrieval", "graphdb", "flow", "reliability"];

// Parts 1-4 each belong to one idea, so they carry its colour in the sidebar and the contents.
const PART_IDEA = { 1: "model", 2: "retrieval", 3: "flow", 4: "reliability" };

// The strip: every piece of the docs assistant, lit up to `lit`.
function strip(lit) {
  const items = STAGES.map(
    ([name, idea], i) => `<li class="${idea}${i < lit ? " lit" : ""}">${name}</li>`,
  );
  const label = lit === 0 ? "Nothing built yet" : `${lit} of ${STAGES.length} pieces built`;
  return `<ol class="strip" aria-label="The docs assistant so far: ${label}">${items.join("")}</ol>`;
}

startBook({
  title: "Tokens to <em>Agents</em>",
  chapters: CHAPTERS,
  partClass: (part) => PART_IDEA[part[0]] || "",
  ideas: IDEAS,
});

document.querySelectorAll("[data-strip]").forEach((el) => {
  el.innerHTML = strip(Number(el.dataset.strip));
});

// On a chapter: the strip under the title.
const chapter = CHAPTERS.find((c) => c.file === here);
const h1 = document.querySelector("main h1");
if (chapter && h1 && chapter.lit !== undefined) h1.insertAdjacentHTML("afterend", strip(chapter.lit));
