---
name: cloud-product-catalog
description: 抓取各大云厂商（AWS、Azure、GCP、阿里云等）官方文档站点的产品目录，生成结构化的 products-<vendor>.json（产品名称、分类、描述、链接），并在此基础上维护跨云产品映射数据，服务于本仓库（cloud-compare）的云平台产品对比文档，以及基于映射数据生成可直接打开的静态查询页面 index.html。当用户提到"抓取/更新 AWS（或 Azure/GCP/阿里云）产品列表"、"生成产品目录 JSON"、"同步云产品数据"、"跨云产品映射/对应关系"、"重新生成 index 页面"，或者要在 cloud-compare 仓库里补充某个云厂商的产品数据时，都应主动使用本 skill——即使用户没有直接说"skill"或给出脚本细节。目前已实现 AWS/Azure/GCP/阿里云抓取和查询页面生成，跨云映射逻辑的分类覆盖会持续在这个 skill 里迭代。
---

# Cloud Product Catalog

维护 cloud-compare 仓库的结构化云产品数据：从各云厂商官方文档站点抓取产品目录，
统一成同一套 JSON schema，最终支撑跨云产品的映射与对比（`cloud-compare-cn.md` /
`cloud-compare-en.md` 等文档背后的数据来源）。

## 运行环境

| 依赖 | 版本要求 |
|---|---|
| Python | 3.8+（建议 3.10+） |
| Node.js | 18.0+ |

这个 skill 会持续扩展，当前状态：

| 云厂商 | 状态 | 脚本 | 输出 |
|---|---|---|---|
| AWS | ✅ 已实现 | `scripts/fetch_aws_products.py` | `products-aws.json`（仓库根目录） |
| Azure | ✅ 已实现 | `scripts/fetch_azure_products.py` | `products-azure.json`（仓库根目录） |
| GCP | ✅ 已实现 | `scripts/fetch_gcp_products.py` | `products-gcp.json`（仓库根目录） |
| 阿里云 | ✅ 已实现 | `scripts/fetch_alibabacloud_products.py` | `products-alibabacloud.json`（仓库根目录） |
| 跨云产品映射 | ✅ 已实现（覆盖 AWS 全部 30 个分类 + 阿里云 13 个一级分类，214 个映射分组；category 已归一为 35 个 canonical 主名） | `scripts/build_mapping.py` | `product-mapping.json`（仓库根目录） |
| 查询页面 | ✅ 已实现 | `build-index.js`（仓库根目录） | `index.html`（仓库根目录） |
| 完整性校验 | ✅ 已实现 | `scripts/check_completeness.py` | 命令行报告 |

> **日常维护原则**：后续厂商产品更新走**增量**流程——重跑抓取脚本拿新源
> 数据，然后在 `build_mapping.py` 的现有 GROUPS 基础上做局部追加/修改，
> 不要全量重写映射。详见下方"日常更新流程：增量，不要全量覆盖"一节。

## 已有能力：抓取 AWS 产品目录

在**仓库根目录**下执行：

```bash
python .claude/skills/cloud-product-catalog/scripts/fetch_aws_products.py
```

会请求 `https://docs.aws.amazon.com/` 首页，解析出"Product guides & references"
模块下全部产品，输出 `products-aws.json` 到当前工作目录（默认就是仓库根目录，
需要自定义路径可加 `--output`）。

**实现要点**（改动脚本前务必先理解，否则容易解析出空结果）：

1. AWS 文档首页是客户端渲染的，产品数据不在可见 HTML 里，而是整份落地页数据
   以 URL 编码的 XML 塞进了隐藏的 `<input id="landing-page-xml" value="...">`
   属性里，需要先正则取出再 `urllib.parse.unquote` 解码。如果 AWS 改版导致
   这个 input 消失或改名，脚本会直接报错提示，需要重新找新的数据来源。
2. 解码后的 XML 里，`<section id="products">` 就是"Product guides & references"
   模块，其下每个 `<list-card>` 是一个分类，分类下的 `<list-card-item>` 才是产品。
3. 模块里混有"决策指南"类引导文档（比如"Choosing an AWS analytics service"），
   不是真实产品，脚本按 `href` 含 `/decision-guides/` 或标题以 "Choosing" 开头
   过滤掉。如果发现漏网的非产品条目，优先在这里补规则，而不是事后手动删数据。
