# 跨云产品映射笔记

`scripts/build_mapping.py` 生成 `product-mapping.json`，把 AWS/Azure/GCP
的产品按功能对应关系分组，供 cloud-compare 做产品对照查询用。这份笔记记
下方法论和推进过程中做的取舍，新增分组或调整现有分组时先看一眼，避免重复
踩坑。

**当前状态**：`GROUPS` 已覆盖 AWS 全部 30 个原生分类；三份源数据中出现的
55 个原始 category 名（AWS 30 + Azure 21 + GCP 14，含跨厂商重复）已通过
`CATEGORY_CANONICAL` 映射表归并为 35 个 canonical 主名，最终输出的
`product-mapping.json` 中所有 category 字段统一用主名。三份源数据中的
产品（AWS 308、Azure 204、GCP 213，共 725 条）都能在 `product-mapping.json`
中查到，0 缺失。

## Category 归一化（CATEGORY_CANONICAL）

三份源数据中出现的 category 名称并不统一（AWS 30 个、Azure 21 个、GCP 14
个），同一功能在不同厂商那里可能叫不同的名字（AWS "Machine Learning" vs
Azure "AI + machine learning" vs GCP "AI and ML"），甚至同一家内部也有
大小写/单复数/连字符差异。如果按原始名分别统计，`unmapped` 字段会出现
55 个分类、其中 14+ 组本质上是同一件事——既不便阅读也不便统计。

`build_mapping.py` 顶部的 `CATEGORY_CANONICAL` 字典把这些"原始分类名"
归一到一个"主名"（canonical）。`build()` 在最开始就把每个产品的
`categories` 字段 canonical 化，所有按分类的统计（referenced_by_category、
all_categories、unmapped）都用归一后的名字。GROUPS 里 `"category"` 字段
也走一遍 `canonical_category()`，所以即便误写了 Azure/GCP 风格的原始名
也会被自动归到主名。

**主名选取原则**：
- 优先用 AWS 风格的分类名（AWS 分类体系最完整、命名最准确）。
- 三家完全一致时（Compute/Storage/Containers）保留通用名。
- 跨厂商表述差异较大且没有明显主名时（如 Azure "Hybrid + multicloud"
  vs GCP "Distributed, hybrid, and multicloud"），新造一个统一主名
  （"Hybrid & Multicloud"）。

**新增分组时**：`"category"` 字段直接写 canonical 主名，不要写 Azure/GCP
风格的原始名。如果要引入新的 canonical 映射（比如厂商将来又改分类词表），
在 `CATEGORY_CANONICAL` 里加一条映射，并相应在 `CATEGORY_LABELS_CN` 里
给新主名加中文翻译。

**CATEGORY_LABELS_CN 的 key 是 canonical 主名**，不再是原始名。原始名
通过 `CATEGORY_CANONICAL` 先归一，再从 `CATEGORY_LABELS_CN` 查中文。

## 两条独立的完整性保证：`GROUPS` 覆盖 vs `allCategories` 兜底

`GROUPS` 里精心配对的跨云映射是这份数据真正有价值的部分，但"每个产品都
要在 product-mapping.json 里有体现"这个更基础的要求不依赖 `GROUPS` 覆盖
到哪——所以 `build()` 里单独算了一份 `allCategories`：三份
`products-*.json` 里实际出现过的全部分类名（AWS 自己 30 个、加上
Azure/GCP 各自不同的叫法，比如 AWS 叫 "Database"，Azure/GCP 都叫
"Databases"，彼此不强行统一），`unmapped` 是按这份完整清单统计的。这样
即便将来厂商新增了产品/分类而 `GROUPS` 还没顾上，没被配对的产品也会以
单厂商条目的形式出现在 `unmapped.<category>.<vendor>.trulyUnmapped` 里，
不会从这份文件里"消失"。跑完脚本后可以用下面这段代码验证三份源数据里的
产品是不是都能在 `product-mapping.json` 里查到（0 条缺失才算数）：

