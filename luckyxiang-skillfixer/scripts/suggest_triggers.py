"""LLM-assisted trigger phrase and description generation via claude -p."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


def _run_claude(prompt: str, timeout: int = 30, model: str | None = None) -> str:
    """Run claude -p and return the text output."""
    cmd = ["claude", "-p", prompt]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    cwd = tempfile.gettempdir()

    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, env=env, shell=True, cwd=cwd,
        )
        return proc.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""


def _extract_json_array(text: str) -> list[str]:
    """Extract a JSON array from LLM output, handling code fences."""
    if not text:
        return []

    cleaned = re.sub(r'^```\w*\n?', '', text)
    cleaned = re.sub(r'\n?```$', '', cleaned, flags=re.MULTILINE)

    json_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
    if json_match:
        try:
            items = json.loads(json_match.group(0))
            if isinstance(items, list):
                return [str(item) for item in items]
        except json.JSONDecodeError:
            pass

    return [p.strip().strip('"\'') for p in text.split(",") if p.strip()]


def _extract_json_object(text: str) -> dict:
    """Extract a JSON object from LLM output, handling code fences."""
    if not text:
        return {}

    cleaned = re.sub(r'^```\w*\n?', '', text)
    cleaned = re.sub(r'\n?```$', '', cleaned, flags=re.MULTILINE)

    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return {}


def batch_generate_for_description(
    skill_name: str,
    body: str,
    desc: str,
    target_length: int = 300,
    model: str | None = None,
) -> dict:
    """One LLM call to generate triggers + anti_triggers + new_description.

    Returns {"triggers": [...], "anti_triggers": [...], "description": "..."}
    """
    prompt = (
        f"为名为 {skill_name} 的 skill 生成以下内容，以 JSON 对象返回：\n"
        f"1. triggers: 6 个触发短语的数组（用户会说什么来触发它）\n"
        f"2. anti_triggers: 4 个不适用场景短语的数组\n"
        f"3. description: {target_length}+ 字符的 description（含 USE FOR 和 DO NOT USE FOR 段）\n"
        f"skill 功能：{desc[:200] or body[:200]}\n"
        f"skill 内容：{body[:400]}\n"
        f'返回格式：{{"triggers": [...], "anti_triggers": [...], "description": "..."}}\n'
        f"只返回 JSON 对象。"
    )

    output = _run_claude(prompt, timeout=45, model=model)
    result = _extract_json_object(output)

    # Validate and fill defaults
    if not isinstance(result.get("triggers"), list):
        result["triggers"] = _extract_json_array(output) if not result else []
    if not isinstance(result.get("anti_triggers"), list):
        result["anti_triggers"] = []
    if not isinstance(result.get("description"), str) or len(result.get("description", "")) < 50:
        result["description"] = ""

    return result


def generate_trigger_phrases(
    skill_name: str,
    skill_body: str,
    existing_desc: str = "",
    count: int = 6,
    model: str | None = None,
) -> list[str]:
    """Generate USE FOR trigger phrases for a skill."""
    prompt = (
        f"为名为 {skill_name} 的 skill 生成 {count} 个触发短语（用户会说什么来触发它）。"
        f"skill 功能：{existing_desc[:200] or skill_body[:200]}。"
        f"以 JSON 数组格式返回，例如：[\"写文章\", \"帮我写\", \"写稿子\"]。只返回 JSON 数组。"
    )

    output = _run_claude(prompt, model=model)
    return _extract_json_array(output)[:count]


def generate_anti_trigger_phrases(
    skill_name: str,
    skill_body: str,
    existing_desc: str = "",
    count: int = 4,
    model: str | None = None,
) -> list[str]:
    """Generate DO NOT USE FOR anti-trigger phrases for a skill."""
    prompt = (
        f"为名为 {skill_name} 的 skill 生成 {count} 个「不适用场景」短语（什么情况下不该用它）。"
        f"skill 功能：{existing_desc[:200] or skill_body[:200]}。"
        f"以 JSON 数组格式返回，例如：[\"简单查询\", \"写短内容\", \"纯代码实现\"]。只返回 JSON 数组。"
    )

    output = _run_claude(prompt, model=model)
    return _extract_json_array(output)[:count]


def expand_description(
    skill_name: str,
    current_desc: str,
    skill_body: str,
    trigger_phrases: list[str] | None = None,
    anti_trigger_phrases: list[str] | None = None,
    target_length: int = 300,
    model: str | None = None,
) -> str:
    """Expand a short description using LLM."""
    use_for = ""
    if trigger_phrases:
        use_for = "USE FOR: " + "、".join(trigger_phrases)

    dont = ""
    if anti_trigger_phrases:
        dont = "DO NOT USE FOR: " + "、".join(anti_trigger_phrases)

    prompt = (
        f"为名为 {skill_name} 的 skill 写一段 description（目标 {target_length}+ 字符，上限 1024）。"
        f"当前 description：{current_desc[:300]}。"
        f"skill 内容摘要：{skill_body[:400]}。"
        f"{use_for} {dont} "
        f"要求：1-2句功能概述 + USE FOR 段 + DO NOT USE FOR 段。只返回 description 文本。"
    )

    output = _run_claude(prompt, model=model)
    if output and len(output) >= 100:
        return output
    return current_desc


def generate_tags(
    skill_name: str,
    description: str,
    count: int = 5,
    model: str | None = None,
) -> list[str]:
    """Generate tags for a skill from its description."""
    prompt = (
        f"为名为 {skill_name} 的 skill 生成 {count} 个标签。描述：{description[:300]}。"
        f"以 JSON 数组格式返回，例如：[\"写作\", \"公众号\", \"content-creation\"]。只返回 JSON 数组。"
    )

    output = _run_claude(prompt, model=model)
    return _extract_json_array(output)[:count]


def generate_examples_from_body(
    skill_name: str,
    skill_body: str,
    count: int = 2,
    model: str | None = None,
) -> str:
    """Generate usage examples for a skill based on its body content."""
    prompt = (
        f"为名为 {skill_name} 的 skill 生成 {count} 个使用示例（用户输入 → skill 输出）。"
        f"skill 内容：{skill_body[:500]}。用 Markdown 格式输出示例。只返回示例内容。"
    )

    return _run_claude(prompt, model=model)