4. 同一产品经常挂在多个分类下（例如 DynamoDB 同属 Database 和 Serverless），
   脚本按产品名合并，`categories` 存成数组，避免映射时把同一产品当成多条记录。

只用 Python 标准库（`urllib`、`re`、`xml.etree.ElementTree`、`json`），不依赖
第三方包，换环境也能直接跑。

## 已有能力：抓取 Azure 产品目录

在**仓库根目录**下执行：

```bash
python .claude/skills/cloud-product-catalog/scripts/fetch_azure_products.py
```

会请求 `https://azure.microsoft.com/en-us/products`（"Browse all products"
页面），解析出页面里按分类罗列的全部产品，输出 `products-azure.json`。

Azure 这个页面是服务端渲染的真实营销站 HTML（不像 AWS 那样有整页结构化数据），
所以这个脚本用 `beautifulsoup4` + `lxml` 解析，需要先 `pip install
beautifulsoup4 lxml`——这是当前唯一一个有第三方依赖的抓取脚本，属于按厂商
页面结构不同做出的合理取舍，不代表以后每个脚本都要引入依赖。详细的页面结构
分析、踩过的坑（分类怎么分组、卡片里怎么分辨"Product"链接和"Pricing"链接、
产品会重复挂多个分类等）记录在 `references/azure.md`，改动这个脚本前先看一眼。

## 已有能力：抓取 GCP 产品目录

在**仓库根目录**下执行：

```bash
python .claude/skills/cloud-product-catalog/scripts/fetch_gcp_products.py
```

会请求 `https://docs.cloud.google.com/` 首页内嵌的 `<devsite-catalog>`
产品目录组件所调用的后端接口（用官方 `docType:Product` 过滤），输出
`products-gcp.json`，213 个产品、14 个分类。

这是 GCP 抓取的第三版实现，前两版都踩过坑后放弃了：第一版抓
`cloud.google.com/products` 营销页的"Browse by category"模块，覆盖不全
（约 90 个，只是精选导览）；第二版改抓 `docs.cloud.google.com` 的 19 个
分类落地页，覆盖到 392 条但混了不少"任务型指南"（不是真产品，且没有
可靠字段能和真产品区分开）。第三版找到了首页内嵌的产品目录组件真正调用的
接口，用 Google 自己的 `docType:Product` 分类做过滤，比自己瞎猜标题特征
可靠得多，产出的数据既干净又比前两版更完整（比如 App Engine、
Identity-Aware Proxy 这些产品在前两版里其实都没抓到）。

只用 Python 标准库（`urllib`、`re`、`json`），不依赖第三方包——虽然这个
接口本身是要靠浏览器抓包才找到的，但找到之后请求本身是一次性的普通 POST，
不需要在脚本运行时启动浏览器。

详细的三版排查过程、接口请求格式怎么抓到的、分类名怎么从
`<select name="keywords">` 下拉框映射出来的，记录在 `references/gcp.md`，
改动这个脚本前先看一眼，避免又走回前两版的老路。

## 已有能力：抓取阿里云产品目录

在**仓库根目录**下执行：

```bash
python .claude/skills/cloud-product-catalog/scripts/fetch_alibabacloud_products.py
```

会请求 `https://www.alibabacloud.com/en/product`（阿里云国际站产品列表页），
解析出全部产品，输出 `products-alibabacloud.json`（165 个产品，13 个分类）。

**实现要点**（改动脚本前务必先理解，否则容易被反爬拦下）：

1. **反爬惩罚页**：这个 URL 直接 `curl` 会被阿里云风控拦下，返回一个只有
   `<punish-component />` 的 SPA 骨架页（约 92KB），看不到任何真实数据。
   必须同时满足两个条件才能拿到正常页面（约 180KB）：
   - 带完整的浏览器请求头（User-Agent、Accept、Accept-Language、
     Accept-Encoding、Referer、Sec-Fetch-* 等），缺关键字段会被识别成爬虫；
   - 跟随 302 重定向到 `?_p_lc=1` 这个带参数的 URL（urllib 默认会跟）。
   拿到正常页面后，`<title>` 应该是 "Alibaba Cloud Products and Cloud
   Computing Services"，如果不是说明被风控了。

