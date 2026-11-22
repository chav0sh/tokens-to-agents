# Notes for Part 0 (Start here)

Ideas used on `00-start.html`, and where each came from. Restated in our own words on the page.

| Idea | Source |
|---|---|
| The AI stack has three layers: application development, model development, infrastructure. You start at the top and move down only as needed. | AIE ch. 1, "Three Layers of the AI Stack" |
| AI engineering differs from ML engineering in three ways: you adapt a model someone else trained instead of training one; the models are bigger, slower and cost more per call; outputs are open-ended, so evaluation is a much bigger problem. | AIE ch. 1, "AI Engineering Versus ML Engineering" |
| Two ways to adapt a model: prompt-based (instructions and context, weights unchanged) and finetuning (weights change). Prompt-based is easier to start with and needs less data. | AIE ch. 1, "AI Engineering Versus ML Engineering" |
| ML knowledge is no longer required to build AI applications, though it still helps. | AIE ch. 1, "Model development" |
| The simplest architecture is query → model → response. Components are then added as needs arise: context, guardrails, router and gateway, cache, agent patterns; then monitoring and orchestration. | AIE ch. 10, "AI Engineering Architecture" |
| Context construction (retrieval and tools) is usually the first thing added. | AIE ch. 10, "Step 1. Enhance Context" |
| An LLM application is a loop: the user's problem is converted into the model's domain (text), the model completes it, and the completion is converted back into the user's domain. | PE ch. 4, "The Anatomy of the Loop" |

Our own framing, not from the books: the back-end column of the comparison table, the docs-assistant example and
its diagram, the reading routes.
