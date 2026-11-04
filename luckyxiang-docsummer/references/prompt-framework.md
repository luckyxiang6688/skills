# Prompt Framework: CoD + CoVe 混合

## 理论基础

### Chain-of-Density (CoD)

来源：Salesforce/MIT 论文 "From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting" (2023)

核心发现：
- 一次性生成的总结信息密度低（entity-sparse）
- 通过迭代"识别缺失实体 → 融入"可以显著提升密度
- 每次迭代保持同等长度，迫使 LLM 用具体信息替换模糊描述
- 5 次迭代后，总结的信息密度远高于一次性生成

关键概念：
- **Entity（实体）**：文档中的关键信息单元。定义为 Relevant（相关）、Specific（具体）、Novel（未出现）、Faithful（原文存在）
- **密度迭代**：不是追加信息，而是替换泛泛描述为具体信息
- **终止条件**：LLM 判断无重要缺失实体时停止

### Chain-of-Verification (CoVe)

来源：Meta 论文 "Chain-of-Verification Reduces Hallucination in Large Language Models" (2023)

核心发现：
- LLM 生成的总结中，部分内容是"编造的"（hallucination）
- 通过让 LLM 自己生成验证问题，再独立回答，可以有效识别编造内容
- 4 步流程：Draft → Plan Verification → Execute Verification → Final Response

关键概念：
- **关键声明（Claim）**：总结中包含数据、结论、因果关系的句子
- **验证问题**：针对每个声明生成的事实核查问题
- **独立验证**：回答验证问题时参考原文，而非总结本身
- **验证结果分类**：VERIFIED / PARTIALLY_VERIFIED / UNVERIFIED / CONTRADICTED

## 我们的混合框架

### 为什么需要混合

- 单独用 CoD：信息密度高，但可能包含编造内容
- 单独用 CoVe：内容准确，但可能遗漏关键信息
- 混合使用：CoD 确保信息完整，CoVe 确保内容准确

### 流程

```
DRAFT → DENSITY (×2-3) → VERIFY → 最终输出
  ↑         ↑                ↑
  |         |                |
初稿允许    迭代补充          逐条核实
稀疏       缺失实体          删除无法验证
           保持同等长度       的内容
```

### 各步骤的 prompt 设计原则

#### DRAFT prompt

- `<role>` 明确角色边界（提取者，不是评论者）
- `<constraints>` 用编号列表（C1-C6），LLM 对编号约束的遵守度高于段落式指令
- `<output-spec>` 精确定义输出结构，避免 LLM 自行发挥
- `<content>` 放原文，与指令分离（XML 标签隔离）

#### DENSITY prompt

- 明确定义"关键实体"的 4 个维度（Relevant/Specific/Novel/Faithful）
- 要求列出缺失实体列表（强制 LLM 显式思考，而非隐式修改）
- 硬约束"不增加长度"（替换而非追加）
- 终止信号 `DENSITY_COMPLETE`（避免无限迭代）

#### VERIFY prompt

- 要求提取"关键声明"并逐条分类（强制系统性验证，而非选择性检查）
- 4 级验证结果（VERIFIED/PARTIALLY_VERIFIED/UNVERIFIED/CONTRADICTED）
- 明确处理策略（保留/修正/删除）
- 输出指令"不要输出验证过程"（避免污染最终总结）

### 长文档适配

对于 >8000 字的文档，DRAFT 步骤改为 3 个子步骤：

1. **全局扫描**（子步骤 1a）：读取文档前 5%，输出文档地图
2. **分块精读**（子步骤 1b）：按章节分块，每块 ≤4000字，输出核心命题+关键论据+重要数据
3. **整合**（子步骤 1c）：基于地图+块级总结，按长度级别组装初稿

DENSITY 和 VERIFY 步骤不变。区别在于：
- DENSITY 对比的是"整合后的初稿"vs"块级总结"（而非全文，因为全文可能超出上下文）
- VERIFY 核实的关键段落从原文中重新读取（而非全部原文）

### 英文文档特殊处理

当文档为英文时，DRAFT prompt 的 `<constraints>` 中追加：
```
C4-EN. 英文文档处理：输出使用中文，但保留关键术语的英文原文。
      格式：中文描述 + 英文术语（中文释义）。
      示例："该模型采用 Transformer（变换器）架构"
      专业术语首次出现时附英文，后续使用中文即可。
```
