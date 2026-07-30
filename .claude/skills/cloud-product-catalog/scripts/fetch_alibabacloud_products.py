#!/usr/bin/env python3
"""抓取阿里云国际站产品列表页（https://www.alibabacloud.com/en/product），
输出 products-alibabacloud.json，字段结构与 products-aws.json / products-azure.json /
products-gcp.json 保持一致，供跨云产品映射使用。

属于 cloud-product-catalog skill 的阿里云抓取脚本（第一版实现）。

页面结构要点（改动前先理解）：

1. 这个 URL 直接 curl 会被阿里云的反爬系统拦下，返回一个只有
   <punish-component /> 的 SPA 骨架页面（约 92KB），看不到任何真实数据。
   必须做两件事才能拿到正常页面（约 180KB）：
   - 带完整的浏览器请求头（User-Agent、Accept、Accept-Language、
     Accept-Encoding、Referer 等），缺一个都可能被识别成爬虫；
   - 跟随 302 重定向到 `? _p_lc=1` 这个带参数的 URL（curl 用 -L，
     Python 的 urllib 默认就会跟）。
   拿到正常页面后，`<title>` 应该是 "Alibaba Cloud Products and Cloud
   Computing Services"，如果还是 punish 页面说明被风控了，需要换 IP 或
   降低请求频率。

2. 正常页面里的产品数据**不是渲染后的 DOM**，而是整份配置以 HTML 转义
   的 JSON 形式塞在一个 `<div class="J_tb_lazyload render-container-data"
   data-data="...">` 的属性里。需要先正则取出 `data-data` 的值，再做
   HTML 实体反转义（`&quot;` → `"` 等），最后才能 `json.loads` 解析。
   这个 div 在页面里只出现一次，作为数据锚点很稳定。

3. 解析出来的 JSON 结构是：
   ```
   {
     "nav":     [{"firstLevelNav": "分类名", "firstLevelNavID": "..."}, ...],
     "content": [{"FirstLevelHead": "分类名",
                   "productCard": [{"cardTitle": "子分类名",
                                     "cardList": [{"title": "产品名",
                                                    "desc": "一句话简介",
                                                    "url":  "product/xxx"}, ...]},
                                    ...]}, ...]
   }
   ```
   `nav` 和 `content` 都是 14 个一级分类，但产品实际在 `content` 里。
   `productCard.cardTitle` 是二级分类（比如 "Cloud Server"、"Storage"），
   同一一级分类下可能有多个二级分类。

4. `url` 字段有两种格式：相对路径（`product/ecs`）和绝对路径
   （`https://www.alibabacloud.com/product/polardb`）。脚本统一补全为绝对
   路径，避免下游处理时再判断一次。

5. 同一产品经常挂在多个分类下（比如 Container Service for Kubernetes
   同时属于 "Container & Middleware / Kubernetes" 和
   "Elastic Computing / Container"），脚本按产品名合并，`categories` 存成
   数组——和 AWS/Azure/GCP 脚本的处理方式一致，避免映射时把同一产品当
   成多条记录。

6. "Alibaba Cloud Academy" 一级分类下混了大量认证培训条目（ACA/ACP/ACE
   Certification、Alibaba Cloud Certification Course 等），它们链接到
   `edu.alibabacloud.com` 教育站点而不是产品页，跨云映射用不上。脚本按
   域名（`https://edu.alibabacloud.com/`）整体过滤，比按名称关键词稳定——
   阿里云后续新出认证课程时不会被漏掉。

只用 Python 标准库（`urllib`、`re`、`html`、`json`），不依赖第三方包。

用法：
    python .claude/skills/cloud-product-catalog/scripts/fetch_alibabacloud_products.py
    python .claude/skills/cloud-product-catalog/scripts/fetch_alibabacloud_products.py --output products-alibabacloud.json
"""

import argparse
import datetime
import html as htmllib
import json
import re
import urllib.request

