# 通俗易懂解读 — 固定 9 节结构规范

> **强制规则**：9 节结构不可更改。节标题、节 ID、必含组件都是强制的。
> 如果素材不足以支撑某节内容，在该节标注 `[素材不足]`，仍保留该节结构。

## 总览

plainreport 输出固定 9 节问答式结构，不根据素材数量动态调整。每节回答读者自然会产生的一个问题。

## 快速检查表

| 节 | id | 必含组件 | 禁止 |
|----|-----|---------|------|
| 1 | s1 | `.analogy` + `.stat-row` + `.card-grid` | 禁止省略统计行 |
| 2 | s2 | `.analogy` + `.card-grid` + `.table-wrap` + `.key-point` | 禁止省略能力边界 |
| 3 | s3 | `.analogy` + `.subsection` + `.svg-wrap`(≥1) | 禁止无 SVG |
| 4 | s4 | `.example-box` + `.step` + `.svg-wrap`(≥1) | 禁止无示例步骤 |
| 5 | s5 | `.card-grid` + `.key-point` | 禁止无数据支撑 |
| 6 | s6 | `.table-wrap`(3列) | 禁止少于3列 |
| 7 | s7 | `.pros-cons`(`.con`+`.pro`) | 禁止用其他布局替代 |
| 8 | s8 | `.scenario-grid` + `.scenario-card` | 禁止无场景卡片 |
| 9 | s9 | `.svg-wrap`(径向总结SVG) | 禁止无总结图 |

---

## 第 1 节：是什么？

**目的**：让读者用最快速度建立对主题的直觉认知。

**内容要素**：
- 一句话定义 + 日常类比（.analogy 块）
- 关键统计数字（.stat-row + .stat-box）
- 核心能力/特性卡片（.card-grid + .card）
- 类型/分类表格（.table-wrap）

**必配 SVG**：无（用统计行 + 卡片网格代替）

**HTML 结构**：
```html
<div class="section" id="s1">
  <div class="section-title"><span class="section-num">1</span> {主题名} 是什么？</div>

  <p><strong>{主题}</strong> 是一款...{一句话定义}...</p>

  <div class="analogy">{日常类比解释，让非技术读者秒懂}</div>

  <div class="stat-row">
    <div class="stat-box"><div class="num">{数字1}</div><div class="label">{标签1}</div></div>
    <div class="stat-box"><div class="num">{数字2}</div><div class="label">{标签2}</div></div>
    <div class="stat-box"><div class="num">{数字3}</div><div class="label">{标签3}</div></div>
    <div class="stat-box"><div class="num">{数字4}</div><div class="label">{标签4}</div></div>
  </div>

  <p>{核心能力概括}：</p>
  <div class="card-grid">
    <div class="card">
      <h4>{能力1标题}</h4>
      <p>{能力1描述}</p>
    </div>
    <div class="card">
      <h4>{能力2标题}</h4>
      <p>{能力2描述}</p>
    </div>
    <div class="card">
      <h4>{能力3标题}</h4>
      <p>{能力3描述}</p>
    </div>
  </div>

  <p>{支持的类型/分类}：</p>
  <div class="table-wrap">
    <table>
      <thead><tr><th>{分类维度1}</th><th>{分类维度2}</th><th>{分类维度3}</th></tr></thead>
      <tbody><!-- 数据行 --></tbody>
    </table>
  </div>
</div>
```

---

## 第 2 节：支持哪些能力？

**目的**：清晰列出主题具备的能力清单，每项能力带通俗说明，让读者快速判断"它能做什么"。

**内容要素**：
- 能力分类表格（.table-wrap）：能力名 / 通俗说明 / 是否核心能力
- 核心能力卡片（.card-grid + .card）：重点能力用卡片展开说明
- 类比块（.analogy）：整体能力范围的类比

**必配 SVG**：无

