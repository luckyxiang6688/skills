# Output Quality Rubric

Evaluates the overall quality of the skill's output.

## Evaluation Criteria

Score the skill's output on these dimensions:

1. **Relevance** — Is the output relevant to the user's request?
2. **Accuracy** — Is the information correct and factual?
3. **Completeness** — Does it cover the important aspects?
4. **Clarity** — Is it well-organized and easy to understand?
5. **Usefulness** — Would the output actually help the user?

## Rating Levels

| Score | Label | Description |
|-------|-------|-------------|
| 5 | Excellent | Highly relevant, accurate, complete, clear, and immediately useful. Professional quality. |
| 4 | Good | Relevant and mostly accurate. Minor gaps in completeness or clarity. Still useful. |
| 3 | Adequate | Addresses the request but with notable issues: partial coverage, some inaccuracy, or unclear presentation. |
| 2 | Poor | Tangentially relevant or substantially inaccurate. Significant gaps. Barely useful. |
| 1 | Very Poor | Irrelevant, inaccurate, or empty. Not useful at all. |

## Output Format

Return JSON:
```json
{"explanation": "<15-60 words evaluating quality>", "score": <1-5>}
```