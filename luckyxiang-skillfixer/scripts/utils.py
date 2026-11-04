"""Shared utilities for skillfixer scripts."""

import difflib
import json
import re
import shutil
from pathlib import Path

import yaml


def parse_skill_md(skill_path: Path) -> dict:
    """Parse SKILL.md, returning frontmatter dict and body string."""
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

    fm = yaml.safe_load(fm_text) or {}
    return {
        "frontmatter": fm,
        "body": body,
        "content": content,
        "fm_start": 0,
        "fm_end": end_idx,
        "total_lines": len(lines),
    }


def write_skill_md(skill_path: Path, frontmatter: dict, body: str) -> None:
    """Write SKILL.md with updated frontmatter and body."""
    skill_file = skill_path / "SKILL.md"

    # Serialize frontmatter, preserving multi-line description
    fm_text = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # Ensure description uses | block scalar if it's multi-line
    if "description" in frontmatter and "\n" in str(frontmatter["description"]):
        desc = frontmatter["description"]
        fm_lines = fm_text.split("\n")
        new_fm_lines = []
        skip_desc = False
        for line in fm_lines:
            if skip_desc:
                if line and not line.startswith("  "):
                    skip_desc = False
                else:
                    continue
            if line.startswith("description:"):
                # Replace with block scalar format
                desc_lines = desc.split("\n")
                new_fm_lines.append("description: |")
                for dl in desc_lines:
                    new_fm_lines.append(f"  {dl}")
                skip_desc = True
            else:
                new_fm_lines.append(line)
        fm_text = "\n".join(new_fm_lines)

    content = f"---\n{fm_text}---\n\n{body}\n"
    skill_file.write_text(content, encoding="utf-8")


def backup_skill_md(skill_path: Path) -> Path:
    """Backup SKILL.md to SKILL.md.bak."""
    skill_file = skill_path / "SKILL.md"
    backup = skill_path / "SKILL.md.bak"
    shutil.copy2(skill_file, backup)
    return backup


def restore_skill_md(skill_path: Path) -> None:
    """Restore SKILL.md from SKILL.md.bak."""
    backup = skill_path / "SKILL.md.bak"
    skill_file = skill_path / "SKILL.md"
    if backup.exists():
        shutil.copy2(backup, skill_file)
        backup.unlink()


def compute_diff(old_content: str, new_content: str) -> str:
    """Compute a readable diff between old and new content."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, lineterm="")
    return "\n".join(diff)


def load_eval_result(json_path: Path) -> dict:
    """Load evaluation JSON result."""
    return json.loads(json_path.read_text(encoding="utf-8"))


def find_latest_eval(skill_name: str, results_dir: Path) -> Path | None:
    """Find the latest evaluation JSON for a skill in the results directory."""
    pattern = f"{skill_name}_eval_*.json"
    files = sorted(results_dir.glob(pattern))
    if files:
        return files[-1]
    return None


def extract_anti_triggers_from_body(body: str) -> list[str]:
    """Extract anti-trigger phrases from body text."""
    phrases = []
    # Look for "不要/不应/避免/不得/不支持" patterns
    matches = re.findall(
        r'(?:不要|不应|避免|不得|不支持|不要用于|不适用)[^\n。,，]{3,50}',
        body, re.IGNORECASE,
    )
    for m in matches:
        m = m.strip()
        if len(m) > 5:
            phrases.append(m)
    return phrases[:8]


def extract_triggers_from_body(body: str) -> list[str]:
    """Extract trigger phrases from body text."""
    phrases = []
    # Look for trigger word lists
    matches = re.findall(
        r'(?:触发词|触发|Trigger)[：:]\s*(.*?)(?:\n\n|\n#)',
        body, re.IGNORECASE | re.DOTALL,
    )
    for block in matches:
        items = re.findall(r'["\']([^"\']+)["\']', block)
        phrases.extend(items)

    # Look for "当用户说/当用户问" patterns
    when_matches = re.findall(
        r'(?:当用户(?:说|问|输入)|when the user)[：:]*\s*["\']([^"\']+)["\']',
        body, re.IGNORECASE,
    )
    phrases.extend(when_matches)

    return phrases[:15]