```python
covered = {"aws": set(), "azure": set(), "gcp": set()}
for g in mapping["groups"]:
    for vendor, items in g["products"].items():
        covered[vendor].update(it["name"] for it in items)
for cat in mapping["unmapped"].values():
    for vendor, obj in cat.items():
        covered[vendor].update(it["name"] for e in obj["trulyUnmapped"] for it in e["products"][vendor])
        covered[vendor].update(obj["mappedUnderOtherCategory"])
# 对每个 vendor：products-<vendor>.json 里的产品名集合 - covered[vendor] 应该是空集
```

`unmapped` 兜底扫描出来的产品不强制要求中文翻译（`resolve()` 调用时传了
`require_translation=False`，缺翻译时 `description-cn` 就是 `null`，不会
像 `GROUPS` 里那样直接报错）——七百多个产品全部现填中文翻译不现实，
先保证"有没有被收进这份文件"这个更硬的要求，翻译可以后续慢慢补，补上后
脚本会自动读到，不用改代码。`GROUPS` 里的翻译要求不变，因为那才是这份
数据真正有价值的部分（confirmed 的跨云对应关系），必须严格把关。

## 为什么匹配逻辑不能自动化

抽查过三云"Compute"分类下的旗舰产品名称：

```
AWS:   Amazon Elastic Compute Cloud
Azure: Virtual Machines
GCP:   Compute Engine
```

三个名字没有任何字符串重叠，`id` 字段也只是各自站点内部的 slug，互不相通。
这意味着**没有任何机械规则能把同类产品自动配对**，必须靠读描述、理解功能
定位来判断——这也是为什么 `build_mapping.py` 本身不做匹配决策，匹配结果
以 `GROUPS` 常量的形式硬编码在脚本里，脚本只负责校验引用的产品名是否真实
存在、自动补全 link/description、以及算出每个分类下还剩哪些产品没处理。

## 分类边界不对齐，映射天然是"按功能"而不是"按分类名"

AWS 有独立的 **Serverless** 分类，但 Azure/GCP 都没有对应的顶层分类——它们
的无服务器产品分散在 Compute、Application development、Integration 等
其他分类里（比如 GCP 的 Cloud Run/Cloud Run functions/App Engine 其实都在
"Application hosting"分类下，不在"Compute"）。所以 Serverless 分类下的
Azure/GCP 产品是**跨着它们自己的分类体系去引用**的，不是从它们各自的
"Serverless"标签里挑出来的（因为根本不存在这个标签）。

反过来，同一个产品经常横跨多个功能分组：比如 AWS Fargate 在 AWS 自己的
分类里同时属于 Compute 和 Serverless，在映射表里也相应出现在
`compute-paas-app-hosting`（间接，见下方"参考 cloud-compare-en-new.md"一节）
和 `serverless-containers` 分组里，这是预期行为，不是重复录入的错误。

## "unmapped" 按分类统计，且区分"真没覆盖"和"覆盖在别的分类下"

`unmapped` 字段先按分类统计：对每个分类，把这个分类下所有分组引用过的
产品名去掉，剩下的就是这个分类里"看起来没被覆盖"的产品。但这批"看起来
没被覆盖"的产品还会再拆成两组：

- `trulyUnmapped`：真的没有任何分组引用过，需要关注的才是这一份。
- `mappedUnderOtherCategory`：产品同时挂了多个分类（比如 AWS Lambda 同时
  属于 Compute 和 Serverless），只是覆盖它的那个分组挂在别的分类下（比如
  `serverless-functions` 挂在 Serverless 分类），所以在 Compute 分类的
  统计里看起来"没覆盖"，实际上已经在映射表里了。

