# SVG 图表绘制指南

> 所有 SVG 图表必须内嵌在 HTML 中，使用深色主题配色，与报告整体风格一致。

## 通用配色规则

| 用途 | 颜色 | CSS 变量 |
|------|------|---------|
| 主强调 | `#6c8cff` | `--accent` |
| 次强调 | `#a78bfa` | `--accent2` |
| 成功/正面 | `#34d399` | `--accent3` |
| 警告/中性 | `#f59e0b` | `--accent4` |
| 危险/负面 | `#f472b6` | `--accent5` |
| 信息/辅助 | `#22d3ee` | `--accent6` |
| 背景填充 | `#1e2030` | `--bg3` |
| 边框 | `#2a2d42` | `--border` |
| 主文字 | `#e0e0e8` | `--text` |
| 副文字 | `#9ca0b0` | `--text2` |

## 通用 SVG 属性

```xml
<svg viewBox="0 0 WIDTH HEIGHT" xmlns="http://www.w3.org/2000/svg">
```

- 使用 `viewBox` 实现响应式缩放
- 不设置固定 width/height，让 CSS `.svg-wrap svg { max-width:100%; height:auto; }` 控制
- 文字使用 `font-family="-apple-system, 'Segoe UI', sans-serif"`

---

## 图表类型 1：时间线图

**用途**：展示演进脉络（如 LeNet → EfficientNet）

**模板**：
```xml
<svg viewBox="0 0 900 320" xmlns="http://www.w3.org/2000/svg">
  <!-- 主轴线 -->
  <line x1="60" y1="160" x2="840" y2="160" stroke="#2a2d42" stroke-width="3"/>

  <!-- 节点 1 -->
  <circle cx="100" cy="160" r="18" fill="#6c8cff" opacity="0.9"/>
  <text x="100" y="165" text-anchor="middle" fill="#fff" font-size="11" font-weight="700">年份</text>
  <text x="100" y="120" text-anchor="middle" fill="#6c8cff" font-size="14" font-weight="700">名称</text>
  <text x="100" y="200" text-anchor="middle" fill="#9ca0b0" font-size="11">描述1</text>
  <text x="100" y="216" text-anchor="middle" fill="#9ca0b0" font-size="11">描述2</text>

  <!-- 更多节点... -->

  <!-- 连接箭头 -->
  <polygon points="835,155 845,160 835,165" fill="#2a2d42"/>
</svg>
```

**设计规则**：
- 节点间距均匀分布
- 每个节点：年份在圆内，名称在上方，描述在下方
- 不同节点用不同强调色区分
- 末尾加箭头表示"继续演进"

---

## 图表类型 2：流程图

**用途**：展示端到端数据流/处理管线

**模板**：
```xml
<svg viewBox="0 0 900 200" xmlns="http://www.w3.org/2000/svg">
  <!-- 步骤框 -->
  <rect x="20" y="60" width="120" height="80" rx="10" fill="#1e2030" stroke="#6c8cff" stroke-width="2"/>
  <text x="80" y="95" text-anchor="middle" fill="#6c8cff" font-size="14" font-weight="700">步骤名</text>
  <text x="80" y="115" text-anchor="middle" fill="#9ca0b0" font-size="11">维度: H×W×C</text>

  <!-- 箭头 -->
  <line x1="140" y1="100" x2="170" y2="100" stroke="#6c8cff" stroke-width="2"/>
  <polygon points="168,95 178,100 168,105" fill="#6c8cff"/>

  <!-- 更多步骤... -->
</svg>
```

**设计规则**：
- 每步用圆角矩形，内含步骤名 + 维度/数据标注
- 步骤间用箭头连接
- 关键步骤边框用强调色，普通步骤用 `#2a2d42`
- 维度/数据变化用副文字色标注

---

## 图表类型 3：架构图

**用途**：展示模块堆叠/网络结构

**模板**：
```xml
<svg viewBox="0 0 400 600" xmlns="http://www.w3.org/2000/svg">
  <!-- 输入 -->
  <rect x="100" y="20" width="200" height="40" rx="8" fill="#1e2030" stroke="#6c8cff" stroke-width="2"/>
  <text x="200" y="45" text-anchor="middle" fill="#6c8cff" font-size="13" font-weight="600">输入层</text>

  <!-- 模块堆叠 -->
  <rect x="80" y="80" width="240" height="50" rx="8" fill="#1e2030" stroke="#a78bfa" stroke-width="2"/>
  <text x="200" y="100" text-anchor="middle" fill="#a78bfa" font-size="13" font-weight="600">卷积层 C1</text>
  <text x="200" y="118" text-anchor="middle" fill="#9ca0b0" font-size="11">6 @ 28×28</text>

  <!-- 连接线 -->
  <line x1="200" y1="60" x2="200" y2="80" stroke="#2a2d42" stroke-width="2"/>

  <!-- 更多层... -->

  <!-- 输出 -->
  <rect x="100" y="540" width="200" height="40" rx="8" fill="#1e2030" stroke="#34d399" stroke-width="2"/>
  <text x="200" y="565" text-anchor="middle" fill="#34d399" font-size="13" font-weight="600">输出层</text>
</svg>
```