PAGE_URL = "https://www.alibabacloud.com/en/product"
BASE_URL = "https://www.alibabacloud.com/"
MODULE_TITLE = "Alibaba Cloud product catalog"
DEFAULT_OUTPUT_FILE = "products-alibabacloud.json"

# 完整模拟 Chrome 126 在 Windows 上的请求头，缺一些字段（特别是
# Accept-Language、Referer）会触发阿里云的风控 punish 页面
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.alibabacloud.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1",
}

# 全页 <a href="...product/xxx">锚文本</a> 的扫描（补充 data-data 之外的产品入口）。
# 限定必须含 /product/ 路径段，避免把首页 /en/product 这类导航链接也捞进来；
# 锚文本限制在 2–60 字符、且不含 HTML 标签，保证拿到的是可读的产品名而不是图标。
PRODUCT_LINK_RE = re.compile(
    r'<a\s+[^>]*href="((?:https?://www\.alibabacloud\.com)?/?(?:en/)?product/[a-z0-9\-]+)"'
    r"[^>]*>([^<]{2,60})</a>",
    re.IGNORECASE,
)

# 补充产品的分类手动覆盖表。
# 页脚链接补进来的产品不在 data-data 配置里，阿里云产品页本身又不标注分类
# （没有 breadcrumb / JSON-LD），所以无法自动获取归属。这里对已知明确归属的
# 产品手动指定，key 是产品名，value 是 categories 数组（与 data-data 里
# [一级分类, 二级分类] 的格式保持一致）。未覆盖到的产品默认 "Uncategorized"，
# 交给下游 mapping 阶段人工对应，不靠脆弱的关键词猜测。
CATEGORY_OVERRIDES = {
    "Model Studio": ["Artificial Intelligence"],
}