第一版脚本只有一份不区分这两种情况的 `unmapped` 列表，实测发现这样很
容易让人误判——早期推进时有用户直接问"为什么这么多 unmapped，有些明显
在参考文档里有对应关系"，一查发现列表里一大半（AWS App Runner/Lambda、
Azure Container Apps/Functions、SQL Server on Azure Virtual Machines、
Oracle on Google Cloud Compute 等）其实都已经在别的分类下被覆盖了，只有
个位数是真的漏了（当时正好也顺带发现一个真漏掉的：cloud-compare-en-new.md
的 Auto Scaling 行——AWS EC2 Auto Scaling ↔ Azure Virtual Machine
Scale Sets，那时压根没建这个分组，属于纯粹的疏漏，已经补上了）。之后就
把 `unmapped` 拆成了这两份，看 `trulyUnmapped` 就知道真正还要处理什么，
不用自己再去每个分组里搜一遍。

`trulyUnmapped` 里的每一项不是一个裸产品名，而是包成了和 `groups` 数组
里完全同构的对象（同样有 `category`/`name`/`confidence`/`products`/
`notes` 等字段），只是 `products` 里只有这个产品自己所在的厂商有内容，
其余厂商都是空数组，`confidence` 固定是 `"none"`——这样前端不用为"已经
配好对的行"和"暂时只有一家云、还没配对的行"写两套渲染逻辑，都当成同一种
"行"来遍历展示就行。`category`/`name` 直接取这个产品自己在
`products-*.json` 里的原始分类和名字，不是我们发明的分组名。
`mappedUnderOtherCategory` 不需要这么处理，因为它对应的产品已经完整地
出现在 `groups` 里了，这里只是留个索引提示"看着没覆盖但其实在别处"。

**`trulyUnmapped` 条目的 `name-cn` 故意留空字符串**：这些条目的 `name`
就是产品官方名（如 "Amazon EC2"、"Azure Virtual Machines"），按 SKILL.md
的规则产品官方名称不翻译；空字符串标记"没有人工起过中文显示名"，前端
`transform.js` 会自动 fallback 到英文 `name` 显示，不会出现空白。不要在
这里填一个翻译后的中文名——那会混淆"分组名（可以翻译）"和"产品官方名
（不翻译）"的边界。同样道理，分组层级（`groups[].name-cn`）和分类层级
（`category-cn`）的翻译是必需填的，产品条目层级（`products[].name`）
则始终保留英文原文。

## 推进过程中踩到的典型问题

- **颗粒度不对等**：AWS 用一个 Amazon RDS 覆盖 MySQL/PostgreSQL/SQL Server
  等多种引擎，Azure/GCP 按引擎拆成了好几个独立产品（Azure Database for
  MySQL、Azure Database for PostgreSQL……）。这种情况下一个 AWS 产品要对应
  一组 Azure/GCP 产品，不是 1:1。
- **单边产品**：不是每个功能分组三家都齐——图数据库（Amazon Neptune）、
  时序数据库（Amazon Timestream）目前查到 Azure/GCP 都没有独立对应产品；
  反过来 Azure Spot Virtual Machines 这种定价形态的产品，AWS/GCP 虽然有
  等价能力（EC2 Spot、Spot VM），但没有做成独立产品条目，所以在这份数据
  里也是单边的。遇到单边情况，`confidence` 标成 `low` 并在 `notes` 里
  写清楚原因，不要为了凑齐三家硬拉一个不相关的产品进来。
- **数据源本身的缺口**：GCP Pub/Sub 是消息/事件场景里最直接对应
  SNS/SQS/EventBridge 的产品，但它没有出现在 `products-gcp.json` 里——
  不是抓漏了，是 Google 自己的文档目录接口没有把它标记成
  `docType:Product`（这是 `docs.cloud.google.com` 数据源本身的已知局限，
  见 `references/gcp.md`）。遇到这种情况先去确认是不是数据源缺失，而不是
  想当然地认为该产品不存在。
