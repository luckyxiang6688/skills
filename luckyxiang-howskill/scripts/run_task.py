"""Single task executor: runs one task via claude -p and applies graders."""

import json
import time
from pathlib import Path

from scripts.utils import run_claude_prompt, find_project_root
from scripts.grade_text import grade_text
from scripts.grade_prompt import grade_prompt


def run_single_task(
    task: dict,
    eval_dir: Path,
    timeout: int = 120,
    model: str | None = None,
    judge_model: str | None = None,
    global_graders: list | None = None,
    verbose: bool = False,
) -> dict:
    """Execute a single task and grade the output.

    Args:
        task: Task definition dict (id, name, inputs, expected, graders).
        eval_dir: Directory of the eval.yaml (for resolving relative paths).
        timeout: Timeout for claude -p execution.
        model: Model for skill execution.
        judge_model: Model for LLM-as-Judge (overrides model).
        global_graders: Graders from eval.yaml to apply to all tasks.
        verbose: Print progress.

    Returns:
        Task result dict.
    """
    task_id = task.get("id", "unknown")
    task_name = task.get("name", task_id)

    if verbose:
        print(f"  Running task: {task_name} ({task_id})", flush=True)

    # Get prompt
    inputs = task.get("inputs", {})
    prompt = inputs.get("prompt", "")
    if not prompt:
        prompt_file = inputs.get("prompt_file", "")
        if prompt_file:
            pf = eval_dir / prompt_file
            if pf.exists():
                prompt = pf.read_text(encoding="utf-8")

    if not prompt:
        return {
            "id": task_id,
            "name": task_name,
            "status": "error",
            "error": "未提供 prompt",
            "grader_results": [],
            "score": 0.0,
        }

    # Execute
    start = time.time()
    result = run_claude_prompt(
        prompt=prompt,
        timeout=timeout,
        model=model,
        project_root=find_project_root(),
    )
    duration_ms = int((time.time() - start) * 1000)

    if not result["success"]:
        return {
            "id": task_id,
            "name": task_name,
            "status": "error",
            "error": result["error"],
            "duration_ms": duration_ms,
            "grader_results": [],
            "score": 0.0,
        }

    output = result["output"]

    # Collect all graders (global + task-specific)
    all_graders = list(global_graders or [])
    all_graders.extend(task.get("graders", []))

    # Also check expected shorthand fields
    expected = task.get("expected", {})
    if expected.get("output_contains") or expected.get("output_not_contains"):
        shorthand_config = {}
        if expected.get("output_contains"):
            shorthand_config["contains"] = expected["output_contains"]
        if expected.get("output_not_contains"):
            shorthand_config["not_contains"] = expected["output_not_contains"]
        all_graders.append({
            "type": "text",
            "name": "expected_content",
            "config": shorthand_config,
        })

    # Run graders
    grader_results = []
    for grader_def in all_graders:
        gtype = grader_def.get("type", "")
        gname = grader_def.get("name", gtype)
        gconfig = grader_def.get("config", {})

        if gtype == "text":
            gr = grade_text(output, gconfig)
            gr["name"] = gname
            grader_results.append(gr)

        elif gtype == "prompt":
            rubric = gconfig.get("rubric", "")
            # Resolve rubric path relative to eval_dir
            if rubric and not rubric.startswith("You are"):
                rubric_path = eval_dir / rubric
                if rubric_path.exists():
                    rubric = rubric_path.read_text(encoding="utf-8")
            if not rubric:
                rubric = "评估输出是否满足用户请求。评分 1-5：1=很差，3=合格，5=优秀。返回 JSON：{\"explanation\": \"<总结>\", \"score\": 1-5}"

            gr = grade_prompt(
                original_prompt=prompt,
                skill_output=output,
                rubric=rubric,
                model=judge_model or model,
                timeout=60,
                project_root=find_project_root(),
            )
            gr["name"] = gname
            grader_results.append(gr)

    # Compute task score (average of grader scores, weighted)
    total_weight = 0.0
    weighted_sum = 0.0
    for gr in grader_results:
        weight = 1.0  # Default weight
        # Could add weight from grader_def if needed
        weighted_sum += gr["score"] * weight
        total_weight += weight

    task_score = weighted_sum / total_weight if total_weight > 0 else 1.0

    return {
        "id": task_id,
        "name": task_name,
        "status": "completed",
        "prompt": prompt[:500],
        "output": output[:2000],
        "duration_ms": duration_ms + sum(gr.get("duration_ms", 0) for gr in grader_results),
        "grader_results": grader_results,
        "score": round(task_score, 2),
        "tool_calls": result["tool_calls"],
    }