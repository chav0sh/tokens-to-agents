# Notes for Part 3 (Building the flow: chapters 12–16)

Ideas used, and where each came from. Restated in our own words on the pages.

| Idea | Source |
|---|---|
| Tools extend what a model can do: knowledge augmentation (read), capability extension (calculator, code), write actions (which carry the most risk). | AIE ch. 6, "Tools" |
| Function calling: the model is given tool definitions and returns the tool name and arguments; the application executes. | AIE ch. 6, "Function calling"; PE ch. 8, "Tool Usage", "LLMs Trained for Tool Usage" |
| Tool definitions are prompts: clear names, descriptions, few and simple arguments, readable errors. | PE ch. 8, "Guidelines for Tool Definitions" |
| An agent perceives an environment and acts on it with tools; planning can be sequential, parallel, conditional or a loop; agents fail in planning, in tool use and in efficiency. | AIE ch. 6, "Agent Overview", "Planning", "Complex plans", "Agent Failure Modes and Evaluation" |
| ReAct: interleave reasoning and acting, observing each result. | PE ch. 8, "ReAct: Iterative Reasoning and Action"; HOLLM ch. 7, "Agents: Creating a System of LLMs" |
| A workflow of fixed tasks is often better than a conversational agent; agents can drive parts of a workflow. | PE ch. 9, "Would a Conversational Agent Suffice?", "Basic LLM Workflows", "Advanced LLM Workflows" |
| Chains connect prompt templates and models; memory as a buffer, a window or a summary of the conversation. | HOLLM ch. 7, "Chains: Extending the Capabilities of LLMs", "Memory: Helping LLMs to Remember Conversations" |
| Memory: internal knowledge, short-term (the context) and long-term (external storage, retrieved). | AIE ch. 6, "Memory" |
| An orchestrator defines components and chains them; judge one by integration, extensibility and support for complex pipelines. | AIE ch. 10, "AI Pipeline Orchestration" |

## Run, not from the books (2026-11-22, `app/agent.py`, `nvidia/nemotron-3.5-lightning-30b-a3b`)

- Chapter 12: the raw tool call (421 input tokens, 28 output).
- Chapter 13: the agent loop's three steps and its answer; the workflow's wrong first answer ("12 days total") and
  the right one after the comparison moved into code; the router test (first prompt 5/8 and 6/8 in two runs, final
  prompt 7/8 in both; the miss is the injection attempt).
- Chapter 14: the pipe chain's output and `create_agent`'s three messages (langchain 1.4.9, langchain-core 1.7.6).
- Chapter 15: the graph (langgraph 1.2.20) and its answer.
- Chapter 16: the follow-up with and without saved history; the MCP round trip (`mcp` 2.3.0, run with
  `uv run --with mcp`; the package is not a dependency of this repo).

## Things that went wrong while writing, kept because they teach

- **The router first used `with_structured_output`.** In one run it worked; minutes later the provider rejected the
  same request with HTTP 400 (`unknown field guided_json`) on every attempt, while a different schema still worked.
  The router now uses tool calling with `tool_choice="required"`. Chapter 19 can use this as a real example of a
  provider changing under you. Chapter 1's structured-output snippet still ran when retried.
- **The MCP Python SDK changed its API between versions 1 and 2** (`FastMCP` became `MCPServer`, the client class
  changed). My first attempt used the version 1 names and failed. Chapter 16 says which version its code is for.
- **The first router prompt misrouted Maria's holiday question as "other"** in the very first run (with structured
  output). With tool calling the same prompt got that question right. Small models are not stable classifiers.

## Not from the books and not run

- None of the books covers LangGraph or MCP.
- LangGraph interrupts (human in the loop), resume after a crash, the SQLite and Postgres savers; MCP resources,
  prompts and the HTTP transport: described from documentation and general knowledge.
- The tables of alternative frameworks and memory products.
