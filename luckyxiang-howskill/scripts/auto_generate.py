"""Auto-generate an eval suite from a SKILL.md file.

Parses the skill's description and body to extract:
- Trigger phrases (USE FOR / DO NOT USE FOR)
- Example prompts from the body
- Skill type classification

Generates: eval.yaml, trigger_tests.yaml, tasks/*.yaml
"""

import re
from pathlib import Path

import yaml

from scripts.utils import parse_skill_md


def classify_skill_type(skill: dict) -> str:
    """Classify skill into a type for metric weight defaults.

    Returns: "content_creation", "analysis", "workflow", or "utility".
    """
    desc = skill["description"].lower()
    body = skill["body"].lower()
    combined = f"{desc} {body}"

    if any(w in combined for w in ["write", "写", "generate", "生成", "create", "创建", "article", "文章", "report", "报告"]):
        return "content_creation"
    elif any(w in combined for w in ["analyze", "分析", "research", "研究", "evaluate", "评估", "graph", "graphify"]):
        return "analysis"
    elif any(w in combined for w in ["step", "步骤", "workflow", "流程", "pipeline", "first", "second", "第三步"]):
        return "workflow"
    else:
        return "utility"


def extract_triggers(description: str) -> tuple[list[str], list[str]]:
    """Extract USE FOR and DO NOT USE FOR phrases from description.

    Returns (positive_triggers, negative_triggers).
    """
    positive = []
    negative = []

    # USE FOR
    use_match = re.search(
        r"USE\s+FOR[:\s]+(.*?)(?:DO\s+NOT|$)",
        description, re.IGNORECASE | re.DOTALL,
    )
    if use_match:
        text = use_match.group(1)
        positive = [t.strip().strip('",').strip("'") for t in re.split(r'[,;，；\n]', text) if t.strip() and len(t.strip()) > 2]

    # DO NOT USE FOR
    dont_match = re.search(
        r"DO\s+NOT\s+USE\s+FOR[:\s]+(.*?)$",
        description, re.IGNORECASE | re.DOTALL,
    )
    if dont_match:
        text = dont_match.group(1)
        negative = [t.strip().strip('",').strip("'") for t in re.split(r'[,;，；\n]', text) if t.strip() and len(t.strip()) > 2]

    # Fallback: extract from trigger/triggers field or description keywords
    if not positive:
        # Try to find quoted phrases or key actions
        positive = re.findall(r'"([^"]+)"', description)
        if not positive:
            positive = [description[:50]]

    return positive[:15], negative[:10]


def extract_examples(body: str) -> list[dict]:
    """Extract example prompts from the skill body.

    Looks for patterns like "User prompt:", "Example:", code blocks with prompts, etc.
    """
    examples = []

    # Look for "**User prompt:**" or "**用户：**" patterns
    user_prompt_blocks = re.findall(
        r'\*\*(?:User prompt|用户|User|Prompt)[：:]*\*\*\s*[:：]?\s*`?([^`\n]+)`?',
        body, re.IGNORECASE,
    )
    for prompt in user_prompt_blocks:
        prompt = prompt.strip()
        if len(prompt) > 5:
            examples.append({"prompt": prompt, "source": "body_example"})

    # Look for "- X:" pattern (trigger examples)
    trigger_examples = re.findall(
        r'^\s*[-*]\s*["\']([^"\']+)["\']',
        body, re.MULTILINE,
    )
    for prompt in trigger_examples:
        if len(prompt) > 5:
            examples.append({"prompt": prompt, "source": "trigger_list"})

    # Look for "when the user says" patterns
    when_patterns = re.findall(
        r'(?:when|when the user|if the user|用户说|用户问)\s+(?:says?\s+)?["\']([^"\']+)["\']',
        body, re.IGNORECASE,
    )
    for prompt in when_patterns:
        if len(prompt) > 5:
            examples.append({"prompt": prompt, "source": "when_pattern"})

    return examples[:10]