**HTML 结构**：
```html
<div class="section" id="s2">
  <div class="section-title"><span class="section-num">2</span> 支持哪些能力？</div>

  <div class="analogy">{能力范围的整体类比，如"就像一辆车，能自动导航、自动刹车、自动泊车，但不会自己找停车场"}</div>

  <p>{主题}具备以下核心能力：</p>
  <div class="card-grid">
    <div class="card">
      <h4>{能力1标题}</h4>
      <p>{能力1通俗说明：做什么、怎么做、效果如何}</p>
    </div>
    <div class="card">
      <h4>{能力2标题}</h4>
      <p>{能力2通俗说明}</p>
    </div>
    <div class="card">
      <h4>{能力3标题}</h4>
      <p>{能力3通俗说明}</p>
    </div>
  </div>

  <div class="subsection" id="s2-full">
    <div class="subsection-title">完整能力清单</div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>能力</th><th>通俗说明</th><th>核心？</th></tr></thead>
        <tbody>
          <tr>
            <td><strong>{能力1}</strong></td>
            <td>{用日常语言说明这项能力具体做什么}</td>
            <td><span class="tag tag-green">核心</span></td>
          </tr>
          <tr>
            <td><strong>{能力2}</strong></td>
            <td>{通俗说明}</td>
            <td><span class="tag tag-blue">扩展</span></td>
          </tr>
          <!-- 更多行... -->
        </tbody>
      </table>
    </div>
  </div>

  <div class="key-point">{能力边界说明：哪些事它能做，哪些事它做不了，需要什么额外条件}</div>
</div>
```

**内容生成规则**：
- 每项能力必须用**日常语言**说明，不用技术术语
- 核心能力用 `.card` 卡片展开（3-5项），全部能力用表格列出
- 表格第三列用 `.tag-green`（核心）或 `.tag-blue`（扩展）标签区分
- **必须包含能力边界**：明确说明哪些事做不到或需要额外条件（如避障需要伴飞计算机）
- 类比块必须点明"能做什么"和"不能做什么"的边界

---

## 第 3 节：怎么做？

**目的**：用分层图和类比讲清楚"内部是怎么运作的"。

**内容要素**：
- 整体架构类比（.analogy 块）
- 分层架构图（SVG，核心图表）
- 按关键机制分 sub-section，每个都有类比块 + 流程图

**必配 SVG**：分层架构图（≥1），每个子节额外 0-1 个

**HTML 结构**：
```html
<div class="section" id="s2">
  <div class="section-title"><span class="section-num">2</span> {主题名} 怎么做的？</div>

  <div class="subsection">
    <div class="subsection-title">2.1 整体架构：一个"{类比意象}"</div>
    <p>{架构概述，用类比解释}</p>
    <div class="svg-wrap">
      <svg><!-- 分层架构图 --></svg>
    </div>
    <div class="svg-caption">图 1：{架构图标题}</div>
  </div>

  <div class="subsection">
    <div class="subsection-title">2.2 {机制名}："{类比意象}"</div>
    <div class="analogy">{机制类比}</div>
    <p>{机制详细解释}</p>
    <div class="svg-wrap">
      <svg><!-- 机制流程图 --></svg>
    </div>
    <div class="svg-caption">图 N：{流程图标题}</div>
  </div>

  <!-- 更多子节... -->
</div>
```

---

## 第 4 节：举例说明

**目的**：用具体的、分步骤的场景让读者"看到"它怎么工作。

**内容要素**：
- 1-3 个完整场景（.example-box + .step）
- 每个场景编号步骤，从开始到结束
- 过渡/流程图（SVG）

**必配 SVG**：过渡/流程图（≥1）

**HTML 结构**：
```html
<div class="section" id="s4">
  <div class="section-title"><span class="section-num">4</span> 举例说明</div>

  <div class="example-box">
    <h4>场景一：{场景标题}</h4>
    <div class="step"><div class="step-num">1</div><div class="step-text"><strong>{步骤名}</strong>：{详细描述}</div></div>
    <div class="step"><div class="step-num">2</div><div class="step-text"><strong>{步骤名}</strong>：{详细描述}</div></div>
    <!-- 更多步骤... -->
  </div>

  <div class="svg-wrap">
    <svg><!-- 过渡/流程图 --></svg>
  </div>
  <div class="svg-caption">图 N：{流程图标题}</div>
</div>
```

---

## 第 5 节：效果怎么样？

**目的**：用具体数字和事实说明实际表现。

**内容要素**：
- 性能/效果指标卡片（.card-grid + .card）
- 关键要点高亮块（.key-point）