def fetch_url(url: str) -> str:
    """下载指定 URL 的 HTML，处理 gzip / Brotli 压缩。

    urllib 的默认 redirect handler 会自动跟随 302，不需要手动处理
    ?_p_lc=1 这一步。但如果目标站点改了风控策略需要手动加 cookie
    时，可以在这里加一个 opener 装上 HTTPCookieProcessor。
    """
    req = urllib.request.Request(url, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        # resp.read() 可能是 gzip 压缩的，urllib 不会自动解压，需要看
        # Content-Encoding 头手动处理
        raw = resp.read()
        encoding = resp.headers.get("Content-Encoding", "").lower()
        if encoding == "gzip":
            import gzip
            raw = gzip.decompress(raw)
        elif encoding == "br":
            try:
                import brotli
                raw = brotli.decompress(raw)
            except ImportError:
                raise RuntimeError(
                    "服务器返回了 Brotli 压缩的响应但本地未安装 brotli 包，"
                    "请 pip install brotli 或在请求头里去掉 Accept-Encoding 中的 br"
                )
        return raw.decode("utf-8")


def fetch_page_html() -> str:
    """下载产品列表页 HTML。"""
    return fetch_url(PAGE_URL)


def fetch_product_description(url: str) -> str:
    """从产品页的 <meta name="description"> 抓一句简介。

    补充进来的产品（如 Model Studio）在 data-data 配置里没有 desc 字段，
    这里从它们各自的产品页 meta description 补一句，保持和其他产品字段一致。
    抓不到（网络错误、无 meta）时返回空串，不让单个产品的失败拖垮整个抓取。
    """
    try:
        html = fetch_url(url)
    except Exception:
        return ""
    m = re.search(
        r'<meta\s+name="description"\s+content="([^"]+)"', html, re.IGNORECASE
    ) or re.search(
        r'<meta\s+content="([^"]+)"\s+name="description"', html, re.IGNORECASE
    )
    if not m:
        return ""
    return " ".join(m.group(1).split())


def extract_data_payload(page_html: str) -> dict:
    """从页面 HTML 里提取 data-data 属性中的 JSON 配置。

    数据以 HTML 转义的形式塞在 <div class="J_tb_lazyload render-container-data"
    data-data="..."> 里，需要先正则取出再反转义。找不到这个 div 说明阿里云
    改版了，需要重新找数据锚点。
    """
    m = re.search(
        r'<div class="J_tb_lazyload render-container-data" data-data="', page_html
    )
    if not m:
        raise RuntimeError(
            "未找到 <div class=\"J_tb_lazyload render-container-data\"> 数据容器，"
            "页面结构可能已变化（也可能是被风控返回了 punish 页面）"
        )

    # data-data 属性值里所有引号都被转义成 &quot;，所以第一个非转义的
    # 双引号就是属性结束位置
    start = m.end()
    end = page_html.find('"', start)
    if end < 0:
        raise RuntimeError("data-data 属性未闭合，页面结构可能已变化")

    raw = page_html[start:end]
    unescaped = htmllib.unescape(raw)
    return json.loads(unescaped)


def normalize_url(url: str) -> str:
    """把 url 字段统一成绝对路径。"""
    if not url:
        return url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    # 相对路径都以 product/ 开头，补全域名
    return BASE_URL + url.lstrip("/")


def derive_id(url: str) -> str:
    """从 URL 路径最后一段推导产品 ID（仅辅助匹配用，阿里云没有官方内部 ID）。"""
    if not url:
        return None
    path = re.sub(r"[?#].*$", "", url)
    segments = [s for s in path.split("/") if s]
    return segments[-1] if segments else None


def parse_products(payload: dict):
    """从配置 JSON 里提取产品列表，按产品名合并多分类条目。

    返回 (产品列表, 跳过的教育条目数, 分类入口链接集合)。第三个返回值是
    FirstLevelHeadLink（一级分类入口页，如 product/databases、product/security），
    它们也指向 /product/ 路径但不是具体产品，后续扫描全页 <a> 链接时要据此排除。
    """
    merged = {}
    skipped_edu = 0
    category_entry_links = set()
    for group in payload.get("content", []):
        first_level = group.get("FirstLevelHead", "")
        if group.get("FirstLevelHeadLink"):
            category_entry_links.add(normalize_url(group["FirstLevelHeadLink"]))
        for card in group.get("productCard", []):
            second_level = card.get("cardTitle", "")
            for item in card.get("cardList", []):
                name = (item.get("title") or "").strip()
                if not name:
                    continue

                link = normalize_url(item.get("url", ""))

                # 过滤教育/培训类条目：链接指向 edu.alibabacloud.com 的全部跳过。
                # 这些条目混在 "Alibaba Cloud Academy" 一级分类下，是 ACA/ACP/ACE
                # 认证培训（"ACA Big Data Certification"、"Alibaba Cloud Certification
                # Course - ..." 等），不是云产品本身——它们链接到的是教育站点而不是
                # 产品页，跨云映射时用不上。按域名过滤比按名称关键词稳定，避免
                # 阿里云新出认证课程时漏过滤。
                if link.startswith("https://edu.alibabacloud.com/"):
                    skipped_edu += 1
                    continue

                description = " ".join((item.get("desc") or "").split())

                # 一级和二级分类都收进 categories，去重保持顺序
                categories = []
                for cat in (first_level, second_level):
                    cat = cat.strip()
                    if cat and cat not in categories:
                        categories.append(cat)

                if name not in merged:
                    merged[name] = {
                        "name": name,
                        "categories": categories,
                        "description": description,
                        "link": link,
                        "id": derive_id(link),
                    }
                    continue

                # 已存在则合并分类，保留首个非空描述和链接
                entry = merged[name]
                for cat in categories:
                    if cat not in entry["categories"]:
                        entry["categories"].append(cat)
                if not entry["description"] and description:
                    entry["description"] = description
                if not entry["link"] and link:
                    entry["link"] = link
                    entry["id"] = derive_id(link)

    return (
        sorted(merged.values(), key=lambda x: x["name"].lower()),
        skipped_edu,
        category_entry_links,
    )


def parse_extra_products(page_html: str, payload: dict, merged_products):
    """扫描全页 <a href=".../product/xxx"> 链接，把 data-data 配置之外的产品补进来。

    data-data 那份 JSON 只是"重点推荐产品"的策划配置，并不全——像 Model Studio
    这类产品只出现在页脚的导航链接里（<a href=".../product/modelstudio">），
    配置数据里没有。这里把整页 HTML 里所有指向 /product/ 路径的 <a> 链接捞出来，
    和已抓到的产品按 URL 去重后补上。

    补充进来的条目默认归到 "Uncategorized"（产品页不暴露分类，无法自动获取），
    已知明确归属的通过 CATEGORY_OVERRIDES 手动指定（如 Model Studio →
    Artificial Intelligence），简介从产品页 meta description 抓取。

    排除三类非产品链接：
    - 教育站点（edu.alibabacloud.com），和主流程口径一致；
    - 分类入口页（FirstLevelHeadLink，如 product/databases、product/security），
      它们也指向 /product/ 路径但是分类汇总页，不是具体产品；
    - 锚文本和分类名相同的链接（如文本为 "Database"/"Security" 的入口），
      进一步过滤掉导航性质、并非产品名的锚点。
    """
    known_urls = {p["link"] for p in merged_products if p.get("link")}
    known_names = {p["name"] for p in merged_products}

    # 分类入口页 + 分类名清单，用于排除导航类链接
    _, _, category_entry_links = parse_products(payload)
    category_names = set()
    for group in payload.get("content", []):
        if group.get("FirstLevelHead"):
            category_names.add(group["FirstLevelHead"].strip().lower())
        for card in group.get("productCard", []):
            if card.get("cardTitle"):
                category_names.add(card["cardTitle"].strip().lower())

    extra = []
    seen_extra_urls = set()
    for url, text in PRODUCT_LINK_RE.findall(page_html):
        link = normalize_url(url)
        # 去掉 /en/ 前缀，和 data-data 里的 url 归一到同一格式再比较
        link = link.replace("alibabacloud.com/en/product/", "alibabacloud.com/product/")
        name = text.strip()
        if not name:
            continue
        if link in known_urls or link in seen_extra_urls:
            continue
        if link.startswith("https://edu.alibabacloud.com/"):
            continue
        if link in category_entry_links:
            continue
        if name.lower() in category_names:
            continue

        seen_extra_urls.add(link)
        extra.append(
            {
                "name": name,
                # 已知明确归属的用手动覆盖表，否则默认 Uncategorized
                "categories": CATEGORY_OVERRIDES.get(name, ["Uncategorized"]),
                # 页脚链接没有简介，从产品页 meta description 补一句
                "description": fetch_product_description(link),
                "link": link,
                "id": derive_id(link),
            }
        )

    # 按名称合并进总表（页脚链接可能与已抓产品同名但 URL 略不同，避免重复）
    for item in extra:
        if item["name"] in known_names:
            continue
        merged_products.append(item)

    merged_products.sort(key=lambda x: x["name"].lower())
    return merged_products, len(extra)


def scrape():
    page_html = fetch_page_html()
    payload = extract_data_payload(page_html)
    products, skipped_edu, _ = parse_products(payload)
    products, added_extra = parse_extra_products(page_html, payload, products)
    return products, skipped_edu, added_extra


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"输出文件路径（默认 {DEFAULT_OUTPUT_FILE}）",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    products, skipped_edu, added_extra = scrape()

    output = {
        "source": PAGE_URL,
        "module": MODULE_TITLE,
        "fetchedAt": datetime.date.today().isoformat(),
        "totalProducts": len(products),
        "products": products,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(
        f"共抓取 {len(products)} 个产品"
        f"（已过滤 {skipped_edu} 条教育培训条目，"
        f"从页脚链接补充 {added_extra} 个 data-data 之外的产品），"
        f"已写入 {args.output}"
    )


if __name__ == "__main__":
    main()