def generate_trigger_tests(skill: dict) -> dict:
    """Generate trigger_tests.yaml content from skill metadata."""
    positive, negative = extract_triggers(skill["description"])

    # Also try body
    body_positive = re.findall(
        r'(?:Use this skill|使用此 skill|触发词)[^:]*[:：]\s*(.*?)(?:\n\n|\n#)',
        skill["body"], re.IGNORECASE | re.DOTALL,
    )
    for block in body_positive:
        items = [t.strip().strip('-* "\'') for t in block.strip().split("\n") if t.strip().startswith("-") or t.strip().startswith("*")]
        for item in items:
            if item and len(item) > 3:
                positive.append(item)

    # Generate should_trigger from USE FOR phrases
    should_trigger = []
    for phrase in positive[:10]:
        if any(c < '一' or c > '鿿' for c in phrase):
            prompt = phrase if len(phrase) > 10 else f"帮我{phrase}"
        else:
            prompt = phrase if len(phrase) > 5 else f"帮我{phrase}"
        should_trigger.append({
            "prompt": prompt,
            "reason": f"匹配触发短语：{phrase[:50]}",
            "confidence": "high" if len(phrase) > 8 else "medium",
        })

    # Generate should_not_trigger from DO NOT USE FOR + generic negatives
    should_not_trigger = []
    for phrase in negative[:5]:
        prompt = phrase if len(phrase) > 10 else f"帮我{phrase}"
        should_not_trigger.append({
            "prompt": prompt,
            "reason": f"匹配反触发短语：{phrase[:50]}",
            "confidence": "high",
        })

    # Add generic negative prompts if list is short
    generic_negatives = [
        ("帮我debug这段代码", "调试代码，与 skill 无关"),
        ("今天天气怎么样？", "完全无关的请求"),
    ]
    for prompt, reason in generic_negatives:
        if len(should_not_trigger) < 5:
            should_not_trigger.append({
                "prompt": prompt,
                "reason": reason,
                "confidence": "high",
            })

    return {
        "skill": skill["name"],
        "should_trigger_prompts": should_trigger[:8],
        "should_not_trigger_prompts": should_not_trigger[:6],
    }


def build_quality_rubric(skill_type: str) -> str:
    """Build a quality assessment rubric based on skill type."""
    rubrics = {
        "content_creation": """评估输出是否满足以下标准：
1. 输出是否非空且有实质内容（不是拒绝或错误）？
2. 输出是否与用户请求的主题相关？
3. 输出是否有结构化组织（段落、列表、标题等）？
4. 输出是否完整（不是截断的半成品）？
评分 1-5：1=完全失败，2=严重不足，3=基本合格，4=良好，5=优秀。
返回 JSON：{"explanation": "<总结>", "score": 1-5}""",
        "analysis": """评估输出是否满足以下标准：
1. 输出是否包含分析洞察（不是泛泛而谈）？
2. 分析是否有逻辑结构？
3. 输出是否与请求的主题相关？
4. 分析是否完整？
评分 1-5：1=完全失败，2=严重不足，3=基本合格，4=良好，5=优秀。
返回 JSON：{"explanation": "<总结>", "score": 1-5}""",
        "workflow": """评估输出是否满足以下标准：
1. 是否按步骤执行了工作流？
2. 每步输出是否合理？
3. 最终结果是否完整？
4. 是否有明确的错误处理？
评分 1-5：1=完全失败，2=严重不足，3=基本合格，4=良好，5=优秀。
返回 JSON：{"explanation": "<总结>", "score": 1-5}""",
        "utility": """评估输出是否满足以下标准：
1. 输出是否完成了用户请求？
2. 输出是否正确？
3. 输出是否清晰可理解？
评分 1-5：1=完全失败，2=严重不足，3=基本合格，4=良好，5=优秀。
返回 JSON：{"explanation": "<总结>", "score": 1-5}""",
    }
    return rubrics.get(skill_type, rubrics["utility"])


def generate_tasks(skill: dict, skill_type: str) -> list[dict]:
    """Generate eval tasks from SKILL.md frontmatter triggers.

    Uses USE FOR triggers as natural user prompts instead of
    extracting examples from the body (which is unreliable).
    """
    tasks = []
    skill_name = skill["name"]
    description = skill.get("description", "")

    positive_triggers, _ = extract_triggers(description)

    # Task 1: 典型触发场景测试 — 用第一个触发词作为 prompt
    if positive_triggers:
        trigger_phrase = positive_triggers[0]
        tasks.append({
            "id": f"{skill_name}-task-001",
            "name": f"{skill_name} 典型触发测试",
            "description": f"测试 skill 在典型触发场景下的输出质量",
            "inputs": {"prompt": trigger_phrase},
            "expected": {},
            "graders": [
                {
                    "type": "text",
                    "name": "输出非空且无错误",
                    "config": {
                        "not_contains": ["我不知道", "I don't know", "error", "Error", "无法完成"],
                    },
                },
                {
                    "type": "prompt",
                    "name": "输出质量评估",
                    "config": {
                        "rubric": build_quality_rubric(skill_type),
                    },
                },
            ],
        })

    # Task 2: 多触发词组合测试
    if len(positive_triggers) > 1:
        combined = "、".join(positive_triggers[:3])
        tasks.append({
            "id": f"{skill_name}-task-002",
            "name": f"{skill_name} 多触发词测试",
            "description": f"测试 skill 在多个触发词组合场景下的表现",
            "inputs": {"prompt": combined},
            "expected": {},
            "graders": [
                {
                    "type": "text",
                    "name": "输出非空且无错误",
                    "config": {
                        "not_contains": ["我不知道", "I don't know", "error", "Error"],
                    },
                },
            ],
        })

    # Fallback: 无触发词时用 skill name
    if not tasks:
        tasks.append({
            "id": f"{skill_name}-task-001",
            "name": f"{skill_name} 基础功能测试",
            "description": "自动生成的基础功能测试",
            "inputs": {"prompt": f"帮我使用 {skill_name}"},
            "expected": {},
            "graders": [
                {
                    "type": "text",
                    "name": "输出非空且无错误",
                    "config": {
                        "not_contains": ["我不知道", "I don't know", "error", "Error"],
                    },
                },
            ],
        })

    return tasks


