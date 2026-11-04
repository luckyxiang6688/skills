# Grader Guide

## Text Grader

Validates output using substring and regex matching. Fast, deterministic, no LLM cost.

```yaml
graders:
  - type: text
    name: check_content
    config:
      contains: ["关键词1", "keyword2"]         # Must appear (case-insensitive)
      not_contains: ["错误", "error"]            # Must NOT appear (case-insensitive)
      contains_cs: ["ExactCase"]                 # Must appear (case-sensitive)
      not_contains_cs: ["ExactBad"]              # Must NOT appear (case-sensitive)
      regex_match: ["\\d{4}-\\d{2}-\\d{2}"]     # Regex must match
      regex_not_match: ["(?i)fatal error"]       # Regex must NOT match
```

Score = passed_checks / total_checks.

## Prompt Grader (LLM-as-Judge)

Uses Claude to evaluate output quality against a rubric. Returns a 1-5 score normalized to 0.0-1.0.

```yaml
graders:
  - type: prompt
    name: quality_check
    config:
      rubric: |
        Evaluate whether the output satisfies the user's request.
        Score 1-5: 1=very poor, 3=adequate, 5=excellent.
        Return JSON: {"explanation": "...", "score": 1-5}
```

You can also point to a rubric file:

```yaml
graders:
  - type: prompt
    name: intent_check
    config:
      rubric: references/rubrics/intent_resolution.md
```

## Trigger Grader

Tests whether the skill correctly triggers or does not trigger on specific prompts. Defined in `trigger_tests.yaml`.

```yaml
trigger_tests:
  should_trigger_prompts:
    - prompt: "帮我写一篇公众号文章"
      reason: "Direct trigger"
      confidence: high
  should_not_trigger_prompts:
    - prompt: "帮我debug"
      reason: "Unrelated"
      confidence: high
```

Metrics: precision, recall, F1, accuracy.
