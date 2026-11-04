# Eval Suite Format

## eval.yaml

```yaml
name: <string>                    # Unique eval suite name
description: <string>             # What this eval tests
skill: <string>                   # Skill name being evaluated
version: <string>                 # Eval suite version

config:
  trials_per_task: <int>          # How many times to run each task (default: 1)
  timeout_seconds: <int>          # Max time per task (default: 120)
  model: <string>                 # Model for execution (optional)

metrics:
  - name: <string>                # Metric identifier
    weight: <float>               # Relative weight (should sum to ~1.0)
    threshold: <float>            # Minimum score 0-1 to pass
    description: <string>         # What this metric measures

graders:                          # Global graders applied to all tasks
  - type: text
    name: <string>
    config:
      regex_not_match: [<string>]

tasks:
  - "tasks/*.yaml"                # Glob patterns for task files
```

## trigger_tests.yaml

```yaml
skill: <string>

should_trigger_prompts:
  - prompt: <string>
    reason: <string>
    confidence: high|medium

should_not_trigger_prompts:
  - prompt: <string>
    reason: <string>
    confidence: high|medium
```

## Task YAML

```yaml
id: <string>
name: <string>
description: <string>

inputs:
  prompt: <string>                # The user prompt to send

expected:
  output_contains: [<string>]     # Strings that must appear
  output_not_contains: [<string>] # Strings that must not appear

graders:
  - type: text
    name: <string>
    config:
      contains: [<string>]
      not_contains: [<string>]
      regex_match: [<string>]
      regex_not_match: [<string>]
  - type: prompt
    name: <string>
    config:
      rubric: <string>            # Rubric text or path to rubric file
```