def get_metric_defaults(skill_type: str) -> list[dict]:
    """Get default metric weights by skill type."""
    defaults = {
        "content_creation": [
            {"name": "trigger_accuracy", "weight": 0.2, "threshold": 0.9,
             "description": "Skill 是否在正确的 prompt 上被触发"},
            {"name": "output_quality", "weight": 0.5, "threshold": 0.8,
             "description": "输出质量是否达标"},
            {"name": "content_correctness", "weight": 0.3, "threshold": 0.7,
             "description": "输出是否包含预期内容"},
        ],
        "analysis": [
            {"name": "trigger_accuracy", "weight": 0.3, "threshold": 0.9,
             "description": "Skill 是否在正确的 prompt 上被触发"},
            {"name": "output_quality", "weight": 0.4, "threshold": 0.8,
             "description": "分析输出质量是否达标"},
            {"name": "content_correctness", "weight": 0.3, "threshold": 0.7,
             "description": "输出是否包含预期的分析洞察"},
        ],
        "workflow": [
            {"name": "trigger_accuracy", "weight": 0.2, "threshold": 0.9,
             "description": "Skill 是否在正确的 prompt 上被触发"},
            {"name": "output_quality", "weight": 0.3, "threshold": 0.8,
             "description": "工作流输出质量是否达标"},
            {"name": "content_correctness", "weight": 0.5, "threshold": 0.7,
             "description": "输出是否遵循预期的工作流步骤"},
        ],
        "utility": [
            {"name": "trigger_accuracy", "weight": 0.4, "threshold": 0.9,
             "description": "Skill 是否在正确的 prompt 上被触发"},
            {"name": "output_quality", "weight": 0.4, "threshold": 0.8,
             "description": "输出质量是否达标"},
            {"name": "content_correctness", "weight": 0.2, "threshold": 0.7,
             "description": "输出是否包含预期内容"},
        ],
    }
    return defaults.get(skill_type, defaults["utility"])


def auto_generate_eval_suite(skill_path: Path, output_dir: Path | None = None) -> Path:
    """Auto-generate a complete eval suite from a SKILL.md.

    Args:
        skill_path: Path to the skill directory (containing SKILL.md).
        output_dir: Where to write the eval suite. Defaults to skill_path/evals/.

    Returns:
        Path to the generated eval.yaml.
    """
    skill = parse_skill_md(skill_path)
    skill_type = classify_skill_type(skill)

    if output_dir is None:
        output_dir = skill_path / "evals"

    output_dir.mkdir(parents=True, exist_ok=True)
    tasks_dir = output_dir / "tasks"
    tasks_dir.mkdir(exist_ok=True)

    # Generate eval.yaml
    metrics = get_metric_defaults(skill_type)
    eval_spec = {
        "name": f"{skill['name']}-eval",
        "description": f"自动生成的 {skill['name']}（{skill_type}）评估套件",
        "skill": skill["name"],
        "version": "1.0",
        "config": {
            "trials_per_task": 1,
            "timeout_seconds": 300,
        },
        "metrics": metrics,
        "graders": [
            {
                "type": "text",
                "name": "无致命错误",
                "config": {
                    "regex_not_match": [
                        "(?i)fatal error",
                        "(?i)crashed",
                        "(?i)exception occurred",
                    ],
                },
            },
        ],
        "tasks": ["tasks/*.yaml"],
    }

    eval_path = output_dir / "eval.yaml"
    eval_path.write_text(
        yaml.dump(eval_spec, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    # Generate trigger_tests.yaml
    trigger_tests = generate_trigger_tests(skill)
    trigger_path = output_dir / "trigger_tests.yaml"
    trigger_path.write_text(
        yaml.dump(trigger_tests, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    # Generate task files
    tasks = generate_tasks(skill, skill_type)
    for task in tasks:
        task_file = tasks_dir / f"{task['id']}.yaml"
        task_file.write_text(
            yaml.dump(task, allow_unicode=True, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )

    return eval_path