2. **数据不在 DOM 里**：正常页面里的产品数据不是渲染后的 DOM，而是整份
   配置以 HTML 转义的 JSON 形式塞在一个
   `<div class="J_tb_lazyload render-container-data" data-data="...">`
   的属性里。需要先正则取出 `data-data` 的值，再做 HTML 实体反转义
   （`&quot;` → `"` 等），最后 `json.loads` 解析。

3. **JSON 结构**：解析出来的是 `{nav, content, ...}`，产品实际在
   `content[].productCard[].cardList[]` 里，一级分类在 `FirstLevelHead`，
   二级分类在 `cardTitle`，两个都收进 `categories` 数组。

4. **URL 两种格式**：`url` 字段混合了相对路径（`product/ecs`）和绝对路径
   （`https://www.alibabacloud.com/product/polardb`），脚本统一补全为绝对路径。

5. **教育培训条目过滤**：原页面混了 25 条 ACA/ACP/ACE 认证培训课程
   （"ACA Big Data Certification"、"Alibaba Cloud Certification Course - ..."
   等），它们链接到 `edu.alibabacloud.com` 教育站点而不是产品页，跨云映射
   用不上。脚本按域名（`https://edu.alibabacloud.com/`）整体过滤——比按
   名称关键词稳定，阿里云新出认证课程时不会被漏掉。过滤后 "Alibaba Cloud
   Academy" 一级分类整体为空，最终剩 13 个真实产品分类。

6. **data-data 之外的产品**：那份配置 JSON 只是"重点推荐产品"的策划清单，
   并不全——像 Model Studio 只出现在页脚的 `<a href=".../product/modelstudio">`
   导航链接里，配置数据中没有。脚本在解析完 data-data 后，会再扫一遍全页
   `<a href=".../product/xxx">` 链接，把配置之外的产品补进来（排除教育站点、
   分类入口页、锚文本=分类名的导航链接）。补充的产品简介从各自产品页的
   `<meta name="description">` 抓取；分类因产品页不暴露归属，默认
   `["Uncategorized"]`，已知明确归属的用脚本顶部的 `CATEGORY_OVERRIDES`
   手动指定（如 Model Studio → Artificial Intelligence）。注意 DashVector
   这类产品虽有独立产品页，但根本没出现在列表页 HTML 里，仍抓不到——
   要覆盖这类长尾产品需另换数据源（sitemap / 帮助文档产品列表），尚未实现。

只用 Python 标准库（`urllib`、`re`、`html`、`json`），不依赖第三方包。

## 统一输出 Schema

所有厂商的产品目录 JSON 都应遵循同一份结构，方便后续做跨云映射时字段对得上：

```json
{
  "source": "抓取来源 URL",
  "module": "对应官方文档站点里的模块/入口名称",
  "fetchedAt": "YYYY-MM-DD",
  "totalProducts": 308,
  "products": [
    {
      "name": "产品名称（官方原文，不翻译）",
      "categories": ["该产品所属的一个或多个分类"],
      "description": "官方一句话简介",
      "link": "产品文档首页链接",
      "id": "该厂商站点内部使用的产品标识，没有则为 null"
    }
  ]
}
```

## 变更日志（diffs）

每次运行抓取脚本或 `build_mapping.py` 时，脚本在重写产物 JSON 的同时，会
把本次变更记录到 `diffs/refresh-diff-YYYY-MM-DD.txt`（按日期聚合，同一天多次
运行追加到同一个文件）。记录内容包括：

- 目标文件路径和时间戳
- 产品级变更摘要：新增/下线的产品名、产品总数变化（仅产品目录 JSON）
- 统一 diff（unified diff）展示具体行级变化

例如运行 AWS 抓取脚本后，日志里会出现类似内容：

```text
============================================================
操作: AWS 产品目录抓取
文件: products-aws.json
时间: 2026-08-03T14:32:10

变更摘要:
  新增产品（2 个）: Amazon Foo, Amazon Bar
  下线/移除产品（1 个）: Amazon OldService
  产品总数: 308 -> 309
  抓取日期: 2026-08-02 -> 2026-08-03

--- products-aws.json
+++ products-aws.json
@@ -1234,7 +1234,7 @@
 ...
```

运行 `build_mapping.py` 时，摘要会变成映射相关的自然语言描述，例如：

