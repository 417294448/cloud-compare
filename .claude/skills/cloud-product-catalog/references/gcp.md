# GCP 产品目录抓取笔记

当前实现（第三版）直接调用 `https://docs.cloud.google.com/` 首页内嵌的
`<devsite-catalog>` 组件所请求的后端接口，抓到 213 个产品，字段干净、
分类明确。前两版都被放弃了，但排查过程值得记下来，避免以后走回头路。

## 第一版（已放弃）：cloud.google.com/products 的"Browse by category"

最早直接抓营销首页的"Browse by category"模块，发现这个模块的产品卡片
**只有点击分类筛选按钮之后才会懒加载渲染进 DOM**，必须用 Playwright 逐个
点击 11 个分类按钮。抓出来只有约 90 个产品，用户反馈"页面提示 150+，是不是
漏抓了"。

排查后确认没有漏抓：这个模块本身就是**精选导览**，不是全量目录（验证过没有
"查看更多"按钮、没有异步分批加载、没有滚动触发渲染，同一分类反复抓结果稳定）。
问题不在抓取方法，而在这个数据源本来就不完整。

## 第二版（已放弃）：docs.cloud.google.com 的 19 个分类落地页

用户要求换成 `docs.cloud.google.com` 重新抓。发现文档首页顶部导航有个
"分类"下拉菜单，链接到 19 个 `/docs/<slug>` 分类落地页（AI and ML、
Compute、Databases……），每个页面都是服务端渲染的静态 HTML，产品卡片在
`<section class="category-expandable">` 里，结构清晰，抓出来有 392 条。

问题是：这些落地页本质是"文档导览页"，不是纯产品目录，里面混了不少**任务型
指南**（比如 Costs and usage management 分类下的"Administer quotas"
"Export your carbon footprint""Track costs with budgets"），和真正的产品
（Cloud Billing、Carbon Footprint）用一模一样的卡片样式混在一起，没有任何
可靠的字段能区分两者（不像 AWS 的决策指南有统一的 `/decision-guides/`
链接特征）。当时想过用标题动词开头做启发式过滤，但风险是既会误杀真产品，
也会漏掉不以动词开头的指南，不够可靠，所以放弃了这个数据源。

## 第三版（当前实现）：直接调用 devsite-catalog 组件的后端接口

用户提示"确认抓的是不是 `id="main-content"` 里 `class="catalog-results-container"`
模块"，重新去看文档首页，发现首页本身就嵌了一个官方产品目录组件：

```html
<devsite-catalog query="category:GoogleCloudUseCases+docType:Product+docType:LandingPage"
                  maxresults="1000" sortorder="alphabetical" items-per-page="12" ...>
  <select name="keywords" label="Technology areas" multiple>
    <option value="featuredProduct">Featured products</option>
    <option value="GoogleCloudDocsAiAndMl">AI and ML</option>
    ...
  </select>
</devsite-catalog>
```

关键在 `query` 属性：`docType:Product`——这是 Google 自己给内容打的分类
标签，用它过滤就能拿到官方认定的"这是一个产品"的干净列表，不用再自己猜
标题像不像产品。

这个组件渲染结果本身也是懒加载的（不在静态 HTML 里），但这次没有再用
Playwright 硬点按钮，而是用 Playwright **只做了一次性的抓包**，把组件
实际发出的请求原样搬到 `urllib` 里直接发，之后就不再需要浏览器了：

1. 打开首页，监听网络请求，找到组件调用的接口：
   `POST https://docs.cloud.google.com/_d/dynamic_content`
2. 抓到请求体格式（是个位置数组，不是普通 JSON object）：
   ```json
   [null,null,null,"category:GoogleCloudUseCases+docType:Product+docType:LandingPage",null,null,null,null,1001,null,null,null,3,1]
   ```
   第 4 个元素就是标签上的 `query` 属性原文，第 9 个 `1001` 对应
   `maxresults="1000"`。请求头需要带 `Content-Type: text/plain;charset=UTF-8`
   和 `X-Requested-With: XMLHttpRequest`，否则会被当成普通页面请求拒绝。
3. 响应第一行是 `)]}'`——Google 内部接口常用的**防 JSON 劫持前缀**，必须
   先丢掉这一行，剩下的部分才是合法 JSON（嵌套数组，`json.loads` 直接能
   解析，不需要 bs4）。
4. 响应结构是 `[[条目1, 条目2, ...], 1]`，每个条目是个 26 个字段的定长
   数组，位置含义（用得上的几个）：
   - `[0]` 产品名称
   - `[4]` 描述
   - `[6]` 文档链接（带 `?hl=en&authuser=1` 之类的查询参数，抓下来要去掉）
   - `[20]` 标签数组，里面混了 `doctype:*`、`product:*`、`category:*`
     三种前缀的标签，产品所属分类就在 `category:<slug>` 里。

## 分类名怎么来的

`category:<slug>` 里的 `slug` 是内部代号（比如
`category:googleclouddocssecurity`），不是人类可读名称。刚好首页
`<devsite-catalog>` 组件自带的 `<select name="keywords">` 下拉筛选器
就是这些分类的官方名单，`<option value="GoogleCloudDocsSecurity">Security</option>`
——把 value 转小写就能和 `category:` 标签精确匹配上
（`googleclouddocssecurity` ↔ `GoogleCloudDocsSecurity`）。脚本里
`discover_category_labels` 就是从首页动态解析这个下拉框，不要把分类名单
写死。

## 已知的数据特点（供合并/映射时参考）

- 少数产品会有多条记录，对应不同的文档版本号（比如 Cloud Service Mesh 有
  `v1.27`、`v1.28`、不带版本号三个链接）。合并时优先保留不带版本号的规范
  链接，脚本里 `VERSION_SEGMENT_RE` 就是干这个的。
- 这份数据比第二版的 392 条更"准"也更"全"：交叉比对发现只有约 163 个
  产品名两边都有，说明第二版那份数据既混了噪音、也漏了不少真产品（比如
  App Engine、Identity-Aware Proxy 这些在 392 条里根本没出现过）。
- 有些日常认知里的"GCP 功能"（比如 Cloud Quotas、Committed use
  discounts）在这份数据里找不到——不是抓漏了，是 Google 自己的
  `docType:Product` 分类就没把它们算作独立产品（更像是某个核心产品下的
  能力点）。以官方分类为准，不要凭自己的常识往回加。
- 没有官方内部产品 ID，`id` 字段和 Azure 脚本一样从链接路径最后一段
  近似推导，仅供辅助匹配。
