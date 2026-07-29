# Azure 产品目录抓取笔记

来源页面：`https://azure.microsoft.com/en-us/products`（"Browse all products" 页面）。

## 和 AWS 的区别

AWS 文档首页是客户端渲染的 SPA，整份数据以 URL 编码的 XML 塞进一个隐藏的
`<input>` 属性里，拿到后可以当结构化数据直接解析（见 `fetch_aws_products.py`）。

Azure 这个产品页是服务端渲染的营销站（Adobe AEM 搭的），产品信息就直接躺在
可见的 HTML 里，不用找隐藏数据源，但 HTML 本身不是规范 XML（标签、属性都是
真实网页那一套），所以改用 `BeautifulSoup + lxml` 解析，而不是
`xml.etree.ElementTree`。

## 页面结构

页面由一堆 AEM 组件堆出来，每个产品分类对应**连续的若干个**
`<div class="grid-image-<slug> ...">`（`<slug>` 是分类的 URL slug，比如
`ai-machine-learning`、`analytics`）。抓取时实测的规律是每个分类固定 3 个：

1. 第一个：带 `<h2>` 标题（人类可读的分类名，比如 "AI + machine learning"），
   本身不含产品卡片。
2. 第二个：空的，不含标题也不含卡片（用途不明，可能是给其他布局变体用的）。
3. 第三个：不带标题，包含该分类下全部的 `<div class="card h-100">`，
   每个 `card` 就是一个产品。

**不要依赖"固定 3 个"这个数字去做位置索引**——用了会脆。更稳的做法是按文档顺序
遍历所有 `grid-image-*` 区块，遇到带 `<h2>` 的就更新"当前分类"，遇到带
`card` 的就把里面的产品记到当前分类下。这样即使 Azure 以后改成 2 个或 4 个
区块也不会解析错乱。

## 单个产品卡片的结构

```html
<div class="card h-100" id="content-card-vertical-ocXXXX">
  <div class="card-body pt-3">
    <h3 class="h5"> 产品名称 </h3>
    <div data-oc-token-text> <p>一句话描述</p> </div>
    <div class="link-group">
      <a ... href="https://azure.microsoft.com/en-us/products/xxx"> Product </a>
      <a ... href="https://azure.microsoft.com/en-us/pricing/details/xxx/"> Pricing </a>
    </div>
  </div>
</div>
```

- 产品名：卡片内第一个 `h3`（个别情况可能是 h4/h5，用 `find(["h3","h4","h5"])`
  兜底）。
- 描述：卡片内第一个 `<p>`。
- 产品链接：卡片里可能有 "Product" / "Pricing" / "Documentation" 等好几个
  链接，认准链接文字**精确等于 "Product"** 的那个，不要用第一个 `<a>`
  （第一个经常是 Pricing 或者别的）。
- 有极少数卡片是空的（`card-body` 里什么都没有），那是用来对齐网格布局的
  占位卡片，`h3` 取不到文本时直接跳过，不算产品。

## 已知的数据特点（供合并/映射时参考）

- 一个产品会挂在多个分类下（比如 App Service 同属 Compute / Mobile / Web），
  按产品名合并，`categories` 存数组，处理方式和 AWS 脚本一致。
- 同一产品在不同分类下的描述文案偶尔会不一样（营销站针对不同场景写了不同
  slogan，比如 Azure AI Search 在 "AI + machine learning" 分类下和在
  "Web" 分类下的描述就不同）。脚本策略是保留第一次出现的描述，如果后续
  发现某个产品的描述明显对不上主营场景，属于已知的数据噪音，不是 bug。
- Azure 卡片没有类似 AWS `id="dynamodb"` 那种官方内部标识，`id` 字段是从
  产品链接路径的最后一段推出来的（如 `.../products/virtual-machines/sql-server/`
  → `sql-server`），仅供辅助匹配，不保证跨厂商命名规则一致。
