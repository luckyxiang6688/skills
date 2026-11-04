# Intent Resolution Rubric

Evaluates how well the skill resolved the user's expressed intent.

## Evaluation Criteria

You are an impartial grader that scores how well an AI skill *resolved* the user's intent.

### Steps

1. **Identify the expressed intent** from the user's prompt.
2. **Check resolution.** Does the skill's output actually complete or satisfy that intent?
   - Direct answer → does it fully address the request?
   - Action → does it confirm completion?
   - Clarification → does it progress towards fulfillment?
   - Empty/irrelevant → does not resolve the intent.
3. **Verify correctness and completeness.** Are the facts accurate? Is anything important missing?
4. **Weigh impact.** Minor style issues matter only for tie-breaking; resolution quality dominates.

## Rating Levels

| Score | Label | Description |
|-------|-------|-------------|
| 5 | Excellent | Intent fully fulfilled with accurate, thorough, relevant output. No gaps. |
| 4 | Good | Intent mostly resolved; only minor, non-blocking gaps. |
| 3 | Adequate | Core intent addressed but notable omissions or vagueness. |
| 2 | Poor | Partial or incorrect resolution. Unlikely to satisfy. |
| 1 | Very Poor | Intent ignored or badly misunderstood. Irrelevant output. |

## Output Format

Return JSON:
```json
{"explanation": "<15-60 words summarizing performance>", "score": <1-5>}
```