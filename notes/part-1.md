# Notes for Part 1 (The model: chapters 1–3)

Ideas used, and where each came from. Restated in our own words on the pages.

| Idea | Source |
|---|---|
| A model produces a probability for every possible next token; one is sampled; repeat. | AIE ch. 2, "Sampling Fundamentals"; PE ch. 2, "One Token at a Time" |
| Temperature divides the logits before softmax: higher flattens, lower sharpens. | AIE ch. 2, "Sampling Strategies" (Temperature); PE ch. 2, "Temperature and Probabilities" |
| Top-k keeps the k most likely tokens; top-p keeps the smallest set whose probabilities reach p (commonly 0.9–0.95). | AIE ch. 2, "Sampling Strategies" (Top-k, Top-p) |
| 100 tokens are roughly 75 words. Tokenizers split rare words into pieces. | AIE ch. 1, "Language models"; HOLLM ch. 2, "LLM Tokenization"; PE ch. 2, "Counting Tokens" |
| Outputs vary between calls; structured output needs constraining and checking. | AIE ch. 2, "The Probabilistic Nature of AI", "Structured Outputs" |
| Chat APIs take role-tagged messages; the history is resent each call. | PE ch. 3, "Chat Completion API" |
| Prompt parts: system prompt, user prompt, examples, context. Models use the start and end of a prompt better than the middle. | AIE ch. 5, "System Prompt and User Prompt", "Context Length and Context Efficiency" |
| Ideal prompt: introduction, context, then a refocus on the question; the weak middle ("Valley of Meh"). Assemble by ranking elements and fitting a token budget. | PE ch. 6, "Anatomy of the Ideal Prompt", "Elastic Snippets", "Putting It All Together" |
| Zero-shot, few-shot, chain of thought; break a task into subtasks; version prompts and evaluate changes. | AIE ch. 5, "Prompt Engineering Best Practices"; HOLLM ch. 6; PE ch. 5 "Few-Shot Prompting", ch. 8 "Chain of Thought" |
| Model selection: filter by hard attributes, shortlist with public data, test with your own evals, monitor. API versus self-hosting: privacy, performance, cost, control. | AIE ch. 4, "Model Selection Workflow", "Model Build Versus Buy" |
| Public benchmarks narrow the list but cannot decide. | AIE ch. 4, "Navigate Public Benchmarks" |
| Time to first token and tokens per second describe latency. | AIE ch. 9, "Inference Performance Metrics" |

## Computed or run, not from the books (2026-11-22)

- Token splits: `tiktoken`, encoding `o200k_base`. 10, 14 and 12 tokens for the three sentences.
- Sampling demo: softmax of logits 5, 3.5, 3, 2, −1; at temperature 1 → 70.9%, 15.8%, 9.6%, 3.5%, 0.2%.
- Cost: prices are made up ($0.30/$2.50 and $3/$15 per million); the sums were computed.
- Latency example numbers are made up; the formula is first token + tokens ÷ speed.
- Chapter 1 snippets were run on `nvidia/nemotron-3.5-lightning-30b-a3b`; the outputs on the page are from that run.
  Chapter 2's template was run without a model call. Chapter 3's `get_llm` was only constructed, never called.
- Our own framing: the back-end comparisons, the three model tiers, the tool tables.