```text
============================================================
操作: 跨云产品映射重建
文件: product-mapping.json
时间: 2026-08-03T14:35:00

变更摘要:
  映射分组数: 214 -> 215
  新增分类: Artificial Intelligence
  真正未映射产品数: 351 -> 349
  生成时间: 2026-08-02 -> 2026-08-03

--- product-mapping.json
+++ product-mapping.json
@@ ...
```

`diffs/` 目录由脚本自动创建，无需手动维护。日常更新时可通过该文件
快速确认本次抓取或映射调整到底改了哪些内容。

## 扩展指南：新增一个云厂商

1. 新脚本放在 `scripts/fetch_<vendor>_products.py`（如
   `fetch_azure_products.py`），输出文件放仓库根目录，命名为
   `products-<vendor>.json`，字段严格遵循上面的 schema——不要为了图方便
   加厂商私有字段到顶层，如果确实需要额外信息，放在产品对象里的自定义字段
   即可，不影响下游按 `name`/`categories`/`description` 做映射。
2. 每个厂商官网结构都不一样，先花时间摸清楚数据到底藏在哪：是像 AWS 这样
   藏在隐藏字段里的整页数据、像 Azure 这样直接服务端渲染在 HTML 里、还是
   像 GCP 这样必须真实点击交互才会懒加载出来（甚至可能需要找公开 API）。
   摸清楚之前不要急着写解析逻辑，用 `curl`/无头浏览器分别测一下静态 HTML
   里到底有没有数据，避免走 AWS/Azure 的老路却发现这个厂商根本不吃这一套。
   如果这个厂商的抓取思路比较复杂、值得记录，在 `references/<vendor>.md`
   里写清楚，避免下次改动时重新摸索一遍。
3. 抓完之后跑一下脚本，人工过一眼产出的 JSON（数量是否合理、有没有混入
   非产品条目、描述是否为空），不需要跑完整的评测流程，但基本的正确性要
   自己确认一遍再交付。

## 已有能力：跨云产品映射

在**仓库根目录**下执行：

```bash
python .claude/skills/cloud-product-catalog/scripts/build_mapping.py
```

读取四份 `products-<vendor>.json`（AWS/Azure/GCP/阿里云），输出
`product-mapping.json`：把功能定位相同的产品按分组归到一起（比如"通用
虚拟机"分组下是 EC2/Virtual Machines/Compute Engine/ECS），每组标注
`confidence`（high/medium/low）和 `notes` 说明取舍依据，某一侧没有
清晰对应产品时对应数组留空而不是硬凑。

**这不是一个能自动配对的脚本**：产品名称之间没有任何机械关联键（EC2 /
Virtual Machines / Compute Engine / ECS 四个名字毫无字符串重叠），配对
结果是人工/语义判断后硬编码在脚本顶部的 `GROUPS` 常量里，脚本只负责校验
产品名是否真实存在、自动补全 link/description、以及按分类算出还有哪些
产品没被任何分组覆盖。`unmapped` 字段按分类/厂商拆成 `trulyUnmapped`
（真的没有任何分组处理过，需要关注的是这一份）和 `mappedUnderOtherCategory`
（产品同时挂了多个分类，其实已经被别的分类下的分组引用了，只是不在当前
分类下，不代表没人管）——第一版脚本没做这个区分，全量做完之后大部分
unmapped 其实都属于后者，容易让人误以为漏了很多，所以拆开了。
`trulyUnmapped` 里每一项都包成和 `groups` 同构的对象（`category`/`name`/
`products` 等字段一应俱全，只是 `products` 里只有它自己所在的厂商有内容，
其余厂商是空数组，`category`/`name` 直接用这个产品自己在源数据里的分类
和名字），方便前端不用区分"已配对"和"暂未配对"两种数据形状。

分组层级的 `category`/`name`/`notes` 和每条产品自带的 `description`
都同时提供英文原文和 `-cn` 后缀的中文翻译（比如 `name` / `name-cn`），
方便页面按语种切换显示；产品官方名称和链接不翻译。新增分组或引用新产品时
要同步在 `DESCRIPTION_CN` 里补中文翻译，漏填时脚本会直接报错，不会静默
生成缺中文的记录。

