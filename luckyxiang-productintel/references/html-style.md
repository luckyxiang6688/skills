# productintel HTML 报告样式模板

> 从 Skydio 竞品分析报告提取并参数化的完整 HTML/CSS/JS 模板。
> Skill 步骤4 生成 HTML 时引用此文件。

## 设计规格

| 属性 | 值 |
|------|-----|
| 主色调 | `#1a365d`（深蓝） |
| 副色调 | `#2c5282`（中蓝） |
| 强调色 | `#3182ce`（亮蓝） |
| 背景色 | `#f7fafc`（浅灰） |
| 卡片背景 | `#ffffff` |
| 正文字体 | `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` |
| 代码字体 | `'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace` |
| 左侧导航宽度 | `260px` |
| 移动端断点 | `768px` |

## CSS 变量系统

```css
:root {
  --primary: #1a365d;
  --secondary: #2c5282;
  --accent: #3182ce;
  --bg: #f7fafc;
  --card-bg: #ffffff;
  --text: #1a202c;
  --text-light: #4a5568;
  --border: #e2e8f0;
  --success: #38a169;
  --warning: #d69e2e;
  --danger: #e53e3e;
  --nav-width: 260px;
  --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}
```

## 完整 HTML 骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{COMPANY_NAME}} 竞品分析报告</title>
<style>
/* === 重置与基础 === */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: var(--font-body);
  color: var(--text);
  background: var(--bg);
  line-height: 1.7;
}

/* === 左侧导航栏 === */
.left-nav {
  position: fixed;
  top: 0; left: 0;
  width: var(--nav-width);
  height: 100vh;
  background: var(--primary);
  color: #fff;
  overflow-y: auto;
  z-index: 1000;
  padding: 20px 0;
  transition: transform 0.3s ease;
}
.left-nav::-webkit-scrollbar { width: 4px; }
.left-nav::-webkit-scrollbar-track { background: transparent; }
.left-nav::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 2px; }
.nav-brand {
  padding: 0 20px 16px;
  font-size: 1.3em;
  font-weight: 800;
  letter-spacing: 2px;
  border-bottom: 1px solid rgba(255,255,255,0.15);
  margin-bottom: 8px;
}
.nav-brand small {
  display: block;
  font-size: 0.55em;
  font-weight: 400;
  letter-spacing: 0;
  opacity: 0.7;
  margin-top: 2px;
}
.nav-list { list-style: none; }
.nav-item {
  display: block;
  padding: 8px 16px;
  color: rgba(255,255,255,0.85);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
  cursor: pointer;
}
.nav-item:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}
.nav-item.active {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border-left: 3px solid var(--accent);
  font-weight: 600;
}
.nav-category {
  padding: 16px 16px 4px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.5;
  font-weight: 700;
  color: rgba(255,255,255,0.7);
}
.nav-sub-item {
  display: block;
  padding: 6px 16px 6px 36px;
  color: rgba(255,255,255,0.75);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
  cursor: pointer;
}
.nav-sub-item:hover {
  background: rgba(255,255,255,0.08);
  color: #fff;
}
.nav-sub-item.active {
  background: rgba(255,255,255,0.12);
  color: #fff;
  border-left: 3px solid var(--accent);
  font-weight: 600;
}

