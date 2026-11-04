"""HTML report generator for skill evaluation results.

Generates a self-contained HTML file with inline CSS, dashboard-style layout,
progress bars, expandable task details, and improvement suggestions.
"""

import json
import time
from datetime import datetime
from pathlib import Path

from scripts.aggregate import score_to_label


def _score_color(score: float) -> str:
    """Map score to a color."""
    if score >= 0.9:
        return "#22c55e"  # green
    elif score >= 0.7:
        return "#3b82f6"  # blue
    elif score >= 0.5:
        return "#f59e0b"  # amber
    elif score >= 0.3:
        return "#ef4444"  # red
    else:
        return "#dc2626"  # dark red


def _status_icon(status: str) -> str:
    """Map status to icon."""
    status = status.upper()
    if status == "PASS":
        return "&#x2705;"
    elif status == "WARN":
        return "&#x26A0;&#xFE0F;"
    elif status == "CRITICAL":
        return "&#x274C;"
    elif status == "INFO":
        return "&#x2139;&#xFE0F;"
    elif status == "FAIL":
        return "&#x274C;"
    return "&#x2753;"


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


CSS = """
:root {
  --bg: #0f172a;
  --surface: #1e293b;
  --surface2: #334155;
  --text: #f1f5f9;
  --text-muted: #94a3b8;
  --accent: #3b82f6;
  --green: #22c55e;
  --amber: #f59e0b;
  --red: #ef4444;
  --border: #475569;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  padding: 2rem;
  max-width: 960px;
  margin: 0 auto;
}

h1 { font-size: 1.8rem; margin-bottom: 0.5rem; }
h2 { font-size: 1.3rem; margin: 1.5rem 0 0.75rem; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
h3 { font-size: 1.1rem; margin: 1rem 0 0.5rem; }

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.dashboard {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.score-ring {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  background: var(--surface);
  border-radius: 12px;
  padding: 1.5rem;
}

.score-ring .big-score {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
}

.score-ring .label {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-top: 0.3rem;
}

.dim-bars {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dim-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.dim-bar .dim-name {
  flex: 0 0 140px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.dim-bar .bar-track {
  flex: 1;
  height: 24px;
  background: var(--surface2);
  border-radius: 4px;
  overflow: hidden;
}

.dim-bar .bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.dim-bar .dim-score {
  flex: 0 0 50px;
  font-size: 0.85rem;
  font-weight: 600;
  text-align: right;
}

.checks-list {
  list-style: none;
  padding: 0;
}

.checks-list li {
  padding: 0.4rem 0;
  font-size: 0.85rem;
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.checks-list li .icon { flex-shrink: 0; }
.checks-list li .msg { flex: 1; }

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

th, td {
  padding: 0.6rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
  font-size: 0.85rem;
}

th { color: var(--text-muted); font-weight: 600; }

.task-detail {
  background: var(--surface2);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 0.75rem;
}

.task-detail .prompt-preview {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  white-space: pre-wrap;
  max-height: 80px;
  overflow: hidden;
}

.task-detail .output-preview {
  font-size: 0.8rem;
  white-space: pre-wrap;
  max-height: 200px;
  overflow: auto;
  background: var(--bg);
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 0.5rem;
}

.grader-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-right: 0.3rem;
}

.grader-badge.pass { background: rgba(34,197,94,0.2); color: var(--green); }
.grader-badge.fail { background: rgba(239,68,68,0.2); color: var(--red); }

.suggestion {
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}

.suggestion.critical { background: rgba(239,68,68,0.15); border-left: 3px solid var(--red); }
.suggestion.warn { background: rgba(245,158,11,0.15); border-left: 3px solid var(--amber); }
.suggestion.info { background: rgba(59,130,246,0.15); border-left: 3px solid var(--accent); }

.trigger-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.trigger-metric-card {
  background: var(--surface2);
  border-radius: 6px;
  padding: 0.75rem;
  text-align: center;
}

.trigger-metric-card .value { font-size: 1.5rem; font-weight: 700; }
.trigger-metric-card .label { font-size: 0.75rem; color: var(--text-muted); }

.footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.collapsible-toggle {
  cursor: pointer;
  user-select: none;
  color: var(--accent);
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.collapsible-toggle:hover { text-decoration: underline; }

.collapsible-content { display: none; }
.collapsible-content.open { display: block; }
"""