**设计规则**：
- 纵向堆叠，从上到下
- 输入层用蓝色边框，输出层用绿色边框
- 中间层按类型用不同颜色（卷积=紫，池化=青，全连接=橙）
- 每层标注名称 + 关键参数
- 层间用细线连接

---

## 图表类型 4：原理示意图

**用途**：展示核心机制（如卷积滑动、池化操作）

**模板**（卷积滑动示例）：
```xml
<svg viewBox="0 0 700 300" xmlns="http://www.w3.org/2000/svg">
  <!-- 输入矩阵 -->
  <g transform="translate(30,30)">
    <text x="75" y="-8" text-anchor="middle" fill="#6c8cff" font-size="13" font-weight="600">输入</text>
    <!-- 网格 -->
    <rect x="0" y="0" width="150" height="150" fill="none" stroke="#2a2d42" stroke-width="1"/>
    <!-- 网格线 + 数值 -->
    <!-- 高亮窗口 -->
    <rect x="30" y="30" width="60" height="60" fill="rgba(108,140,255,.15)" stroke="#6c8cff" stroke-width="2" rx="2"/>
  </g>

  <!-- 卷积核 -->
  <g transform="translate(280,60)">
    <text x="45" y="-8" text-anchor="middle" fill="#a78bfa" font-size="13" font-weight="600">卷积核</text>
    <rect x="0" y="0" width="90" height="90" fill="none" stroke="#a78bfa" stroke-width="2" rx="4"/>
    <!-- 核数值 -->
  </g>

  <!-- 箭头 -->
  <text x="245" y="110" fill="#9ca0b0" font-size="20">⊗</text>

  <!-- 输出 -->
  <g transform="translate(460,50)">
    <text x="60" y="-8" text-anchor="middle" fill="#34d399" font-size="13" font-weight="600">输出</text>
    <rect x="0" y="0" width="120" height="120" fill="none" stroke="#34d399" stroke-width="1"/>
    <!-- 高亮计算结果 -->
  </g>
</svg>
```

**设计规则**：
- 左侧输入 → 中间操作 → 右侧输出
- 高亮区域用半透明强调色填充
- 操作符号用大号文字（⊗, +, ↓ 等）
- 标注关键数值

---

## 图表类型 5：对比图

**用途**：横向对比多个方案的性能/特征

**模板**（柱状对比）：
```xml
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg">
  <!-- Y 轴 -->
  <line x1="60" y1="20" x2="60" y2="260" stroke="#2a2d42" stroke-width="2"/>
  <!-- X 轴 -->
  <line x1="60" y1="260" x2="760" y2="260" stroke="#2a2d42" stroke-width="2"/>

  <!-- 柱状 -->
  <rect x="100" y="80" width="60" height="180" rx="4" fill="#6c8cff" opacity="0.8"/>
  <text x="130" y="75" text-anchor="middle" fill="#6c8cff" font-size="12" font-weight="600">值</text>
  <text x="130" y="280" text-anchor="middle" fill="#9ca0b0" font-size="12">标签</text>

  <!-- 更多柱... -->
</svg>
```

**设计规则**：
- 柱状图用强调色，不同系列用不同颜色
- 数值标注在柱顶
- 标签在 X 轴下方
- Y 轴标注刻度

---

## 图表类型 6：关系图

**用途**：展示模块依赖/实体关系

**模板**：
```xml
<svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
  <!-- 节点 -->
  <rect x="200" y="20" width="160" height="50" rx="25" fill="#1e2030" stroke="#6c8cff" stroke-width="2"/>
  <text x="280" y="50" text-anchor="middle" fill="#6c8cff" font-size="14" font-weight="600">节点A</text>

  <!-- 连线 -->
  <line x1="280" y1="70" x2="280" y2="120" stroke="#2a2d42" stroke-width="2"/>
  <text x="290" y="100" fill="#9ca0b0" font-size="11">关系</text>

  <!-- 更多节点和连线... -->
</svg>
```

**设计规则**：
- 节点用圆角矩形或椭圆
- 连线用细线 + 关系标签
- 层级从上到下或从左到右
- 不同类型节点用不同颜色

---

## SVG 生成注意事项

1. **viewBox 尺寸**：根据内容量合理设置，常见尺寸：
   - 时间线：900×320
   - 流程图：900×200（横向）或 400×600（纵向）
   - 架构图：400×500~800
   - 原理图：700×300
   - 对比图：800×300
   - 关系图：600×400

2. **文字可读性**：
   - 标题文字 ≥ 13px
   - 描述文字 ≥ 11px
   - 使用 `text-anchor="middle"` 居中
   - 避免文字重叠

3. **颜色一致性**：严格使用上方配色表，不要引入新颜色

4. **圆角**：矩形统一用 `rx="8"` 或 `rx="10"`

5. **透明度**：填充用 `opacity="0.8"` 或 `0.9`，背景高亮用 `rgba()` 半透明

6. **边框粗细**：主边框 2px，辅助边框 1px