/* === 汉堡菜单（移动端） === */
.hamburger {
  display: none;
  position: fixed;
  top: 12px; left: 12px;
  z-index: 1100;
  width: 40px; height: 40px;
  background: var(--primary);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.hamburger span {
  display: block;
  width: 20px; height: 2px;
  background: #fff;
  margin: 3px 0;
  transition: 0.3s;
}
.nav-overlay {
  display: none;
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 999;
}

/* === 主内容区 === */
.main-content {
  margin-left: var(--nav-width);
  min-height: 100vh;
}
.container { max-width: 1100px; margin: 0 auto; padding: 20px; }

/* === 报告头部 === */
.header {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  padding: 40px 0;
  margin-bottom: 30px;
}
.header .container { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px; }
.header h1 { font-size: 2em; font-weight: 700; }
.header .meta { font-size: 0.9em; opacity: 0.85; margin-top: 8px; }
.header .logo-area { text-align: right; }
.header .logo-area .brand { font-size: 1.5em; font-weight: 800; letter-spacing: 2px; }

/* === 章节容器 === */
.section {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.section h2 {
  font-size: 1.5em;
  color: var(--primary);
  border-bottom: 3px solid var(--accent);
  padding-bottom: 10px;
  margin-bottom: 20px;
}
.section h3 {
  font-size: 1.2em;
  color: var(--secondary);
  margin: 24px 0 12px;
  padding-left: 12px;
  border-left: 4px solid var(--accent);
}
.section h4 {
  font-size: 1.05em;
  color: var(--text);
  margin: 16px 0 8px;
}

/* === 表格 === */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 20px;
  font-size: 0.92em;
}
th, td {
  padding: 10px 14px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}
th {
  background: var(--primary);
  color: white;
  font-weight: 600;
}
tr:nth-child(even) { background: #f8fafc; }
tr:hover { background: #edf2f7; }

/* === 产品分类卡片（核心组件） === */
.product-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin: 20px 0;
}
.product-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.2s, box-shadow 0.2s;
}
.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}
.product-card-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.product-card-header .icon {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4em;
  flex-shrink: 0;
}
.product-card-header .title-group { flex: 1; }
.product-card-header .title-group h4 {
  margin: 0;
  font-size: 1.1em;
  font-weight: 700;
}
.product-card-header .title-group .subtitle {
  font-size: 0.8em;
  opacity: 0.85;
  margin-top: 2px;
}
.product-card-body {
  padding: 0 20px 16px;
  background: white;
}
.product-card-body .item {
  display: flex;
  align-items: baseline;
  padding: 7px 0;
  border-bottom: 1px solid #f0f0f0;
  gap: 8px;
}
.product-card-body .item:last-child { border-bottom: none; }
.product-card-body .item .name {
  font-weight: 600;
  font-size: 0.92em;
  white-space: nowrap;
}
.product-card-body .item .desc {
  font-size: 0.82em;
  color: var(--text-light);
  line-height: 1.4;
}
.product-card-body .sub-group {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed #e0e0e0;
}
.product-card-body .sub-group-title {
  font-size: 0.78em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
  opacity: 0.6;
}

