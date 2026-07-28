# 跨云产品映射查询页面（index.html）设计

## 背景与目标

仓库根目录的 `product-mapping.json` 维护了 AWS / Azure / GCP 之间的跨云产品映射数据：
- `groups`：67 条已做精细配对的跨云产品分组，覆盖 Compute / Database / Serverless / Developer Tools / Management & Governance 五个试点分类。
- `unmapped.<category>.<vendor>.trulyUnmapped`：646 条尚未做跨云配对的单厂商产品记录，字段结构与 `groups` 中的条目完全一致（category / name / confidence / products.{aws,azure,gcp} / notes，均有 `-cn` 中文字段），只是 `confidence` 固定为 `"none"`，且 `products` 里只有一个厂商有数据。

目标是基于这份数据生成一个静态的 `index.html`，作为跨云产品的多维度查询工具：按分类、厂商、关键词筛选，快速找到某个产品在其他云厂商的对应物，或确认某个分类下哪些产品还没有做跨云配对。

## 数据整合

`groups` 和 `unmapped.*.trulyUnmapped` 结构一致，可以直接拼接成一份统一的 `rows` 数组，每条记录渲染为表格的一行，无需区分数据来源：

```
row = {
  id, category, categoryCn,
  name, nameCn,
  confidence,           // "high" | "medium" | "low" | "none"
  notes, notesCn,
  products: {
    aws:   [{ name, link, description, descriptionCn }, ...],
    azure: [...],
    gcp:   [...],
  }
}
```

`unmapped.<category>.<vendor>.mappedUnderOtherCategory` 是纯字符串数组（引用已在别的分类下出现过的产品名），不需要在页面里单独展示。

分类下拉列表使用 `allCategories`（55 个），中文标签取自 `categoryLabels-cn`。

汇总后预计约 713 行数据。

## 技术方案

- 写一个 Node 脚本 `build-index.js`（提交到仓库），职责：
  1. 读取 `product-mapping.json`。
  2. 按上述结构拼出统一的 `rows` 数组和 `categories` 列表。
  3. 把 `{ generatedAt, categories, rows }` 序列化后，通过字符串替换注入到内置的 HTML 模板中（`window.__DATA__ = {...}`）。
  4. 生成最终的 `index.html`，写到仓库根目录。
- 最终产物 `index.html` 是零依赖的纯静态单文件：数据内嵌在 `<script>` 标签里，不使用 `fetch` 读取外部 JSON，避免 `file://` 协议下的 CORS 限制，可以直接双击用浏览器打开。
- 不引入任何构建工具或第三方前端框架/CDN 依赖；筛选、渲染逻辑用原生 JS 实现。
- 以后 `product-mapping.json` 更新后，重新运行 `node build-index.js` 即可重新生成页面，无需手工同步数据。

## 页面交互

**顶部**
- 标题 + 副标题（简要说明用途/数据来源）。
- 语言切换按钮：EN / 中文，默认英文。切换范围覆盖 UI 文字（按钮、筛选标签、表头等）+ 数据内容（分类名、分组名、产品描述、notes）。产品官方名称和链接始终保持原文，不翻译。

**筛选栏**
- 分类下拉框（含"全部分类"选项）。
- 厂商筛选：AWS / Azure / GCP 三个可勾选的 chip，多选时取"与"关系（即只保留同时具备所有勾选厂商对应产品的行），用于快速找"这几家云都有对应产品"的场景。
- 关键词搜索框：实时匹配产品名 / 分组名 / 描述（中英文字段都参与匹配，不受当前显示语言影响，保证切换语言后搜索结果不跳变）。
- 筛选结果计数："Showing X of 713"。

**主表格**
- 列：分类 | 概念名称 | AWS 产品 | Azure 产品 | GCP 产品 | 置信度徽标。
- 置信度徽标颜色区分：高（High）/ 中（Medium）/ 低（Low）/ 暂未匹配（Unmatched，对应 `confidence: none`），四档配色。
- 单元格内若该厂商有多个产品，堆叠列出（产品名可点击跳转官方文档，下方附一行描述）；若该厂商无对应产品，显示统一的占位符 `–`。
- 按分类分组展示，组内先按置信度排序（high → medium → low → none），保证已配对的概念排在前面、未配对的单厂商产品排在组内靠后位置。每个分类分组带小标题和该组命中数量。
- 每行可展开/收起查看 `notes`（配对依据或"尚未找到跨云对应产品"之类的说明），默认收起，只有存在 notes 时才显示展开入口。
- 筛选结果为空时显示明确的"无匹配结果"提示。

## 视觉风格

实现时会调用 `frontend-design` 技能产出一版有辨识度的排版（清晰的字体层级、克制配色、响应式布局），避免默认浏览器表格的呆板观感。本期不做统计图表/仪表盘（用户已确认只需要基础查询功能）。

## 范围之外（本期不做）

- 不做置信度筛选器（只做展示徽标，不作为筛选维度）。
- 不做汇总统计图表/仪表盘。
- 不引入分页或虚拟滚动（约 713 行原生 JS 渲染 + 筛选足够流畅）。
- 不修改现有的 `cloud-compare-*.md` 文档，`index.html` 是独立的新增查询工具。
