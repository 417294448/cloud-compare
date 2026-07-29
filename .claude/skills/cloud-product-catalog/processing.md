# 跨云产品映射（product-mapping.json）任务进度

> 本文档用于记录 `build_mapping.py` 中 `GROUPS`（跨云产品映射分组）的补全进度，
> 便于中断（如关机）后可以直接接续执行，无需重新梳理上下文。

## 任务目标

确保 `products-aws.json`、`products-azure.json`、`products-gcp.json` 三个源文件中的**所有产品**，
最终都能在 `product-mapping.json` 中体现（要么被收录进某个 `GROUPS` 映射分组，要么作为
`unmapped.trulyUnmapped` 的自包含条目出现）。

推进方式（用户已确认）：**按 AWS 分类下的产品数量从大到小，依次为全部 ~30 个 AWS 分类补充
`GROUPS` 映射条目**，参考 `cloud-compare-en-new.md` 中已有的人工整理映射关系校正准确性。

**当前状态（2026-07-29）：✅ 全部 30 个 AWS 分类已处理完毕，三个源文件 0 缺失。**

## 相关文件

- `scripts/build_mapping.py` —— 核心脚本，包含 `CATEGORY_LABELS_CN`、`DESCRIPTION_CN`、`GROUPS`、
  `build()`、`main()`。运行方式：
  ```bash
  python .claude/skills/cloud-product-catalog/scripts/build_mapping.py
  ```
  输出到仓库根目录 `product-mapping.json`。
- `references/mapping.md` —— 映射方法论说明（为什么不能机械匹配、`pilotCategories` vs
  `allCategories` 完整性保证、如何扩展新分类）。
- `products-aws.json` / `products-azure.json` / `products-gcp.json` —— 三个源数据文件（仓库根目录）。
- `cloud-compare-en-new.md` —— 人工维护的跨云产品对照文档，用于校验/参考不确定的映射关系。

## 分类总览

AWS 侧原生分类（`products-aws.json` 中出现的 `category`）共 **30 个**，按产品数量从大到小排列：

| # | 分类 | 产品数 | 状态 |
|---|---|---|---|
| 1 | Developer Tools | 38 | ✅ 已完成 |
| 2 | Management & Governance | 38 | ✅ 已完成 |
| 3 | Machine Learning | 33 | ✅ 已完成 |
| 4 | Security, Identity, & Compliance | 26 | ✅ 已完成 |
| 5 | Analytics | 20 | ✅ 已完成 |
| 6 | Networking & Content Delivery | 15 | ✅ 已完成 |
| 7 | Business Applications | 15 | ✅ 已完成 |
| 8 | Compute | 15 | ✅ 已完成 |
| 9 | Serverless | 11 | ✅ 已完成 |
| 10 | Database | 11 | ✅ 已完成 |
| 11 | Migration & Transfer | 11 | ✅ 已完成 |
| 12 | Media Services | 10 | ✅ 已完成 |
| 13 | Internet of Things (IoT) | 10 | ✅ 已完成 |
| 14 | Storage | 9 | ✅ 已完成 |
| 15 | Containers | 5 | ✅ 已完成 |
| 16 | Cryptography & PKI | 6 | ✅ 已完成 |
| 17 | Application Integration | 8 | ✅ 已完成 |
| 18 | Front-End Web & Mobile | 8 | ✅ 已完成 |
| 19 | General Reference | 8 | ✅ 已完成 |
| 20 | End User Computing | 6 | ✅ 已完成 |
| 21 | Customer Enablement Services | 6 | ✅ 已完成 |
| 22 | AWS Management Console | 4 | ✅ 已完成 |
| 23 | Cloud Financial Management | 4 | ✅ 已完成 |
| 24 | Game Development | 3 | ✅ 已完成 |
| 25 | Blockchain | 2 | ✅ 已完成 |
| 26 | Quantum Computing | 1 | ✅ 已完成 |
| 27 | Satellite | 1 | ✅ 已完成 |
| 28 | Marketplace | 1 | ✅ 无需处理（已通过交叉引用覆盖） |
| 29 | Partner Central | 1 | ✅ 已完成 |
| 30 | Compute HPC | 1 | ✅ 已完成 |

**统计**：共 30 个分类 → **全部 30 个已覆盖**（其中 Marketplace 通过 `mgmt-marketplace`
分组交叉引用覆盖，无需独立条目）。

## 最终统计

- `GROUPS` 共 **213 个映射分组**，覆盖全部 30 个 AWS 分类。
- 完整性校验结果（2026-07-29 通过）：
  - **AWS：308/308** 产品已映射
  - **Azure：204/204** 产品已映射
  - **GCP：213/213** 产品已映射
- 三个源文件的所有产品都能在 `product-mapping.json` 的 `groups` 或
  `unmapped.<category>.<vendor>.trulyUnmapped` 中找到，0 缺失。

## 后续待办（收尾工作）

1. ✅ ~~运行最终完整性校验~~ —— 已完成，0 缺失。
2. ✅ ~~更新 `SKILL.md` 与 `references/mapping.md`~~ —— 已把"试点 3 分类"的措辞更新为
   "全量 30 个 AWS 分类覆盖完成"，并在 `references/mapping.md` 补充了"全量推进阶段
   额外踩到的坑"一节（覆盖文档/参考类条目、SDK 拆分、单云合并分组、文档过时产品等
   新增场景）。
3. ✅ ~~关于 `index.html` 的疑虑~~ —— 之前本文档记录该页面"尚未实际构建"，**这是错误
   记录**：实际 `build-index.js`、`index.template.html`、`lib/transform.js`、`lib/query.js`
   及配套单元测试都已存在且工作正常（2026-07-29 验证：`node build-index.js` 成功生成
   530 行 × 55 分类的 `index.html`，`node --test lib/*.test.js` 10 个测试全过）。
   `SKILL.md` 中关于该查询页面的描述与事实相符，无需修改。

## 如何继续（关机重启后）

主任务与收尾工作已全部完成。后续如需扩展（厂商新增产品、新增云厂商、调整
分组、更新文档），按 `SKILL.md` 与 `references/mapping.md` 中的扩展指南
操作即可。
