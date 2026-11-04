# Task Adherence Rubric

Evaluates how well the skill followed its own documented instructions and workflow.

## Evaluation Criteria

Score whether the skill followed its documented behavior:

1. **Format adherence** — Did the output match the expected format described in the skill?
2. **Workflow adherence** — Did the skill follow its documented steps/process?
3. **Scope adherence** — Did the skill stay within its defined scope (no overreach)?
4. **Constraint adherence** — Did the skill respect stated constraints and limitations?

## Rating Levels

| Score | Label | Description |
|-------|-------|-------------|
| 5 | Excellent | Perfectly followed all documented instructions. Output matches expected format and scope. |
| 4 | Good | Mostly adhered to instructions. Minor deviations that don't affect usefulness. |
| 3 | Adequate | Followed core instructions but missed some steps or format requirements. |
| 2 | Poor | Significant deviations from documented behavior. Output doesn't match expectations. |
| 1 | Very Poor | Completely ignored documented instructions. Output bears no resemblance to expected behavior. |

## Output Format

Return JSON:
```json
{"explanation": "<15-60 words on adherence>", "score": <1-5>}
```