目前已覆盖 AWS 全部 30 个原生分类 + 阿里云 13 个一级分类，共 214 个映射
分组。后续若厂商新增产品/分类，按"扩展指南：跨云产品映射"一节的流程在
`GROUPS` 里追加条目即可，不用改脚本逻辑。

**但"每个产品都要在 product-mapping.json 里有体现"不依赖 GROUPS 覆盖到
哪个分类**：脚本会额外统计四份源数据里出现过的全部分类（`allCategories`），
并通过 `CATEGORY_CANONICAL` 把不同厂商对同一功能的不同命名（AWS "Machine
Learning" vs Azure "AI + machine learning" vs GCP "AI and ML" vs 阿里云
"Artificial Intelligence"）归一为 35 个 canonical 主名。`GROUPS` 还没顾
上的分类里的产品会以单厂商条目的形式出现在 `unmapped.<category>.<vendor>.
trulyUnmapped` 里，不会因为还没写分组就从文件里消失。这批兜底条目不强制
要求中文翻译（`GROUPS` 里精心配对的产品翻译要求不变）。跑过验证：四份
`products-*.json` 里合计 890 个产品（AWS 308 + Azure 204 + GCP 213 +
阿里云 165），全部能在 `product-mapping.json` 里查到，0 缺失。

仓库根目录下的 `cloud-compare-en-new.md` 是一份人工维护、覆盖更全（还有
OCI/阿里云/IBM Cloud）的多云产品对照表，新增分组前先去那份文档里查一下
对应的 Service Type 行，比自己从零判断功能定位靠谱得多——推进过程中用它
校准出好几处修正（比如发现最初把 AWS Outposts 和 VMware 类产品错误地
归了一组，实际上应该对应 Azure Stack/GCP Distributed Cloud 这条产品线）。
但文档给的候选产品名不能直接照抄，要先在 `products-*.json` 里确认真实
存在（厂商改过名、文档年代较早引用了已下线产品的情况都遇到过）。分类边界
不对齐（比如 AWS 有独立的 Serverless 分类，Azure/GCP 没有，只能从它们别的
分类里跨着引用）、颗粒度不对等（AWS 一个 RDS 对应 Azure/GCP 好几个按引擎
拆分的产品）等踩过的坑，连同参考文档校准的具体案例，都记在
`references/mapping.md`，新增分组前先看一眼。

## 日常更新流程：增量，不要全量覆盖

后续任何云厂商的产品有更新（新增产品、改名、下线），按以下顺序做，
**始终在当前版本的基础上做局部变更，不要推倒重来**：

1. **跑抓取脚本**更新源数据：
   ```bash
   python .claude/skills/cloud-product-catalog/scripts/fetch_<vendor>_products.py
   ```
   这会全量重新生成 `products-<vendor>.json`——源数据的更新是正常的，
   因为它就是镜像官网现状。

2. **对照新旧 `products-<vendor>.json` 找差异**：用 git diff 或简单脚本
   列出新增的产品、消失的产品、改名/描述变化的产品。

3. **在 `build_mapping.py` 里做增量修改**，**不要全量重写**：
   - **新增的产品**：判断能否加入某个现有 GROUP，能则在 GROUPS 的对应
    `products.<vendor>` 列表里追加名字，不能则不动（脚本会自动把它
    收进 `unmapped.<category>.<vendor>.trulyUnmapped`）。**无论进 GROUP
    还是落入 trulyUnmapped，新增产品都应在 `DESCRIPTION_CN.<vendor>`
    里补中文描述**；trulyUnmapped 虽不强制校验中文，但缺中文时页面在中文
    模式下会 fallback 到英文名称和描述，体验差。
   - **消失/改名的产品**：在 GROUPS 里把对应的引用删掉或改成新名——
     `resolve()` 会因为找不到而报错，这是**故意的校验**，强迫你处理
     而不是留一个死引用。
   - **新出现的分类**：如果新分类没被 `CATEGORY_CANONICAL` 覆盖到，
     会污染 `allCategories`，需要补一条归一规则。
   - **永远以当前 GROUPS 为基础做局部追加/修改**，不要因为一次更新
     就把现有 214 个 GROUP 全部推翻重配——既浪费已积累的人工判断，
     也会让 git diff 完全不可读。