def generate_html_report(
    skill_name: str,
    static_result: dict,
    dynamic_result: dict | None,
    aggregate_result: dict | None,
    output_path: Path,
) -> Path:
    """Generate a complete HTML evaluation report.

    Args:
        skill_name: Name of the evaluated skill.
        static_result: Result from static_analysis.run_static_analysis.
        dynamic_result: Result from trigger + task evaluation (or None).
        aggregate_result: Result from aggregate (or None).
        output_path: Where to save the HTML file.

    Returns:
        Path to the generated HTML file.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Compute overall score
    static_score = static_result.get("overall_score", 0.0)
    dynamic_score = aggregate_result.get("overall_score", 0.0) if aggregate_result else 0.0

    if aggregate_result:
        overall_score = (static_score * 0.3 + dynamic_score * 0.7)
    else:
        overall_score = static_score

    overall_label = score_to_label(overall_score)
    overall_color = _score_color(overall_score)

    # --- Header ---
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Skill 评估报告 - {_escape_html(skill_name)}</title>
<style>{CSS}</style>
</head>
<body>

<h1>Skill 评估报告</h1>
<p style="color:var(--text-muted);margin-bottom:1rem;">
  <strong>Skill:</strong> {_escape_html(skill_name)} &nbsp;|&nbsp;
  <strong>日期:</strong> {now} &nbsp;|&nbsp;
  <strong>总分:</strong> <span style="color:{overall_color}">{overall_score:.2f} ({overall_label})</span>
</p>

<!-- 评分仪表盘 -->
<div class="dashboard">
  <div class="score-ring">
    <div class="big-score" style="color:{overall_color}">{overall_score:.2f}</div>
    <div class="label">{overall_label}</div>
  </div>
  <div class="dim-bars">
"""

    # --- Static analysis dimension bars ---
    DIM_CN = {
        "content_structure": "内容结构",
        "trigger_design": "触发设计",
        "user_experience": "用户体验",
        "security": "安全性",
        "token_budget": "Token 预算",
    }
    for dim in static_result.get("dimensions", []):
        dname = DIM_CN.get(dim["dimension"], dim["dimension"])
        dscore = dim["score"]
        dcolor = _score_color(dscore)
        dlabel = score_to_label(dscore)
        html += f"""
    <div class="dim-bar">
      <span class="dim-name">{_escape_html(dname)} ({dlabel})</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:{dscore*100:.0f}%;background:{dcolor}"></div>
      </div>
      <span class="dim-score" style="color:{dcolor}">{dscore:.2f}</span>
    </div>
"""

    # Dynamic metrics bars
    METRIC_CN = {
        "trigger_accuracy": "触发准确性",
        "output_quality": "输出质量",
        "content_correctness": "内容正确性",
    }
    if aggregate_result and aggregate_result.get("metrics"):
        html += """  </div>
</div>

<h2>动态评估指标</h2>
<div class="dim-bars">
"""
        for mname, mdata in aggregate_result["metrics"].items():
            mval = mdata["value"]
            mcolor = _score_color(mval)
            mlabel = score_to_label(mval)
            mpassed = mdata.get("passed", False)
            status = "&#x2705;" if mpassed else "&#x274C;"
            mname_cn = METRIC_CN.get(mname, mname)
            html += f"""
  <div class="dim-bar">
    <span class="dim-name">{_escape_html(mname_cn)} ({mlabel}) {status}</span>
    <div class="bar-track">
      <div class="bar-fill" style="width:{mval*100:.0f}%;background:{mcolor}"></div>
    </div>
    <span class="dim-score" style="color:{mcolor}">{mval:.2f}</span>
  </div>
"""

    html += """  </div>
</div>
"""

    # --- Static Analysis Details ---
    html += """
<h2>静态分析详情</h2>
"""

    for dim in static_result.get("dimensions", []):
        dname = DIM_CN.get(dim["dimension"], dim["dimension"])
        dscore = dim["score"]
        dcolor = _score_color(dscore)
        html += f"""
<div class="card">
  <h3 style="color:{dcolor}">{_escape_html(dname)} &mdash; {dscore:.2f}</h3>
  <ul class="checks-list">
"""
        for text, deduction, severity in dim.get("checks", []):
            icon = _status_icon(severity)
            html += f"""    <li><span class="icon">{icon}</span><span class="msg">{_escape_html(text)}</span></li>\n"""

        html += """  </ul>
</div>
"""

    # --- Trigger Metrics ---
    if dynamic_result and dynamic_result.get("trigger_metrics"):
        tm = dynamic_result["trigger_metrics"]
        html += """
<h2>触发准确性</h2>
<div class="trigger-metrics-grid">
"""
        for key, label in [("precision", "精确率"), ("recall", "召回率"), ("f1", "F1 值"), ("accuracy", "准确率")]:
            val = tm.get(key, 0.0)
            color = _score_color(val)
            html += f"""
  <div class="trigger-metric-card">
    <div class="value" style="color:{color}">{val:.2f}</div>
    <div class="label">{label}</div>
  </div>
"""
        html += """</div>

<div class="card">
  <table>
    <tr><th>测试 Prompt</th><th>预期</th><th>实际</th><th>结果</th></tr>
"""
        for r in dynamic_result.get("trigger_results", []):
            expected = "应触发" if r["expected"] else "不应触发"
            actual = "已触发" if r["actual"] else "未触发"
            result_icon = "&#x2705;" if r["correct"] else "&#x274C;"
            html += f"""    <tr>
      <td>{_escape_html(r['prompt'][:80])}</td>
      <td>{expected}</td>
      <td>{actual}</td>
      <td>{result_icon}</td>
    </tr>
"""
        html += """  </table>
</div>
"""

    # --- Task Results ---
    if aggregate_result and aggregate_result.get("total_tasks", 0) > 0:
        html += """
<h2>任务结果</h2>
<div class="card">
  <table>
    <tr><th>任务</th><th>得分</th><th>状态</th><th>耗时</th></tr>
"""
        # Get task results from dynamic_result
        task_results = dynamic_result.get("task_results", []) if dynamic_result else []
        for t in task_results:
            tcolor = _score_color(t.get("score", 0))
            status = "&#x2705;" if t.get("status") == "completed" else "&#x274C;"
            dur = f"{t.get('duration_ms', 0) / 1000:.1f}s"
            html += f"""    <tr>
      <td>{_escape_html(t.get('name', t.get('id', 'unknown')))}</td>
      <td style="color:{tcolor}">{t.get('score', 0):.2f}</td>
      <td>{status}</td>
      <td>{dur}</td>
    </tr>
"""
        html += """  </table>
</div>
"""

        # Task details (collapsible)
        for t in task_results:
            task_id = t.get("id", "unknown")
            html += f"""
<div class="collapsible-toggle" onclick="toggleDetail('{task_id}')">
  &#x25B6; 详情: {_escape_html(t.get('name', task_id))}
</div>
<div class="collapsible-content" id="detail-{task_id}">
  <div class="task-detail">
    <div class="prompt-preview">{_escape_html(t.get('prompt', 'N/A'))}</div>
"""
            # Grader badges
            for gr in t.get("grader_results", []):
                badge_class = "pass" if gr.get("passed") else "fail"
                html += f"""    <span class="grader-badge {badge_class}">{_escape_html(gr.get('name', gr.get('type', '?')))}: {gr.get('score', 0):.2f}</span>\n"""

            # Output preview
            output_text = t.get("output", "")
            if output_text:
                html += f"""    <div class="output-preview">{_escape_html(output_text[:1500])}</div>
"""

            html += """  </div>
</div>
"""