- **分类边界之外的等价产品**：AWS Database Migration Service 和
  Azure/GCP 的数据库迁移服务是明显的对应关系，但 AWS 把它归到了
  Migration & Transfer 分类，不在早期推进范围内。这种情况不代表就不能
  引用——`db-migration-service` 分组照样把它加了进来（`resolve()` 只校验
  产品名是否存在，不检查它是不是"属于"当前分组标的分类），`notes` 里
  说明这是跨分类引用即可，产品在多个分组里被重复引用也没关系（Google
  Cloud Armor 同时被 sec-firewall-management / sec-network-firewall /
  sec-ddos-protection / sec-waf 引用就是另一个例子）。
- **发现的数据质量问题**：AWS 的 Serverless 分类里有一条产品名就叫
  `"Serverless"`（描述是"Introduction to core serverless concepts and
  services in the AWS Cloud"），明显是分类介绍页而不是真实产品，和之前
  过滤掉的"决策指南"是同一类噪音，只是没有命中现有的过滤规则（不含
  `/decision-guides/`，标题也不以 "Choosing" 开头）。这条目前直接跳过、
  留在 `unmapped` 里，没有强行拉进任何分组。如果以后要清理，可以在
  `fetch_aws_products.py` 里加一条规则：产品名和它自己所属的某个分类名
  完全一致时，大概率是分类介绍页，值得怀疑。

## 参考 cloud-compare-en-new.md 校准映射关系

仓库根目录下的 `cloud-compare-en-new.md` 是一份人工维护的多云产品对照表
（还覆盖了 OCI/阿里云/IBM Cloud），按 Service Type 分行列出各家对应产品，
比我们自己从零猜配对靠谱得多。推进过程中用它校准过几遍，几点经验：

- **不能直接照抄产品名**：文档里的产品名不一定和 `products-*.json` 里的
  实际名字完全一致，常见原因是厂商改过名（比如 GCP "Cloud Functions" 已
  改名 "Cloud Run functions"、Azure "Cache for Redis" 已改名 "Azure
  Managed Redis"），也可能是这份数据源本身省略了品牌前缀（Azure 的
  "Notification Hubs""Logic Apps""Service Bus" 在文档里写的是带 "Azure "
  前缀的全名，但 `products-azure.json` 里存的就是不带前缀的短名）。加进
  `GROUPS` 之前，先用 `python -c "import json; ..."` 之类的一行脚本在对应
  的 `products-*.json` 里搜一下这个名字（精确匹配 + 关键词模糊匹配都试一下）
  再决定用哪个，脚本的校验步骤也会在名字对不上时直接报错、逼着你处理。
- **文档给的候选产品不一定还存在**：查证过程中发现文档里 Azure CycleCloud
  （HPC）、Azure Edge Zones（边缘计算）、Azure Time Series Insights（时序
  数据库）这几个产品都没有出现在 `products-azure.json` 里，模糊搜索也搜不到
  近似名字——Time Series Insights 经查证是微软已经官宣退役的服务，文档这条
  建议已经过时；另外两个没查到确切结论，暂时按"数据源里没有"处理，保持
  对应分组的这一侧留空，不能因为文档写了就硬编一个查不到的名字进去。
- **文档的判断有时比自己瞎猜的分组更精确**：最初把 AWS Outposts 和
  Azure VMware Solution/Nutanix Cloud Clusters、GCP VMware Engine 归了
  一组（都算"专属/私有基础设施"），参考文档的 Hybrid Cloud Service 行才
  发现搞错了方向——Outposts 真正对应的是 Azure Stack、GCP Distributed
  Cloud 这条"把云厂商软硬件栈搬到本地"的产品线，VMware 云托管是完全
  另一条产品线（AWS 那边的对应产品是 Amazon Elastic VMware Service）。
  拿不准某个分组该怎么配对时，先去文档里查一下有没有现成的 Service Type
  行，比自己凭印象瞎配靠谱。