4. **重新生成 + 校验**：
   ```bash
   python .claude/skills/cloud-product-catalog/scripts/build_mapping.py
   ```
   跑完先判断 `product-mapping.json` 是否真的变了，再决定要不要重建页面：
   ```bash
   git diff --quiet product-mapping.json && echo "映射无变化，跳过页面重建" || echo "映射已变化，需要重建页面"
   ```
   - **映射无变化**（`git diff --quiet` 退出码 0，即抓到的产品没有引起任何
     分组/unmapped 变动）：`index.html` 的数据来自 `product-mapping.json`，
     映射没变页面内容就不会变，**跳过后续 `node build-index.js`**，直接跑
     校验即可，避免产生一个除了 `generatedAt` 日期外毫无意义的页面改动。
   - **映射已变化**（退出码 1）：才继续重建页面。
   ```bash
   node build-index.js        # 仅映射变化时才需要
   node --test lib/*.test.js
   python .claude/skills/cloud-product-catalog/scripts/check_completeness.py
   ```
   校验全绿才算完成。check_completeness 会兜底确认源数据、mapping、页面三层
   一致——即使跳过了 build-index，它也能确认现有 index.html 与 mapping 仍然
   同步，所以跳过是安全的。

**反面教材**：不要因为某个厂商新增了 5 个产品就重新设计 GROUPS 结构、
重排分类、或批量改写 notes——这些"大扫除"式修改会让 incremental 的
价值判断被稀释，也让 review 变得不可能。一次更新只改必须改的那部分。

## 扩展指南：跨云产品映射

新增/调整映射分组时：

1. 先去 `cloud-compare-en-new.md` 里查对应的 Service Type 行，把
   候选产品名列出来，再去对应的 `products-*.json` 里核对是否真实存在
   （厂商改过名、文档引用了已下线产品的情况都遇到过，不能直接照抄）；
   文档没覆盖到的部分，再自己对照读描述判断功能定位。参考
   `references/mapping.md` 里"参考 cloud-compare-en-new.md 校准映射关系"
   和"推进过程中踩到的典型问题"两节。
2. 把新分组加进 `build_mapping.py` 的 `GROUPS` 常量，`name`/`name-cn` 可以
   先照抄文档对应行的 Service Type 当草稿，但如果这个分组的实际配对内容
   比文档写的更精确，就用更准确的说法（自己新拆的分组就在 notes 里注明
   "自拟"）；每引用一个新产品，都要去 `DESCRIPTION_CN` 里给对应厂商补一条
   中文描述翻译，重新跑脚本——脚本会自动校验产品名和翻译是否齐全、自动
   补全字段、自动重算 `unmapped`，不要手改生成出来的 `product-mapping.json`。
3. 分组粒度原则：跟着文档的 Service Type 拆分粒度走，一个分组对应"同一种
   功能定位"，允许一对多、允许某一侧留空，但不要为了三家凑齐硬拉功能明显
   不同的产品进同一组。

### 定期回查 unmapped 是否漏配

接入新厂商或厂商改了产品名（比如 GCP 把 Cloud Dataproc 改名为 Managed
Service for Apache Spark）后，unmapped 里可能躺着"其实能配"的产品。
用 `cloud-compare-en-new.md` 当权威对照回查一遍 unmapped 是个低成本
高收益的动作：

1. 从 `product-mapping.json` 的 `unmapped.<category>.<vendor>.trulyUnmapped`
   列出所有未配对产品名。
2. 逐个在 `cloud-compare-en-new.md` 里搜产品名，看文档里有没有对应行
   （注意文档可能用了改名前的旧名，搜不到时试一下产品的旧名/别名）。
3. 命中的就加到对应 GROUP（必要时新建 GROUP）；没命中的保持 unmapped——
   通常是该厂商特有产品，比如中国合规类（ICP 备案）、细分行业类
   （GameShield）、该厂商独有生态（SOFAStack）。

历史上通过这个方法找回的配对：GCP Managed Service for Apache Spark
（Dataproc 改名后回来源数据就能配上）、Alibaba Log Service / Smart
Access Gateway / Domains / WHOIS（文档明确列出但 mapping 初版漏配）。

## 已有能力：生成查询页面 index.html

`product-mapping.json` 更新之后（不管是新增/修改 `GROUPS`、扩展分类覆盖，
还是重新跑了抓取脚本），在**仓库根目录**下补跑一次：

