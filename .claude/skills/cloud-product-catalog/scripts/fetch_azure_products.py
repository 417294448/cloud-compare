#!/usr/bin/env python3
"""抓取 Azure 官方产品页（https://azure.microsoft.com/en-us/products）的产品信息，
输出 products-azure.json，字段结构与 products-aws.json 保持一致，供跨云产品映射使用。

属于 cloud-product-catalog skill 的 Azure 抓取脚本，建议在仓库根目录下执行。
页面结构的分析过程见 references/azure.md。

依赖：beautifulsoup4 + lxml（Azure 页面是真实的营销站 HTML，不是像 AWS 那样的
结构化 XML 数据，用标准库手写解析容易因为标签不规范而出错，这里用 bs4 更稳）。
    pip install beautifulsoup4 lxml

用法：
    python .claude/skills/cloud-product-catalog/scripts/fetch_azure_products.py
    python .claude/skills/cloud-product-catalog/scripts/fetch_azure_products.py --output products-azure.json
"""

import argparse
import datetime
import json
import urllib.parse
import urllib.request

try:
    from bs4 import BeautifulSoup
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "本脚本依赖 beautifulsoup4 和 lxml，请先执行：pip install beautifulsoup4 lxml"
    ) from exc

SOURCE_URL = "https://azure.microsoft.com/en-us/products"
DEFAULT_OUTPUT_FILE = "products-azure.json"
MODULE_TITLE = "Browse all Azure products (by category)"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def clean_text(text) -> str:
    return " ".join((text or "").split())


def derive_id(link):
    # Azure 卡片没有像 AWS 那样的内部产品标识，退而用链接路径的最后一段
    # 当作近似 id（如 .../products/virtual-machines/sql-server/ -> sql-server）。
    if not link:
        return None
    segments = [s for s in urllib.parse.urlparse(link).path.split("/") if s]
    return segments[-1] if segments else None


def parse_products(soup: BeautifulSoup):
    # 每个产品分类在页面里是一组连续的 <div class="grid-image-<slug> ...">：
    # 第一个带 <h2> 标题（分类名），后面某个不带标题的会包含若干
    # <div class="card h-100">（每张卡片就是一个产品）。按文档顺序遍历、
    # 记住"最近一次看到的分类标题"，比死记位置更稳，也不怕分类之间空区块数量不一致。
    is_category_section = lambda c: c and c.startswith("grid-image-")
    is_card = lambda c: c and c == "card"

    sections = soup.find_all("div", class_=is_category_section)
    current_category = None
    products = []

    for section in sections:
        heading = section.find("h2")
        if heading:
            current_category = clean_text(heading.get_text())
            continue

        if not current_category:
            continue

        for card in section.find_all("div", class_=is_card):
            title_tag = card.find(["h3", "h4", "h5"])
            name = clean_text(title_tag.get_text()) if title_tag else None
            if not name:
                # 纯粹用来对齐网格的空卡片，跳过
                continue

            desc_tag = card.find("p")
            description = clean_text(desc_tag.get_text()) if desc_tag else None

            link = None
            for a in card.find_all("a"):
                if clean_text(a.get_text()) == "Product":
                    link = a.get("href")
                    break
            if link:
                link = link.split("?")[0]

            products.append(
                {
                    "name": name,
                    "category": current_category,
                    "description": description,
                    "link": link,
                    "id": derive_id(link),
                }
            )

    return products


def merge_by_name(products):
    # 同一产品常常挂在多个分类下（如 App Service 同属 Compute/Mobile/Web），
    # 合并为一条记录，categories 存成数组。不同分类下的营销文案描述偶尔略有
    # 出入，这里保留第一次出现的描述，与 AWS 脚本的合并策略保持一致。
    merged = {}
    for p in products:
        entry = merged.setdefault(
            p["name"],
            {
                "name": p["name"],
                "categories": [],
                "description": p["description"],
                "link": p["link"],
                "id": p["id"],
            },
        )
        if p["category"] not in entry["categories"]:
            entry["categories"].append(p["category"])
    return sorted(merged.values(), key=lambda x: x["name"].lower())


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

    page_html = fetch_html(SOURCE_URL)
    soup = BeautifulSoup(page_html, "lxml")

    products = merge_by_name(parse_products(soup))

    output = {
        "source": SOURCE_URL,
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
