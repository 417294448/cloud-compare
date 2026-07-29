# Cloud Service Product Comparison

## Table of Contents
- [Interactive Query Page (index.html)](#interactive-query-page-indexhtml)
- [International Services](#international-services)
- [Chinese Services](#chinese-services)

## Interactive Query Page (index.html)

**[index.html](index.html)** is a self-contained, zero-dependency static page that lets you browse and search the cross-cloud product mapping in your browser — no server, no build step at view time; just double-click to open.

**Features**

- **4-vendor comparison** — every row shows the matched products across AWS, Azure, GCP, and Alibaba Cloud side by side.
- **Category browsing** — 35 unified categories spanning compute, database, storage, networking, ML, security, and more.
- **Vendor filter** — toggle vendor chips to keep only rows that have products on the selected clouds.
- **Full-text search** — search across product names, concept names, descriptions (both English and Chinese).
- **Bilingual** — switch between English and 中文 with one click.
- **Light / dark theme** — independent theme toggle.

**How it's built (don't edit by hand)**

`index.html` is a generated artifact. The data pipeline is:

```
products-{aws,azure,gcp,alibabacloud}.json   ← scraped from official sites
                    ↓
        product-mapping.json                  ← curated cross-cloud grouping
                    ↓
              index.html                      ← generated static page
```

Regenerate after any data update:

```bash
node build-index.js
```

The template lives in `index.template.html`; data-flattening logic is in `lib/transform.js`; filter/sort logic is in `lib/query.js`. See `.claude/skills/cloud-product-catalog/SKILL.md` for the full maintenance workflow.

## International Services
This section provides a comparison of major international cloud service providers, covering service types such as computing, storage, and networking. [View Detailed Information](cloud-compare-en.md)

Compared Cloud Providers:
- AWS (Amazon Web Services)
- Azure (Microsoft Azure)
- GCP (Google Cloud Platform)
- OCI (Oracle Cloud Infrastructure)
- Alibaba Cloud (International)
- IBM Cloud

Service Categories:
- Analytics
- Application Integration
- Blockchain
- Business Applications
- Compute
- Containers
- Database
- Developer Tools
- End User Computing
- Front-end Web & Mobile
- Game Development
- Internet of Things
- Machine Learning
- Management & Governance
- Media Services
- Migration & Transfer
- Networking & Content Delivery
- Security, Identity & Compliance
- Storage
- Quantum Technologies
- Robotics
- Satellite
- Hybrid + Multicloud
- Domain Registration

## Chinese Services
这里是中国主流云厂商的产品对照表，涵盖了计算、存储、网络等服务类型。[查看详细信息](cloud-compare-cn.md)

对比的云厂商：
- 阿里云 (Alibaba Cloud)
- 腾讯云 (Tencent Cloud)
- 华为云 (Huawei Cloud)
- 百度云 (Baidu Cloud)
- 天翼云 (China Telecom Cloud)
- AWS (作为参考)

涵盖服务类型：
- 计算服务
- 容器服务
- 存储服务
- 数据库
- 网络服务
- 安全服务
- 中间件
- 数据分析与大数据
- 人工智能
- 开发工具
- 视频及媒体服务
- 数据迁移
- 运维管理
- 解决方案
- 云通信
- 监控与运维
- 区块链
- 边缘计算
- 微服务与API
- 消息队列
- 数据治理
- 混合云管理
- 安全合规
- 云网络优化
- 云原生DevOps
- IoT & 物联网
- 智能地图服务
- 域名注册