#!/usr/bin/env python3
"""抓取 AWS 官方文档首页"Product guides & references"模块的产品信息，
输出 products-aws.json，供后续与其他云平台产品做映射使用。

属于 cloud-product-catalog skill 的 AWS 抓取脚本，建议在仓库根目录下执行，
使产出的 JSON 与其他云厂商的产品目录文件（如 products-azure.json）保持同级。

用法：
    python .claude/skills/cloud-product-catalog/scripts/fetch_aws_products.py
    python .claude/skills/cloud-product-catalog/scripts/fetch_aws_products.py --output products-aws.json
"""

import argparse
import datetime
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

SOURCE_URL = "https://docs.aws.amazon.com/"
DEFAULT_OUTPUT_FILE = "products-aws.json"
MODULE_TITLE = "Product guides & references"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def extract_landing_page_xml(page_html: str) -> str:
    # 首页是客户端渲染的，完整落地页数据以 URL 编码的 XML 形式藏在
    # <input id="landing-page-xml" value="..."> 中，需要先取出再解码。
    match = re.search(r'id="landing-page-xml"[^>]*value="([^"]+)"', page_html)
    if not match:
        raise RuntimeError("未找到 landing-page-xml 隐藏字段，页面结构可能已变化")
    return urllib.parse.unquote(match.group(1))


def find_products_section(root: ET.Element) -> ET.Element:
    for section in root.iter("section"):
        if section.get("id") == "products":
            return section
    raise RuntimeError('未找到 id="products" 的 section')


def clean_text(text: str) -> str:
    return " ".join((text or "").split())


def parse_products(section: ET.Element):
    products = []
    for list_card in section.find("cards").findall("list-card"):
        category = clean_text(list_card.findtext("title"))
        items = list_card.find("list-card-items")
        if items is None:
            continue
        for item in items.findall("list-card-item"):
            href = item.get("href")
            name = clean_text(item.findtext("title"))
            description = clean_text(item.findtext("abstract"))
            if not name:
                continue
            # 跳过“决策指南”类引导文档，它们不是真实产品
            if href and "/decision-guides/" in href:
                continue
            if name.startswith("Choosing"):
                continue

            link = href
            if link and link.startswith("/"):
                link = "https://docs.aws.amazon.com" + link
            if link:
                link = link.split("?")[0]

            products.append(
                {
                    "name": name,
                    "category": category,
                    "description": description,
                    "link": link,
                    "id": item.get("id"),
                }
            )
    return products


def merge_by_name(products):
    # 同一产品可能出现在多个分类下（如 DynamoDB 同属 Database 和 Serverless），
    # 合并为一条记录，categories 存成数组，避免映射时出现同名重复项。
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
    xml_text = extract_landing_page_xml(page_html)
    root = ET.fromstring(xml_text)
    section = find_products_section(root)

    products = merge_by_name(parse_products(section))

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
