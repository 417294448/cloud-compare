#!/usr/bin/env python3
"""校验 products-*.json → product-mapping.json → index.html 三层数据是否完整一致。

每次跑完抓取脚本（fetch_*_products.py）、build_mapping.py 或 build-index.js
之后，都应该跑一次这个脚本确认没有产品丢失。三类问题都会被发现：

1. 源 JSON 里的产品没进 product-mapping.json（漏映射）——通常是 build_mapping.py
   的 unmapped 统计逻辑有 bug，或者新增分类没被 allCategories 覆盖到。
2. 源 JSON 里的产品没进 index.html（漏渲染）——通常是改了 product-mapping.json
   但忘了重新跑 build-index.js，或者 build-index.js 的 transform 逻辑漏了某类条目。
3. product-mapping.json 引用了源 JSON 里不存在的产品（脏引用）——通常是手动改过
   product-mapping.json，或者厂商改了产品名后 GROUPS 没同步更新（虽然
   build_mapping.py 的 resolve() 本身也会查，但如果有人绕过脚本直接改 JSON
   就会漏掉）。

校验方式：产品名按"小写 + 非字母数字替换为空格"归一化后做集合比对，可以容忍
厂商官网显示名里微小的标点差异（如 "AWS Fargate" vs "AWS  Fargate"），但改名、
缺失、多余引用都会被查出来。

退出码：0 = 全部一致；1 = 有任一缺失/多余/不同步。适合作为 CI 或提交前的
最后一步校验。

用法：
    python .claude/skills/cloud-product-catalog/scripts/check_completeness.py
"""

import json
import re
import sys
from pathlib import Path

# 脚本位于 <repo>/.claude/skills/cloud-product-catalog/scripts/，
# parents[4] 才是仓库根目录（[0]=scripts [1]=cloud-product-catalog [2]=skills [3]=.claude [4]=<repo>）。
ROOT = Path(__file__).resolve().parents[4]

SOURCE_FILES = {
    "aws": "products-aws.json",
    "azure": "products-azure.json",
    "gcp": "products-gcp.json",
    "alibaba": "products-alibabacloud.json",
}
MAPPING_FILE = "product-mapping.json"
INDEX_FILE = "index.html"


def normalize(name):
    """归一化产品名，用于跨文件比对。

    小写 + 非字母数字字符替换为空格，容忍标点/大小写/多余空白的差异，
    但不会因为改了词而误判一致。
    """
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect_source_names():
    """从三份 products-*.json 收集产品名，返回 {vendor: {normalize_name: original_name}}。"""
    result = {}
    for vendor, filename in SOURCE_FILES.items():
        data = load_json(ROOT / filename)
        result[vendor] = {normalize(p["name"]): p["name"] for p in data["products"]}
    return result


def collect_mapping_names(mapping):
    """从 product-mapping.json 的 groups + unmapped.trulyUnmapped 收集产品名。

    返回 {vendor: set(normalize_name)}。unmapped.mappedUnderOtherCategory 只是
    一个名字列表（不是完整产品对象），且这些名字必然也出现在某个 group 里，
    所以不需要单独算。
    """
    names = {vendor: set() for vendor in SOURCE_FILES}

    def add_from_group(group):
        for vendor in SOURCE_FILES:
            for p in group.get("products", {}).get(vendor, []):
                names[vendor].add(normalize(p["name"]))

    for group in mapping.get("groups", []):
        add_from_group(group)
    for cat_bucket in mapping.get("unmapped", {}).values():
        for vendor in SOURCE_FILES:
            for entry in cat_bucket.get(vendor, {}).get("trulyUnmapped", []):
                add_from_group(entry)
    return names


def collect_index_names(html_text):
    """从 index.html 内嵌的 PAYLOAD 数据里收集产品名。

    index.html 由 build-index.js 生成，数据内嵌在 `var PAYLOAD = {...};` 里。
    如果找不到 PAYLOAD（比如模板改了变量名），返回 None 让上层报错，
    而不是静默当成"页面里一个产品都没有"。
    """
    m = re.search(r"var PAYLOAD = (\{.*?\});?\s*\n", html_text, re.DOTALL)
    if not m:
        return None
    payload = json.loads(m.group(1))
    names = {vendor: set() for vendor in SOURCE_FILES}
    for row in payload.get("rows", []):
        for vendor in SOURCE_FILES:
            for p in row.get("products", {}).get(vendor, []):
                names[vendor].add(normalize(p["name"]))
    return names, len(payload.get("rows", []))


def main():
    sources = collect_source_names()
    mapping = load_json(ROOT / MAPPING_FILE)
    mapping_names = collect_mapping_names(mapping)

    index_path = ROOT / INDEX_FILE
    if not index_path.exists():
        print(f"ERROR: {INDEX_FILE} not found — run node build-index.js first", file=sys.stderr)
        return 1
    index_result = collect_index_names(index_path.read_text(encoding="utf-8"))
    if index_result is None:
        print(
            f"ERROR: could not extract PAYLOAD from {INDEX_FILE} (template variable name may have changed)",
            file=sys.stderr,
        )
        return 1
    index_names, index_row_count = index_result

    # 期望的 rows 数量 = groups 数 + trulyUnmapped 条目数（buildRows 的逻辑）
    expected_rows = len(mapping.get("groups", [])) + sum(
        len(cat_bucket.get(vendor, {}).get("trulyUnmapped", []))
        for cat_bucket in mapping.get("unmapped", {}).values()
        for vendor in SOURCE_FILES
    )

    problems = []

    # 检查 1: 源 JSON -> mapping 缺失
    for vendor in SOURCE_FILES:
        missing = set(sources[vendor]) - mapping_names[vendor]
        for n in sorted(missing):
            problems.append(
                f"[{vendor}] missing in product-mapping.json: {sources[vendor][n]}"
            )

    # 检查 2: 源 JSON -> index.html 缺失
    for vendor in SOURCE_FILES:
        missing = set(sources[vendor]) - index_names[vendor]
        for n in sorted(missing):
            problems.append(
                f"[{vendor}] missing in index.html: {sources[vendor][n]}"
            )

    # 检查 3: mapping 引用了源 JSON 不存在的产品
    for vendor in SOURCE_FILES:
        extra = mapping_names[vendor] - set(sources[vendor])
        for n in sorted(extra):
            problems.append(f"[{vendor}] stale reference in product-mapping.json: {n}")

    # 检查 4: index.html 行数与 mapping 期望行数不一致（提示没重新跑 build-index.js）
    if index_row_count != expected_rows:
        problems.append(
            f"index.html rows ({index_row_count}) != expected from product-mapping.json "
            f"({expected_rows}) — did you forget to re-run node build-index.js?"
        )

    total_products = sum(len(s) for s in sources.values())
    if problems:
        print(f"FAIL: found {len(problems)} problem(s) across {total_products} source products")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(
        f"OK: {total_products} source products fully covered; "
        f"product-mapping.json has no stale references; "
        f"index.html rows ({index_row_count}) matches mapping."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
