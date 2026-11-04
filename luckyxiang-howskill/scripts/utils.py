"""Shared utilities for skill-evaluator scripts."""

import json
import os
import re
import subprocess
import time
import uuid
from pathlib import Path

import yaml


def parse_skill_md(skill_path: Path) -> dict:
    """Parse a SKILL.md file, returning structured metadata.

    Returns dict with keys: name, description, version, author, tags, triggers,
    frontmatter (raw dict), body (str), content (full str), line_count,
    total_lines.
    """
    skill_file = skill_path / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError(f"SKILL.md missing frontmatter: {skill_file}")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError(f"SKILL.md unclosed frontmatter: {skill_file}")

    fm_text = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1:]).strip()

    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}

    return {
        "name": fm.get("name", ""),
        "description": fm.get("description", ""),
        "version": fm.get("version", ""),
        "author": fm.get("author", ""),
        "tags": fm.get("tags", []) or fm.get("triggers", []),
        "triggers": fm.get("triggers", []) or fm.get("trigger", ""),
        "frontmatter": fm,
        "body": body,
        "content": content,
        "total_lines": len(lines),
        "body_lines": len(lines) - end_idx - 1,
        "path": str(skill_path),
    }


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English, ~2 for CJK."""
    cjk_chars = len(re.findall(r'[一-鿿぀-ゟ゠-ヿ]', text))
    other_chars = len(text) - cjk_chars
    return int(other_chars / 4 + cjk_chars / 2)


def load_eval_suite(eval_path: Path) -> dict:
    """Load an eval.yaml and resolve task file references.

    Returns dict with: name, description, skill, version, config, metrics,
    graders, tasks (list of loaded task dicts).
    """
    content = (eval_path).read_text(encoding="utf-8")
    eval_spec = yaml.safe_load(content)

    eval_dir = eval_path.parent

    # Resolve task file globs
    loaded_tasks = []
    for pattern in eval_spec.get("tasks", []):
        for task_file in sorted(eval_dir.glob(pattern)):
            task_content = task_file.read_text(encoding="utf-8")
            task = yaml.safe_load(task_content)
            task["_source_file"] = str(task_file)
            loaded_tasks.append(task)
    eval_spec["tasks"] = loaded_tasks

    # Resolve trigger tests if present
    trigger_file = eval_dir / "trigger_tests.yaml"
    if trigger_file.exists():
        trigger_content = trigger_file.read_text(encoding="utf-8")
        eval_spec["trigger_tests"] = yaml.safe_load(trigger_content)
    else:
        eval_spec["trigger_tests"] = None

    return eval_spec


def find_project_root() -> Path:
    """Find project root by walking up looking for .claude/ directory."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def run_claude_prompt(
    prompt: str,
    timeout: int = 120,
    model: str | None = None,
    project_root: Path | None = None,
    capture_output: bool = True,
) -> dict:
    """Run claude and capture structured output.

    Returns dict with: output (str), tool_calls (list), duration_ms (int),
    success (bool), error (str|None).
    """
    cmd = ["claude", "--output-format", "stream-json", "--verbose"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    cwd = str(project_root) if project_root else None

    start = time.time()
    tool_calls = []
    output_parts = []
    error = None
    success = True

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

        stdout, _ = proc.communicate(input=prompt.encode("utf-8"), timeout=timeout)
        duration_ms = int((time.time() - start) * 1000)

        for line in stdout.decode("utf-8", errors="replace").strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = event.get("type", "")

            if etype == "assistant":
                for item in event.get("message", {}).get("content", []):
                    if item.get("type") == "tool_use":
                        tool_calls.append({
                            "name": item.get("name", ""),
                            "input": item.get("input", {}),
                        })
                    elif item.get("type") == "text":
                        output_parts.append(item.get("text", ""))

            elif etype == "result":
                output_parts.append(event.get("result", ""))

    except subprocess.TimeoutExpired:
        duration_ms = int((time.time() - start) * 1000)
        if proc.poll() is None:
            proc.kill()
        error = f"Timeout after {timeout}s"
        success = False
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        error = str(e)
        success = False

    return {
        "output": "\n".join(output_parts).strip(),
        "tool_calls": tool_calls,
        "duration_ms": duration_ms,
        "success": success,
        "error": error,
    }


def run_trigger_check(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int = 30,
    project_root: Path | None = None,
    model: str | None = None,
) -> bool:
    """Run a single trigger check query. Returns True if skill would be triggered.

    Strategy: Since `claude -p` doesn't support Skill tool invocation, we use an
    LLM-as-Judge approach — ask Claude whether the query should trigger the skill,
    based on the skill's USE FOR / DO NOT USE FOR description.
    """
    if project_root is None:
        project_root = find_project_root()

    judge_prompt = (
        f"You are evaluating whether a user query should trigger a specific Claude Code Skill.\n\n"
        f"Skill name: {skill_name}\n"
        f"Skill description:\n{skill_description}\n\n"
        f"User query: \"{query}\"\n\n"
        f"Based on the skill's USE FOR and DO NOT USE FOR patterns, should this query trigger "
        f"the skill {skill_name}?\n\n"
        f"Respond with ONLY one word: YES or NO.\n"
        f"- YES if the query matches the skill's USE FOR patterns or intent\n"
        f"- NO if the query matches the skill's DO NOT USE FOR patterns, or is unrelated"
    )

    # On Windows, claude is a .cmd wrapper so we need shell=True, but
    # shell=True breaks long Unicode command-line arguments.
    # Solution: pipe the prompt via stdin instead of -p flag.
    cmd = ["claude", "--output-format", "stream-json", "--verbose"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    start = time.time()
    output_parts = []

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=str(project_root),
            env=env,
            shell=True,
        )

        stdout, _ = proc.communicate(input=judge_prompt.encode("utf-8"), timeout=timeout)

        for line in stdout.decode("utf-8", errors="replace").strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("type") == "assistant":
                for item in event.get("message", {}).get("content", []):
                    if item.get("type") == "text":
                        output_parts.append(item.get("text", ""))
            elif event.get("type") == "result":
                output_parts.append(event.get("result", ""))

    except subprocess.TimeoutExpired:
        if proc.poll() is None:
            proc.kill()
        return False
    except Exception:
        return False

    full_response = "\n".join(output_parts).strip()
    upper = full_response.upper()

    # Check for YES/NO in response (English or Chinese)
    if "YES" in upper or "是" in full_response:
        return True
    if "NO" in upper or "否" in full_response or "不" in full_response:
        return False

    # Ambiguous response — default to False
    return False
