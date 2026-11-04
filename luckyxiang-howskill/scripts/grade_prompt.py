"""LLM-as-Judge grader: uses claude -p to evaluate output quality against a rubric.

Sends the original prompt + skill output + rubric to Claude and asks for
a structured JSON score (1-5, normalized to 0.0-1.0).
"""

import json
import os
import subprocess
import time
from pathlib import Path

from scripts.utils import find_project_root


def grade_prompt(
    original_prompt: str,
    skill_output: str,
    rubric: str,
    model: str | None = None,
    timeout: int = 60,
    project_root: Path | None = None,
) -> dict:
    """Grade skill output using LLM-as-Judge.

    Args:
        original_prompt: The user prompt that was sent to the skill.
        skill_output: The skill's output text.
        rubric: Evaluation rubric text (or path to rubric file).
        model: Optional model override for the judge.
        timeout: Timeout for the judge call.
        project_root: Project root for claude -p.

    Returns:
        dict with score (0-1), passed (bool), feedback (str), details.
    """
    # Load rubric from file if it's a path
    rubric_text = rubric
    if rubric.endswith(".md") or rubric.endswith(".yaml"):
        rubric_path = Path(rubric)
        if rubric_path.exists():
            rubric_text = rubric_path.read_text(encoding="utf-8")

    judge_prompt = f"""你是一位公正的评估员，正在对 AI skill 的输出进行评分。

## 用户原始 Prompt
{original_prompt}

## Skill 输出
{skill_output}

## 评分标准（Rubric）
{rubric_text}

## 评估步骤
1. 从 prompt 中识别用户的表达意图。
2. 检查 skill 的输出是否满足或完成了该意图。
3. 验证输出的正确性和完整性。
4. 从 rubric 的评分等级中选择最接近的整数分数（1-5）。

请以 JSON 格式返回评估结果，格式如下：
```json
{{"explanation": "<15-60 字的中文总结>", "score": <整数 1-5>}}
```

不要在 JSON 之外输出任何文字。"""

    cmd = ["claude", "--output-format", "stream-json", "--verbose"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    cwd = str(project_root) if project_root else str(find_project_root())

    start = time.time()
    output_parts = []

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=cwd,
            env=env,
            shell=True,
        )

        stdout_bytes, _ = proc.communicate(input=judge_prompt.encode("utf-8"), timeout=timeout)

        for line in stdout_bytes.decode("utf-8", errors="replace").strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("type") == "result":
                output_parts.append(event.get("result", ""))
            elif event.get("type") == "assistant":
                for item in event.get("message", {}).get("content", []):
                    if item.get("type") == "text":
                        output_parts.append(item.get("text", ""))

    except subprocess.TimeoutExpired:
        if proc.poll() is None:
            proc.kill()
        return {
            "type": "prompt",
            "score": 0.0,
            "passed": False,
            "feedback": f"评估调用超时（{timeout}秒）",
            "details": {},
        }
    except Exception as e:
        return {
            "type": "prompt",
            "score": 0.0,
            "passed": False,
            "feedback": f"评估调用失败：{e}",
            "details": {},
        }

    judge_output = "\n".join(output_parts).strip()

    # Parse JSON from judge output
    # Try to extract JSON block from the output
    json_match = None
    # Look for JSON in code blocks
    import re
    json_block = re.search(r'```json\s*(\{.*?\})\s*```', judge_output, re.DOTALL)
    if json_block:
        json_match = json_block.group(1)
    else:
        # Try to find raw JSON object
        json_block = re.search(r'\{[^{}]*"explanation"[^{}]*"score"[^{}]*\}', judge_output, re.DOTALL)
        if json_block:
            json_match = json_block.group(0)

    if json_match:
        try:
            result = json.loads(json_match)
            raw_score = result.get("score", 0)
            explanation = result.get("explanation", "")

            # Normalize 1-5 to 0.0-1.0
            normalized = (raw_score - 1) / 4

            return {
                "type": "prompt",
                "score": round(normalized, 2),
                "raw_score": raw_score,
                "passed": normalized >= 0.6,
                "feedback": explanation,
                "details": result,
                "duration_ms": int((time.time() - start) * 1000),
            }
        except json.JSONDecodeError:
            pass

    # Fallback: couldn't parse structured output
    return {
        "type": "prompt",
        "score": 0.0,
        "passed": False,
        "feedback": f"无法解析评估输出：{judge_output[:200]}",
        "details": {"raw_output": judge_output[:500]},
        "duration_ms": int((time.time() - start) * 1000),
    }