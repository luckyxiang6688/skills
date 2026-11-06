# Claude Code Skill 合集

8 个可复用的 Claude Code Skill。每个 Skill 把一类重复性的产品/分析工作固化成可执行的流程——把「每次都靠临场发挥」变成「每次都有稳定的产出标准」。

## 什么是 Skill

Skill 是给 AI 的一份可复用作业指导书：定义什么时候该用它、按什么步骤做、产出什么格式、什么情况下不许用。它解决的是**输出稳定性**问题——同一个任务，不同的人、不同的时间问，结果不该差太远。

## 清单

### 产品与调研

| Skill | 解决什么问题 |
|---|---|
| [luckyxiang-askproduct](luckyxiang-askproduct/) | 把产品讨论结构化：先给判断、再由人挑战或确认，自动记录版本避免重复讨论；每个观点必须标注来源，禁止无凭据结论 |
| [luckyxiang-productintel](luckyxiang-productintel/) | 竞品官网深度情报采集：自动发现站点结构、sitemap 全量扫描、双通道采集、数据可靠性分级标注，输出结构化竞品分析报告 |

### 文档与报告

| Skill | 解决什么问题 |
|---|---|
| [luckyxiang-deepreport](luckyxiang-deepreport/) | 多源素材 → 深度分析报告（单文件 HTML，带 SVG 图表与交互面板）；内置不可跳过的事实验证环节，降低幻觉 |
| [luckyxiang-plainreport](luckyxiang-plainreport/) | 多源素材 → 通俗解读（用日常类比替代术语，用问答结构替代学术框架），面向非技术读者 |
| [luckyxiang-docsummer](luckyxiang-docsummer/) | 文档高精度总结：CoD（密度迭代）+ CoVe（事实验证）混合框架，4 级精度可选，输出 MD + HTML |

### Skill 工程化（自举）

| Skill | 解决什么问题 |
|---|---|
| [luckyxiang-writeskill](luckyxiang-writeskill/) | 从需求到成品创建新 Skill，内置 4 类模板，自动分类与质量验证 |
| [luckyxiang-howskill](luckyxiang-howskill/) | 评估任意 Skill 的质量：静态分析（触发设计、结构、Token 预算、安全性）+ 动态评估（触发准确率、LLM-as-Judge 输出质量），生成评分仪表盘 |
| [luckyxiang-skillfixer](luckyxiang-skillfixer/) | 根据评估结果自动修复 SKILL.md，形成「写 → 评 → 修」的闭环 |

## 一个共同的设计取向

这几个 Skill 里反复出现的三条约束，是我做产品时的习惯带过来的：

1. **触发边界必须写清**：不只写「什么时候用」，还要写「什么时候不许用、该用哪个替代」——否则模型会误触发
2. **验证环节不可跳过**：报告类 Skill 都内置了独立的事实验证步骤，而不是生成完就交付
3. **来源必须可追溯**：结论要能回到证据，不能只有观点
