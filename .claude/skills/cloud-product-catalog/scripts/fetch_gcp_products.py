#!/usr/bin/env python3
"""抓取 Google Cloud 官方文档首页（https://docs.cloud.google.com/）内嵌的
<devsite-catalog> 产品目录组件数据，输出 products-gcp.json，字段结构与
products-aws.json / products-azure.json 保持一致，供跨云产品映射使用。

属于 cloud-product-catalog skill 的 GCP 抓取脚本。这是第三版实现：
第一版抓 cloud.google.com/products 营销页的"Browse by category"模块，覆盖
不全（约 90 个）；第二版改抓 docs.cloud.google.com 的 19 个分类落地页，
覆盖到 392 条但混了不少任务指南（不是真产品）。这一版直接调用
<devsite-catalog> 组件本身请求的后端接口，用官方的 docType:Product 过滤，
干净且更完整（213 个）。三版的排查过程和为什么放弃前两版记在
references/gcp.md，改动前先看一眼，避免走回头路。

只用 Python 标准库（urllib、re、json），不依赖第三方包。

用法：
    python .claude/skills/cloud-product-catalog/scripts/fetch_gcp_products.py
    python .claude/skills/cloud-product-catalog/scripts/fetch_gcp_products.py --output products-gcp.json
"""

import argparse
import datetime
import json
import re
import urllib.parse
import urllib.request

HOME_URL = "https://docs.cloud.google.com/"
CATALOG_ENDPOINT = "https://docs.cloud.google.com/_d/dynamic_content"
CATALOG_QUERY = "category:GoogleCloudUseCases+docType:Product+docType:LandingPage"
DEFAULT_OUTPUT_FILE = "products-gcp.json"
MODULE_TITLE = "Google Cloud product catalog"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# 同一产品的文档偶尔会同时存在带版本号和不带版本号的链接
# （如 /service-mesh/docs 和 /service-mesh/v1.27/docs），合并时优先保留
# 不带版本号的规范链接。
VERSION_SEGMENT_RE = re.compile(r"/(v?\d+(?:\.\d+)*|\d{3,})(/|$)")


def clean_text(text) -> str:
    return " ".join((text or "").split())


def fetch_home_html() -> str:
    req = urllib.request.Request(HOME_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def discover_category_labels(home_html: str):
    # 首页的 <devsite-catalog> 组件自带一个 <select name="keywords"> 分类
    # 筛选器，option 的 value 是内部分类 slug（大小写不敏感），文本是人类
    # 可读名称。后面要用它把每个产品 tags 里的 category:<slug> 翻译成可读
    # 分类名，不要把这份映射写死在脚本里——Google 增删分类时它会跟着首页
    # 的下拉框一起变，动态提取才不用维护。
    match = re.search(r'<select name="keywords"[^>]*>(.*?)</select>', home_html, re.S)
    if not match:
        raise RuntimeError('未找到 <select name="keywords"> 分类筛选器，页面结构可能已变化')
    options = re.findall(r'<option value="([^"]+)">([^<]+)</option>', match.group(1))
    if not options:
        raise RuntimeError("分类筛选器里没有解析出任何 option，页面结构可能已变化")
    return {value.lower(): clean_text(label) for value, label in options}


def fetch_catalog_items():
    # 这个请求体格式是从浏览器实际发出的请求里原样抓下来的（<devsite-catalog>
    # 组件内部调用），第 4 个元素就是标签上的 query 属性，第 9 个 1001 对应
    # maxresults="1000"（+1）。响应第一行是 Google 用来防 JSON 劫持的
    # )]}' 前缀，必须先去掉这一行才能当正常 JSON 解析。
    request_body = json.dumps(
        [None, None, None, CATALOG_QUERY, None, None, None, None, 1001, None, None, None, 3, 1]
    )
    req = urllib.request.Request(
        CATALOG_ENDPOINT,
        data=request_body.encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "text/plain;charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": USER_AGENT,
            "Origin": "https://docs.cloud.google.com",
            "Referer": HOME_URL,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")

    _, _, json_text = raw.partition("\n")
    payload = json.loads(json_text)
    return payload[0]


def strip_query(link):
    if not link:
        return None
    parts = urllib.parse.urlsplit(link)
    return urllib.parse.urlunsplit(parts._replace(query="", fragment=""))


def derive_id(link):
    # GCP 目录条目没有像 AWS docs 那样的官方内部产品标识，退而用链接路径
    # 最后一段近似代替，和 Azure 脚本的处理方式一致，仅供辅助匹配。
    if not link:
        return None
    segments = [s for s in urllib.parse.urlparse(link).path.split("/") if s]
    return segments[-1] if segments else None


def parse_items(items, slug_to_label):
    products = []
    for item in items:
        name = clean_text(item[0])
        if not name:
            continue

        link = strip_query(item[6])
        description = clean_text(item[4])

        categories = []
        for tag in item[20] or []:
            if not tag.startswith("category:"):
                continue
            label = slug_to_label.get(tag[len("category:") :])
            if label and label not in categories:
                categories.append(label)

        products.append(
            {
                "name": name,
                "categories": categories,
                "description": description,
                "link": link,
            }
        )
    return products


def merge_by_name(products):
    merged = {}
    for p in products:
        if p["name"] not in merged:
            merged[p["name"]] = {
                "name": p["name"],
                "categories": list(p["categories"]),
                "description": p["description"],
                "link": p["link"],
                "id": derive_id(p["link"]),
            }
            continue

        entry = merged[p["name"]]
        for category in p["categories"]:
            if category not in entry["categories"]:
                entry["categories"].append(category)

        entry_is_versioned = bool(VERSION_SEGMENT_RE.search(entry["link"] or ""))
        candidate_is_versioned = bool(VERSION_SEGMENT_RE.search(p["link"] or ""))
        if entry_is_versioned and not candidate_is_versioned:
            entry["link"] = p["link"]
            entry["id"] = derive_id(p["link"])

    return sorted(merged.values(), key=lambda x: x["name"].lower())


def scrape():
    home_html = fetch_home_html()
    slug_to_label = discover_category_labels(home_html)
    raw_items = fetch_catalog_items()
    return merge_by_name(parse_items(raw_items, slug_to_label))


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

    products = scrape()

    output = {
        "source": HOME_URL,
        "module": MODULE_TITLE,
        "fetchedAt": datetime.date.today().isoformat(),
        "totalProducts": len(products),
        "products": products,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"共抓取 {len(products)} 个产品，已写入 {args.output}")


if __name__ == "__main__":
    main()
