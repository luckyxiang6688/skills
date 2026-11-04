---
name: luckyxiang-howskill
description: |
  两层评估任意 Claude Code Skill 的质量：静态分析（元数据、触发设计、内容结构、用户体验、安全性、Token 预算）+ 动态评估（触发准确性、LLM-as-Judge 输出质量、文本模式匹配）。生成 HTML 仪表盘报告，含评分、详细检查项和改进建议。

  USE FOR: 评估skill、skill质量检查、测试skill触发、评估skill输出、生成评估报告、skill评估、skill质量评估、skill测试、eval-skill、/eval-skill、评估一下这个skill、这个skill怎么样、帮我检查skill质量

  DO NOT USE FOR: 创建新skill、编辑skill、写skill代码、安装skill、管理skill依赖
version: "1.0"
author: luckyxiang-howskill
tags: [evaluation, quality, testing, assessment]
---

# LuckyXiang HowSkill — Skill 质量评估工具

两层评估任意 Claude Code Skill 的质量，生成 HTML 仪表盘报告。

## 快速参考

| 命令 | 说明 |
|------|------|
| `/eval-skill <path>` | **完整评估（静态 + 动态，默认）** |
| `/eval-skill <path> --static-only` | 仅静态分析（快速，不消耗 token，仅当用户明确要求时使用） |

> **重要**：默认执行完整评估（静态 + 动态）。`--static-only` 仅在用户明确说"只跑静态"、"快速评估"时使用。不要主动省略动态评估。

## 执行方式

**必须通过 Python 脚本执行评估，不要手动分析或手写报告。**

### 完整评估（静态 + 动态，默认）

```bash
python3 "{luckyxiang-howskill}/scripts/run_eval.py" "<skill_path>" --verbose
```

### 仅静态分析（快速）

```bash
python3 "{luckyxiang-howskill}/scripts/run_eval.py" "<skill_path>" --static-only --verbose
```

### 参数

- `<skill_path>`：被评估 skill 的目录路径（包含 SKILL.md 的目录）
- `--static-only`：跳过动态评估
- `--verbose` / `-v`：打印进度
- `--timeout <秒>`：每个任务超时（默认 120）
- `--model <模型>`：执行模型
- `--judge-model <模型>`：LLM-as-Judge 模型

### 输出

报告固定输出到 `D:\work\claude\howskill\`，文件名格式：`<skill-name>_eval_<时间戳>.html` + `.json`

## 使用流程

### 第 1 步：指定要评估的 skill

用户提供包含 SKILL.md 的 skill 目录路径。

```
/eval-skill ~/.claude/skills/graphify
/eval-skill ~/.claude/skills/luckyxiang-writer
```

### 第 2 步：执行完整评估（静态 + 动态，默认）

**默认始终执行完整评估，不要只跑静态。** 完整评估包含两个阶段：

**阶段 A：静态分析** — 读取 SKILL.md，按加权评分评估 6 个维度：

| 维度 | 权重 | 检查内容 |
|------|------|---------|
| 内容结构 | 30% | 标准章节、代码块、表格、frontmatter 完整性 |
| 触发设计 | 25% | USE FOR / DO NOT USE FOR、反触发覆盖 |
| 用户体验 | 20% | 用途清晰度、工作流指引、示例质量、范围边界 |
| 安全性 | 10% | 敏感信息泄露、注入模式、危险操作、路径安全 |
| Token 预算 | 15% | 行数、预估 token 数 |

**阶段 B：动态评估** — 紧接静态分析之后自动执行：

1. **自动生成评估套件** — 若无 `evals/` 目录，从 SKILL.md 自动生成 `eval.yaml`、`trigger_tests.yaml` 和任务文件
2. **触发测试** — 通过 `claude -p` 发送正/负 prompt，检测 skill 是否被调用，计算精确率/召回率/F1
3. **任务执行** — 逐个任务用 `claude -p` 运行，捕获输出
4. **评分** — 应用 3 种 grader：
   - **text** — 子串/正则匹配（快速，确定性）
   - **prompt**（LLM-as-Judge） — Claude 按 rubric 评估输出质量（1-5 分，归一化到 0.0-1.0）
   - **trigger** — 正/负触发准确性

### 第 3 步：生成报告

在 `D:\work\claude\howskill\` 输出两个文件：

- **HTML 报告** — 仪表盘：评分圆环、维度进度条、触发指标、任务详情、改进建议
- **JSON 结果** — 机器可读数据，方便程序化对比分析

## 评估套件格式

如需自定义评估，在 skill 目录下创建 `evals/`：

```
skill-to-evaluate/
├── SKILL.md
└── evals/
    ├── eval.yaml           # 指标、配置、全局 graders
    ├── trigger_tests.yaml  # 正/负触发测试 prompt
    └── tasks/
        └── task-001.yaml   # 单个测试任务
```

详见 `references/eval-format.md`。

## Grader 类型

| Grader | 评估内容 | 速度 |
|--------|---------|------|
| text | 输出包含/不包含特定文本模式 | 即时 |
| prompt | LLM-as-Judge 按 rubric 评分 | ~10s/任务 |
| trigger | Skill 在正确 prompt 上激活 | ~5s/prompt |

## 异常处理

- **未找到 SKILL.md** — 报错，提示正确路径
- **无评估套件** — 从 SKILL.md 内容自动生成
- **claude -p 超时** — 标记任务失败，继续执行剩余任务
- **评估输出无法解析** — 回退到评分 0.0，原始输出记入详情