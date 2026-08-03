"""统一记录 JSON 文件变更，生成可读的 diff 日志。

每次抓取脚本或 build_mapping.py 重写产物 JSON 时，调用 write_json_with_diff()
会在 diffs/refresh-diff-YYYY-MM-DD.txt 中追加一段变更记录，包含：
- 操作类型、目标文件路径和时间戳
- 自然语言变更摘要（新增/下线产品、映射分组/分类/未覆盖产品数量变化等）
- 统一 diff（unified diff）展示具体行级变化

日志文件按日期聚合，同一天多次运行会追加到同一个文件。
"""

import datetime
import difflib
import json
from pathlib import Path

DIFF_DIR = Path("diffs")


def _diff_path() -> Path:
    today = datetime.date.today().isoformat()
    return DIFF_DIR / f"refresh-diff-{today}.txt"


def _ensure_diff_dir() -> None:
    DIFF_DIR.mkdir(parents=True, exist_ok=True)


def _format_change(old, new, label, formatter=str):
    """如果 old/new 不同，返回一句自然语言描述；相同返回空串。"""
    if old == new:
        return ""
    return f"{label}: {formatter(old)} -> {formatter(new)}"


def _product_catalog_summary(old_data, new_data):
    """产品目录 JSON 的变更摘要。"""
    summary = []
    if not (
        isinstance(old_data, dict)
        and isinstance(new_data, dict)
        and "products" in old_data
        and "products" in new_data
    ):
        return summary

    old_names = {p.get("name") for p in old_data.get("products", []) if p.get("name")}
    new_names = {p.get("name") for p in new_data.get("products", []) if p.get("name")}
    added = sorted(new_names - old_names)
    removed = sorted(old_names - new_names)

    if added:
        summary.append(f"新增产品（{len(added)} 个）: {', '.join(added)}")
    if removed:
        summary.append(f"下线/移除产品（{len(removed)} 个）: {', '.join(removed)}")

    count_change = _format_change(
        len(old_names), len(new_names), "产品总数"
    )
    if count_change:
        summary.append(count_change)

    fetched_change = _format_change(
        old_data.get("fetchedAt"), new_data.get("fetchedAt"), "抓取日期"
    )
    if fetched_change:
        summary.append(fetched_change)

    return summary


def _count_truly_unmapped(unmapped):
    """统计 mapping 中 trulyUnmapped 的产品条数。"""
    count = 0
    if not isinstance(unmapped, dict):
        return 0
    for cat in unmapped.values():
        if not isinstance(cat, dict):
            continue
        for vendor in cat.values():
            entries = vendor.get("trulyUnmapped") if isinstance(vendor, dict) else None
            if isinstance(entries, list):
                count += len(entries)
    return count


def _mapping_summary(old_data, new_data):
    """product-mapping.json 的变更摘要。"""
    summary = []
    if not (isinstance(old_data, dict) and isinstance(new_data, dict)):
        return summary

    old_groups = old_data.get("groups")
    new_groups = new_data.get("groups")
    if isinstance(old_groups, list) and isinstance(new_groups, list):
        change = _format_change(len(old_groups), len(new_groups), "映射分组数")
        if change:
            summary.append(change)

    old_cats = old_data.get("allCategories") or list(old_data.get("unmapped", {}).keys())
    new_cats = new_data.get("allCategories") or list(new_data.get("unmapped", {}).keys())
    if isinstance(old_cats, list) and isinstance(new_cats, list):
        change = _format_change(len(old_cats), len(new_cats), "分类数")
        if change:
            summary.append(change)
        old_set, new_set = set(old_cats), set(new_cats)
        added_cats = sorted(new_set - old_set)
        removed_cats = sorted(old_set - new_set)
        if added_cats:
            summary.append(f"新增分类: {', '.join(added_cats)}")
        if removed_cats:
            summary.append(f"移除分类: {', '.join(removed_cats)}")

    old_unmapped = _count_truly_unmapped(old_data.get("unmapped"))
    new_unmapped = _count_truly_unmapped(new_data.get("unmapped"))
    change = _format_change(old_unmapped, new_unmapped, "真正未映射产品数")
    if change:
        summary.append(change)

    generated_change = _format_change(
        old_data.get("generatedAt"), new_data.get("generatedAt"), "生成时间"
    )
    if generated_change:
        summary.append(generated_change)

    return summary


def _build_summary(old_data, new_data):
    """根据数据形状选择对应的摘要生成器。"""
    if isinstance(new_data, dict) and "groups" in new_data:
        return _mapping_summary(old_data, new_data)
    return _product_catalog_summary(old_data, new_data)


def write_json_with_diff(path, data, operation=None, indent=2):
    """将 data 序列化为 JSON 写入 path，并追加 diff 到当日日志文件。

    Args:
        path: 目标 JSON 文件路径（字符串或 Path）。
        data: 要写入的 Python 对象，会被 json.dumps 序列化。
        operation: 本次操作的自然语言描述，例如 "AWS 产品目录抓取"。
        indent: JSON 缩进空格数，与现有脚本保持一致。

    Returns:
        bool: 是否实际产生了内容变更（True=有变更，False=无变更）。
    """
    path = Path(path)

    old_text = ""
    old_data = None
    if path.exists():
        old_text = path.read_text(encoding="utf-8")
        try:
            old_data = json.loads(old_text)
        except Exception:
            pass

    new_text = json.dumps(data, ensure_ascii=False, indent=indent) + "\n"
    path.write_text(new_text, encoding="utf-8")

    _ensure_diff_dir()
    diff_file = _diff_path()

    header_lines = [
        "=" * 60,
    ]
    if operation:
        header_lines.append(f"操作: {operation}")
    header_lines.extend([
        f"文件: {path}",
        f"时间: {datetime.datetime.now().isoformat(timespec='seconds')}",
        "",
    ])

    summary = _build_summary(old_data, data)
    if summary:
        header_lines.append("变更摘要:")
        header_lines.extend(f"  {line}" for line in summary)
        header_lines.append("")

    if old_text == new_text:
        header_lines.append("本次无变更。")
        header_lines.append("")
        with diff_file.open("a", encoding="utf-8") as f:
            f.write("\n".join(header_lines))
        return False

    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True) if old_text else [],
        new_text.splitlines(keepends=True),
        fromfile=str(path),
        tofile=str(path),
    )

    with diff_file.open("a", encoding="utf-8") as f:
        f.write("\n".join(header_lines))
        f.write("".join(diff))
        f.write("\n")

    return True