```bash
node build-index.js
```

会从 `product-mapping.json` 重新拍平数据（`groups` 加上
`unmapped.<category>.<vendor>.trulyUnmapped`，合并成统一的 `rows` 列表）
并内嵌进 `index.html`——一个零依赖的静态单文件页面，可直接双击用浏览器
打开，按分类/厂商/关键词查询跨云产品映射，支持中英文切换和浅色/深色主题。

几个容易踩的点：

1. `index.html` 是生成产物，**不要手改**，改动一律通过
   `index.template.html`（页面结构/样式/交互逻辑）配合重新跑
   `build-index.js` 完成，否则下次生成会把手改的内容覆盖掉。
2. 只改了 `product-mapping.json`、没重新跑 `build-index.js`，或者跑完
   `build-index.js` 但浏览器里还是打开着旧的页面标签页，都看不到最新数据——
   `index.html` 里的数据是构建时内嵌的静态内容，不会在浏览器里自动感知
   `product-mapping.json` 的变化，跑完脚本还要刷新/重新打开页面。
3. 纯逻辑部分（数据拍平、筛选/排序/分组）分别在 `lib/transform.js` 和
   `lib/query.js`，配有 `node --test lib/*.test.js` 的单元测试；改动这两个
   文件后先跑一下测试再重新生成页面。
4. 页面顶栏右上角有一个回网站首页（https://www.cloudproduct.top/）的链接
   （`.home-link`，文案走 `UI_STRINGS` 的 `homeText`/`homeLabel` 双语）。
   顶栏新增控件时保持与语言切换一致的 28px 高度和 mono 字体边框风格；新增
   界面文案一律进 `UI_STRINGS` 双语，并在 `applyStaticText()` 里应用。
5. **浏览器标签页 `<title>` 也要双语**：`<head>` 里的 `<title>` 只是首屏
   默认文案（英文），语言切换时靠 `UI_STRINGS` 里的 `docTitle` 字段（
   `en` / `cn` 各一份），在 `applyStaticText()` 里通过
   `document.title = t.docTitle` 同步更新。改 `<title>` 文案时必须同步改
   `UI_STRINGS.en.docTitle` 和 `UI_STRINGS.cn.docTitle`，否则切换语言后
   标签页标题会停留在旧文案。曾踩过的坑：早期版本只给页面内
   `<h1 id="page-title">` 做了双语，漏了 `<title>`，导致切换中文后浏览器
   标签页仍显示英文。

## 扩展指南：接入第 N 个新厂商到映射和页面

当 `products-<newvendor>.json` 已经能稳定生成，下一步把它接入
`product-mapping.json` 和 `index.html`，让整个体系从"三朵云对照"扩成
"四朵云对照"。这一节以阿里云接入为例，记录除"改 build_mapping.py"之外
还需要做的所有配套改动——只做 mapping 不改前端，结果就是数据进去了
但页面看不到。

### 一、build_mapping.py 需要的改动

1. `SOURCE_FILES` 加 `"<newvendor>": "products-<newvendor>.json"`。
2. `CATEGORY_CANONICAL` 把新厂商的所有分类归一到 canonical 主名：
   - **一级分类**：与 canonical 主名同义时归一（如 "Elastic Computing" →
     "Compute"），同形时不用重复列。
   - **二级分类（重要，阿里云踩过的坑）**：如果源 JSON 的 `categories`
     数组同时含一级和二级（如 `["Elastic Computing", "Cloud Server"]`），
     二级分类会作为独立分类混入 `allCategories`，把 canonical 主名清单
     从 35 个污染到 80 个。必须把每个二级分类也归一到对应一级主名
     （相当于在前端分类维度上丢弃二级信息）。GROUP 配对时已经按产品
     精确判断，不依赖分类，所以丢二级是安全的。
3. `DESCRIPTION_CN.<newvendor>` 给每个被 GROUPS 引用的产品加中文描述，
   缺一条 `resolve()` 就会报错（unmapped 兜底条目允许不翻，但前端中文
   模式会 fallback 到英文，体验差；建议补全）。
4. `GROUPS` 里给已有分组加 `"<newvendor>": [...]`。阿里云接入时 100 个
   GROUP 加了 `alibaba` 引用，128 个产品配上了对；剩下 36 个留在
   unmapped（多为该厂商特有，比如中国 ICP 备案、CloudESL 电子价签）。

