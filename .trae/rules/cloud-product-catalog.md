---
description: 抓取/更新 AWS、Azure、GCP、阿里云产品目录，生成结构化 products-<vendor>.json，维护跨云产品映射 product-mapping.json，并生成静态查询页面 index.html。当用户提到"抓取/更新某云产品列表""生成产品目录 JSON""同步云产品数据""跨云产品映射/对应关系""重新生成 index 页面"，或要在本仓库补充某云厂商产品数据时使用。
---

# Cloud Product Catalog（云产品目录与跨云映射）

> **本 rule 是执行速查表，详细说明、扩展指南与最新约定以 skill 文档
> `.claude/skills/cloud-product-catalog/SKILL.md` 为准。** 当 skill 与 rule
> 出现冲突时，优先以 skill 为事实来源；若发现本 rule 的命令或注意事项已
> 滞后，应同步更新本 rule 并引用最新的 skill 文档。

维护本仓库的结构化云产品数据：从各云厂商官方站点抓取产品目录，统一成同一套 JSON
schema，支撑跨云产品映射与对比页面。所有脚本都是纯命令行程序，在**仓库根目录**执行。

## 数据流运行环境

| 依赖 | 版本要求 |
|---|---|
| Python | 3.8+（建议 3.10+） |
| Node.js | 18.0+ |

## 数据流

```
products-<vendor>.json  →  product-mapping.json  →  index.html
（四个源数据，抓取得到）   （映射，脚本+人工分组）   （查询页面，构建产物）
```

每次运行抓取脚本或 `build_mapping.py` 时，脚本会自动把本次 JSON 变更记录到
`diffs/refresh-diff-YYYY-MM-DD.txt`（按日期聚合、追加），包含新增/下线产品
摘要和统一 diff，方便 review 具体改了什么。

## 核心命令

```bash
# 1. 抓取/更新某云产品目录（全量重生成对应 products-<vendor>.json）
python .claude/skills/cloud-product-catalog/scripts/fetch_aws_products.py
python .claude/skills/cloud-product-catalog/scripts/fetch_azure_products.py   # 需先 pip install beautifulsoup4 lxml
python .claude/skills/cloud-product-catalog/scripts/fetch_gcp_products.py
python .claude/skills/cloud-product-catalog/scripts/fetch_alibabacloud_products.py

# 2. 重新生成跨云映射（读取四份 products-*.json，输出 product-mapping.json）
python .claude/skills/cloud-product-catalog/scripts/build_mapping.py

# 2.5 判断映射是否真的变了（变了才需要重建页面）
git diff --quiet product-mapping.json && echo "映射无变化，跳过页面重建" || echo "映射已变化，需要重建页面"

# 3. 重新生成查询页面（仅当 product-mapping.json 有变化时才需要跑）
node build-index.js

# 4. 校验（改完必跑：单元测试 + 三层一致性校验）
node --test lib/*.test.js
python .claude/skills/cloud-product-catalog/scripts/check_completeness.py
```

完整更新流程：跑抓取脚本 → git diff 对比新旧源数据 → 在 `build_mapping.py` 的
`GROUPS` 做**增量**修改 → 跑 build_mapping.py → 判断 `product-mapping.json`
是否变化：**无变化则跳过 `node build-index.js`**（映射没变页面内容就不会变，
check_completeness 会确认现有页面仍同步），**有变化才重建页面** → 最后跑第 4
步校验，全绿才算完成。

## 关键注意事项

- **增量，不全量覆盖**：厂商新增/改名/下线产品时，只在 `build_mapping.py` 现有
  `GROUPS` 基础上局部追加/修改，不要推翻重配。新引用的产品要在 `DESCRIPTION_CN`
  对应厂商下补中文描述，否则脚本报错。
- **index.html 是构建产物，不要手改**：改动一律通过 `index.template.html` + 重跑
  `build-index.js`。纯逻辑在 `lib/transform.js`、`lib/query.js`，改后先跑
  `node --test lib/*.test.js`。
- **映射没变就跳过页面重建**：`index.html` 的数据来自 `product-mapping.json`，
  跑完 `build_mapping.py` 后用 `git diff --quiet product-mapping.json` 判断——
  映射无变化时不要重跑 `build-index.js`，避免产生除 `generatedAt` 日期外无意义
  的页面改动；有变化才重建。
- **check_completeness.py 是最后一道关**：每次跑完抓取、build_mapping 或
  build-index 之后都要跑一次，确认源数据 → 映射 → 页面三层一致（退出码 0 = 通过）。
- **阿里云抓取要点**：需带完整浏览器请求头（否则被风控返回 punish 页）；产品数据
  在 `<div class="render-container-data" data-data="...">` 的转义 JSON 里，脚本还会
  补扫全页 `<a href=".../product/xxx">` 链接抓配置之外的产品（如 Model Studio）。

## 参考文档（按需查阅）

- 详细 skill 说明：`.claude/skills/cloud-product-catalog/SKILL.md`
- 各厂商抓取踩坑：`.claude/skills/cloud-product-catalog/references/azure.md`、`gcp.md`
- 映射分组原则与校准：`.claude/skills/cloud-product-catalog/references/mapping.md`
- 人工维护的多云对照表（新增分组先查它）：`cloud-compare-en-new.md`

## 本 rule 的维护约定

1. **事实来源**：本 rule 是执行速查表，详细实现说明、扩展指南、踩坑记录、
   新增厂商接入步骤等都以 `.claude/skills/cloud-product-catalog/SKILL.md`
   及 `references/` 下的 skill 文档为唯一事实来源。
2. **同步触发条件**：当 skill 文档发生以下变更时，应同步检查并更新本 rule：
   - 新增/删除/重命名云厂商或脚本；
   - 核心命令、输出文件路径、校验方式变化；
   - 关键注意事项（如增量原则、页面重建条件、反爬要求）发生变化；
   - 运行环境依赖版本变化。
3. **同步方式**：以 skill 文档为准，仅把本 rule 中**执行时最常用的命令和
   最关键的约束**精简保留；遇到细节疑问优先回到 skill 文档确认，不要把
   长篇实现细节复制到 rule 中，避免两边各自腐烂。
4. **冲突处理**：skill 与 rule 不一致时，一律以 skill 为准；本 rule 滞后时
   按上述同步触发条件更新。
