# Notes for Part 5 (Designing the system: chapters 21–24)

| Idea | Source |
|---|---|
| Start from the simplest architecture and add components as needs arise: context, guardrails, router and gateway, caches, agent patterns; monitoring and orchestration alongside. | AIE ch. 10, "AI Engineering Architecture" and its five steps |
| An application converts the user problem into the model domain and back; the loop grows in complexity. | PE ch. 4, "The Anatomy of the Loop", "Exploring the Complexity of the Loop" |
| Plan an AI application from the use case: the role of AI and humans, expectations, milestones, the last-mile challenge. | AIE ch. 1, "Planning AI Applications", "Setting Expectations", "Milestone Planning" |
| Text-to-SQL as RAG over tabular data; a worked workflow design. | AIE ch. 6, "RAG with tabular data"; PE ch. 9, "Example Workflow: Shopify Plug-in Marketing" |

## This book's own material (not from the three books)

- Chapter 21: the eight-stage replay and its table reuse failures and measurements from chapters 4–19. The "ordinary
  service" layout is a typical design; the book's app has no web API, queue or CI.
- Chapter 22: the seven questions, the four tables and the picker are a summary of the earlier chapters. The
  budget table rounds measured times; its token counts are estimates.
- Chapter 23: four designs on paper. **None was built or run.** Costs are assumed token counts times the example
  prices (computed: $0.000965, $0.00135, $0.012, $0.09 per use).
- Chapter 24: the weekend plan, the habits for working with a coding assistant, the list of mistakes and the starter
  projects are advice, drawn from what happened while the app was built.
- The app is about 900 lines of Python across six files (`wc -l app/*.py`: 922 on 2026-11-22).