### 二、check_completeness.py 需要的改动

`SOURCE_FILES` 同步加新厂商，否则校验脚本会以为新厂商的产品"不在
任何源数据里"而报错。

### 三、lib/transform.js 需要的改动

`VENDORS` 数组从 `['aws', 'azure', 'gcp']` 扩到 `['aws', 'azure', 'gcp',
'<newvendor>']`。`buildRows` 拍平数据时按这个数组遍历，少了它新厂商的
产品就不会出现在 rows 里——表现为 check_completeness 报"missing in
index.html"几百条。

### 四、lib/query.js 需要的改动

搜索 haystack 里的 vendor 数组同步扩，否则新厂商的产品在搜索框里搜不到。

### 五、index.template.html 需要的改动（最容易漏的一块）

UI 上要把"三列"改成"四列"，每一处都得改：

1. `<colgroup>` 加一列，重新分配宽度（阿里云接入时从
   `28%+24%×3` 改成 `22%+19.5%×4`），否则 `table-layout: fixed` 失效，
   最后一列溢出。
2. `<thead>` 加新的 `<th class="th-vendor th-vendor--<newvendor>">` 列，
   带上 SVG 图标。
3. 厂商筛选 chip 加 `<button class="vendor-chip vendor-chip--<newvendor>"
   data-vendor="<newvendor>">`。
4. CSS 加颜色变量 `--accent-<newvendor>`（浅色/深色两套），以及对应的
   `.vendor-chip--<newvendor>.is-active`、`.th-vendor--<newvendor>`、
   `.product--<newvendor>` 三个使用点。
5. `renderRow` 加一个 `renderProductCell(row.products.<newvendor>,
   '<newvendor>')`。
6. `colspan="4"` 改成 `colspan="5"`（共两处：空态提示、分类行）。
7. 小屏媒体查询的 `min-width` 要相应调大（阿里云接入时从 900px 调到
   1100px），否则在 860-1100px 宽度区间内会被挤压。
8. 标题类文案同步加上新厂商名，共五处：`<title>`（首屏默认文案）、
   `UI_STRINGS.en.docTitle`、`UI_STRINGS.cn.docTitle`（语言切换时
   `applyStaticText()` 用 `document.title = t.docTitle` 更新标签页标题）、
   `page-subtitle`、`UI_STRINGS.en.subtitle` 和 `UI_STRINGS.cn.subtitle`。

### 六、跑通完整流程

```bash
python .claude/skills/cloud-product-catalog/scripts/build_mapping.py
node build-index.js
node --test lib/*.test.js
python .claude/skills/cloud-product-catalog/scripts/check_completeness.py
```

四步全绿才算接入完成。任何一步失败都说明前面有改动漏了。

## 已有能力：完整性校验

在**仓库根目录**下执行：

```bash
python .claude/skills/cloud-product-catalog/scripts/check_completeness.py
```

一次性校验三层数据是否一致：四份 `products-*.json`（源）→
`product-mapping.json`（映射）→ `index.html`（页面）。每次跑完抓取脚本、
`build_mapping.py` 或 `build-index.js` 之后都应该跑一次，作为交付前的最后
一道关。

会查的四类问题：

1. 源 JSON 里的产品没进 `product-mapping.json`（漏映射）——通常是
   `build_mapping.py` 的 unmapped 统计逻辑有 bug，或新增分类没被
   `allCategories` 覆盖到。
2. 源 JSON 里的产品没进 `index.html`（漏渲染）——通常是改了 mapping
   但忘了重新跑 `node build-index.js`。
3. `product-mapping.json` 引用了源 JSON 里不存在的产品（脏引用）——
   通常是手动改过生成产物，或厂商改了产品名后 `GROUPS` 没同步更新。
4. `index.html` 内嵌的 rows 数和 `product-mapping.json` 期望的行数
   不一致——同样提示 mapping 和页面不同步。

比对方式是产品名归一化（小写 + 非字母数字替换为空格）后做集合运算，能容忍
标点/空白差异，但改名、缺失、多余引用都会查出来。退出码 0 = 全部一致、
1 = 有问题，适合接入 CI 或作为提交前的校验步骤。