- **文档也会把颗粒度不同的东西合并展示，不代表能照抄进同一个分组**：
  比如文档的 Wide Column Database 行给 Azure 填的是 Cosmos DB（靠
  Cassandra API 提供兼容能力），但 Cosmos DB 是多模型数据库，不是专门的
  宽列/Cassandra 兼容产品；这种情况下优先选数据源里定位更精确的产品
  （Azure Managed Instance for Apache Cassandra），把文档给的那个多模型
  产品记在 `notes` 里当备选说明，而不是直接采用，并相应下调
  `confidence`（比如从 high 降到 medium）。
- **文档按 Service Type 分行，一行经常对应多个更细的产品**：文档把
  "Event Bus""Message & Task Queue""Message Notification Service""Message
  Middleware""Workflow Orchestration"分成了五个独立的行，比我们最初笼统
  的一个"无服务器消息与事件驱动"大分组精细得多，参考这个拆法把原来的
  大分组拆成了 `serverless-event-bus`、`serverless-message-queue`、
  `serverless-pubsub-notification`、`serverless-message-broker`、
  `serverless-workflow-orchestration` 五个分组。拿不准一个功能分组要不要
  拆细的时候，看文档是怎么分行的，通常文档的拆分粒度就是比较合理的参考。
- **`name` 字段拿不准怎么起时可以先照抄文档对应行的 Service Type 当草稿**，
  方便交叉查阅原文档验证；但如果这个分组的实际配对内容比文档写的更精确
  （比如 db-cloud-native-distributed-sql 组，文档写的是笼统的
  "High-Performance Relational Database"，这里用更能体现共性的"云原生
  分布式关系型数据库"），就不用被文档的措辞捆死。自己新拆出来的分组
  （文档没有对应行，比如"专属宿主机""VMware 云托管服务""虚拟机镜像
  管理""加密工具与代码签名""B2B EDI 数据交换"）在 `notes` 里注明了
  "cloud-compare-en-new.md 未单独列出此行，按功能定位自拟"，别误以为是
  从文档抄来的。（最初这几个分组把这条注释塞进了单独的 `serviceType`
  字段里，和 `name` 字段高度重复，后来去掉了 `serviceType`，统一并进
  `name`/`notes`。）

## 新增/调整分组时怎么做

1. 先去 `cloud-compare-en-new.md` 里找对应的 Service Type 行，把候选
   产品名列出来，再逐个去对应的 `products-*.json` 里核对是否真实存在
   （精确匹配 + 关键词模糊搜索都试一下）——很多时候能省掉从零判断功能
   定位的功夫，但候选名字不能直接照抄，参考上面"参考
   cloud-compare-en-new.md 校准映射关系"一节里踩过的坑。
2. 文档里没有覆盖到的产品（比如 AWS 特有的服务、文档年代较早还没收录
   的新产品），才需要自己读描述、理解功能定位来判断怎么分组，参考
   `build_mapping.py` 顶部注释里说的方法。
3. 新增分组直接加进 `GROUPS` 常量，`name`/`name-cn`、`notes`/`notes-cn`
   两个语言版本都要填；每引用一个新产品，都要去 `DESCRIPTION_CN` 里给
   对应厂商补一条中文描述翻译（key 用产品在 `products-*.json` 里的官方
   名称）。重新跑脚本——脚本会自动校验产品名有没有打错、中文翻译有没有
   漏填、自动重算 `unmapped`，不需要手改输出的 `product-mapping.json`。
4. 分组粒度参考前面"推进过程中踩到的典型问题"一节的经验：跟着文档的
   Service Type 拆分粒度走，一个分组对应"同一种功能定位"，允许一对多
   （一个 AWS 产品对应 Azure/GCP 好几个细分产品），允许某一侧留空，但
   不要为了凑数把功能明显不同的产品硬拉到一组里。

## 全量推进阶段额外踩到的坑（30 个 AWS 分类铺满过程中）