**必配 SVG**：无

**HTML 结构**：
```html
<div class="section" id="s5">
  <div class="section-title"><span class="section-num">5</span> 效果怎么样？</div>

  <p>{总体评价}：</p>
  <div class="card-grid">
    <div class="card">
      <h4>{指标1标题}</h4>
      <p>{指标1数据+解释}</p>
    </div>
    <!-- 更多卡片... -->
  </div>

  <div class="key-point">{关键要点总结}</div>
</div>
```

---

## 第 6 节：解决了哪些痛点？

**目的**：用"没有它时"vs"有了它后"的对比展示价值。

**内容要素**：
- 前后对比表格（3列：痛点 / 没有时的困境 / 有了后的改变）

**必配 SVG**：无

**HTML 结构**：
```html
<div class="section" id="s6">
  <div class="section-title"><span class="section-num">6</span> 解决了哪些痛点？</div>

  <div class="table-wrap">
    <table>
      <thead><tr><th>痛点</th><th>没有 {主题} 时</th><th>有了 {主题} 后</th></tr></thead>
      <tbody>
        <tr>
          <td><strong>{痛点1}</strong></td>
          <td>{没有时的困境}</td>
          <td>{有了后的改变}</td>
        </tr>
        <!-- 更多行... -->
      </tbody>
    </table>
  </div>
</div>
```

---

## 第 7 节：目前还有哪些问题？

**目的**：客观呈现不足和正在改进的方向。

**内容要素**：
- 问题列表（.pros-cons 双栏，左侧 .con = 问题，右侧 .pro = 改进方向）

**必配 SVG**：无

**HTML 结构**：
```html
<div class="section" id="s7">
  <div class="section-title"><span class="section-num">7</span> 目前还有哪些问题？</div>

  <div class="pros-cons">
    <div class="con">
      <h4>现存问题与挑战</h4>
      <ul>
        <li><strong>{问题1}</strong>：{描述}</li>
        <!-- 更多... -->
      </ul>
    </div>
    <div class="pro">
      <h4>正在改进的方向</h4>
      <ul>
        <li><strong>{改进1}</strong>：{描述}</li>
        <!-- 更多... -->
      </ul>
    </div>
  </div>
</div>
```

---

## 第 8 节：主要应用场景

**目的**：展示实际用途，让读者判断与自己需求是否匹配。

**内容要素**：
- 图标场景卡片（.scenario-grid + .scenario-card）
- 按分类的详细表格

**必配 SVG**：无

**HTML 结构**：
```html
<div class="section" id="s8">
  <div class="section-title"><span class="section-num">8</span> 主要应用场景</div>

  <div class="scenario-grid">
    <div class="scenario-card">
      <div class="icon">{emoji图标}</div>
      <h4>{场景名}</h4>
      <p>{一句话描述}</p>
    </div>
    <!-- 更多卡片... -->
  </div>

  <div class="subsection">
    <div class="subsection-title">按{分类维度}分类的典型应用</div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>{分类}</th><th>优势</th><th>典型应用</th><th>代表产品</th></tr></thead>
        <tbody><!-- 数据行 --></tbody>
      </table>
    </div>
  </div>
</div>
```

---

## 第 9 节：一图总结

**目的**：用一个径向/关系 SVG 图把全部内容浓缩在一张图中。

**内容要素**：
- 径向总结图（SVG）：中心圆 = 主题，周围 6 框 = 6 个核心维度的精炼概括

**必配 SVG**：径向总结图（1 个，必需）

**HTML 结构**：
```html
<div class="section" id="s9">
  <div class="section-title"><span class="section-num">9</span> 一图总结</div>

  <div class="svg-wrap">
    <svg><!-- 径向总结图 --></svg>
  </div>
  <div class="svg-caption">图 N：{主题} 全景总结</div>
</div>
```

---

## 图表编号规则

- SVG 图表从第 3 节开始编号：图 1（第 3 节），图 2、图 3...（后续节）
- 第 1-2 节不用 SVG，用统计行、卡片、表格
- 第 5-8 节通常不用 SVG
- 第 9 节必配 1 个径向总结图
- 图表编号全局连续，不按节重置