# --- Suggestions ---
    suggestions = static_result.get("suggestions", [])
    if suggestions:
        html += """
<h2>改进建议</h2>
"""
        for s in suggestions:
            sev = s.get("severity", "info").lower()
            html += f"""<div class="suggestion {sev}">
  <strong>[{sev.upper()}]</strong> {_escape_html(s.get('message', ''))} &mdash; <em>{_escape_html(s.get('dimension', ''))}</em>
</div>
"""

    # --- Footer ---
    html += f"""
<div class="footer">
  由 skill-evaluator 生成 &nbsp;|&nbsp; {now} &nbsp;|&nbsp;
  静态评分: {static_score:.2f} &nbsp;|&nbsp;
  动态评分: {dynamic_score:.2f}
</div>
"""

    html += """
<script>
function toggleDetail(id) {
  var el = document.getElementById('detail-' + id);
  el.classList.toggle('open');
  var toggle = el.previousElementSibling;
  if (el.classList.contains('open')) {
    toggle.innerHTML = toggle.innerHTML.replace('\\u25B6', '\\u25BC');
  } else {
    toggle.innerHTML = toggle.innerHTML.replace('\\u25BC', '\\u25B6');
  }
}
</script>

</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def save_json_results(
    skill_name: str,
    static_result: dict,
    dynamic_result: dict | None,
    aggregate_result: dict | None,
    output_path: Path,
) -> Path:
    """Save machine-readable JSON results file."""
    now = datetime.now().isoformat()

    data = {
        "eval_id": f"eval-{int(time.time())}",
        "skill": skill_name,
        "timestamp": now,
        "static_analysis": static_result,
        "dynamic_evaluation": dynamic_result,
        "aggregate": aggregate_result,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_path