下面这些是在把 `GROUPS` 从最初的 Compute/Database/Serverless 三个分类
扩展到全部 30 个 AWS 分类的过程中遇到的、上面各节没覆盖到的场景：

- **AWS 把"文档/参考页面"也当作产品列出来**：General Reference 分类下的
  AWS Glossary、AWS Service Endpoints、Tagging AWS Resources、Service
  Quotas reference 等本质是文档页面，不是云服务。但既然 `products-aws.json`
  把它们当产品列出，按"0 缺失"的硬要求就必须收进 `product-mapping.json`。
  处理方式是合并成一个低置信度的单云分组
  （`genref-aws-docs-and-references`），并在 `notes` 里写明"本质是文档/
  参考页面，不是独立云服务"。类似的还有 AWS Support（在
  `genref-support-plan` 单云分组里）——参考文档给出的 Azure/GCP 对应
  产品（Azure Support、Google Cloud Support）都没作为独立产品列入
  `products-azure.json` / `products-gcp.json`，因为这两家把支持计划文档
  放在产品目录页之外。
- **同品牌下的"平台 + 平台专属 SDK"要拆开**：AWS Amplify 在
  `products-aws.json` 里同时存在 4 条记录——主产品（Web/移动全栈开发
  平台）+ Android/iOS/Unity 三个平台专属 SDK。前三条对应
  cloud-compare-en-new.md 的 Mobile and Web Application Development 行，
  但 SDK 三条没有跨云对应。处理方式：主产品进
  `frontend-mobile-web-dev-platform` 跨云分组，三个 SDK 合并成
  `frontend-amplify-mobile-sdks` 单云分组。
- **同一产品被多组引用是正常且必要的**：Azure Static Web Apps 既在
  `compute-paas-app-hosting`（作为通用 PaaS 托管）又在
  `frontend-mobile-web-dev-platform`（作为 Amplify 的对应）；Azure
  Virtual Desktop 在 EUC 分类下被引用了 3 次（虚拟桌面、应用流式传输、
  Web 安全浏览器）。这是产品定位天然横跨多个品类的结果，不要为了避免
  "重复"硬把它们塞进单一组。
- **"文档声称有但实际不存在"的对应产品**：参考文档给的 Azure PlayFab
  （游戏）、Azure Orbital（卫星地面站）、Azure Blockchain Service
  （区块链）、Google Quantum AI（量子计算）等，在 `products-azure.json` /
  `products-gcp.json` 里都查不到——多数情况是产品已下线/改名/退役，
  按"对应侧留空 + notes 说明文档过时"处理，**不要**硬编一个名字进去。
  特别注意参考文档的区块链一节：文档写的 GCP 列是空白，但实际
  `products-gcp.json` 里有 Blockchain Node Engine 这个第一方托管节点
  产品，应该把它作为 Amazon Managed Blockchain 的 GCP 对应——文档也会
  有过时/不全的情况，参考但不盲从。
- **AWS 拆分/改名产品**：参考文档给的"Amazon GameLift"在
  `products-aws.json` 里实际是两条——Amazon GameLift Servers 和
  Amazon GameLift Streams（功能拆分）；文档给的"Amazon AppStream 2.0"
  实际是 Amazon WorkSpaces Applications（改名）。这两种情况都在
  `notes` 里写明旧名→新名的对应关系，方便日后交叉验证。
- **同分类下"产品组组合并"**：Customer Enablement Services（AWS IQ、
  AWS Professional Services、AWS Managed Services 等）和 Cloud
  Financial Management（AWS Pricing Calculator、Savings Plans、AWS
  Flat-Rate Plans）这两类，每个产品独立建组都会变成 6+3 个低置信度
  单云分组，信噪比很低。处理方式是合并成一条"组合条目"
  （`custenable-aws-services-portfolio` /
  `finmgmt-pricing-and-savings-tools`），同品类下多个 AWS 独有能力
  放一起，Azure/GCP 列留空，避免映射表被这类条目淹没。