/* 产品分类卡片颜色 */
.product-card.cat-drones .product-card-header { background: linear-gradient(135deg, #1a365d, #2c5282); color: white; }
.product-card.cat-drones .icon { background: rgba(255,255,255,0.2); }
.product-card.cat-docks .product-card-header { background: linear-gradient(135deg, #2d3748, #4a5568); color: white; }
.product-card.cat-docks .icon { background: rgba(255,255,255,0.2); }
.product-card.cat-software .product-card-header { background: linear-gradient(135deg, #2b6cb0, #3182ce); color: white; }
.product-card.cat-software .icon { background: rgba(255,255,255,0.2); }
.product-card.cat-platform .product-card-header { background: linear-gradient(135deg, #553c9a, #6b46c1); color: white; }
.product-card.cat-platform .icon { background: rgba(255,255,255,0.2); }
.product-card.cat-extend .product-card-header { background: linear-gradient(135deg, #276749, #38a169); color: white; }
.product-card.cat-extend .icon { background: rgba(255,255,255,0.2); }
.product-card.cat-services .product-card-header { background: linear-gradient(135deg, #744210, #b7791f); color: white; }
.product-card.cat-services .icon { background: rgba(255,255,255,0.2); }
.product-card .dev-tag {
  display: inline-block;
  background: #fefcbf;
  color: #744210;
  font-size: 0.7em;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  margin-left: 4px;
  vertical-align: middle;
}
.product-card .core-tag {
  display: inline-block;
  background: #e9d8fd;
  color: #44337a;
  font-size: 0.7em;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  margin-left: 4px;
  vertical-align: middle;
}

/* === 指标卡片（用于产品详细页） === */
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 16px 0;
}
.metric-card {
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}
.metric-card .value { font-size: 2em; font-weight: 800; }
.metric-card .label { font-size: 0.85em; opacity: 0.9; margin-top: 4px; }

/* === 高亮提示框 === */
.highlight {
  background: #ebf8ff;
  border-left: 4px solid var(--accent);
  padding: 12px 16px;
  margin: 16px 0;
  border-radius: 0 8px 8px 0;
  font-size: 0.95em;
}

/* === 传感器卡片 === */
.sensor-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  margin: 12px 0;
  overflow: hidden;
}
.sensor-card-header {
  background: var(--primary);
  color: white;
  padding: 10px 16px;
  font-weight: 600;
  font-size: 0.95em;
}
.sensor-card-header small {
  font-weight: 400;
  opacity: 0.85;
  margin-left: 8px;
}
.sensor-card-body {
  padding: 8px 16px;
}
.sensor-item {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
  gap: 8px;
}
.sensor-item:last-child { border-bottom: none; }
.sensor-item .s-name {
  font-weight: 700;
  font-size: 0.9em;
  white-space: nowrap;
}
.sensor-item .s-spec {
  font-family: var(--font-mono);
  font-size: 0.82em;
  color: var(--accent);
}
.sensor-item .s-desc {
  font-size: 0.82em;
  color: var(--text-light);
}

/* === 标签系统 === */
.tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 600;
  margin: 2px 4px 2px 0;
}
.tag-high { background: #c6f6d5; color: #22543d; }
.tag-mid { background: #fefcbf; color: #744210; }
.tag-low { background: #fed7d7; color: #742a2a; }
.tag-new { background: #bee3f8; color: #2a436a; }
.tag-core { background: #e9d8fd; color: #44337a; }

/* === 可靠性标签 === */
.reliability-high { color: var(--success); font-weight: 600; }
.reliability-medium { color: var(--warning); font-weight: 600; }
.reliability-low { color: var(--danger); font-weight: 600; }

/* === 列表 === */
ul, ol { margin: 8px 0 16px 24px; }
li { margin-bottom: 4px; }

/* === 代码块 === */
code {
  font-family: var(--font-mono);
  background: #edf2f7;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
}
pre {
  background: #1a202c;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
  font-size: 13px;
  line-height: 1.5;
}

/* === 响应式 === */
@media (max-width: 768px) {
  .left-nav { transform: translateX(-100%); }
  .left-nav.open { transform: translateX(0); }
  .nav-overlay.open { display: block; }
  .hamburger { display: flex; }
  .main-content { margin-left: 0; }
  .container { padding: 60px 16px 32px; }
  .product-grid { grid-template-columns: 1fr; }
  .metrics { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 769px) and (max-width: 1024px) {
  .product-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
</head>
<body>

<!-- 汉堡菜单按钮 -->
<button class="hamburger" onclick="toggleNav()">
  <span></span><span></span><span></span>
</button>

<!-- 遮罩层 -->
<div class="nav-overlay" onclick="toggleNav()"></div>

<!-- 左侧导航栏 -->
<nav class="left-nav" id="leftNav">
  <div class="nav-brand">
    {{COMPANY_NAME}}
    <small>竞品分析报告</small>
  </div>

  <!-- 导航项由步骤4动态生成，格式如下： -->
  <!--
  <ul class="nav-list">
    <li><a class="nav-item" href="#sec1">一、公司概况</a></li>
    <li><a class="nav-item" href="#sec2">二、产品线总览</a></li>
    <li class="nav-category">硬件产品</li>
    <li><a class="nav-sub-item" href="#sec3-1">3.1 产品A</a></li>
    <li class="nav-category">软件平台</li>
    <li><a class="nav-sub-item" href="#sec4-1">4.1 平台A</a></li>
    <li><a class="nav-item" href="#sec8">八、核心价值</a></li>
  </ul>
  -->
  {{NAV_ITEMS}}
</nav>

<!-- 主内容区 -->
<main class="main-content">

<!-- 报告头部（阶段4.1骨架写入时包含） -->
<div class="header">
  <div class="container">
    <div>
      <h1>{{COMPANY_NAME}} 竞品分析报告</h1>
      <div class="meta">数据采集日期：{{COLLECTION_DATE}} | 报告生成日期：{{REPORT_DATE}}</div>
    </div>
    <div class="logo-area">
      <div class="brand">{{COMPANY_NAME}}</div>
    </div>
  </div>
</div>

<div class="container">
<!-- SECTION_INSERT_POINT — 分段写入标记，每章节追加到此处，标记始终保持在最后 -->
</div>
</main>

<script>
// 汉堡菜单切换
function toggleNav() {
  document.getElementById('leftNav').classList.toggle('open');
  document.querySelector('.nav-overlay').classList.toggle('open');
}

// IntersectionObserver 滚动高亮
const sections = document.querySelectorAll('.section');
const navLinks = document.querySelectorAll('.nav-item, .nav-sub-item');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navLinks.forEach(link => link.classList.remove('active'));
      const id = entry.target.id;
      const activeLink = document.querySelector(`.nav-item[href="#${id}"], .nav-sub-item[href="#${id}"]`);
      if (activeLink) activeLink.classList.add('active');
    }
  });
}, { rootMargin: '-10% 0px -80% 0px' });

sections.forEach(section => observer.observe(section));

// 点击导航项关闭移动端菜单
navLinks.forEach(link => {
  link.addEventListener('click', () => {
    if (window.innerWidth <= 768) toggleNav();
  });
});
</script>
</body>
</html>
```

## 导航项生成规则

根据采集到的产品结构动态生成导航项。使用 `<ul class="nav-list">` 包裹，格式：

```html
<ul class="nav-list">
  <!-- 一级章节 -->
  <li><a class="nav-item" href="#sec1">一、公司概况</a></li>
  <li><a class="nav-item" href="#sec2">二、产品线总览</a></li>

  <!-- 分类标签 -->
  <li class="nav-category">硬件产品</li>
  <!-- 二级子项 -->
  <li><a class="nav-sub-item" href="#sec3-1">3.1 产品A</a></li>
  <li><a class="nav-sub-item" href="#sec3-2">3.2 产品B</a></li>

  <li class="nav-category">软件平台</li>
  <li><a class="nav-sub-item" href="#sec5-1">5.1 平台A</a></li>

  <!-- 固定章节 -->
  <li><a class="nav-item" href="#sec8">八、核心价值</a></li>
  <li><a class="nav-item" href="#sec10">十、数据可靠性</a></li>
</ul>
```

## 产品线总览（第2节）生成规则

**必须使用 `product-card` 组件**，而不是简单表格或卡片。按产品分类分组，每个分类一张卡片。

```html
<!-- 产品线总览示例 -->
<div class="section" id="sec2">
  <h2>二、产品线总览</h2>
  <div class="highlight">
    <strong>核心理念：</strong>{一句话总结公司产品体系的设计理念}
  </div>
  <div class="product-grid">
    <!-- 硬件产品分类 -->
    <div class="product-card cat-drones">
      <div class="product-card-header">
        <div class="icon">&#9992;</div>  <!-- 图标：用HTML实体 -->
        <div class="title-group">
          <h4>无人机 Drones</h4>       <!-- 分类名 -->
          <div class="subtitle">4款产品，覆盖全场景</div>  <!-- 数量+描述 -->
        </div>
      </div>
      <div class="product-card-body">
        <div class="item">
          <span class="name">X10</span>   <!-- 产品名 -->
          <span class="desc">中型四旋翼，主力产品</span>  <!-- 一句话描述 -->
        </div>
        <div class="item">
          <span class="name">X10D<span class="dev-tag">国防</span></span>  <!-- 标签 -->
          <span class="desc">国防版，EW抗干扰</span>
        </div>
        <!-- 更多产品... -->
        <div class="sub-group">          <!-- 子分组（可选） -->
          <div class="sub-group-title">配件</div>
          <div class="item">
            <span class="name">传感器套件</span>
            <span class="desc">3款可互换载荷</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 软件分类 -->
    <div class="product-card cat-software">
      <div class="product-card-header">
        <div class="icon">&#128187;</div>
        <div class="title-group">
          <h4>软件 Software</h4>
          <div class="subtitle">端到端覆盖</div>
        </div>
      </div>
      <div class="product-card-body">
        <div class="item">
          <span class="name">核心软件<span class="core-tag">核心</span></span>
          <span class="desc">描述</span>
        </div>
      </div>
    </div>

    <!-- 更多分类... -->
  </div>
</div>
```

### 产品详细页生成规则

产品详细能力（第3节起）每个产品独立一个 `h3`，使用：
- `metrics` 指标卡片展示关键规格
- `table` 展示参数表
- `sensor-card` 展示传感器/载荷套件
- `highlight` 展示核心亮点

```html
<h3 id="sec3-1">3.1 产品名 — 一句话定位</h3>
<p><strong>定位：</strong>详细描述</p>

<div class="metrics">
  <div class="metric-card">
    <div class="value">数值</div>
    <div class="label">指标名</div>
  </div>
  <!-- 更多指标 -->
</div>

<h4>核心参数</h4>
<table>
  <tr><th>参数</th><th>数值</th><th>备注</th></tr>
  <tr><td>参数名</td><td>数值</td><td>备注</td></tr>
</table>

<h4>传感器/功能</h4>
<div class="sensor-card">
  <div class="sensor-card-header">传感器名<small>— 用途</small></div>
  <div class="sensor-card-body">
    <div class="sensor-item">
      <span class="s-name">名称</span>
      <span class="s-spec">规格</span>
      <span class="s-desc">— 应用场景</span>
    </div>
  </div>
</div>
```

## 卡片颜色映射

| 产品分类 | CSS 类 | 图标 | 颜色 | 适用场景 |
|---------|--------|------|------|---------|
| 硬件产品 | `.cat-drones` | `&#9992;` | 深蓝渐变 | 无人机、机器人、设备、武器 |
| 基础设施 | `.cat-docks` | `&#127968;` | 灰色渐变 | 停机坪、充电站、基站、工厂 |
| 软件 | `.cat-software` | `&#128187;` | 蓝色渐变 | 应用、SaaS、工具 |
| 平台 | `.cat-platform` | `&#129504;` | 紫色渐变 | 引擎、框架、中间件、AI平台 |
| 扩展 | `.cat-extend` | `&#128279;` | 绿色渐变 | API、集成、SDK、开发者工具 |
| 服务 | `.cat-services` | `&#128737;` | 棕色渐变 | 咨询、培训、合规、保障 |

## HTML 实体图标参考

| 用途 | 实体 | 显示 |
|------|------|------|
| 无人机/飞行器 | `&#9992;` | ✈ |
| 基础设施/建筑 | `&#127968;` | 🏠 |
| 电脑/软件 | `&#128187;` | 💻 |
| 大脑/AI | `&#129504;` | 🧠 |
| 链接/集成 | `&#128279;` | 🔗 |
| 盾牌/安全 | `&#128737;` | 🛡 |
| 火箭 | `&#128640;` | 🚀 |
| 船/海事 | `&#9875;` | ⚓ |
| 卫星/太空 | `&#128752;` | 🛰 |
| 雷达/传感器 | `&#128225;` | 📡 |
| 齿轮/制造 | `&#9881;` | ⚙ |
| 武器/导弹 | `&#127919;` | 🎯 |

## 使用方式

Skill 步骤4 生成 HTML 时（分段写入模式）：

1. 读取此文件获取 CSS/JS/HTML 骨架
2. 替换 `{{COMPANY_NAME}}`、`{{COLLECTION_DATE}}`、`{{REPORT_DATE}}`、`{{NAV_ITEMS}}` 占位符
3. **阶段4.1**：用 Write 工具写入骨架文件（包含 CSS、导航栏、header、`<!-- SECTION_INSERT_POINT -->` 标记）
4. **阶段4.2~4.N**：逐章节用 Edit 工具追加内容：
   - `old_string` = `<!-- SECTION_INSERT_POINT — 分段写入标记，每章节追加到此处，标记始终保持在最后 -->`
   - `new_string` = 章节 HTML 内容 + `<!-- SECTION_INSERT_POINT — 分段写入标记，每章节追加到此处，标记始终保持在最后 -->`
5. **阶段4.N+1**：最后一个章节追加后，移除 `<!-- SECTION_INSERT_POINT -->` 标记
6. **产品线总览必须使用 `product-card` 组件**，按分类分组，每个分类一张卡片
7. 产品详细能力使用 `metrics` + `table` + `sensor-card` 组件
8. 每个主要章节用 `<div class="section" id="secN">` 包裹（IntersectionObserver 需要）
