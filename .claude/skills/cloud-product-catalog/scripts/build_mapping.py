#!/usr/bin/env python3
"""基于 products-aws.json / products-azure.json / products-gcp.json，
生成跨云产品功能映射 product-mapping.json，供 cloud-compare 做产品对照查询。

产品名称之间没有任何可靠的机械关联键（见 references/mapping.md），无法靠
脚本自动配对，必须靠人工/语义判断。这个脚本本身不做匹配决策——匹配结果
以 GROUPS 常量的形式硬编码在下面，脚本只负责：

1. 校验 GROUPS 里引用的每个产品名在对应厂商的数据里真实存在（防止手滑
   打错名字，或者厂商改了产品名之后映射表没跟着更新）。
2. 从源数据里把 link/description 之类的字段自动补全，不用手抄。
3. 自动算出每个分类下"没有被任何分组引用"的产品，按厂商列出来，并进一步
   拆成 trulyUnmapped（真的没有任何分组处理过）和
   mappedUnderOtherCategory（产品同时挂了多个分类，已经被别的分类下的
   分组引用了，只是不在当前这个分类下——比如 AWS Lambda 同时属于 Compute
   和 Serverless，只被 Serverless 分类下的分组引用，在 Compute 分类的
   统计里就属于这一类，不是真的没处理）。不这么拆分的话，unmapped 列表
   会显得比实际情况差很多，容易让人误以为漏了一堆产品。trulyUnmapped
   里每一项都包成和 groups 数组同构的对象（category/name/products/notes
   等字段一应俱全），只是 products 里只有它自己所在的厂商有内容、其余
   厂商是空数组，category/name 直接用这个产品自己在源数据里的分类和
   名字——这样前端遍历"行"的时候不用区分"已配对"和"暂未配对"两种数据
   形状。

新增/修改映射关系时，直接编辑 GROUPS，然后重新运行这个脚本，不要手改
生成出来的 product-mapping.json。

仓库根目录下的 cloud-compare-en-new.md 是一份人工维护的多云产品对照表
（含 OCI/阿里云/IBM Cloud，比这里覆盖的三朵云更全），拿不准某个分组该怎么
配对时，先去那份文档里查一下对应的 Service Type 行，比自己瞎猜靠谱。
但那份文档也不是绝对权威——它给的候选产品名要在 products-*.json 里能查到
才采纳，查不到的（比如已经改名、下线，或者压根没被抓进这份数据源的）要么
换成数据源里的实际名字，要么在 notes 里注明"参考文档提到但当前数据源没有"，
不能直接照抄，脚本的校验步骤会在名字对不上时直接报错，逼着你处理这种情况
而不是留一个死链接。`name` 字段是分组的显示名称，拿不准怎么起时可以先照
抄那份文档对应行的 Service Type 当草稿，但不用被文档的措辞捆死——如果
这个分组的实际配对内容比文档写的更精确（比如把 Aurora/Spanner 归一组，
文档写的是笼统的"High-Performance Relational Database"，而这里更想强调
"云原生分布式关系型数据库"这个共性），可以用更准确的说法，本轮试点里
自己新拆出来的分组（文档没有对应行）也是照这个思路自己起名，并在 notes
里注明是自拟的。

输出的 category / name / notes 是分组层级的描述字段，description 是每条
产品记录自带的字段（直接取自各厂商官方文档，本身就是英文）——这几个字段
都同时提供英文原文和 "-cn" 后缀的中文翻译两个版本，方便页面按语种切换
显示。产品的官方名称（products.<vendor>[].name）和链接不翻译，跨语言
场景下品牌名通常保留原文。

新增分组或产品时的翻译维护规则：
- GROUPS 里每个分组要同时填 name/name-cn、notes/notes-cn（notes 可以为
  空字符串，但两个语言版本都要给，不要漏填一边）。
- 每引用一个新产品，都要去 DESCRIPTION_CN 里给对应厂商加一条中文翻译，
  key 用产品在 products-*.json 里的官方名称（和 GROUPS 里引用的名字
  一致）。漏填翻译时 resolve() 会直接报错，不会静默生成一个缺中文的
  产品记录。

用法：
    python .claude/skills/cloud-product-catalog/scripts/build_mapping.py
"""

import argparse
import datetime
import json
import re

from diff_logger import write_json_with_diff

DEFAULT_OUTPUT_FILE = "product-mapping.json"

SOURCE_FILES = {
    "aws": "products-aws.json",
    "azure": "products-azure.json",
    "gcp": "products-gcp.json",
    "alibaba": "products-alibabacloud.json",
}

# 三份数据里出现过的全部分类名的中文翻译（AWS 自己的 30 个分类，加上
# Azure/GCP 各自的命名——三家的分类词表并不统一，比如 AWS 叫
# "Database"，Azure/GCP 都叫 "Databases"，这里按各自原文分别给翻译，
# 不强行统一成一套词表）。GROUPS 里的分组目前只用到 AWS 风格的
# Compute/Database/Serverless 三个，其余是给 unmapped 里各厂商自己的
# 分类兜底用的。
# 三份源数据中出现的 category 名称并不统一（AWS 30 个、Azure 21 个、GCP 14 个），
# 同一功能在不同厂商那里可能叫不同的名字（AWS "Machine Learning" vs Azure "AI +
# machine learning" vs GCP "AI and ML"），甚至同一家内部也有大小写/单复数/
# 连字符差异。如果按原始名分别统计，product-mapping.json 的 unmapped 字段会
# 出现 55 个分类、其中 14+ 组本质上是同一件事。
#
# CATEGORY_CANONICAL 把这些"原始分类名"归一到一个"主名"（canonical），
# build() 输出时所有 category 字段统一用主名，不再保留各家原始命名。
# 主名选取原则：
# - 优先用 AWS 风格的分类名（AWS 分类体系最完整、命名最准确）。
# - 三家完全一致时（Compute/Storage/Containers）保留通用名。
# - 主名同时也是 GROUPS 里 "category" 字段应该使用的值——新增分组时
#   直接写主名，不要写 Azure/GCP 风格的原始名。
CATEGORY_CANONICAL = {
    # 三家完全一致，主名就是原名
    "Compute": "Compute",
    "Storage": "Storage",
    "Containers": "Containers",

    # B 类：同义不同名，统一到 AWS 风格
    "Machine Learning": "Machine Learning",
    "AI + machine learning": "Machine Learning",
    "AI and ML": "Machine Learning",

    "Database": "Database",
    "Databases": "Database",

    "Networking & Content Delivery": "Networking & Content Delivery",
    "Networking": "Networking & Content Delivery",

    "Security, Identity, & Compliance": "Security, Identity, & Compliance",
    "Security": "Security, Identity, & Compliance",
    "Identity": "Security, Identity, & Compliance",

    "Analytics": "Analytics",
    "Data analytics": "Analytics",

    "Internet of Things (IoT)": "Internet of Things (IoT)",
    "Internet of Things": "Internet of Things (IoT)",

    "Migration & Transfer": "Migration & Transfer",
    "Migration": "Migration & Transfer",

    "Developer Tools": "Developer Tools",
    "Developer tools": "Developer Tools",

    "Management & Governance": "Management & Governance",
    "Management and governance": "Management & Governance",

    "Media Services": "Media Services",
    "Media": "Media Services",

    "Application Integration": "Application Integration",
    "Integration": "Application Integration",

    # 跨厂商表述差异较大，需要新造一个统一主名
    "Hybrid + multicloud": "Hybrid & Multicloud",
    "Distributed, hybrid, and multicloud": "Hybrid & Multicloud",

    # C/D 类：边界争议组，按用户确认的合并
    "End User Computing": "End User Computing",
    "Virtual desktop infrastructure": "End User Computing",

    "Front-End Web & Mobile": "Front-End Web & Mobile",
    "Mobile": "Front-End Web & Mobile",
    "Web": "Front-End Web & Mobile",

    "DevOps": "Developer Tools",
    "Application development": "Developer Tools",

    "Observability and monitoring": "Management & Governance",

    # 阿里云 13 个一级分类（products-alibabacloud.json）——按其官方英文原名
    # 归一到 canonical 主名。阿里云自身没有给分类起标准化名字，跟随 AWS 风格。
    "Elastic Computing": "Compute",
    "Artificial Intelligence": "Machine Learning",
    "Container & Middleware": "Containers",
    "Developer Services": "Developer Tools",
    "Enterprise Applications & Cloud Communication": "Business Applications",
    "Hybrid Cloud": "Hybrid & Multicloud",
    "Networking & CDN": "Networking & Content Delivery",
    # "Analytics"、"Database"、"Storage"、"Security"、"Internet of Things"、
    # "Media Services" 这几个阿里云原名与 canonical 主名同形或在已有映射里
    # 覆盖（"Security" → "Security, Identity, & Compliance"、"Internet of
    # Things" → "Internet of Things (IoT)" 已在上面定义），不需要重复列。

    # 阿里云的二级分类（products-alibabacloud.json 里 categories[1]）——它们
    # 不是真正的产品分类，只是阿里云自己的导航分组（比如 "Elastic Computing /
    # Cloud Server"、"Database / Relational Database"），如果不归一会污染
    # allCategories。这里把它们统一映射到对应的一级 canonical 主名，等同于
    # 丢弃二级信息（GROUP 配对时已经按产品精确判断，不依赖分类）。
    "Cloud Server": "Compute",
    "Container Service": "Containers",
    "Container": "Containers",
    "Elastic Orchestration": "Management & Governance",
    "HPC": "Compute HPC",
    "Hybrid Cloud Application": "Hybrid & Multicloud",
    "Serverless": "Serverless",
    "Warehouse Service": "Storage",
    "Relational Database": "Database",
    "NoSQL Database": "Database",
    "Data Warehouse": "Analytics",
    "Dedicated Cluster": "Database",
    "Utility & Tools": "Management & Governance",
    "Essential Storage Service": "Storage",
    "Hybrid Cloud Data Connectivity": "Hybrid & Multicloud",
    "Hybrid Cloud Storage": "Storage",
    "Storage Data Service": "Storage",
    "Data Transport": "Migration & Transfer",
    "Backup, Migration and Disaster Recovery": "Migration & Transfer",
    "Data Computing": "Analytics",
    "Data Development": "Developer Tools",
    "Data Search and Analytics": "Analytics",
    "Big Data Application and Visualization": "Analytics",
    "Intelligent Search and Recommendation": "Machine Learning",
    "Applications": "Business Applications",
    "Message Queue": "Application Integration",
    "Micro Services": "Containers",
    "API & SDK": "Developer Tools",
    "Corporate IT Governance": "Management & Governance",
    "Application Services": "Business Applications",
    "Blockchain": "Blockchain",
    "Cloud Communication": "Business Applications",
    "Corporate Office Collaboration": "Business Applications",
    "Domains & Website": "Networking & Content Delivery",
    "Intelligent Services": "Machine Learning",
    "Private Cloud": "Hybrid & Multicloud",
    "Media Technology": "Media Services",
    "CDN and Edge": "Networking & Content Delivery",
    "Cloud Network": "Networking & Content Delivery",
    "Cross Region Network": "Networking & Content Delivery",
    "Hybrid Cloud Network": "Networking & Content Delivery",
    "Business Security": "Security, Identity, & Compliance",
    "Cloud Security": "Security, Identity, & Compliance",
    "Data Security": "Security, Identity, & Compliance",
    "Hybrid Cloud Security": "Security, Identity, & Compliance",
    "Identity Management": "Security, Identity, & Compliance",
    "Security Service": "Security, Identity, & Compliance",
    "Analytics": "Analytics",
}

# CATEGORY_LABELS_CN 的 key 是 canonical 主名（不再是原始名）。
# 原始名通过 CATEGORY_CANONICAL 先归一，再从这里查中文标签。
CATEGORY_LABELS_CN = {
    "AWS Management Console": "AWS 管理控制台",
    "Analytics": "分析",
    "Application Integration": "应用集成",
    "Application hosting": "应用托管",
    "Blockchain": "区块链",
    "Business Applications": "业务应用",
    "Cloud Financial Management": "云财务管理",
    "Compute": "计算服务",
    "Compute HPC": "高性能计算",
    "Containers": "容器",
    "Cross-product": "跨产品",
    "Cryptography & PKI": "加密与公钥基础设施",
    "Customer Enablement Services": "客户赋能服务",
    "Database": "数据库",
    "Developer Tools": "开发者工具",
    "End User Computing": "最终用户计算",
    "Front-End Web & Mobile": "前端 Web 与移动",
    "Game Development": "游戏开发",
    "General Reference": "通用参考",
    "Hybrid & Multicloud": "混合与多云",
    "Industry solutions": "行业解决方案",
    "Internet of Things (IoT)": "物联网",
    "Machine Learning": "机器学习",
    "Management & Governance": "管理与治理",
    "Marketplace": "应用市场",
    "Media Services": "媒体服务",
    "Migration & Transfer": "迁移与传输",
    "Mixed reality": "混合现实",
    "Networking & Content Delivery": "网络与内容分发",
    "Partner Central": "合作伙伴中心",
    "Quantum Computing": "量子计算",
    "Satellite": "卫星",
    "Security, Identity, & Compliance": "安全、身份与合规",
    "Serverless": "无服务器",
    "Storage": "存储",
}


def canonical_category(category):
    """把源数据里的原始 category 名归一到主名。未知分类原样返回（不会丢）。"""
    return CATEGORY_CANONICAL.get(category, category)

# 每条产品描述的中文翻译，key 是产品在 products-*.json 里的官方名称。
# 只需要覆盖 GROUPS 里实际引用到的产品，不用覆盖每个厂商的全部产品。
DESCRIPTION_CN = {
    "aws": {
        "Amazon Elastic Compute Cloud": "使用 Amazon EC2 在云端创建和运行虚拟服务器",
        "Amazon Lightsail": "启动和管理虚拟专用服务器",
        "AWS Elastic Beanstalk": "运行和管理 Web 应用",
        "AWS Batch": "以任意规模运行批处理作业",
        "AWS ParallelCluster": "在 AWS 云上部署和管理高性能计算集群",
        "AWS Parallel Computing Service": "轻松以近乎任意规模运行高性能计算（HPC）工作负载",
        "AWS Outposts": "在本地运行 AWS 基础设施",
        "Amazon Elastic VMware Service": "在您的 VPC 内于 Amazon EC2 上迁移和运行 VCF 环境",
        "Amazon Linux": "现代高性能 Linux 操作系统产品组合",
        "EC2 Image Builder": "自动化「黄金」服务器镜像的生命周期管理",
        "AWS Local Zones": "让延迟敏感型应用更靠近终端用户运行",
        "AWS Wavelength": "为 5G 设备提供超低时延应用",
        "Amazon Relational Database Service": "在云中设置、运行和扩展关系型数据库",
        "Amazon Aurora": "高性能托管关系型数据库引擎",
        "Amazon Aurora DSQL": "面向高可用应用的最快无服务器分布式 SQL 数据库",
        "Amazon DynamoDB": "托管型 NoSQL 数据库",
        "Amazon DocumentDB (with MongoDB compatibility)": "完全托管的文档数据库",
        "Amazon Keyspaces (for Apache Cassandra)": "兼容 Cassandra 的托管数据库",
        "Amazon ElastiCache": "内存缓存服务",
        "Amazon MemoryDB": "兼容 Redis、持久化的内存数据库服务",
        "Amazon Neptune": "完全托管的图数据库服务",
        "Amazon Timestream": "完全托管的时序数据库",
        "Oracle Database@AWS": "在 AWS 数据中心内访问由 OCI 管理的 Oracle Exadata 基础设施",
        "AWS Database Migration Service": "以最短停机时间迁移数据库",
        "AWS Lambda": "无需考虑服务器即可运行代码",
        "AWS Fargate": "面向容器的无服务器计算",
        "AWS App Runner": "让开发者轻松规模化运行生产级 Web 应用",
        "Amazon API Gateway": "构建、部署和管理 API",
        "Amazon EventBridge": "面向 SaaS 应用和 AWS 服务的无服务器事件总线",
        "Amazon Simple Queue Service": "托管消息队列",
        "Amazon Simple Notification Service": "发布/订阅、短信、邮件和移动推送通知",
        "Amazon MQ": "托管消息代理服务",
        "AWS Step Functions": "面向分布式应用的协调服务",
        "AWS AppSync": "加速开发全托管、可扩展的 GraphQL API",
        "Amazon Simple Storage Service": "可从任意位置检索任意数据量的对象存储",
        "Amazon EC2 Auto Scaling": "根据需求自动扩缩多种资源",
        "AWS Serverless Application Model": "在 AWS 上构建无服务器应用",
        "AWS Serverless Application Repository": "发现、部署和发布无服务器应用",
        "Serverless": "AWS 云上无服务器核心概念与服务简介",
        "AWS SDK for .NET": "使用 .NET 专属 API 和库开发应用程序",
        "AWS SDK for C++": "使用 C++ 专属 API 开发应用程序",
        "AWS SDK for Go": "使用 Go 专属 API 和库开发应用程序",
        "AWS SDK for Java": "使用 Java 专属 API 和库开发应用程序",
        "AWS SDK for JavaScript": "使用 JavaScript 专属 API 和库开发应用程序",
        "AWS SDK for Kotlin": "使用 Kotlin 专属 API 开发应用程序",
        "AWS SDK for PHP": "使用 PHP 专属 API 和库开发应用程序",
        "AWS SDK for Python (Boto3)": "使用 Python 专属 API 和库开发应用程序",
        "AWS SDK for Ruby": "使用 Ruby 专属 API 和库开发应用程序",
        "SDK for Rust": "使用 Rust 专属 API 开发应用程序",
        "SDK for SAP ABAP": "使用客户端模块库开发应用程序",
        "SDK for Swift": "使用 Swift 专属 API 开发应用程序",
        "AWS Tools for PowerShell": "基于 .NET SDK 功能构建的 PowerShell 模块",
        "Amazon CodeCatalyst": "统一的软件开发服务，用于在 AWS 上开发和交付",
        "Amazon Corretto": "免费、跨平台、可用于生产环境的 OpenJDK 发行版",
        "AWS Cloud9": "在云端 IDE 中编写、运行和调试代码",
        "AWS CloudShell": "直接从浏览器访问 AWS 资源和工具的命令行环境",
        "AWS Cloud Control API": "使用统一 API 管理 AWS 及第三方云基础设施",
        "AWS CodeArtifact": "面向软件开发的制品管理服务",
        "AWS CodeBuild": "构建和测试代码",
        "AWS CodeDeploy": "自动化代码部署",
        "AWS CodePipeline": "使用持续交付发布软件",
        "AWS X-Ray": "分析和调试你的应用程序",
        "AWS Toolkit for JetBrains": "面向 JetBrains 系列集成开发环境（IDE）的开源插件",
        "AWS Toolkit for Visual Studio Code": "面向 Visual Studio Code 编辑器的开源扩展",
        "Toolkit for Visual Studio": "面向 Visual Studio 集成开发环境（IDE）的插件",
        "AWS CloudFormation": "使用模板创建和管理资源",
        "AWS Config": "跟踪和评估配置变更",
        "AWS Trusted Advisor": "优化性能和安全性",
        "AWS Account Management": "以组的方式管理你的 AWS 账户",
        "AWS Management Console": "由多个 AWS 服务控制台组成的基于 Web 的用户界面",
        "AWS Organizations": "跨 AWS 账户的集中治理与管理",
        "AWS Service Catalog": "创建和使用标准化产品",
        "AWS Marketplace": "购买或销售运行在 AWS 上的软件",
        "AWS Control Tower": "设置并治理安全合规的多账户环境",
        "AWS CloudTrail": "跟踪和监控用户、角色或 AWS 服务的活动",
        "Amazon CloudWatch": "监控资源和应用程序",
        "AWS License Manager": "跨多个 AWS 区域跟踪和管理软件许可证",
        "AWS Systems Manager": "获取运维洞察并采取行动",
        "AWS Security Hub": "统一的安全与合规中心",
        "AWS IAM Identity Center": "管理对 AWS 账户和应用的单点登录访问",
        "AWS Billing and Cost Management": "提供帮助你支付账单和优化成本的功能",
        "Amazon Managed Grafana": "大规模可视化和分析你的运营数据",
        "Amazon Managed Service for Prometheus": "为你的容器提供高可用、安全的托管监控",
        "AWS Sustainability": "提供一套功能，帮助你了解使用 AWS 服务对环境的影响",
        "AWS Health": "查找可能影响你 AWS 资源的事件信息",
        "AWS Resource Groups": "查看你 AWS 账户中跨区域的资源",
        "Amazon Bedrock": "访问一流的基础模型，构建生成式 AI 应用",
        "Amazon Comprehend": "发现文本中的洞察和关联",
        "Amazon Forecast": "使用机器学习提高预测准确性",
        "Amazon Lex": "构建语音和文本聊天机器人",
        "Amazon Rekognition": "分析图像和视频",
        "Amazon Personalize": "为你的应用构建实时推荐能力",
        "Amazon Polly": "将文本转换为逼真的语音",
        "Amazon Textract": "从文档中提取文本和数据",
        "Amazon SageMaker AI": "大规模构建、训练和部署机器学习模型",
        "Amazon Transcribe": "自动语音识别",
        "Amazon Translate": "自然流畅的语言翻译",
        "AWS Identity and Access Management": "使用 IAM 安全地管理对服务和资源的访问",
        "Amazon Cognito": "为你的应用提供身份管理",
        "AWS Directory Service": "使用 AWS 服务搭建和运行 Microsoft Active Directory",
        "Amazon GuardDuty": "托管式威胁检测服务",
        "Amazon Inspector": "大规模自动化、持续的漏洞管理",
        "Amazon Detective": "调查潜在的安全问题",
        "Amazon Macie": "大规模发现并保护你的敏感数据",
        "Amazon Verified Permissions": "面向自定义应用的权限管理与授权",
        "AWS Artifact": "按需访问 AWS 合规报告",
        "AWS Audit Manager": "审计你的 AWS 使用情况，简化风险与合规评估",
        "AWS Certificate Manager": "预配、管理和部署 SSL/TLS 证书",
        "AWS Private Certificate Authority": "创建私有证书以标识资源并保护数据",
        "AWS CloudHSM": "基于硬件的密钥存储，满足合规要求",
        "AWS Key Management Service": "托管式加密密钥的创建与控制",
        "AWS Secrets Manager": "轮换、管理和检索密钥",
        "AWS Firewall Manager": "只需几步即可跨 VPC 部署网络安全",
        "AWS Network Firewall": "只需几步即可跨 Amazon VPC 部署网络安全",
        "AWS Shield": "DDoS 防护",
        "AWS WAF": "过滤恶意 Web 流量",
        "AWS Resource Access Manager": "简单、安全地共享 AWS 资源",
        "AWS Payment Cryptography": "全托管的支付加密服务",
        "AWS Security Incident Response": "帮助你应对安全事件并获得 CIRT 协助",
        "AWS GovCloud (US)": "将敏感工作负载迁移到云端",
        "Amazon Cloud Directory": "存储数亿个应用专属对象",
        "Amazon AppFlow": "面向 SaaS 应用和 AWS 服务的无代码集成",
        "Amazon Athena": "使用 SQL 查询 Amazon S3 中的数据",
        "Amazon CloudSearch": "托管式搜索服务",
        "Amazon Data Firehose": "全托管的实时流数据投递服务",
        "Amazon DataZone": "借助内置治理能力打通组织边界的数据",
        "Amazon EMR": "托管式 Hadoop 框架",
        "Amazon FinSpace": "存储、编目、准备和分析金融行业数据",
        "Amazon Kinesis": "分析实时视频和数据流",
        "Amazon Managed Service for Apache Flink": "使用 Apache Flink 处理和分析流数据",
        "Amazon Managed Streaming for Apache Kafka": "全托管的 Apache Kafka 服务",
        "Amazon OpenSearch Service": "在 AWS 云中部署、运行和扩展 OpenSearch 集群",
        "Amazon Quick": "快速的商业分析服务",
        "Amazon Redshift": "快速、简单、经济高效的数据仓库服务",
        "Amazon SageMaker": "涵盖全部数据、分析与 AI 能力的统一中心",
        "AWS Clean Rooms": "无需共享原始数据即可协作分析集体数据集",
        "AWS Data Exchange": "在云中查找、订阅并使用第三方数据",
        "AWS Data Pipeline": "面向周期性、数据驱动工作流的编排服务",
        "AWS Entity Resolution": "关联分散在多个应用、渠道和数据存储中的记录",
        "AWS Glue": "简单、可扩展的无服务器数据集成",
        "AWS Lake Formation": "在数天内构建安全的数据湖",
        "Amazon CloudFront": "全球内容分发网络",
        "Amazon Route 53": "高可用且可扩展的域名系统（DNS）Web 服务",
        "Amazon Virtual Private Cloud": "隔离的云资源",
        "AWS App Mesh": "监控和控制微服务",
        "AWS Virtual Private Network": "安全访问你的网络资源",
        "AWS Cloud Map": "面向云资源的服务发现",
        "AWS Direct Connect": "与 AWS 建立专用网络连接",
        "AWS Global Accelerator": "提升全球应用的可用性和性能",
        "Elastic Load Balancing": "将传入流量分发到多个目标",
        "Amazon Application Recovery Controller (ARC)": "为应用灾难恢复迁移流量",
        "Amazon VPC Lattice": "简化服务间的连接、安全性和监控",
        "AWS Verified Access": "无需 VPN 即可安全访问企业应用",
        "Amazon Chime": "轻松无烦恼的会议、视频通话和聊天",
        "Amazon Chime SDK": "实时消息、音频、视频和屏幕共享",
        "Amazon Connect Customer": "全渠道云联络中心",
        "Amazon Pinpoint": "多渠道营销通信",
        "Amazon Simple Email Service": "大规模收发邮件服务",
        "Amazon WorkMail": "安全的电子邮件和日历服务",
        "AWS App Studio": "构建内部应用，实现流程自动化并简化组织活动",
        "AWS AppFabric": "跨 SaaS 应用聚合和分析数据",
        "AWS End User Messaging Push": "面向应用到个人的推送通知服务",
        "AWS End User Messaging SMS": "面向应用到个人的短信服务",
        "AWS End User Messaging Social": "面向应用到个人的 WhatsApp 消息服务",
        "AWS Supply Chain": "借助机器学习驱动的供应链应用降低风险、节省成本",
        "AWS Wickr": "通过端到端加密保护企业通信",
        "AWS Application Discovery Service": "发现本地应用，简化迁移流程",
        "AWS Mainframe Modernization": "迁移、现代化改造、运维和运行大型机工作负载",
        "AWS Migration Hub": "在一个地方跟踪所有迁移进度",
        "AWS Data Transfer Terminal": "用于快速将数据传输到 AWS 的安全物理场所",
        "AWS Transfer Family": "全托管的 SFTP、FTPS 和 FTP 服务",
        "AWS DataSync": "简单、快速的在线数据传输",
        "AWS Schema Conversion Tool": "将源数据库模式（schema）和大部分代码转换为目标兼容格式",
        "AWS Transform": "使用智能体 AI 加速基础设施、应用和代码的转型",
        "AWS Transform MGN": "自动化应用迁移与现代化改造",
        "Amazon Interactive Video Service": "使用 IVS 构建引人入胜的直播体验",
        "AWS Cloud Digital Interface SDK": "将时序关键的非压缩视频工作流迁移到云端",
        "AWS Deadline Cloud": "为渲染项目提供简化的渲染管理和可扩展基础设施",
        "AWS Elemental Inference": "将机器学习模型应用于视频",
        "AWS Elemental MediaConnect": "可靠、安全的直播视频传输",
        "AWS Elemental MediaConvert": "转换基于文件的视频内容",
        "AWS Elemental MediaLive": "转换直播视频内容",
        "AWS Elemental MediaPackage": "视频源发起与打包",
        "AWS Elemental MediaTailor": "视频个性化与商业化变现",
        "AWS Elemental On-Premises": "使用本地软件编码和打包视频资产",
        "AWS IoT Core": "将设备连接到云端",
        "AWS IoT Device Defender": "面向 IoT 设备的安全管理",
        "AWS IoT Device Management": "对 IoT 设备进行入网、组织和远程管理",
        "AWS IoT ExpressLink": "快速、轻松地开发安全的 IoT 设备",
        "AWS IoT FleetWise": "释放车辆数据的价值",
        "AWS IoT Greengrass": "面向设备的本地计算、消息传递与同步",
        "AWS IoT SiteWise": "IoT 数据采集与解读工具",
        "AWS IoT TwinMaker": "通过为现实世界系统创建数字孪生来优化运营",
        "AWS IoT Wireless": "为 LoRaWAN 和 Sidewalk 终端设备提供安全双向通信",
        "FreeRTOS": "面向微控制器的实时操作系统",
        "Amazon Elastic Block Store": "Amazon EC2 的块存储卷",
        "Amazon Elastic File System": "面向 Amazon EC2 的全托管文件系统",
        "Amazon FSx": "启动、运行和扩展功能丰富、高性能的文件系统",
        "Amazon Glacier": "AWS 云中低成本的归档存储",
        "AWS Backup": "跨 AWS 服务的集中式备份",
        "AWS Elastic Disaster Recovery": "面向 AWS 的可扩展、经济高效的应用容灾恢复",
        "AWS Snowball Edge": "在 AWS 与本地之间迁移 PB 级数据，或在边缘处理数据",
        "AWS Storage Gateway": "混合存储集成",
        "AWS App2Container": "将现有应用容器化并迁移",
        "Amazon Elastic Container Registry": "轻松存储、管理和部署容器镜像",
        "Amazon Elastic Container Service": "高度安全、可靠且可扩展的容器运行方式",
        "Amazon Elastic Kubernetes Service": "在 AWS 上运行 Kubernetes，无需自行运维 Kubernetes 集群",
        "Red Hat OpenShift Service on AWS": "云端托管的 OpenShift",
        "AWS Crypto Tools": "无需专业密码学背景也能正确使用加密能力",
        "AWS Signer": "校验 AWS Lambda 与 IoT 设备代码的数字签名",
        "Amazon MWAA": "面向 Apache Airflow 的托管编排服务",
        "Amazon Simple Workflow Service": "构建可跨分布式组件协调工作的应用",
        "AWS B2B Data Interchange": "实现基于 EDI 的 B2B 交易自动化交换",
        "Amazon Location Service": "安全便捷地为应用添加位置数据",
        "Amazon Silk": "打造更快、更流畅的移动浏览体验",
        "AWS Amplify": "构建、部署、托管并管理可扩展的 Web 和移动应用",
        "AWS Amplify (AWS Mobile SDK for Android)": "构建由 AWS 提供支持的原生 Android 应用",
        "AWS AmplifyiOS (AWS Mobile SDK for iOS)": "构建由 AWS 提供支持的原生 iOS 应用",
        "AWS Device Farm": "在 AWS 云中的真实设备上测试 Android、iOS 与 Web 应用",
        "AWS Mobile SDK for Unity": "为使用 Unity 编写的游戏提供可用的 .NET 类",
        "AWS Support": "了解 AWS Support 提供的组件与功能",
        "AWS Diagnostic Tools": "面向 Partner-Led Support 计划合作伙伴的诊断工具",
        "AWS Glossary": "查询 AWS 术语定义",
        "AWS Lifecycle changes": "及时了解 AWS 服务可用性变更",
        "AWS Security Credentials": "了解如何指定 AWS 安全凭证",
        "AWS Service Endpoints": "通过端点以编程方式连接 AWS 服务",
        "Service Quotas reference": "查看 AWS 服务的工作负载配额",
        "Tagging AWS Resources": "以标签形式为 AWS 资源分配元数据",
        "Amazon DCV": "安全连接远程服务器上的图形密集型 3D 应用",
        "Amazon WorkSpaces": "云中虚拟桌面",
        "Amazon WorkSpaces Applications": "将桌面应用安全流式传输到浏览器",
        "Amazon WorkSpaces Core": "与第三方解决方案配合使用的虚拟桌面基础设施",
        "Amazon WorkSpaces Secure Browser": "安全访问内部网站与 SaaS 应用",
        "Amazon WorkSpaces Thin Client": "经济实惠、易于管理的虚拟桌面接入设备",
        "AWS Incident Detection and Response": "为生产工作负载提供主动监控与事件管理",
        "AWS IQ": "寻找 AWS 认证的第三方专家，承接按需项目工作",
        "AWS Managed Services": "面向 AWS 的基础设施运维管理",
        "AWS Professional Services": "为企业云计算落地提供专家协助",
        "AWS re:Post Private": "为组织内部云社区构建专属知识库",
        "AWS Training and Certification": "探索 AWS 学习资源",
        "Amazon Q": "由生成式 AI 驱动的智能助手",
        "AWS Console Mobile Application": "随时随地查看和管理资源以支持事件响应",
        "AWS Sign-In": "登录与登出账户的相关帮助",
        "AWS Flat-Rate Plans": "为集成的 AWS 服务包提供简化计费",
        "AWS Pricing Calculator": "为 AWS 使用场景创建成本估算",
        "Savings Plans": "以灵活定价节省计算用量成本",
        "Amazon GameLift Servers": "简单、快速、高性价比的专用游戏服务器托管",
        "Amazon GameLift Streams": "面向全球设备的高帧率低时延游戏串流",
        "Amazon Lumberyard": "免费的跨平台 3D 游戏引擎（已不再提供二进制分发）",
        "Amazon Managed Blockchain": "创建和管理可扩展的区块链网络",
        "AWS Blockchain Templates": "在 AWS 上快速创建并部署开源区块链框架",
        "Amazon Braket": "加速量子计算研究",
        "AWS Ground Station": "全托管的卫星地面站即服务",
        "AWS Partner Central": "管理 AWS Partner Network（APN）会员身份并访问 AWS 合作伙伴资源",
        "Research and Engineering Studio on AWS": "创建并管理面向科研协作的门户",
        "Amazon Connect Decisions": "面向供应链规划与决策的自适应智能解决方案",
        "Amazon Connect Health": "围绕医疗服务提供者构建的医疗智能体 AI",
        "AWS Cloud Development Kit (AWS CDK)": "使用熟悉的编程语言定义云基础设施",
        "AWS Fault Injection Service": "通过受控实验提升应用的韧性与性能",
        "AWS Infrastructure Composer": "通过可视化构建器设计并构建现代基础设施",
        "AWS Microservice Extractor for .NET": "减少将大型应用改造为微服务的时间与工作量",
        "AWS Toolkit for Microsoft Azure DevOps": "面向托管及本地 Microsoft Azure DevOps 的扩展",
        "Agent Toolkit for AWS": "为 AI 编码代理在 AWS 上构建、部署、管理应用提供工具与护栏",
        "Kiro": "基于规格驱动开发的 AI 编码工具",
        "Porting Assistant for .NET": "将 Microsoft .NET Framework 应用移植到 .NET Core",
        "SDKs and Tools Reference Guide": "查找适用于多个 SDK 和工具的信息参考指南",
        "Toolkit for .NET Refactoring": "减少为 AWS Cloud 重构遗留 .NET 应用的时间与工作量",
        "AWS Deep Learning AMIs": "在 Amazon EC2 上运行深度学习的 AMI",
        "AWS Deep Learning Containers": "用于深度学习的 Docker 镜像",
        "AWS HealthImaging": "管理医学影像数据",
        "AWS HealthLake": "安全地存储、转换、查询和分析健康数据",
        "AWS HealthOmics": "将组学数据转化为洞察",
        "AWS Panorama": "利用边缘计算机视觉改进业务运营",
        "Amazon A2I": "轻松实现对机器学习预测结果的人工审核",
        "Amazon Bedrock AgentCore": "使用任意框架和模型大规模部署与运行智能体",
        "Amazon CodeGuru": "找出代码中开销最大的代码行",
        "Amazon Comprehend Medical": "检测并返回非结构化临床文本中的有用信息",
        "Amazon DevOps Guru": "借助 ML 驱动的云运维提升应用可用性",
        "Amazon Fraud Detector": "更快地检测更多在线欺诈行为",
        "Amazon Kendra": "用机器学习重塑企业搜索",
        "Amazon Machine Learning": "了解 Amazon 机器学习服务",
        "Amazon Monitron": "通过预测性维护和机器学习减少设备意外停机",
        "Amazon Nova": "Amazon Bedrock 的基础模型系列",
        "Amazon Nova Act": "构建和管理可靠的 AI 智能体集群，自动化 UI 工作流",
        "Apache MXNet on AWS": "可扩展的开源深度学习框架",
        "Claude Platform on AWS": "在 AWS 计费和安全性下访问原生 Anthropic 平台",
        "AWS AppConfig": "快速将应用配置部署到任意规模的应用",
        "AWS Command Line Interface": "管理 AWS 服务的命令行工具",
        "AWS Compute Optimizer": "识别最优的 AWS 计算资源",
        "AWS DevOps Agent": "解决并主动预防 AWS 故障的 AI 智能体",
        "AWS Launch Wizard": "在 AWS 上轻松调整、配置和部署第三方应用",
        "AWS Proton": "自动化管理容器和无服务器部署",
        "AWS Resilience Hub": "帮助应用做好应对中断的准备和防护",
        "AWS Resource Explorer": "在 AWS 中搜索和发现相关资源",
        "AWS Security Agent": "主动保护应用安全的 AI 智能体",
        "AWS Service Management Connector": "在 ITSM 工具中预配、管理和运维 AWS 资源",
        "AWS Systems Manager Incident Manager": "缓解并恢复影响 AWS 上托管应用的事件",
        "AWS Telco Network Builder": "自动化部署和管理 AWS 上的电信网络",
        "AWS User Notifications": "统一各 AWS 服务的通知体验",
        "AWS Well-Architected Tool": "审查和改进工作负载",
        "Amazon Data Lifecycle Manager": "自动化管理 Amazon EBS 快照和基于 EBS 的 AMI",
        "Amazon Q Developer in chat applications": "AWS 的 ChatOps",
        "Service Quotas": "大规模查看和管理 AWS 工作负载配额",
        "Tag Editor": "批量添加、编辑或删除 AWS 资源标签",
        "AWS Interconnect": "配置与其他云服务提供商的私有连接",
        "AWS RTB Fabric": "在 AWS 上就近部署实时竞价应用",
        "Amazon Security Lake": "几次点击即可自动集中管理安全数据",
        "Security Documentation": "按分类整理的安全文档",
    },
    "azure": {
        "Virtual Machines": "几秒钟内即可预配 Windows 和 Linux 虚拟机",
        "Linux Virtual Machines": "为 Ubuntu、Red Hat 等系统预配虚拟机",
        "App Service": "快速创建强大的 Web 和移动云应用",
        "Static Web Apps": "从源代码到全球高可用性的一站式全栈开发体验",
        "Azure Spring Apps": "通过微软和 VMware 提供的全托管服务构建和部署 Spring Boot 应用",
        "Batch": "云规模的作业调度与计算管理",
        "Azure Stack Hub": "作为集成硬件系统出售，软件预装在经过验证的硬件上",
        "Azure Stack Edge": "一款将 Azure 的计算、存储和智能能力带到边缘的 Azure 托管设备",
        "Azure VMware Solution": "在 Azure 上原生运行您的 VMware 工作负载",
        "Nutanix Cloud Clusters": "为 Nutanix 工作负载优化成本，简化扩展、灵活性、应用迁移与灾难恢复",
        "Azure Linux": "探索一款由微软维护、针对 Azure 虚拟机和 AKS 工作负载优化的 Linux 发行版",
        "Azure VM Image Builder": "用一款简单易用的工具简化镜像构建流程",
        "Windows Server": "值得信赖的 Windows Server 工作负载云平台",
        "Azure Spot Virtual Machines": "以大幅折扣预配闲置计算容量，运行可中断的工作负载",
        "Azure Dedicated Host": "一台专用于承载您 Windows 和 Linux Azure 虚拟机的专属物理服务器",
        "Azure Database for MySQL": "通过全托管、可扩展的 MySQL 数据库实现现代化",
        "Azure Database for PostgreSQL": "通过全托管、智能且可扩展的 PostgreSQL 数据库实现创新",
        "Azure SQL Database": "使用云中托管的智能 SQL 数据库构建可扩展的应用",
        "Azure SQL Managed Instance": "使用托管且始终保持最新的 SQL 实例实现 SQL Server 应用现代化",
        "Azure SQL": "在现代 SQL 云数据库家族上迁移、现代化并创新",
        "SQL Server on Azure Virtual Machines": "以更低的总体拥有成本（TCO）将 SQL Server 工作负载迁移到云端",
        "Azure HorizonDB": "在一款专为性能打造的新一代 PostgreSQL 云数据库服务上构建和扩展关键业务应用",
        "Azure Cosmos DB": "构建或现代化可扩展的高性能应用",
        "Azure DocumentDB": "构建 AI 驱动的应用，并采用开源、兼容 MongoDB 的引擎",
        "Azure Managed Instance for Apache Cassandra": "通过云中的托管实例实现 Cassandra 数据集群现代化",
        "Azure Managed Redis": "借助最新的 Redis 创新技术，使用全托管的内存数据库",
        "Azure Database Migration Service": "简化向 Azure 的数据迁移",
        "Azure Functions": "通过端到端开发体验执行事件驱动的无服务器代码函数",
        "Azure Container Apps": "使用无服务器容器构建和部署现代应用与微服务",
        "API Management": "安全、大规模地向开发者、合作伙伴和员工发布 API",
        "Event Grid": "大规模场景下的可靠事件投递",
        "Queue Storage": "根据流量有效扩展应用",
        "Notification Hubs": "向任意平台的任意后端发送推送通知",
        "Service Bus": "跨私有云和公有云环境进行连接",
        "Logic Apps": "跨云自动化数据访问与使用",
        "Azure Blob Storage": "大规模可扩展且安全的对象存储",
        "Virtual Machine Scale Sets": "管理和扩展多达数千台 Linux 和 Windows 虚拟机",
        "Azure Compute Fleet": "轻松大规模预配和管理 Azure 计算容量",
        "Azure Container Instances": "通过虚拟机监控程序隔离启动容器",
        "Azure Kubernetes Service (AKS)": "在托管 Kubernetes 上部署和扩展容器",
        "Azure Quantum": "探索当今多样化的量子硬件、软件和解决方案",
        "Azure Virtual Desktop": "随时随地提供安全的远程桌面体验",
        "Cloud Services": "创建高可用、可无限扩展的云应用和 API",
        "SDKs": "获取所需的 SDK 和命令行工具",
        "Azure DevOps": "供团队共享代码、跟踪工作、交付软件的一站式服务",
        "Azure Lab Services": "为课程、培训、黑客马拉松等场景搭建虚拟实验室",
        "Cloud Shell": "通过基于浏览器的 Shell 简化 Azure 管理",
        "Azure Artifacts": "创建、托管并与团队共享软件包",
        "Azure Pipelines": "持续构建、测试并部署到任意平台和云",
        "Azure Monitor": "全面洞察你的应用程序、基础设施和网络",
        "Azure App Testing": "通过高规模负载测试优化应用性能",
        "Microsoft Playwright Testing": "可扩展的端到端现代 Web 应用测试服务",
        "Azure Repos": "获取无限量的云托管私有 Git 仓库",
        "Azure Resource Manager": "简化你管理应用资源的方式",
        "Azure Policy": "大规模实施企业治理与标准",
        "Azure Advisor": "你的个性化 Azure 最佳实践建议引擎",
        "Microsoft Defender for Cloud": "将威胁防护扩展到任意基础设施",
        "Azure Managed Grafana": "将 Grafana 仪表板部署为全托管的 Azure 服务",
        "Azure OpenAI in Foundry Models": "将先进的编程与语言模型应用到各种使用场景",
        "Azure Language in Foundry Tools": "使用 AI 构建能理解、分析和生成人类语言的应用",
        "Azure AI Bot Service": "创建机器人并跨渠道连接",
        "Azure Vision in Foundry Tools": "通过图像和视频分析探索视觉 AI",
        "Azure AI Custom Vision": "轻松为你的独特场景定制最先进的计算机视觉模型",
        "Azure AI Personalizer": "为每位用户提供个性化、相关的体验",
        "Azure Document Intelligence in Foundry Tools": "加速从文档中提取信息",
        "Azure Machine Learning": "使用企业级服务支持端到端的机器学习生命周期",
        "Azure Translator in Foundry Tools": "通过即时的 AI 翻译打破语言障碍",
        "Microsoft Entra ID (formerly Azure AD)": "同步本地目录并启用单点登录",
        "Microsoft Entra External ID": "为客户和合作伙伴个性化并保护对任意应用的访问",
        "Microsoft Sentinel": "云原生 SIEM 与智能安全分析",
        "Azure Information Protection": "随时随地更好地保护你的敏感信息",
        "Azure Key Vault": "保护并掌控密钥和其他机密信息",
        "Azure Cloud HSM": "全托管、客户自有的单租户硬件安全模块，在你的私有虚拟网络中提供安全密钥存储和加密操作",
        "Azure Firewall Manager": "面向全球分布式软件定义边界的集中网络安全策略与路由管理",
        "Azure Firewall": "使用云原生网络安全保护你的 Azure 虚拟网络资源",
        "Azure DDoS Protection": "保护你的 Azure 资源免受分布式拒绝服务（DDoS）攻击",
        "Azure Web Application Firewall": "一项云原生 Web 应用防火墙（WAF）服务，为 Web 应用提供强大防护",
        "Azure Synapse Analytics": "洞察时效无与伦比的无限分析",
        "Azure AI Search": "为数据源、记忆和检索增强生成（RAG）流水线连接智能体到统一上下文层",
        "Microsoft Purview": "治理、保护和管理你的数据资产",
        "HDInsight": "预配云上的 Hadoop、Spark、R Server、HBase 和 Storm 集群",
        "Azure Data Factory": "轻松实现企业级混合数据集成",
        "Azure Data Explorer": "快速、高度可扩展的数据探索服务",
        "Azure Open Datasets": "托管和共享精选开放数据集的云平台，加速机器学习模型开发",
        "Data Lake Analytics": "让大数据变得简单的分布式分析服务",
        "Azure Data Lake Storage": "面向高性能分析的可扩展、安全数据湖",
        "Power BI": "借助 AI 驱动的仪表板和报表，将数据转化为可交互、可分享的洞察",
        "Azure Data Share": "一项简单、安全的服务，用于与外部组织共享大数据",
        "Azure Databricks": "基于 Apache Spark™ 分析设计 AI",
        "Azure Stream Analytics": "对快速流动的流数据进行实时分析",
        "Azure Content Delivery Network": "快速、可靠、覆盖全球的内容分发网络",
        "Azure DNS": "在 Azure 中托管你的域名系统（DNS）域",
        "Azure Virtual Network": "在云中创建你自己的私有网络基础设施",
        "Azure VPN Gateway": "建立安全的跨本地连接",
        "Azure ExpressRoute": "体验快速、可靠的 Azure 专用连接",
        "Azure Front Door": "面向全球用户提供优化体验的现代云 CDN",
        "Azure Private Link": "私密访问托管在 Azure 平台上的服务，让数据始终留在微软网络内",
        "Azure Load Balancer": "为你的应用提供高可用性和网络性能",
        "Azure Network Watcher": "网络性能监控与诊断解决方案",
        "Azure Traffic Manager": "为高性能和高可用性路由传入流量",
        "Azure Bastion": "全托管服务，帮助安全地远程访问你的虚拟机",
        "Azure App Configuration": "快速、可扩展的应用配置参数存储",
        "Azure Virtual WAN": "通过 Azure 优化并自动化分支机构间的连接",
        "Azure Communication Services": "构建多渠道通信体验",
        "Azure Migrate": "通过统一平台简化迁移与现代化改造",
        "Azure Data Box": "借助 Azure Data Box 加速离线数据迁移，无需网络带宽即可快速迁移海量数据集",
        "Azure Files": "简单、安全的无服务器企业级云文件共享",
        "Azure IoT Hub": "连接、监控和管理数十亿个 IoT 资产",
        "Azure IoT Edge": "将云端智能和分析能力延伸到边缘设备",
        "Azure IoT Central": "从概念验证走向价值验证",
        "Azure Digital Twins": "使用 IoT 空间智能创建物理环境的模型",
        "Azure Disk Storage": "高性能、高持久性的块存储",
        "Archive Storage": "业界领先的低价存储方案，适合不常访问的数据",
        "Azure Backup": "通过内置的大规模备份管理简化数据保护",
        "Azure Site Recovery": "借助内置的容灾恢复服务保障业务持续运行",
        "Azure Container Registry": "构建、存储、保护和复制容器镜像与制品",
        "Azure Red Hat OpenShift": "在托管的 Red Hat OpenShift 上部署和扩展容器",
        "Azure Maps": "为业务应用与解决方案添加位置数据与地图可视化",
        "Azure DevTest Labs": "使用可复用的模板与制品快速创建环境",
        "AI Anomaly Detector": "在应用中轻松加入异常检测能力。",
        "Azure AI Immersive Reader": "帮助各年龄段和不同能力的用户阅读并理解文本。",
        "Azure AI Metrics Advisor": "监控指标并诊断问题的 AI 服务。",
        "Azure AI Video Indexer": "借助媒体 AI 从音频和视频文件中提取有价值的洞察。",
        "Azure Content Understanding in Foundry Tools": "加速多模态 AI 智能体的开发。",
        "Azure SRE Agent": "通过自主事件缓解与资源优化智能体，自动化重复任务并改进事件响应。",
        "Azure Speech in Foundry Tools": "为应用和智能体提供预构建、可定制的多语言语音 AI 模型。",
        "Content Safety in Foundry Control Plane": "自动审核图像、文本和视频内容。",
        "Data Science Virtual Machines": "为 AI 开发提供丰富的预配置环境。",
        "Foundry Agent Service": "创建可自动化复杂业务流程的 AI 智能体，同时由人来掌控。",
        "Foundry Control Plane": "在整个组织内观测、控制、保护和治理 AI 智能体。",
        "Foundry IQ": "为智能体解锁组织数据知识，交付更优结果。",
        "Foundry Models": "帮助你为每个使用场景找到最合适的模型。",
        "Foundry Tools": "使用可定制的工具、API 和模型构建可上市的 AI 应用。",
        "Health Bot": "专为开发虚拟医疗健康助手而打造的托管服务。",
        "Microsoft Foundry": "AI 应用与智能体工厂。",
        "Microsoft Planetary Computer Pro": "将地理空间数据与企业 AI 和分析结合，助力业务决策。",
        "Microsoft Security Copilot": "由生成式 AI 驱动的安全助手，以 AI 的速度与规模提供防护。",
        "Observability in Foundry Control Plane": "通过端到端监控、追踪和评估，观测并优化 AI 应用与智能体。",
        "Phi open models": "一系列低成本、低延迟、性能出色的小型语言模型（SLM）。",
        "Azure Analysis Services": "企业级分析引擎即服务。",
        "Azure Chaos Studio": "通过故障注入模拟中断，提升应用韧性。",
        "Data Catalog": "从企业数据资产中获取更多价值。",
        "Event Hubs": "接收来自数百万台设备的遥测数据。",
        "Microsoft Fabric": "在统一的 AI 驱动平台上连接所有数据源与分析服务，重塑数据访问、管理与洞察。",
        "Microsoft Graph Data Connect": "安全的高吞吐连接器，将 Microsoft 365 生产力数据集复制到 Azure 租户。",
        "Power BI Embedded": "白标 Power BI，在自有应用中快速提供面向客户的仪表板和分析。",
        "App Configuration": "面向应用配置的快速、可扩展参数存储。",
        "Azure Container Storage": "为有状态容器应用管理持久卷。",
        "Azure Kubernetes Fleet Manager": "大规模管理 Kubernetes 集群。",
        "Azure confidential ledger": "基于可信执行环境的防篡改数据存储，保护数据安全。",
        "Table Storage": "基于半结构化数据集的 NoSQL 键值存储。",
        "Azure Boards": "跨团队规划、跟踪和讨论工作。",
        "Azure Deployment Environments": "使用基于项目的模板快速搭建应用基础设施环境。",
        "Azure Test Plans": "借助探索式测试工具包自信地测试和交付。",
        "DevOps tool integrations": "在 Azure 上使用你喜爱的 DevOps 工具。",
        "GitHub Advanced Security": "帮助开发者更快修复安全问题，降低整体安全风险。",
        "GitHub Advanced Security for Azure DevOps": "从开发之初到交付全程安全开发。",
        "GitHub Copilot": "广泛采用的 AI 开发者工具，提升软件开发速度并激发持续创新。",
        "Github Enterprise": "借助 GitHub Enterprise 与 Microsoft Azure 实现大规模创新。",
        "Microsoft Dev Box": "云端安全、开箱即用的开发工作站，简化开发流程。",
        "Artifact Signing": "面向代码、文档、应用等的全托管端到端签名服务，保护应用安全。",
        "Visual Studio": "功能强大且灵活的环境，用于在云端开发应用。",
        "Visual Studio Code": "功能强大、轻量级的云开发代码编辑器。",
        "Azure Arc": "在任何地方保护、开发和运维基础设施、应用与 Azure 服务。",
        "Azure Local": "在云连接的分布式基础设施上随处运行生产工作负载。",
        "Azure Operator Nexus": "面向关键任务移动网络应用的混合平台，支持容器化和虚拟化网络功能部署。",
        "Azure Operator Service Manager": "简化复杂运营商服务的部署、升级和管理。",
        "Microsoft Entra Domain Services": "在云中管理域控制器。",
        "Microsoft Entra Verified ID": "构建用户自主拥有的身份场景，实现可信、安全、高效的交互。",
        "Azure Health Data Services": "在云端统一并管理健康数据与受保护健康信息（PHI）。",
        "Azure Web PubSub": "基于 WebSockets 与发布-订阅模式构建实时消息 Web 应用。",
        "Microsoft Energy Data Services": "加速能源数据现代化与数字化转型进程。",
        "Azure IoT Operations": "借助 Azure Arc 实现本地智能行动与全局可见性的洞察。",
        "Azure Sphere": "创建、连接并维护从边缘到云端的安全智能 IoT 设备。",
        "Windows for IoT": "以企业级安全与长期支持构建智能边缘解决方案。",
        "Automation": "通过流程自动化简化云管理。",
        "Azure Automanage": "自动化管理云端与本地基础设施。",
        "Azure Blueprints": "快速、可重复地创建受治理的环境。",
        "Azure Copilot": "通过 AI 助手汇聚 Azure 智能体的集体智慧。",
        "Azure Lighthouse": "助力服务提供商大规模、精细化地管理客户。",
        "Azure Managed Applications": "简化云端产品服务的管理。",
        "Azure Resource Manager templates": "以基础设施即代码方式交付所有 Azure 资源。",
        "Azure Resource Mover": "简化在 Azure 区域之间迁移多个资源的流程。",
        "Defender External Attack Surface Management": "发现所有暴露于互联网的资源，守护数字体验安全。",
        "Microsoft Cost Management": "以透明、准确、高效的方式监控、分配并优化云成本。",
        "Update management center": "大规模集中管理更新与合规性。",
        "Content Delivery Network": "全球覆盖的快速可靠内容分发网络。",
        "Azure Storage Mover": "将本地或其他云的数据安全、可扩展地迁移到 Azure。",
        "Azure Application Gateway": "在 Azure 中构建安全、可扩展、高可用的 Web 前端。",
        "Azure NAT Gateway": "提供高可靠、安全、可扩展的互联网出站连接。",
        "Azure Network Function Manager": "在边缘设备上部署 5G 与 SD-WAN 网络功能并扩展 Azure 管理。",
        "Azure Route Server": "使网络设备能够与 Azure 虚拟网络动态交换路由。",
        "Azure Virtual Network Manager": "通过单一窗格集中管理 Azure 中的虚拟网络。",
        "Microsoft Azure Attestation": "统一远程验证平台可信度及其内部二进制文件的完整性。",
        "Microsoft Defender External Attack Surface Management": "发现并管理所有暴露于互联网的资源，保护数字体验安全。",
        "Azure Elastic SAN": "基于 Azure 的云原生存储区域网络（SAN）服务，提供类似本地 SAN 的端到端体验。",
        "Azure Managed Lustre": "全托管的云端并行文件系统，支持在云中运行高性能计算（HPC）工作负载。",
        "Azure NetApp Files": "由 NetApp 提供支持的企业级 Azure 文件共享服务。",
        "Azure Storage Actions": "简化大规模存储数据管理。",
        "Azure Storage Discovery": "通过存储监控获取存储可见性与洞察，优化数据策略。",
        "Storage Accounts": "持久、高可用、可大规模扩展的云存储。",
        "Storage Explorer": "查看和管理 Azure Storage 资源。",
        "Azure Fluid Relay": "借助 Fluid Framework 为应用添加实时协作体验。",
        "Azure SignalR Service": "轻松为 Web 应用添加实时功能。",
    },
    "gcp": {
        "Compute Engine": "一项让您能够在 Google 基础设施上创建和运行虚拟机的计算与托管服务",
        "App Engine": "让用户能够在 Google 基础设施上构建和托管 Web 应用",
        "Batch": "全托管的批处理服务，可大规模调度、排队和执行作业",
        "Cluster Toolkit": "Google 提供的开源软件，可轻松在 Google Cloud 上部署高性能计算（HPC）环境",
        "Cluster Director documentation": "了解 Cluster Director，一项简化部署和管理 AI 或 HPC 优化集群的托管服务",
        "Google Distributed Cloud": "将 Google Cloud 基础设施和服务扩展到边缘的全托管软硬件解决方案",
        "Google Distributed Cloud connected": "在客户本地部署的专用硬件上执行 Kubernetes 工作负载",
        "Google Distributed Cloud (software only) for bare metal": "在使用 Google Cloud 功能的同时，在自有本地环境中创建、管理和升级 GKE 集群，并大规模部署和运行容器化应用",
        "Google Distributed Cloud (software only) for VMware": "为本地容器化应用预配并管理底层资源",
        "Google Cloud VMware Engine": "一项让您能够在 Google Cloud 中运行 VMware 平台的全托管服务",
        "Container-Optimized OS": "一款针对运行容器进行优化的 Compute Engine 操作系统镜像",
        "Deep Learning VM Images": "一款针对深度学习应用和高性能计算优化的 Compute Engine 虚拟机",
        "Cloud SQL": "全托管且高可用的关系型数据库即服务",
        "Cloud SQL for MySQL documentation": "一项全托管数据库服务，帮助您在 Google Cloud 上设置、维护、管理和运维 MySQL 关系型数据库",
        "Cloud SQL for PostgreSQL": "一项全托管数据库服务，帮助您在 Google Cloud 上设置、维护、管理和运维 PostgreSQL 关系型数据库",
        "Cloud SQL for SQL Server documentation": "一项托管数据库服务，帮助您在 Google Cloud 上设置、维护、管理和运维 SQL Server 数据库",
        "AlloyDB for PostgreSQL": "一款下一代兼容 PostgreSQL 的数据库，为希望摆脱专有数据库的客户以及有高要求的 PostgreSQL 用户提供强大的现代化选项",
        "AlloyDB Omni": "AlloyDB for PostgreSQL 的可下载版本，可在数据中心、笔记本电脑、边缘及任意云环境中运行",
        "Spanner": "一项托管的、面向关键业务、全局一致且可扩展的关系型数据库服务",
        "Spanner Omni": "Spanner 的可下载自托管版本（预览版）",
        "Firestore in Native mode": "一款云托管的 NoSQL 数据库，足够简单以支持快速原型开发，同时也足够可扩展和灵活以应对任意规模的增长",
        "Firestore with MongoDB compatibility": "一款云托管的 NoSQL 数据库，足够简单以支持快速原型开发，同时也足够可扩展和灵活以应对任意规模的增长",
        "Datastore": "一款面向 Web 和移动应用的高可扩展 NoSQL 数据库，自动处理分片和复制",
        "Bigtable": "一项面向大规模分析和运营工作负载的高性能 NoSQL 数据库服务，可在任意规模下提供低延迟和高吞吐量",
        "Memorystore for Redis": "一项 Google Cloud 全托管 Redis 服务，让应用无需承担管理复杂 Redis 部署的负担即可使用高可扩展、高可用、安全的 Redis 服务",
        "Memorystore for Redis Cluster": "一项 Google Cloud 全托管 Redis Cluster 服务，让应用无需承担管理复杂 Redis Cluster 部署的负担即可使用高可扩展、高可用、安全的 Redis 服务",
        "Memorystore for Memcached": "一项 Google Cloud 全托管 Memcached 服务，让应用无需承担管理复杂 Memcached 部署的负担即可使用高可扩展、高可用、安全的 Memcached 服务",
        "Memorystore for Valkey": "一项 Google Cloud 全托管 Valkey Cluster 服务",
        "Oracle Database at Google Cloud": "在运行 Oracle Cloud Infrastructure（OCI）Exadata 硬件的 Google Cloud 数据中心内部署您的 Oracle 数据库服务",
        "Oracle on Google Cloud Compute": "在 Google Cloud 上运行 Oracle 工作负载",
        "Database Migration Service": "帮助企业更轻松地将 MySQL 和 PostgreSQL 工作负载平滑迁移到 Cloud SQL",
        "Cloud Run functions": "小型、单一用途的函数",
        "Cloud Run": "一个全托管的应用平台，可在 Google 高度可扩展的基础设施之上运行您的代码、函数或容器",
        "API Gateway": "通过在所有服务间保持一致的、定义良好的 REST API，为您的后端服务提供安全访问",
        "Cloud Endpoints": "一套 API 管理系统，帮助您保护、监控、分析 API 并为其设置配额",
        "Eventarc": "构建事件驱动架构，无需实现、定制或维护底层基础设施",
        "Cloud Tasks": "通过队列和工作服务，让开发者能够管理大量分布式任务（小型异步计算工作单元）",
        "Workflows": "创建和管理无服务器工作流",
        "Cloud Storage": "在 Google Cloud 中实现全球范围的数据存储与检索",
        "AI Hypercomputer": "一套集成了性能优化硬件、开源软件、主流机器学习框架和灵活消费模式的系统",
        "Capacity Planner": "让您了解项目中虚拟机实例资源（包括 vCPU、内存和本地 SSD）的使用情况",
        "Confidential VM": "利用现代 CPU 和机密计算云服务提供的先进安全技术，实现使用中数据的加密",
        "Dual Run": "在现有大型机环境和 Google Cloud 上同时运行工作负载，进行实时测试并快速收集性能与稳定性数据",
        "GPU machine types": "了解支持 GPU 加速工作负载（如机器学习、数据处理和图形处理）的实例选项",
        "Google Cloud Hyperdisk overview": "了解 Hyperdisk 的容量和性能限制、区域可用性以及支持的机器类型",
        "Mainframe Assessment Tool": "自动分析遗留大型机应用，帮助您将其迁移到 Google Cloud",
        "Mainframe Connector": "帮助从大型机导出数据、批量上传到 Google Cloud（通过 Cloud Storage）并导入 BigQuery",
        "Migrate to Containers": "将基于虚拟机的工作负载转换为 Google Kubernetes Engine（GKE）中的容器",
        "Migrate to Virtual Machines": "专为迁移到 Google Cloud 打造的企业级迁移方案",
        "Migration Center": "统一管理迁移到 Google Cloud 过程中使用的各类工具",
        "Persistent Disk": "了解 Persistent Disk 卷及其容量、存储接口类型，以及在 Compute Engine 中的实现方式",
        "Shielded VM": "为 Compute Engine 虚拟机实例提供可验证的完整性，帮助抵御 rootkit 和 bootkit",
        "VM Manager": "一套用于管理大规模虚拟机集群（运行 Windows 和 Linux，基于 Compute Engine）操作系统的工具",
        "Workload Manager": "提供基于规则的验证服务，用于评估在 Google Cloud 上运行的工作负载",
        "Cloud Code": "云原生开发所需的工具，现已集成 Gemini Code Assist，支持你喜爱的操作系统、IDE、语言和云平台",
        "Cloud Workstations": "提供安全的云端托管开发环境的托管服务",
        "Cloud Shell": "通过命令行访问 Google Cloud 项目和资源",
        "Cloud Build": "在快速、一致且可靠的环境中运行你的构建",
        "Cloud Deploy": "创建可靠的软件交付流水线，自动化多个目标环境间的应用部署",
        "Cloud Trace": "一套分布式追踪系统，收集应用的延迟数据并在 Google Cloud 控制台中展示",
        "Cloud Source Repositories": "全托管的私有 Git 仓库，集成持续集成、交付与部署能力",
        "Artifact Registry": "管理所有构建产物和依赖项的通用包管理器",
        "Cloud Deployment Manager": "使用这项基础设施部署服务自动创建和管理 Google Cloud 资源",
        "Security Command Center": "基于云的风险管理解决方案，帮助安全专业人员预防、检测和响应安全问题",
        "Recommender": "为 Google Cloud 服务及其资源提供优化建议",
        "Cloud Asset Inventory": "一项全局清单服务，用于查看、搜索、导出、监控和分析你的 Google Cloud 资产元数据",
        "Cloud Billing": "一套工具集，帮助你跟踪和了解 Google Cloud 支出、支付账单并优化成本",
        "Cloud Identity": "统一的身份、访问、应用与终端管理（IAM/EMM）平台",
        "Cloud Logging": "一项全托管服务，可存储、搜索、分析、监控日志数据并设置告警",
        "Cloud Monitoring": "收集指标数据，并提供工具让你监控和可视化应用及服务的运行表现",
        "Advisory Notifications": "在 Cloud Console 中提供有针对性、及时且合规的安全与隐私事件通知",
        "Cloud Scheduler": "全托管的 cron 服务，用于调度批处理、大数据作业及云基础设施操作等任务",
        "Carbon Footprint": "查看并导出与你的 Google Cloud 工作负载相关的碳足迹数据",
        "Cloud Natural Language API": "让开发者轻松将 Google 自然语言理解技术集成到应用中",
        "Dialogflow CX": "提供适用于大型或高度复杂智能体的高级对话式智能体服务",
        "Dialogflow ES": "提供适用于小型简单智能体的标准对话式智能体服务",
        "Cloud Vision API": "轻松将视觉检测功能集成到应用中",
        "Vision API Product Search": "帮助零售商基于一组参考图片创建能从多个视角直观描述商品的产品集",
        "Cloud Text-to-Speech": "通过强大的神经网络模型合成自然流畅的语音",
        "Document AI": "在单一云端平台上使用机器学习自动分类、提取并丰富文档中的数据，挖掘洞察",
        "Cloud Speech-to-Text": "在应用中使用 Google 的语音识别技术将音频转录为文本",
        "Cloud Translation": "支持以编程方式与 Google 翻译集成",
        "Identity Platform": "提供后端服务、SDK 和 UI 库，让你的应用和服务更容易实现用户身份验证",
        "Sensitive Data Protection": "发现、分类并对 Google Cloud 内外的敏感数据进行去标识化处理",
        "Identity and Access Management (IAM)": "精细化的访问控制，集中管理云资源的可见性",
        "Certificate Authority Service": "一项高可用、可扩展的 Google Cloud 服务，帮助组织简化私有证书颁发机构（CA）的部署与管理",
        "Cloud HSM": "让你能够在硬件安全模块（HSM）集群中托管加密密钥并执行加密操作",
        "Cloud Key Management Service": "为兼容的 Google Cloud 服务及你自己的应用创建和管理加密密钥",
        "Secret Manager": "密钥与凭据管理服务，用于存储和管理 API 密钥、用户名、密码和证书等敏感数据",
        "Google Cloud Armor": "利用 Google 的全球基础设施和安全系统，防护你的服务免受拒绝服务和 Web 攻击",
        "BigQuery": "一个全托管、PB 级的分析型数据仓库，可对海量数据进行近实时分析",
        "Cloud Data Fusion": "一项基于 CDAP 构建的全托管服务，用于在 Google Cloud 上构建和管理数据管道",
        "Cloud Dataflow": "一项全托管服务，以同等的可靠性和表达能力对流式和批处理数据进行转换与增强",
        "Looker": "一个面向商业智能、数据应用和嵌入式分析的企业平台",
        "Knowledge Catalog": "一个统一的智能治理解决方案，面向数据和 AI 资产，支撑大规模的 AI、分析与商业智能",
        "Cloud CDN": "一项低延迟、低成本的内容分发网络，利用 Google 全球分布的边缘节点就近缓存内容",
        "Cloud DNS": "借助 Google 全球网络提供的可靠、稳健、低延迟 DNS 服务，让你的应用和服务面向用户可用",
        "Virtual Private Cloud": "为你的 Google Cloud 资源提供托管网络功能",
        "Cloud VPN": "使用 IPsec VPN 隧道将对端网络连接到你的虚拟私有云（VPC）网络",
        "Cloud Interconnect": "面向你的 Google 虚拟私有云网络的企业级连接",
        "Cloud Load Balancing": "让你的资源可以通过单一 IP 地址对外部或 VPC 内部提供访问",
        "Network Intelligence Center": "面向 Google Cloud 的网络性能监控与诊断",
        "Network Connectivity Center": "Google Cloud 上采用中心辐射模型的网络连接管理方案",
        "Identity-Aware Proxy": "通过验证用户身份，控制对运行在 Google Cloud 上的应用和虚拟机的访问",
        "Transfer Appliance": "一款硬件设备，让你能够在不中断业务运营的情况下捕获数据并安全迁移到 Google Cloud",
        "Storage Transfer Service": "将你的数据从一个云迁移到另一个云",
        "Transcoder API": "为广播公司、制作公司及其他媒体企业将视频转码为现代及下一代格式",
        "Live Stream API": "为广播公司、制作公司及其他媒体企业将直播线性视频流转码为现代及下一代格式",
        "Filestore": "在 Google Cloud 上创建全托管的 NFS 文件服务器",
        "Backup and DR": "托管服务，为运行在 Google Cloud 上的工作负载提供备份和恢复",
        "Google Kubernetes Engine documentation": "部署、管理和扩展基于 Kubernetes 的容器化应用，由 Google Cloud 提供支持",
        "Managed Service for Apache Airflow": "Google Cloud 上全托管的 Apache Airflow 调度与编排服务",
        "Blockchain Node Engine": "托管区块链节点即服务",
        "AI Commerce Search in Gemini Enterprise for Customer Experience": "基于 ML 模型为网站和移动应用提供个性化搜索与推荐。",
        "Agent Assist": "利用 Google ML 技术，在客服与客户交互时实时提供辅助信息。",
        "Agent Platform Vision": "AI 驱动的视频数据摄取、分析与存储平台，支持快速构建和部署应用。",
        "Agent Registry": "用于发现和注册 Agent 及 MCP 服务器的集中式目录。",
        "Agent Studio overview": "Agent Studio 概览：发现模型、工程化提示词并在 Agent Platform 中构建 AI Agent。",
        "Anti Money Laundering AI": "基于客户数据和训练标签构建定制化反洗钱风险模型的 ML 引擎。",
        "Cloud Speech-to-Text documentation": "在应用中使用 Google 语音识别技术将音频转写为文字的文档。",
        "Cloud TPU": "Google 自研 ASIC 芯片，用于加速机器学习工作负载。",
        "Colab Enterprise": "零配置的协作式 Notebook，具备企业级安全与功能。",
        "Customer Experience Insights": "通过语言处理识别来电原因与情绪，帮助呼叫中心改善客户交互。",
        "Deep Learning Containers": "预装优化的深度学习容器，支持 TensorFlow、PyTorch 和 scikit-learn 应用开发与部署。",
        "Enterprise Knowledge Graph": "整合、标准化孤岛数据，将其转化为可用的组织知识。",
        "Gemini Cloud Assist": "覆盖应用设计、部署、监控、排障到性能与成本优化的全生命周期 AI 助手。",
        "Gemini Code Assist Standard and Enterprise overview": "Gemini Code Assist 概览：以 AI 辅助开发团队构建、部署和运维应用。",
        "Gemini Enterprise": "基于 Google 级搜索与 Gemini 能力的云端 AI Agent 套件，重塑知识工作。",
        "Gemini Enterprise Agent Platform": "面向平台与安全管理员的中央控制台，用于构建、扩展、监控和治理 AI Agent 全生命周期。",
        "Gemini for Google Cloud": "嵌入 Cloud Console 的大语言模型接口，提供代码辅助、代码生成与对话能力。",
        "Google Cloud Contact Center as a Service": "AI 驱动的一体化联络中心平台，与 CRM 协同提供统一的客户旅程视图。",
        "Overview of getting inferences on Agent Platform": "使用 Gemini Enterprise Agent Platform 获取在线与批量推理的概览。",
        "TensorFlow Enterprise": "为关键 AI 工作负载提供企业级支持、优化性能与托管服务。",
        "Translation Hub": "面向大批量、多语种文档翻译的自助式翻译服务。",
        "Video Intelligence API": "分析视频内容，检测实体、标记成人内容并识别场景切换。",
        "Video Stitcher API": "动态生成点播视频内容并分发至客户端设备。",
        "API Keys API Documentation": "管理开发者项目关联 API 密钥的文档。",
        "Apigee": "Google Cloud 旗下平台，帮助企业设计、保护并扩展 API。",
        "App Hub": "在单一平台上创建、构建和管理应用。",
        "Application Design Center": "设计并共享可部署的应用架构。",
        "Application Integration": "iPaaS 集成平台，连接并管理应用与数据。",
        "Artifact Analysis": "为 Google Cloud 上的容器提供漏洞扫描和元数据存储。",
        "Cloud Healthcare API": "在 Google Cloud 中管理医疗健康数据。",
        "Developer Connect": "集中式 DevOps 集成，降低配置开销并支持跨项目协作。",
        "Integration Connectors": "从企业集成中连接各种数据源。",
        "Secure Source Manager": "Git 源码管理系统，支持 PR、问题跟踪、区域化和 IAM 集成。",
        "Service Infrastructure": "提供身份认证、日志、监控、网络、计费和配额管理。",
        "Service Usage": "列出并管理 Google Cloud 项目中的 API 和服务。",
        "App Lifecycle Manager": "简化在 Google Cloud 上构建、扩缩和运维应用。",
        "Blockchain RPC": "通过原生 RPC API 对多条区块链进行读写访问的服务。",
        "Buildpacks": "将应用源代码转换为安全、快速、可复用的容器镜像。",
        "Config Controller": "以声明式 Kubernetes 模型创建和管理 Google Cloud 资源。",
        "Config Sync": "将集群持续同步到存储在 Git 中的集中式配置。",
        "Cloud Customer Care": "简化并优化 Google Cloud 的支持体验。",
        "Cloud Hub": "Google Cloud 应用与资源的集中式数据和洞察。",
        "Config Connector": "通过 Kubernetes API 管理 Cloud Spanner、Cloud Storage 等资源。",
        "Device Streaming API documentation": "安全连接 Google 数据中心托管的远程 Android 真机进行应用测试的文档。",
        "Infrastructure Manager": "自动化部署和管理 Google Cloud 基础设施资源的托管服务。",
        "Managed Service for Microsoft Active Directory": "由 Google Cloud 托管的高可用 Microsoft Active Directory 服务。",
        "Service Catalog": "在云组织中向内部企业用户管理和共享解决方案。",
        "Blockchain Analytics": "提取自主流区块链的数据集，用于探索链上交易数据。",
        "Data Studio": "免费的数据报表工具，提供易用的拖拽式编辑器。",
        "Dataform": "帮助数据团队在 BigQuery 中构建、版本控制和编排工作流。",
        "Datastream": "无服务器的变更数据捕获（CDC）与复制服务。",
        "Google Cloud Cortex Framework": "提供数据集成、处理与可视化的参考架构、预置工具和 ML 模板。",
        "Google Cloud Data Agent Kit extension documentation": "Google Cloud Data Agent Kit IDE 扩展的文档，可在 IDE 中连接并使用云端数据资源。",
        "Introduction to BigQuery migration": "将数据仓库迁移到 BigQuery 的完整解决方案介绍。",
        "Looker documentation": "Looker 文档：商业智能、数据应用与嵌入式分析平台，助您探索、共享和可视化数据。",
        "Managed Service for Apache Spark": "全托管云服务，以简单、经济的方式运行 Spark 集群。",
        "Manufacturing Data Engine": "端到端解决方案，提供可扩展的工厂到云端数据接入，配置极简。",
        "Database Center overview": "Database Center 概览：AI 辅助的仪表板，用于监控和管理 Google Cloud 数据库舰队健康。",
        "What is AlloyDB AI": "AlloyDB AI 介绍：在 AlloyDB for PostgreSQL 中集成生成式 AI 能力，含向量搜索与自然语言转 SQL。",
        "Cloud Location Finder": "Google Cloud 云区域位置的权威信息来源。",
        "Service Directory": "统一注册与发现服务的平台，与环境和部署方式无关。",
        "Telecom Network Automation": "基于开源项目 Nephio 的托管云实现，面向电信网络自动化。",
        "Certificate Manager": "为 Cloud Load Balancing 集中管理 SSL 证书。",
        "Cloud Domains": "通过 Google Cloud 注册和管理域名。",
        "Cloud Intrusion Detection System": "监控网络并在检测到恶意活动时告警，由 Palo Alto Networks 提供支持。",
        "Cloud NAT": "为 Google Cloud 提供全托管的软件定义网络地址转换（NAT）。",
        "Cloud Router": "在云网络与本地网络之间建立 BGP 会话。",
        "Cloud Service Mesh": "Google Cloud 的服务网格方案，简化、管理并保护复杂微服务架构。",
        "Media CDN": "面向流媒体的全球边缘网络，依托 Google 遍布全球的边缘缓存。",
        "Network Service Tiers": "按性能或成本优化网络。",
        "Secure Access Connect": "将安全服务边缘（SSE）产品接入 Google Cloud，实现安全处理与安全上网出口。",
        "Secure Web Proxy": "通过显式代理保护 HTTP/S 出站流量。",
        "Service Extensions": "边缘可扩展产品，可在 Media CDN 的请求/响应处理路径中部署自定义代码。",
        "VPC Service Controls": "为 Google 托管服务资源定义安全边界，控制服务间通信。",
        "Agent observability": "介绍 Google Cloud 如何支持智能体可观测性。",
        "Cloud Profiler": "低开销的统计型性能分析器，持续收集生产应用的 CPU 占用与内存分配信息。",
        "Error Reporting": "聚合并展示运行在 Google Cloud 上的应用所产生的错误。",
        "Fault Injection Testing": "主动向系统注入故障，提前验证其韧性，避免影响客户的真实故障。",
        "Google Cloud Observability": "一组帮助了解应用行为、健康状况和性能的可观测性服务。",
        "Google Cloud Observability documentation": "了解应用及其运行系统的行为、健康与性能的可观测性服务文档。",
        "Access Approval": "控制并审批 Google 人员访问贵组织数据的权限。",
        "Access Context Manager": "允许企业根据请求属性配置访问级别并映射到策略。",
        "Access Transparency": "记录 Google 人员访问客户存储在 Google Cloud 数据时的操作。",
        "Assured Open Source Software": "托管服务，让企业开发者使用与 Google 相同的 OSS 包到工作流中。",
        "Assured Workloads": "保护您的工作负载，加速在 Google Cloud 上运行合规工作负载。",
        "Binary Authorization": "为 Kubernetes Engine、Cloud Run 和 Distributed Cloud 应用提供集中的软件供应链安全。",
        "Cloud External Key Manager": "使用在受支持的 EKM 中托管的外部密钥的 Google Cloud 服务。",
        "Cloud Next Generation Firewall": "完全分布式、云原生的防火墙服务，无需重构网络即可实现微分段等精细控制。",
        "Cyber Insurance Hub": "评估组织安全态势，并对接保险伙伴获取 Google Cloud 专属网络安全保险。",
        "Endpoint Verification": "为访问组织数据的 Chrome OS 设备和 Chrome 浏览器建立清单。",
        "Google Cloud Fraud Defense": "保护网站和移动应用免受垃圾信息与滥用的服务。",
        "Google Security Operations": "让安全团队集中存储和分析安全数据，并检测、调查和响应威胁。",
        "Google Threat Intelligence": "为组织提供领先的主动威胁检测能力。",
        "Personalized Service Health": "查看和管理 Google Cloud 服务健康事件、回顾历史事件并准备计划内维护。",
        "Policy Intelligence": "帮助理解和管理策略、主动改善安全配置的一套工具。",
        "Resource Manager": "以编程方式管理 Google Cloud 中组织与项目的访问控制和配置。",
        "Sovereign Controls by Partners": "通过合作伙伴运营的主权控制满足 Google Cloud 的数字主权要求。",
        "Unified Maintenance": "统一管理 Google Cloud 各服务的计划内维护。",
        "Web Risk": "让客户端应用对照 Google 持续更新的不安全网址列表检查 URL。",
        "Parallelstore": "分布式异步对象存储，提供高带宽和高 IOPS。",
    },
    "alibaba": {
        "ACK One": "提供控制面，管理跨裸金属和云的 Kubernetes 集群",
        "AIRec": "为应用提供高质量个性化推荐",
        "API Gateway": "向用户开放数据与服务",
        "ActionTrail": "维护安全与合规",
        "Alibaba Cloud CDN": "加速文件分发到终端用户",
        "Alibaba Cloud DNS": "管理 DNS 设置",
        "Alibaba Cloud PrivateZone": "私有域名管理服务",
        "Alibaba Cloud Service Mesh": "跨多集群的微服务统一流量管理",
        "Alibaba Cloud ZStack": "下一代开源混合云解决方案",
        "Alibaba Mail": "基于公有云的邮件服务",
        "Alibaba eKYC": "快速部署自定义 eKYC 解决方案以满足交付要求",
        "AlibabaMQ for Apache RocketMQ": "分布式消息队列服务",
        "AliwareMQ for IoT": "面向 IoT 和移动设备的消息服务",
        "AnalyticDB for MySQL": "优化的实时数仓",
        "AnalyticDB for PostgreSQL": "在线数据仓库服务",
        "Anti-Bot Service": "Bot 防御，减少自动化攻击",
        "Anti-DDoS": "防护大流量 DDoS 攻击",
        "Application Configuration Management": "集中管理应用配置",
        "Application High Availability Service": "保障应用高可用",
        "Application High availability": "保障应用高可用",
        "Application Real-Time Monitoring Service": "构建业务监控能力",
        "Apsara File Storage NAS": "面向 ECS、HPC、容器的文件存储",
        "Apsara Stack": "在本地部署阿里云服务",
        "ApsaraDB RDS for MariaDB": "功能完备的 MariaDB 托管数据库",
        "ApsaraDB RDS for MySQL": "稳定可靠的 MySQL 托管数据库",
        "ApsaraDB RDS for PostgreSQL": "低延迟高并发的 PostgreSQL 托管数据库",
        "ApsaraDB RDS for SQL Server": "灵活版本与低成本的 SQL Server 托管数据库",
        "ApsaraDB for ClickHouse": "兼容开源 ClickHouse 的云原生在线数仓",
        "ApsaraDB for HBase": "深度优化的 NoSQL 数据库，100% 兼容 Apache HBase",
        "ApsaraDB for MongoDB": "面向文档的数据库服务",
        "ApsaraDB for MyBase": "在阿里云上自主可控的数据库服务集群解决方案",
        "ApsaraDB for OceanBase": "金融级数据库：高稳定、高扩展、高性能",
        "ApsaraDB for Redis": "内存数据库缓存",
        "ApsaraVideo Live": "音视频直播平台",
        "ApsaraVideo VOD": "一体化视频点播（VOD）解决方案",
        "ApsaraVideo for Media Processing": "转码多媒体云服务",
        "Auto Scaling": "根据业务周期自动调整计算资源",
        "Bastionhost": "系统运维与操作审计平台（堡垒机）",
        "Batch Compute": "大规模批处理计算服务",
        "Blockchain as a Service": "安全稳定的区块链平台",
        "Certificate Management Service(Original SSL Certificate)": "申请、购买、管理 SSL 证书",
        "ChatAPP": "通过 WhatsApp 触达全球用户的消息 API",
        "Cloud Architect Design Tools (CADT)": "在 Web 图形界面上构建云架构，无需写代码",
        "Cloud Config": "配置追踪与合规审计",
        "Cloud Enterprise Network": "创建企业级全球网络",
        "Cloud Firewall": "网络安全的第一道防线",
        "Cloud Governance Center": "一站式设置和管理阿里云多账号环境",
        "Cloud Migration Hub": "一站式自动化智能迁移上云工具",
        "Cloud Shell": "使用 CLI 管理云资源",
        "Cloud Storage Gateway": "无缝连接到云存储",
        "CloudAP": "快速集成 Wi-Fi 与 IoT 网络，使用 CloudAC 统一管理",
        "CloudESL": "智能电子价签系统，帮助零售门店高效数据化运营",
        "CloudMonitor": "实时云监控服务",
        "CloudQuotation": "提供稳定、优质的行情数据，超低延迟",
        "Compute Nest": "面向服务商与客户的应用管理服务",
        "Container Registry": "安全的镜像托管平台",
        "Container Service for Kubernetes": "认证 Kubernetes 平台（ACK）",
        "Content Moderation": "图像和视频内容审核",
        "DBStack": "可部署在任意基础设施上的 ApsaraDB 平台，归您所有",
        "Data Encryption Service": "为云用户提供云托管硬件安全模块（HSM）",
        "Data Integration": "实时与离线数据同步",
        "Data Lake Formation": "云原生数据湖框架的关键组件",
        "Data Management": "一体化数据管理解决方案",
        "Data Transfer Plan": "互联网流量使用套餐",
        "Data Transmission Service": "数据迁移与数据同步",
        "Data Transport": "海量数据迁移到阿里云",
        "DataHub": "提供流式数据的发布与订阅功能",
        "DataV": "富有洞察力的大数据可视化",
        "DataWorks": "半成本的全功能数据仓库",
        "Database Autonomy Service": "具备自感知、自修复、自优化、自安全能力的数据库服务",
        "Database Backup": "可靠安全的数据库备份服务",
        "Dataphin": "全链路数据建设与管理",
        "Dedicated DingTalk": "定制、集成、保护移动工作空间",
        "Dedicated Host": "云上的专属物理主机",
        "Direct Mail": "简单高效的邮件服务",
        "Domains": "加入阿里云上的 2000 万域名用户",
        "Drive and Photo Service": "轻松构建企业存储空间",
        "Dynamic Content Delivery Network": "提供动态加速能力",
        "E-MapReduce": "大数据处理服务",
        "ECS Bare Metal Instance": "弹性裸金属计算服务",
        "EMAS HTTPDNS": "防劫持、高精度、低延迟的域名解析服务",
        "EMAS Mobile Testing": "为企业和移动应用提供设备测试的云平台",
        "Edge Node Service (ENS)": "一站式弹性算力资源购买体验（边缘节点）",
        "Elastic Block Storage": "高性能高可靠低延迟的块存储服务",
        "Elastic Compute Service": "高性能云服务器",
        "Elastic Container Instance": "Serverless 容器实例服务",
        "Elastic Desktop Service": "安全高效易用的云桌面服务",
        "Elastic GPU Service": "强大的并行计算能力",
        "Elastic High Performance Computing": "高性能公共计算服务",
        "Elastic IP Address": "独立的公网 IP 资源",
        "Elasticsearch": "Elasticsearch 搜索与分析",
        "Energy Expert": "帮助企业测量和分析碳排放与产品碳足迹",
        "Enterprise Distributed Application Service": "应用部署与微服务解决方案（EDAS）",
        "EventBridge": "Serverless 事件总线服务",
        "Express Connect": "专用物理连接（专线）",
        "Fraud Detection": "实时分析与精准识别风险的管理解决方案",
        "Function Compute": "在 Serverless 环境中运行代码",
        "GameShield": "可定制的网络安全解决方案",
        "Global Accelerator": "全球加速互联网应用以改善用户体验",
        "Global Traffic Manager": "跨 IP 地址的全局加速、调度与容灾",
        "GoChina ICP Filing Assistant": "帮助企业办理 ICP 备案",
        "Hologres": "兼容 PostgreSQL 的实时分析",
        "Hybrid Backup Recovery": "保护数据的 BaaS 解决方案",
        "Hybrid Cloud Distributed Storage": "提供可扩展可靠的分布式块存储与对象存储服务",
        "Hybrid Cloud Storage": "企业级混合云存储阵列",
        "IDaaS": "提供账号、认证、授权、应用与审计能力",
        "Image Search": "高精度视觉搜索解决方案",
        "Intelligent Service Robot": "智能交互聊天机器人平台",
        "Intelligent Speech Interaction": "语音识别与合成平台",
        "IoT Platform": "一站式 IoT 管理平台",
        "Key Management Service": "创建和管理加密密钥（KMS）",
        "Lindorm": "云原生多模型数据库",
        "Link IoT Edge": "将计算从云延伸到边缘的服务平台",
        "Log Service": "面向日志型数据的一体化服务",
        "Machine Learning Platform For AI": "端到端机器学习平台（PAI）",
        "Machine Translation": "定制化优质机器翻译",
        "Managed Security Service": "云上的托管安全服务",
        "MaxCompute": "大规模数据仓库",
        "Message Queue for Apache Kafka": "基于 Apache Kafka 的全托管开箱即用消息队列",
        "Message Queue for RabbitMQ": "开箱即用的全托管 RabbitMQ 服务",
        "Message Service": "在应用之间发送消息",
        "Microservices Engine": "兼容主流开源微服务生态的一站式平台（MSE）",
        "Model Studio": "一站式大模型开发与应用构建平台",
        "NAT Gateway": "公网互联网网关",
        "Network Intelligence Service (NIS)": "自助网络运维服务，可视化网络状态",
        "Object Storage Service": "存储、备份、归档数据（OSS）",
        "Offline Visual Intelligence Software Packages": "视觉生产离线 SDK（图像分割、视频分割等）",
        "OpenAPI Explorer": "更好地调用和请求 API",
        "OpenSearch": "一站式智能搜索服务开发平台",
        "Operation Orchestration Service": "自动化运维服务，管理和执行 O&M 任务",
        "Penetration Test": "全方位深度模拟攻击以测试系统安全",
        "PolarDB": "下一代关系型数据库",
        "PolarDB-X": "可扩展的大型关系型分布式数据库",
        "PrivateLink": "安全、便捷地私网连接到阿里云服务",
        "Quick BI": "大数据分析与可视化",
        "Real-Time Streaming": "超低延迟高并发的直播服务",
        "Realtime Compute for Apache Flink": "实时数据处理平台",
        "Resource Access Management": "授权和管理资源访问（RAM）",
        "Resource Management": "通过目录、文件夹、账号组织管理所有资源",
        "Resource Orchestration Service": "简化计算资源的运维管理",
        "Robotic Process Automation": "自动化业务流程，提升企业效率",
        "SOFAStack™": "基于蚂蚁金融科技的金融级一站式高可用应用研发与运维平台",
        "Secure Content Delivery": "通过阿里云安全 DCDN 加速网站和应用",
        "Security Center": "全天候安全防护",
        "Sensitive Data Discovery & Protection": "保护敏感数据的安全服务",
        "Server Load Balancer": "在资源之间分配流量（SLB）",
        "Serverless Workflow": "编排分布式任务的 Serverless 云服务",
        "Severless Application Engine": "Serverless PaaS 应用托管，按需付费",
        "Short Message Service": "面向企业的短信服务",
        "Simple Application Server": "轻量应用服务器，一键快速部署",
        "Smart Access Gateway": "将企业网络连接到云",
        "Storage Capacity Unit": "通过灵活的存储服务规划与优化存储预算",
        "Super Computing Cluster": "基于 RDMA 网络的并行计算超算集群",
        "Tablestore": "NoSQL 表格存储数据库",
        "Tair": "兼容 Redis 的高性能内存数据库（持久内存 PMEM）",
        "Time Series Database": "百万级 IOPS 的物联网时序数据库",
        "Time Series Database for InfluxDB®️": "低成本高可用可扩展的在线时序数据库",
        "Tracing Analysis": "轻松调试和分析应用",
        "VPN Gateway": "安全连接到 VPC",
        "Virtual Private Cloud": "启动私有云网络",
        "WHOIS": "查询 WHOIS 数据库以检索域名信息",
        "Web Application Firewall": "保护 Web 应用",
        "YiDA": "低代码 SaaS，用于开发企业应用",
        "ZOLOZ Real ID": "数字化远程在线 eKYC 解决方案",
        "mPaaS": "帮助企业构建高质量稳定的移动应用",
    },
}

# 当前只覆盖 3 个分类做试点，跑通之后再铺开到其余 AWS 分类。
# 每个 group 是同一种功能定位在三朵云里的产品集合，某一侧留空数组表示
# 那朵云在这个分类下没有清晰对应的产品（不是漏填，是真的没有）。
GROUPS = [
    # ---------------- Compute ----------------
    {
        "id": "compute-vm",
        "category": "Compute",
        "name": "General-Purpose Virtual Machine (IaaS VM)",
        "name-cn": "通用虚拟机（IaaS VM）",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Elastic Compute Cloud"],
            "azure": ["Virtual Machines", "Linux Virtual Machines"],
            "gcp": ["Compute Engine"],
            "alibaba": ["Elastic Compute Service"],
        },
        "notes": "The flagship virtual machine product of each cloud; the "
        "most direct functional match, matching the Virtual Server row in "
        "cloud-compare-en-new.md.",
        "notes-cn": "三朵云的旗舰虚拟机产品，功能定位最直接对应，"
        "cloud-compare-en-new.md 的 Virtual Server 行也是这么配的。",
    },
    {
        "id": "compute-lightweight-vps",
        "category": "Compute",
        "name": "Lightweight / Entry-Level Virtual Private Server",
        "name-cn": "轻量/入门级虚拟专用服务器",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Lightsail"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Simple Application Server"],
        },
        "notes": "cloud-compare-en-new.md groups Lightsail with Azure App "
        "Service/GCP App Engine (Azure/GCP have no dedicated lightweight "
        "VPS line, so a more general application hosting platform stands "
        "in). App Service/App Engine are already captured in the "
        "compute-paas-app-hosting group, so to avoid the same product "
        "being referenced twice within the same category, Azure/GCP are "
        "left empty here; this alternative view is recorded for reference "
        "only.",
        "notes-cn": "cloud-compare-en-new.md 把 Lightsail 和 Azure App Service/"
        "GCP App Engine 归为一组（Azure/GCP 没有独立的轻量 VPS 产品线，只能用"
        "更通用的应用托管平台顶替）。但 App Service/App Engine 本轮已经收进"
        "了 compute-paas-app-hosting 分组，为避免同一产品在同一分类下被两个"
        "分组重复引用，这里保持 Azure/GCP 留空，只记录这个替代视角供参考。",
    },
    {
        "id": "compute-paas-app-hosting",
        "category": "Compute",
        "name": "PaaS Application Hosting Platform",
        "name-cn": "PaaS 应用托管平台",
        "confidence": "high",
        "products": {
            "aws": ["AWS Elastic Beanstalk"],
            "azure": ["App Service", "Static Web Apps", "Azure Spring Apps"],
            "gcp": ["App Engine"],
            "alibaba": ["Severless Application Engine"],
        },
        "notes": "Based on the Application Hosting Platform and Lightweight "
        "Virtual Server rows in cloud-compare-en-new.md — Azure/GCP use "
        "the same product (App Service/App Engine) to cover two "
        "differently-positioned AWS needs (Elastic Beanstalk and "
        "Lightsail), so the granularity isn't equivalent.",
        "notes-cn": "参考 cloud-compare-en-new.md 的 Application Hosting "
        "Platform 和 Lightweight Virtual Server 两行——Azure/GCP 都用同一个"
        "产品（App Service/App Engine）覆盖了 AWS 这边 Elastic Beanstalk 和"
        "Lightsail 两种不同定位的需求，颗粒度不对等。",
    },
    {
        "id": "compute-batch",
        "category": "Compute",
        "name": "Batch Computing",
        "name-cn": "批处理计算",
        "confidence": "high",
        "products": {
            "aws": ["AWS Batch"],
            "azure": ["Batch"],
            "gcp": ["Batch"],
            "alibaba": ["Batch Compute"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "compute-hpc",
        "category": "Compute",
        "name": "High-Performance Computing (HPC) Cluster",
        "name-cn": "高性能计算（HPC）集群",
        "confidence": "medium",
        "products": {
            "aws": ["AWS ParallelCluster", "AWS Parallel Computing Service"],
            "azure": [],
            "gcp": ["Cluster Toolkit", "Cluster Director documentation"],
            "alibaba": ["Elastic High Performance Computing", "Super Computing Cluster"],
        },
        "notes": "cloud-compare-en-new.md lists Azure CycleCloud as the "
        "counterpart, but it does not appear in products-azure.json "
        "(possibly because the Azure marketing page this data source "
        "scrapes doesn't include this older/more specialized product). "
        "Left empty for Azure pending manual confirmation of whether the "
        "product is still maintained.",
        "notes-cn": "cloud-compare-en-new.md 提到 Azure 对应产品是 Azure "
        "CycleCloud，但它没有出现在 products-azure.json 里（可能是该数据源"
        "用的 Azure 营销页没收录这个偏老/偏专业向的产品），暂时保持 Azure "
        "留空，需要人工确认这个产品是否还在维护。",
    },
    {
        "id": "compute-hybrid-onprem-extension",
        "category": "Compute",
        "name": "Hybrid Cloud Appliance / On-Prem Extension",
        "name-cn": "混合云一体机 / 云能力延伸至本地",
        "confidence": "high",
        "products": {
            "aws": ["AWS Outposts"],
            "azure": ["Azure Stack Hub", "Azure Stack Edge"],
            "gcp": [
                "Google Distributed Cloud",
                "Google Distributed Cloud connected",
                "Google Distributed Cloud (software only) for bare metal",
                "Google Distributed Cloud (software only) for VMware",
            ],
            "alibaba": ["Apsara Stack", "Alibaba Cloud ZStack", "Hybrid Cloud Storage"],
        },
        "notes": "Corrected against the Hybrid Cloud Service row in "
        "cloud-compare-en-new.md: Outposts was originally mis-grouped "
        "with VMware-related products. Outposts actually corresponds to "
        "the product line that brings the cloud vendor's own hardware/"
        "software stack on-premises (Azure Stack, GCP Distributed Cloud), "
        "a different concept from hosting VMware workloads in the cloud "
        "— the latter has been split out into the compute-vmware-hosting "
        "group. Azure Stack Hub/Edge are categorized under Hybrid + "
        "multicloud (not Compute) in products-azure.json; referenced "
        "here across category boundaries.",
        "notes-cn": "参考 cloud-compare-en-new.md 的 Hybrid Cloud Service 行"
        "修正过：最初误把 Outposts 和 VMware 类产品归了一组，实际上 Outposts"
        "对应的是「把云厂商自己的软硬件栈搬到本地」这条产品线（Azure Stack、"
        "GCP Distributed Cloud），和「在云上托管 VMware 工作负载」是两回事，"
        "后者已拆到 compute-vmware-hosting 分组。Azure Stack Hub/Edge 在"
        "products-azure.json 里的分类是 Hybrid + multicloud，不是 Compute，"
        "这里跨分类引用。",
    },
    {
        "id": "compute-vmware-hosting",
        "category": "Compute",
        "name": "VMware Cloud Hosting Service",
        "name-cn": "VMware 云托管服务",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Elastic VMware Service"],
            "azure": ["Azure VMware Solution", "Nutanix Cloud Clusters"],
            "gcp": ["Google Cloud VMware Engine"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "the service type label is self-defined based on the product's "
        "positioning. The AWS counterpart, Amazon Elastic VMware Service, "
        "is categorized under Migration & Transfer (not Compute) in "
        "products-aws.json; referenced here across category boundaries.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，服务类型标签是"
        "按产品定位自拟的。AWS 对应产品 Amazon Elastic VMware Service 在"
        "products-aws.json 里被划分到 Migration & Transfer 分类，不在"
        "Compute 分类下，这里按功能定位跨分类引用。",
    },
    {
        "id": "compute-auto-scaling",
        "category": "Compute",
        "name": "Auto Scaling",
        "name-cn": "自动扩缩容",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon EC2 Auto Scaling"],
            "azure": ["Virtual Machine Scale Sets"],
            "gcp": [],
            "alibaba": ["Auto Scaling"],
        },
        "notes": "Matches the Auto Scaling row in cloud-compare-en-new.md "
        "(this group was initially missed in the pilot — see "
        "references/mapping.md for how it was found). Amazon EC2 Auto "
        "Scaling is categorized under Management & Governance (not "
        "Compute) in products-aws.json; referenced here across category "
        "boundaries. The document lists GCP Managed Instance Groups as "
        "the counterpart, but it doesn't appear in products-gcp.json — "
        "like AWS Spot/Dedicated Host pricing options, it's likely a "
        "sub-feature of Compute Engine rather than a separately "
        "documented product, left empty.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Auto Scaling 行"
        "（这个分组在第一轮试点里被漏掉了，排查过程见"
        "references/mapping.md）。Amazon EC2 Auto Scaling 在"
        "products-aws.json 里被划分到 Management & Governance 分类，不在"
        "Compute 分类下，这里按功能定位跨分类引用。文档给 GCP 一侧填的是"
        "Managed Instance Groups，但它没有出现在 products-gcp.json 里——"
        "和 AWS 的 Spot/专属宿主机购买选项一样，大概率是 Compute Engine 的"
        "子功能而不是单独立项的文档产品，暂时留空。",
    },
    {
        "id": "compute-vm-image-os",
        "category": "Compute",
        "name": "VM Image Management / Cloud-Native Operating System",
        "name-cn": "虚拟机镜像管理 / 云原生操作系统",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Linux", "EC2 Image Builder"],
            "azure": ["Azure VM Image Builder", "Windows Server"],
            "gcp": ["Container-Optimized OS", "Deep Learning VM Images"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined based on functional positioning.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按功能定位"
        "自拟。",
    },
    {
        "id": "compute-spot-capacity",
        "category": "Compute",
        "name": "Spot / Preemptible Capacity Instance",
        "name-cn": "竞价 / 闲置容量实例",
        "confidence": "low",
        "products": {
            "aws": [],
            "azure": ["Azure Spot Virtual Machines"],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. AWS (EC2 Spot) and GCP (Spot VM) both have "
        "equivalent capability, but it's a pricing option of the "
        "flagship VM product rather than a separately listed product in "
        "this data set — only Azure has made it a standalone product "
        "page.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按功能定位"
        "自拟。AWS（EC2 Spot）和 GCP（Spot VM）都有等价能力，但那是"
        "旗舰虚拟机产品的一种定价选项，没有在这份数据里单独列成产品条目，"
        "只有 Azure 把它做成了独立产品页。",
    },
    {
        "id": "compute-dedicated-host",
        "category": "Compute",
        "name": "Dedicated Physical Host",
        "name-cn": "专属物理宿主机",
        "confidence": "low",
        "products": {
            "aws": [],
            "azure": ["Azure Dedicated Host"],
            "gcp": [],
            "alibaba": ["Dedicated Host"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. AWS (EC2 Dedicated Hosts) and GCP (Sole-tenant "
        "nodes) both have equivalent capability, but both are a "
        "purchasing option of the flagship VM product rather than a "
        "separately listed product in this data set — only Azure has "
        "made it a standalone product page, the same single-sided "
        "situation as compute-spot-capacity.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按功能定位"
        "自拟。AWS（EC2 Dedicated Hosts）和 GCP（Sole-tenant nodes）都有"
        "等价能力，但都是旗舰虚拟机产品的一种购买选项，没有在这份数据里"
        "单独列成产品条目，只有 Azure 把它做成了独立产品页，和"
        "compute-spot-capacity 是同一类「单边」情况。",
    },
    {
        "id": "compute-edge",
        "category": "Compute",
        "name": "Edge / Low-Latency Compute Node",
        "name-cn": "边缘 / 低时延计算节点",
        "confidence": "low",
        "products": {
            "aws": ["AWS Local Zones", "AWS Wavelength"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Edge Node Service (ENS)"],
        },
        "notes": "cloud-compare-en-new.md mentions Azure Edge Zones and "
        "GCP Mobile Edge Cloud as counterparts, but neither appears in "
        "products-azure.json / products-gcp.json — after verification, "
        "no confirmed existing product page was found; left empty "
        "pending confirmation of whether these product names have been "
        "renamed or discontinued.",
        "notes-cn": "cloud-compare-en-new.md 提到 Azure Edge Zones、GCP Mobile"
        "Edge Cloud 作为对应产品，但两者都没有出现在 products-azure.json /"
        "products-gcp.json 里，查证后没找到确切的现存产品页，暂时保持"
        "留空，等确认这两个产品名是否已经改名或下线。",
    },
    # ---------------- Database ----------------
    {
        "id": "db-managed-relational",
        "category": "Database",
        "name": "Managed Relational Database (By Engine)",
        "name-cn": "托管关系型数据库（按引擎）",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Relational Database Service"],
            "azure": [
                "Azure Database for MySQL",
                "Azure Database for PostgreSQL",
                "Azure SQL Database",
                "Azure SQL Managed Instance",
                "Azure SQL",
                "SQL Server on Azure Virtual Machines",
            ],
            "gcp": [
                "Cloud SQL",
                "Cloud SQL for MySQL documentation",
                "Cloud SQL for PostgreSQL",
                "Cloud SQL for SQL Server documentation",
            ],
            "alibaba": ["ApsaraDB RDS for MySQL", "ApsaraDB RDS for PostgreSQL", "ApsaraDB RDS for SQL Server", "ApsaraDB RDS for MariaDB"],
        },
        "notes": "Granularity mismatch: AWS uses a single Amazon RDS to "
        "cover multiple engines (MySQL/PostgreSQL/SQL Server, etc.), "
        "while Azure/GCP split them into separate products per engine — "
        "consistent with the Relational Database row in "
        "cloud-compare-en-new.md.",
        "notes-cn": "颗粒度不对等：AWS 用一个 Amazon RDS 覆盖 MySQL/PostgreSQL/"
        "SQL Server 等多种引擎，Azure/GCP 则按引擎拆成了多个独立产品，和"
        "cloud-compare-en-new.md 的 Relational Database 行一致。",
    },
    {
        "id": "db-cloud-native-distributed-sql",
        "category": "Database",
        "name": "Cloud-Native Distributed Relational Database",
        "name-cn": "云原生分布式关系型数据库",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Aurora", "Amazon Aurora DSQL"],
            "azure": ["Azure HorizonDB"],
            "gcp": ["AlloyDB for PostgreSQL", "AlloyDB Omni", "Spanner", "Spanner Omni"],
            "alibaba": ["PolarDB", "PolarDB-X", "ApsaraDB for OceanBase"],
        },
        "notes": "This row in cloud-compare-en-new.md groups Aurora with "
        "Cloud Spanner, validating this group's direction; the document "
        "lists Azure Database for MySQL/PostgreSQL for Azure (reusing "
        "the same product as the plain relational-database row), but "
        "here we prioritize the more precisely positioned Azure "
        "HorizonDB — it's officially positioned to compete with Aurora/"
        "AlloyDB as a high-performance cloud-native PostgreSQL database, "
        "not a plain managed PostgreSQL offering. Spanner's consistency/"
        "scale positioning is stronger than Aurora's, so it's not a "
        "strictly equivalent-tier product — grouped here only by broad "
        "functional category.",
        "notes-cn": "cloud-compare-en-new.md 这一行把 Aurora 和 Cloud Spanner"
        "归一组，验证了这个分组方向；该文档给 Azure 一侧填的是 Azure "
        "Database for MySQL/PostgreSQL（和普通关系型数据库那行复用同一"
        "产品），但这里优先用定位更精确的 Azure HorizonDB——它官方定位就是"
        "对标 Aurora/AlloyDB 的高性能云原生 PostgreSQL 数据库，不是普通版"
        "托管 PostgreSQL。Spanner 的一致性/规模定位比 Aurora 更强，不是"
        "严格意义上的同级产品，仅按功能大类归组。",
    },
    {
        "id": "db-nosql-document",
        "category": "Database",
        "name": "NoSQL Document Database",
        "name-cn": "NoSQL 文档数据库",
        "confidence": "high",
        "products": {
            "aws": [
                "Amazon DynamoDB",
                "Amazon DocumentDB (with MongoDB compatibility)",
            ],
            "azure": ["Azure Cosmos DB", "Azure DocumentDB"],
            "gcp": [
                "Firestore in Native mode",
                "Firestore with MongoDB compatibility",
                "Datastore",
            ],
            "alibaba": ["ApsaraDB for MongoDB"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "db-wide-column-nosql",
        "category": "Database",
        "name": "Wide-Column / Big-Data NoSQL",
        "name-cn": "宽列 / 大数据 NoSQL",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Keyspaces (for Apache Cassandra)"],
            "azure": ["Azure Managed Instance for Apache Cassandra"],
            "gcp": ["Bigtable"],
            "alibaba": ["ApsaraDB for HBase", "Lindorm", "Tablestore"],
        },
        "notes": "This row in cloud-compare-en-new.md lists Azure Cosmos "
        "DB for Azure (providing compatibility via the Cassandra API), "
        "but Cosmos DB is a multi-model database, not a dedicated "
        "wide-column/Cassandra-compatible product — here we prioritize "
        "the more precisely positioned Azure Managed Instance for Apache "
        "Cassandra.",
        "notes-cn": "cloud-compare-en-new.md 这一行 Azure 一侧填的是 Azure "
        "Cosmos DB（靠 Cassandra API 提供兼容能力），但 Cosmos DB 是多模型"
        "数据库，不是专门的宽列/Cassandra 兼容产品，这里优先用定位更精确的"
        "Azure Managed Instance for Apache Cassandra。",
    },
    {
        "id": "db-in-memory-cache",
        "category": "Database",
        "name": "In-Memory Cache Database",
        "name-cn": "内存缓存数据库",
        "confidence": "high",
        "products": {
            "aws": ["Amazon ElastiCache", "Amazon MemoryDB"],
            "azure": ["Azure Managed Redis"],
            "gcp": [
                "Memorystore for Redis",
                "Memorystore for Redis Cluster",
                "Memorystore for Memcached",
                "Memorystore for Valkey",
            ],
            "alibaba": ["ApsaraDB for Redis", "Tair"],
        },
        "notes": "cloud-compare-en-new.md lists Azure Cache for Redis for "
        "Azure — this is the old name; Microsoft has renamed it to Azure "
        "Managed Redis (the new name is what appears in "
        "products-azure.json). When editing the script/mapping table, "
        "use the actual name in the data source, not the old name in "
        "the document.",
        "notes-cn": "cloud-compare-en-new.md 里 Azure 一侧写的是 Azure Cache "
        "for Redis，这是旧名字，微软已经改名成 Azure Managed Redis（在"
        "products-azure.json 里能查到的是新名字），改动脚本/映射表时以数据"
        "源里的实际名字为准，不要照抄文档里的旧名字。",
    },
    {
        "id": "db-graph",
        "category": "Database",
        "name": "Graph Database",
        "name-cn": "图数据库",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Neptune"],
            "azure": ["Azure Cosmos DB"],
            "gcp": [],
        },
        "notes": "cloud-compare-en-new.md points out that Azure Cosmos DB "
        "provides graph database capability via the Gremlin API; this "
        "judgment is adopted here, but Cosmos DB is a multi-model "
        "database, not a dedicated graph database product (a different "
        "role from its appearance in the db-nosql-document group — it's "
        "just another capability surface of the same product), so "
        "confidence is marked medium rather than high. No independent "
        "graph database product was found for GCP.",
        "notes-cn": "cloud-compare-en-new.md 指出 Azure Cosmos DB 通过 "
        "Gremlin API 提供图数据库能力，采纳这个判断加进来，但 Cosmos DB 是"
        "多模型数据库、不是专门的图数据库产品（和它在 db-nosql-document "
        "分组里的角色不是同一件事，这里只是同一个产品的另一种能力面），"
        "所以 confidence 标 medium 而不是 high。GCP 目前没有找到独立的图"
        "数据库产品。",
    },
    {
        "id": "db-time-series",
        "category": "Database",
        "name": "Time Series Database",
        "name-cn": "时序数据库",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Timestream"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Time Series Database", "Time Series Database for InfluxDB®️"],
        },
        "notes": "cloud-compare-en-new.md mentions Azure Time Series "
        "Insights, but it's not in products-azure.json — after "
        "verification, this is a service Microsoft has announced will "
        "be retired, so this suggestion in the document is outdated and "
        "not adopted. No independent time series database product was "
        "found for GCP either.",
        "notes-cn": "cloud-compare-en-new.md 提到 Azure Time Series Insights，"
        "但它不在 products-azure.json 里——查证后这是微软已经宣布退役的"
        "服务，文档这条建议已经过时，不采纳。GCP 同样没有找到独立的时序"
        "数据库产品。",
    },
    {
        "id": "db-oracle-managed",
        "category": "Database",
        "name": "Oracle Database Cloud-Managed Service",
        "name-cn": "Oracle 数据库云托管服务",
        "confidence": "medium",
        "products": {
            "aws": ["Oracle Database@AWS"],
            "azure": [],
            "gcp": ["Oracle Database at Google Cloud", "Oracle on Google Cloud Compute"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. Azure currently has no equivalent "
        "partnership-managed service with Oracle.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按功能定位"
        "自拟。Azure 目前没有和 Oracle 的同类合作托管服务。",
    },
    {
        "id": "db-migration-service",
        "category": "Database",
        "name": "Database Migration Service",
        "name-cn": "数据库迁移服务",
        "confidence": "high",
        "products": {
            "aws": ["AWS Database Migration Service"],
            "azure": ["Azure Database Migration Service"],
            "gcp": ["Database Migration Service"],
            "alibaba": ["Data Transmission Service"],
        },
        "notes": "cloud-compare-en-new.md confirms this correspondence. "
        "AWS Database Migration Service is categorized under Migration "
        "& Transfer (not part of this trial's scope of Compute/Database/"
        "Serverless) in products-aws.json; referenced here across "
        "category boundaries.",
        "notes-cn": "cloud-compare-en-new.md 确认了这组对应关系。AWS "
        "Database Migration Service 在 products-aws.json 里被划分到"
        "Migration & Transfer 分类，不在本轮试点范围（Compute/Database/"
        "Serverless）内，这里按功能定位跨分类引用。",
    },
    # ---------------- Serverless ----------------
    # AWS 有独立的 Serverless 分类，Azure/GCP 都没有对应的顶层分类，
    # 下面这些 Azure/GCP 产品是从它们各自的 Compute/Application 相关
    # 分类里按功能定位挑出来的，不是它们自己分类体系里的"Serverless"。
    {
        "id": "serverless-functions",
        "category": "Serverless",
        "name": "Function as a Service (FaaS)",
        "name-cn": "函数计算（FaaS）",
        "confidence": "high",
        "products": {
            "aws": ["AWS Lambda"],
            "azure": ["Azure Functions"],
            "gcp": ["Cloud Run functions"],
            "alibaba": ["Function Compute"],
        },
        "notes": "cloud-compare-en-new.md lists Cloud Functions for GCP "
        "— this is the old name; Google has renamed it to Cloud Run "
        "functions.",
        "notes-cn": "cloud-compare-en-new.md 里 GCP 一侧写的是 Cloud "
        "Functions，这是旧名字，Google 已经改名成 Cloud Run functions。",
    },
    {
        "id": "serverless-containers",
        "category": "Serverless",
        "name": "Serverless Container Runtime",
        "name-cn": "无服务器容器运行",
        "confidence": "high",
        "products": {
            "aws": ["AWS Fargate", "AWS App Runner"],
            "azure": ["Azure Container Apps"],
            "gcp": ["Cloud Run"],
            "alibaba": ["Elastic Container Instance"],
        },
        "notes": "Functionally overlaps with the compute-paas-app-hosting "
        "group (these products straddle both running containers and "
        "hosting applications); AWS's own data also files Fargate under "
        "both the Compute and Serverless categories.",
        "notes-cn": "和 compute-paas-app-hosting 组功能上有交叉（这些产品本身"
        "横跨「运行容器」和「托管应用平台」两种定位），AWS 自己的数据也把"
        "Fargate 同时归进了 Compute 和 Serverless 两个分类。",
    },
    {
        "id": "serverless-api-gateway",
        "category": "Serverless",
        "name": "Managed API Gateway",
        "name-cn": "托管 API 网关",
        "confidence": "high",
        "products": {
            "aws": ["Amazon API Gateway"],
            "azure": ["API Management"],
            "gcp": ["API Gateway", "Cloud Endpoints"],
            "alibaba": ["API Gateway"],
        },
        "notes": "Azure API Management and GCP API Gateway/Cloud "
        "Endpoints are categorized under Integration and Application "
        "development respectively in their own systems, not under a "
        "\"Serverless\" label — referenced here across category "
        "boundaries based on functional correspondence.",
        "notes-cn": "Azure API Management、GCP API Gateway/Cloud Endpoints 在"
        "各自体系里分别属于 Integration、Application development 分类，"
        "不是「Serverless」标签下的产品，这里按功能对应关系跨分类引用。",
    },
    {
        "id": "serverless-event-bus",
        "category": "Serverless",
        "name": "Serverless Event Bus",
        "name-cn": "无服务器事件总线",
        "confidence": "high",
        "products": {
            "aws": ["Amazon EventBridge"],
            "azure": ["Event Grid"],
            "gcp": ["Eventarc"],
            "alibaba": ["EventBridge"],
        },
        "notes": "Azure Event Grid is categorized under Integration, GCP "
        "Eventarc under Application development — neither is a "
        "\"Serverless\"-labeled product in its own system; referenced "
        "here across category boundaries based on functional "
        "correspondence.",
        "notes-cn": "Azure Event Grid 属于 Integration 分类，GCP Eventarc "
        "属于 Application development 分类，都不是各自体系里的"
        "「Serverless」标签产品，按功能对应关系跨分类引用。",
    },
    {
        "id": "serverless-message-queue",
        "category": "Serverless",
        "name": "Serverless Message Queue",
        "name-cn": "无服务器消息队列",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Simple Queue Service"],
            "azure": ["Queue Storage"],
            "gcp": ["Cloud Tasks"],
            "alibaba": ["Message Service"],
        },
        "notes": "Following cloud-compare-en-new.md, which lists "
        "queueing as its own row (separate from event bus and message "
        "notification) — this more granular split is adopted here. "
        "Azure Queue Storage is categorized under Storage, GCP Cloud "
        "Tasks under Application development — both are cross-category "
        "references.",
        "notes-cn": "参考 cloud-compare-en-new.md 把队列场景单独列了一行"
        "（和事件总线、消息通知分开），采纳这个更精细的拆法。Azure Queue"
        "Storage 属于 Storage 分类，GCP Cloud Tasks 属于 Application"
        "development 分类，都是跨分类引用。",
    },
    {
        "id": "serverless-pubsub-notification",
        "category": "Serverless",
        "name": "Serverless Message Notification / Pub-Sub",
        "name-cn": "无服务器消息通知 / 发布订阅",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Simple Notification Service"],
            "azure": ["Notification Hubs"],
            "gcp": [],
        },
        "notes": "GCP Pub/Sub is the most direct counterpart to SNS in "
        "this scenario, but it doesn't appear in products-gcp.json "
        "(Google's own documentation catalog interface doesn't tag it "
        "as docType:Product — a known data gap, see "
        "references/gcp.md); left empty rather than substituting Cloud "
        "Tasks (task-queue scenarios are already placed in the separate "
        "serverless-message-queue group; the two serve different "
        "purposes). Azure Notification Hubs leans more toward mobile "
        "push notifications and doesn't fully match SNS's general-"
        "purpose pub/sub positioning either, hence confidence is marked "
        "medium.",
        "notes-cn": "GCP Pub/Sub 是这类场景里最直接对应 SNS 的产品，但它没有"
        "出现在 products-gcp.json 里（Google 自己的文档目录接口没有把它"
        "标记为 docType:Product，属于已知数据缺口，见 references/gcp.md），"
        "暂时留空，不用 Cloud Tasks 顶替（任务队列场景已经单独放进"
        "serverless-message-queue 分组，两者定位不同）。Azure Notification"
        "Hubs 更偏移动端推送通知，和 SNS 的通用发布订阅定位也不完全一致，"
        "confidence 标 medium。",
    },
    {
        "id": "serverless-message-broker",
        "category": "Serverless",
        "name": "Managed Message Broker",
        "name-cn": "托管消息中间件",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon MQ"],
            "azure": ["Service Bus"],
            "gcp": [],
            "alibaba": ["Message Queue for RabbitMQ", "AlibabaMQ for Apache RocketMQ"],
        },
        "notes": "Amazon MQ is categorized under Application Integration "
        "(not Serverless) in products-aws.json; referenced here across "
        "category boundaries based on functional positioning. No "
        "corresponding managed message broker product was found for "
        "GCP.",
        "notes-cn": "Amazon MQ 在 products-aws.json 里被划分到 Application "
        "Integration 分类，不是 Serverless，这里按功能定位跨分类引用。GCP"
        "目前没有找到对应的托管消息中间件产品。",
    },
    {
        "id": "serverless-workflow-orchestration",
        "category": "Serverless",
        "name": "Serverless Workflow Orchestration",
        "name-cn": "无服务器工作流编排",
        "confidence": "high",
        "products": {
            "aws": ["AWS Step Functions"],
            "azure": ["Logic Apps"],
            "gcp": ["Workflows"],
            "alibaba": ["Serverless Workflow"],
        },
        "notes": "Azure Logic Apps is categorized under Integration, GCP "
        "Workflows under Application development — both are cross-"
        "category references.",
        "notes-cn": "Azure Logic Apps 属于 Integration 分类，GCP Workflows "
        "属于 Application development 分类，都是跨分类引用。",
    },
    {
        "id": "serverless-graphql-api",
        "category": "Serverless",
        "name": "Managed GraphQL API",
        "name-cn": "托管 GraphQL API",
        "confidence": "medium",
        "products": {
            "aws": ["AWS AppSync"],
            "azure": ["API Management"],
            "gcp": [],
        },
        "notes": "Azure has no dedicated managed GraphQL product; "
        "cloud-compare-en-new.md also assigns this need to API "
        "Management, reusing the same product as the REST API gateway "
        "(so API Management appears in both this group and "
        "serverless-api-gateway — expected). No corresponding product "
        "was found for GCP.",
        "notes-cn": "Azure 没有专门的托管 GraphQL 产品，cloud-compare-en-new.md"
        "把这类需求也归到 API Management 上，和 REST API 网关复用同一个"
        "产品（API Management 因此同时出现在这个分组和"
        "serverless-api-gateway 分组里，属于预期情况）。GCP 目前没有找到"
        "对应产品。",
    },
    {
        "id": "serverless-object-storage",
        "category": "Serverless",
        "name": "Serverless Object Storage",
        "name-cn": "无服务器对象存储",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Simple Storage Service"],
            "azure": ["Azure Blob Storage"],
            "gcp": ["Cloud Storage"],
        },
        "notes": "S3 is categorized under both Serverless and Storage in "
        "AWS's own taxonomy; Azure/GCP's object storage products are not "
        "\"Serverless\"-labeled in their own systems — referenced here "
        "based on functional correspondence.",
        "notes-cn": "S3 在 AWS 自己的分类里同时属于 Serverless 和 Storage；"
        "Azure/GCP 的对象存储不是它们自己体系里的「Serverless」标签产品，"
        "按功能对应关系引用。",
    },
    {
        "id": "serverless-nosql-database",
        "category": "Serverless",
        "name": "Serverless NoSQL Database",
        "name-cn": "无服务器 NoSQL 数据库",
        "confidence": "high",
        "products": {
            "aws": ["Amazon DynamoDB"],
            "azure": [],
            "gcp": [],
        },
        "notes": "See the db-nosql-document group under the Database "
        "category for the full correspondence (Azure Cosmos DB, GCP "
        "Firestore); listed separately here because AWS also "
        "categorizes DynamoDB under Serverless.",
        "notes-cn": "对应关系见 Database 分类下的 db-nosql-document 组"
        "（Azure Cosmos DB、GCP Firestore）；这里单独列出是因为 AWS 把"
        "DynamoDB 同时归入了 Serverless 分类。",
    },
    # ---------------- Developer Tools ----------------
    {
        "id": "devtools-sdk",
        "category": "Developer Tools",
        "name": "SDK / Client Libraries",
        "name-cn": "SDK / 客户端库",
        "confidence": "medium",
        "products": {
            "aws": [
                "AWS SDK for .NET",
                "AWS SDK for C++",
                "AWS SDK for Go",
                "AWS SDK for Java",
                "AWS SDK for JavaScript",
                "AWS SDK for Kotlin",
                "AWS SDK for PHP",
                "AWS SDK for Python (Boto3)",
                "AWS SDK for Ruby",
                "SDK for Rust",
                "SDK for SAP ABAP",
                "SDK for Swift",
                "AWS Tools for PowerShell",
            ],
            "azure": ["SDKs"],
            "gcp": [],
        },
        "notes": "Extreme granularity mismatch: AWS documents a separate "
        "product page per programming language (13 of them), while "
        "Azure bundles everything into a single generic \"SDKs\" "
        "download page and GCP doesn't list a distinct SDK product at "
        "all in this data set (its client libraries are documented "
        "per-service instead of as a standalone product).",
        "notes-cn": "颗粒度差异极大：AWS 给每种编程语言单独开了一个产品页"
        "（13 个），Azure 把所有语言打包成一个通用的「SDKs」下载页，GCP"
        "在这份数据里压根没有一个独立的 SDK 产品条目（客户端库是按各个"
        "服务分别写文档，不是作为独立产品呈现）。",
    },
    {
        "id": "devtools-collaboration-platform",
        "category": "Developer Tools",
        "name": "Development Collaboration Platform",
        "name-cn": "开发协作平台",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon CodeCatalyst"],
            "azure": ["Azure DevOps"],
            "gcp": ["Cloud Code"],
        },
        "notes": "Matches the Development Collaboration Platform row in "
        "cloud-compare-en-new.md. GCP's Cloud Code is more of an IDE "
        "plugin suite than a full project-collaboration platform like "
        "Azure DevOps/CodeCatalyst, so the fit is loose — following the "
        "document's judgment here.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Development "
        "Collaboration Platform 行。GCP 的 Cloud Code 更偏 IDE 插件套件，"
        "不像 Azure DevOps/CodeCatalyst 那样是完整的项目协作平台，贴合度"
        "一般，这里遵循文档的判断。",
    },
    {
        "id": "devtools-java-runtime",
        "category": "Developer Tools",
        "name": "Java Runtime Distribution",
        "name-cn": "Java 运行时发行版",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Corretto"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Java Runtime row in cloud-compare-en-new.md; "
        "the document lists no Azure/GCP counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Java Runtime 行，文档"
        "里 Azure/GCP 一侧也是空的。",
    },
    {
        "id": "devtools-cloud-ide-lab",
        "category": "Developer Tools",
        "name": "Cloud Development Lab Environment",
        "name-cn": "云端开发/实验室环境",
        "confidence": "low",
        "products": {
            "aws": ["AWS Cloud9"],
            "azure": ["Azure Lab Services"],
            "gcp": ["Cloud Workstations"],
        },
        "notes": "Matches the Developer Lab Environment row in "
        "cloud-compare-en-new.md, but the three products aren't a "
        "tight functional match (Cloud9 is a browser IDE, Azure Lab "
        "Services is more about provisioning training/classroom labs, "
        "Cloud Workstations is managed dev environments) — kept per the "
        "document's grouping but confidence is low.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Developer Lab "
        "Environment 行，但三者功能定位并不十分贴合（Cloud9 是浏览器 IDE，"
        "Azure Lab Services 更偏培训/课堂实验室的资源预配，Cloud "
        "Workstations 是托管开发环境）——按文档的分组保留，但 confidence "
        "标低。",
    },
    {
        "id": "devtools-cloud-shell",
        "category": "Developer Tools",
        "name": "Browser-Based Cloud Shell",
        "name-cn": "浏览器云 Shell",
        "confidence": "high",
        "products": {
            "aws": ["AWS CloudShell"],
            "azure": ["Cloud Shell"],
            "gcp": ["Cloud Shell"],
            "alibaba": ["Cloud Shell"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "devtools-resource-management-api",
        "category": "Developer Tools",
        "name": "Unified Resource Management API",
        "name-cn": "统一资源管理 API",
        "confidence": "low",
        "products": {
            "aws": ["AWS Cloud Control API"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Resource Management API row in "
        "cloud-compare-en-new.md; the document lists no Azure/GCP "
        "counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Resource Management "
        "API 行，文档里 Azure/GCP 一侧也是空的。",
    },
    {
        "id": "devtools-artifact-repository",
        "category": "Developer Tools",
        "name": "Artifact Repository",
        "name-cn": "制品库",
        "confidence": "high",
        "products": {
            "aws": ["AWS CodeArtifact"],
            "azure": ["Azure Artifacts"],
            "gcp": ["Artifact Registry"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "devtools-cicd-pipeline",
        "category": "Developer Tools",
        "name": "CI/CD Pipeline (Build, Deploy, Release)",
        "name-cn": "CI/CD 流水线（构建/部署/发布）",
        "confidence": "high",
        "products": {
            "aws": ["AWS CodeBuild", "AWS CodeDeploy", "AWS CodePipeline"],
            "azure": ["Azure Pipelines"],
            "gcp": ["Cloud Build", "Cloud Deploy"],
        },
        "notes": "cloud-compare-en-new.md splits this into three separate "
        "rows (Continuous Integration / Continuous Deployment / "
        "Continuous Delivery), each pointing AWS's three distinct "
        "products at the same Azure Pipelines and largely the same GCP "
        "Cloud Build. Rather than create three near-duplicate groups "
        "that all resolve to the same one or two Azure/GCP products, "
        "they're consolidated here into a single CI/CD pipeline group — "
        "AWS documents build/deploy/release as three separate products, "
        "Azure covers all three with one product (Pipelines), GCP splits "
        "into build vs. deploy.",
        "notes-cn": "cloud-compare-en-new.md 把这块拆成了三行（Continuous "
        "Integration / Continuous Deployment / Continuous Delivery），"
        "但三行分别对应的都是同一个 Azure Pipelines 和基本同一个 GCP "
        "Cloud Build，与其拆成三个高度重复、最终都指向同一两个 Azure/GCP"
        "产品的分组，这里合并成一个 CI/CD 流水线分组——AWS 把构建/部署/"
        "发布拆成三个独立产品，Azure 用一个 Pipelines 覆盖全部三块，GCP"
        "则拆成构建（Cloud Build）和部署（Cloud Deploy）两块。",
    },
    {
        "id": "devtools-apm",
        "category": "Developer Tools",
        "name": "Application Performance Monitoring / Distributed Tracing",
        "name-cn": "应用性能监控 / 分布式追踪",
        "confidence": "medium",
        "products": {
            "aws": ["AWS X-Ray"],
            "azure": ["Azure Monitor"],
            "gcp": ["Cloud Trace"],
            "alibaba": ["Application Real-Time Monitoring Service", "Tracing Analysis"],
        },
        "notes": "cloud-compare-en-new.md lists Azure Application "
        "Insights for this row, but it doesn't appear in "
        "products-azure.json under that name (it's likely surfaced as a "
        "feature of the broader Azure Monitor product on the marketing "
        "page this data source scrapes) — used Azure Monitor instead, "
        "which is a broader observability product than X-Ray/Cloud "
        "Trace's specific distributed-tracing focus, hence medium "
        "confidence.",
        "notes-cn": "cloud-compare-en-new.md 这一行给 Azure 填的是 "
        "Application Insights，但它没有以这个名字出现在 "
        "products-azure.json 里（大概率是被并进了更宽泛的 Azure Monitor"
        "产品页），这里用 Azure Monitor 代替——它的范围比 X-Ray/Cloud "
        "Trace 专注的分布式追踪要宽，所以 confidence 标 medium。",
    },
    {
        "id": "devtools-load-testing",
        "category": "Developer Tools",
        "name": "Load Testing",
        "name-cn": "负载测试",
        "confidence": "low",
        "products": {
            "aws": [],
            "azure": ["Azure App Testing"],
            "gcp": [],
        },
        "notes": "Matches the Load Testing row in cloud-compare-en-new.md "
        "(document lists it as \"Azure Load Testing\", which has since "
        "been folded into the broader \"Azure App Testing\" product in "
        "products-azure.json). AWS/GCP have no dedicated load testing "
        "product in this data set.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Load Testing 行"
        "（文档写的是 Azure Load Testing，在 products-azure.json 里已经"
        "并入了范围更广的 Azure App Testing 产品）。AWS/GCP 在这份数据里"
        "都没有专门的负载测试产品。",
    },
    {
        "id": "devtools-script-testing",
        "category": "Developer Tools",
        "name": "Browser Script / End-to-End Testing",
        "name-cn": "脚本 / 端到端测试",
        "confidence": "low",
        "products": {
            "aws": [],
            "azure": ["Microsoft Playwright Testing"],
            "gcp": [],
        },
        "notes": "Matches the Script Testing row in "
        "cloud-compare-en-new.md; the document lists no AWS/GCP "
        "counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Script Testing 行，"
        "文档里 AWS/GCP 一侧也是空的。",
    },
    {
        "id": "devtools-code-repository",
        "category": "Developer Tools",
        "name": "Managed Git Repository",
        "name-cn": "托管 Git 代码仓库",
        "confidence": "medium",
        "products": {
            "aws": [],
            "azure": ["Azure Repos"],
            "gcp": ["Cloud Source Repositories"],
        },
        "notes": "cloud-compare-en-new.md lists AWS CodeCommit for this "
        "row, but AWS has deprecated CodeCommit for new customers and it "
        "no longer appears in products-aws.json — left empty on the AWS "
        "side rather than reference a discontinued product.",
        "notes-cn": "cloud-compare-en-new.md 这一行给 AWS 填的是 "
        "CodeCommit，但 AWS 已经停止向新客户提供 CodeCommit，"
        "products-aws.json 里也查不到这个产品了——AWS 一侧保持留空，不"
        "引用一个已经下线的产品。",
    },
    {
        "id": "devtools-ide-plugin",
        "category": "Developer Tools",
        "name": "IDE Plugin / Toolkit",
        "name-cn": "IDE 插件 / 工具包",
        "confidence": "medium",
        "products": {
            "aws": [
                "AWS Toolkit for JetBrains",
                "AWS Toolkit for Visual Studio Code",
                "Toolkit for Visual Studio",
            ],
            "azure": [],
            "gcp": ["Cloud Code"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. GCP's Cloud Code plays this role (it's an IDE "
        "plugin suite for VS Code/IntelliJ) and is also referenced in "
        "the devtools-collaboration-platform group under a different "
        "functional lens — expected, since the product genuinely spans "
        "both roles. Azure has no equivalent IDE plugin product in this "
        "data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按功能定位"
        "自拟。GCP 的 Cloud Code 本质上就是这个角色（面向 VS Code/"
        "IntelliJ 的 IDE 插件套件），在 devtools-collaboration-platform"
        "分组里也被引用了，属于同一产品横跨两种功能定位的预期情况。Azure"
        "在这份数据里没有对应的 IDE 插件产品。",
    },
    # ---------------- Management & Governance ----------------
    {
        "id": "mgmt-iac",
        "category": "Management & Governance",
        "name": "Infrastructure as Code",
        "name-cn": "基础设施即代码",
        "confidence": "high",
        "products": {
            "aws": ["AWS CloudFormation"],
            "azure": ["Azure Resource Manager"],
            "gcp": ["Cloud Deployment Manager"],
            "alibaba": ["Resource Orchestration Service"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "mgmt-config-policy",
        "category": "Management & Governance",
        "name": "Configuration / Policy Management",
        "name-cn": "配置与策略管理",
        "confidence": "high",
        "products": {
            "aws": ["AWS Config"],
            "azure": ["Azure Policy"],
            "gcp": ["Security Command Center"],
            "alibaba": ["Cloud Config", "Application Configuration Management"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "mgmt-best-practices-advisor",
        "category": "Management & Governance",
        "name": "Best Practices Recommendations",
        "name-cn": "最佳实践建议",
        "confidence": "high",
        "products": {
            "aws": ["AWS Trusted Advisor"],
            "azure": ["Azure Advisor"],
            "gcp": ["Recommender"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "mgmt-cloud-asset-inventory",
        "category": "Management & Governance",
        "name": "Cloud Asset Inventory",
        "name-cn": "云资产清单",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Config"],
            "azure": [],
            "gcp": ["Cloud Asset Inventory"],
        },
        "notes": "cloud-compare-en-new.md reuses AWS Config for this row "
        "(it's the closest AWS has to an asset-inventory product) and "
        "lists Azure Resource Graph for Azure, which doesn't appear in "
        "products-azure.json — left empty.",
        "notes-cn": "cloud-compare-en-new.md 这一行 AWS 一侧复用的还是 "
        "AWS Config（AWS 最接近资产清单能力的产品），Azure 一侧文档给的是"
        "Azure Resource Graph，但它没有出现在 products-azure.json 里，"
        "保持留空。",
    },
    {
        "id": "mgmt-account-management",
        "category": "Management & Governance",
        "name": "Account Management",
        "name-cn": "账户管理",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Account Management"],
            "azure": [],
            "gcp": ["Cloud Billing"],
        },
        "notes": "cloud-compare-en-new.md lists Azure Subscription "
        "Management for Azure, which doesn't appear in "
        "products-azure.json under that name — left empty.",
        "notes-cn": "cloud-compare-en-new.md 这一行 Azure 一侧给的是 "
        "Azure Subscription Management，在 products-azure.json 里查不到"
        "这个名字，保持留空。",
    },
    {
        "id": "mgmt-console",
        "category": "Management & Governance",
        "name": "Web Management Console",
        "name-cn": "Web 管理控制台",
        "confidence": "low",
        "products": {
            "aws": ["AWS Management Console"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Management Console row in "
        "cloud-compare-en-new.md, but Azure Portal / Cloud Console don't "
        "appear as standalone products in products-azure.json / "
        "products-gcp.json — makes sense, a management portal usually "
        "isn't marketed as a discrete \"product\" the way AWS documents "
        "it.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Management Console "
        "行，但 Azure Portal / Cloud Console 在 products-azure.json / "
        "products-gcp.json 里都不是独立产品条目——也合理，管理门户一般"
        "不会像 AWS 这样被当成一个独立\"产品\"来营销。",
    },
    {
        "id": "mgmt-organization-governance",
        "category": "Management & Governance",
        "name": "Multi-Account / Organization Governance",
        "name-cn": "多账户 / 组织治理",
        "confidence": "low",
        "products": {
            "aws": ["AWS Organizations"],
            "azure": [],
            "gcp": ["Cloud Identity"],
            "alibaba": ["Resource Management"],
        },
        "notes": "cloud-compare-en-new.md lists Azure Management Groups "
        "for Azure, which doesn't appear in products-azure.json — left "
        "empty. GCP's Cloud Identity covers identity/org management more "
        "broadly than just AWS Organizations' scope, so confidence is "
        "low.",
        "notes-cn": "cloud-compare-en-new.md 这一行 Azure 一侧给的是 "
        "Azure Management Groups，在 products-azure.json 里查不到，"
        "保持留空。GCP 的 Cloud Identity 覆盖的身份/组织管理范围比 AWS "
        "Organizations 更宽，所以 confidence 标低。",
    },
    {
        "id": "mgmt-service-catalog",
        "category": "Management & Governance",
        "name": "Service Catalog",
        "name-cn": "服务目录",
        "confidence": "low",
        "products": {
            "aws": ["AWS Service Catalog"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Service Catalog row in "
        "cloud-compare-en-new.md (document lists Azure Marketplace / "
        "Cloud Marketplace, but those are for buying third-party "
        "software — see mgmt-marketplace — not for publishing an "
        "organization's own standardized internal products, which is "
        "what AWS Service Catalog does; neither Azure nor GCP has a "
        "distinct product for that narrower use case in this data set).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Service Catalog 行"
        "（文档给的是 Azure Marketplace / Cloud Marketplace，但那是买"
        "第三方软件的场景——见 mgmt-marketplace，和 AWS Service Catalog"
        "「发布本组织内部标准化产品」这个更窄的场景不是一回事，Azure/GCP"
        "在这份数据里都没有对应窄场景的产品）。",
    },
    {
        "id": "mgmt-marketplace",
        "category": "Management & Governance",
        "name": "Cloud Marketplace",
        "name-cn": "云应用市场",
        "confidence": "low",
        "products": {
            "aws": ["AWS Marketplace"],
            "azure": [],
            "gcp": [],
        },
        "notes": "AWS Marketplace is tagged under AWS's own \"Marketplace\" "
        "category rather than Management & Governance, but is grouped "
        "here to match cloud-compare-en-new.md's Service Catalog row "
        "context. Azure Marketplace / GCP Cloud Marketplace don't appear "
        "as standalone products in this data set.",
        "notes-cn": "AWS Marketplace 在 AWS 自己的分类里属于独立的 "
        "\"Marketplace\" 分类，不是 Management & Governance，这里按"
        "cloud-compare-en-new.md 的 Service Catalog 行上下文归到一起。"
        "Azure Marketplace / GCP Cloud Marketplace 在这份数据里都不是"
        "独立产品条目。",
    },
    {
        "id": "mgmt-multi-account-landing-zone",
        "category": "Management & Governance",
        "name": "Multi-Account Landing Zone",
        "name-cn": "多账户着陆区",
        "confidence": "low",
        "products": {
            "aws": ["AWS Control Tower"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Cloud Governance Center"],
        },
        "notes": "Matches the Multi-Account Management row in "
        "cloud-compare-en-new.md (document lists Azure Landing Zones, "
        "which doesn't appear in products-azure.json — left empty).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Multi-Account "
        "Management 行（文档给的 Azure Landing Zones 在 "
        "products-azure.json 里查不到，保持留空）。",
    },
    {
        "id": "mgmt-audit-log",
        "category": "Management & Governance",
        "name": "Audit Logging",
        "name-cn": "审计日志",
        "confidence": "medium",
        "products": {
            "aws": ["AWS CloudTrail"],
            "azure": ["Azure Monitor"],
            "gcp": ["Cloud Logging"],
            "alibaba": ["ActionTrail"],
        },
        "notes": "cloud-compare-en-new.md reuses Azure Monitor here since "
        "Azure has no separately branded audit-log product; GCP's "
        "dedicated \"Cloud Audit Logs\" also doesn't appear under that "
        "name in products-gcp.json, so the broader Cloud Logging product "
        "is used instead.",
        "notes-cn": "cloud-compare-en-new.md 这一行 Azure 一侧复用的也是"
        "Azure Monitor（Azure 没有单独品牌化的审计日志产品）；GCP 专门的"
        "\"Cloud Audit Logs\"也没有以这个名字出现在 products-gcp.json 里，"
        "改用范围更宽的 Cloud Logging 代替。",
    },
    {
        "id": "mgmt-monitoring-observability",
        "category": "Management & Governance",
        "name": "Monitoring and Observability",
        "name-cn": "监控与可观测性",
        "confidence": "high",
        "products": {
            "aws": ["Amazon CloudWatch"],
            "azure": ["Azure Monitor"],
            "gcp": ["Cloud Monitoring"],
            "alibaba": ["CloudMonitor", "Log Service"],
        },
        "notes": "Matches the Monitoring and Log Service rows in "
        "cloud-compare-en-new.md. Alibaba Cloud splits the two into "
        "CloudMonitor (metrics/alerts) and Log Service (log ingestion "
        "and analysis); both are grouped here.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Monitoring 与 Log "
        "Service 行。阿里云把这两者拆成 CloudMonitor（指标/告警）与 "
        "Log Service（日志接入与分析），此处一并归入。",
    },
    {
        "id": "mgmt-license-management",
        "category": "Management & Governance",
        "name": "Software License Management",
        "name-cn": "软件许可证管理",
        "confidence": "low",
        "products": {
            "aws": ["AWS License Manager"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the License Management row in "
        "cloud-compare-en-new.md (document lists Azure Hybrid Benefit, "
        "which is a pricing/licensing discount program rather than a "
        "distinct product and doesn't appear in products-azure.json).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 License Management "
        "行（文档给的 Azure Hybrid Benefit 是一种定价/授权优惠政策，不是"
        "独立产品，没有出现在 products-azure.json 里）。",
    },
    {
        "id": "mgmt-resource-scheduler",
        "category": "Management & Governance",
        "name": "Automation / Resource Scheduler",
        "name-cn": "自动化 / 资源调度",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Systems Manager"],
            "azure": [],
            "gcp": ["Cloud Scheduler"],
            "alibaba": ["Operation Orchestration Service"],
        },
        "notes": "cloud-compare-en-new.md lists Azure Automation for "
        "Azure, which doesn't appear in products-azure.json — left "
        "empty. GCP Cloud Scheduler is narrower in scope (cron-style job "
        "scheduling) than AWS Systems Manager's broad operations "
        "toolset, so confidence is medium.",
        "notes-cn": "cloud-compare-en-new.md 这一行 Azure 一侧给的是 "
        "Azure Automation，在 products-azure.json 里查不到，保持留空。"
        "GCP Cloud Scheduler 的范围（cron 风格的任务调度）比 AWS Systems "
        "Manager 这套宽泛的运维工具集要窄，所以 confidence 标 medium。",
    },
    {
        "id": "mgmt-security-posture-advisory",
        "category": "Management & Governance",
        "name": "Security Posture / Advisory Notifications",
        "name-cn": "安全态势与咨询通知",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Security Hub"],
            "azure": ["Microsoft Defender for Cloud"],
            "gcp": ["Advisory Notifications"],
        },
        "notes": "AWS Security Hub is categorized under Security, "
        "Identity, & Compliance (not Management & Governance) in "
        "products-aws.json; referenced here across category boundaries "
        "to match the Advisory Notifications / Security Zones rows in "
        "cloud-compare-en-new.md. The document lists Azure Security "
        "Center, which Microsoft has since renamed/folded into "
        "Microsoft Defender for Cloud (the name found in "
        "products-azure.json).",
        "notes-cn": "AWS Security Hub 在 products-aws.json 里被划分到 "
        "Security, Identity, & Compliance 分类，不是 Management & "
        "Governance，这里按 cloud-compare-en-new.md 的 Advisory "
        "Notifications / Security Zones 行跨分类引用。文档给的 Azure "
        "Security Center 微软已经改名/并入了 Microsoft Defender for "
        "Cloud（products-azure.json 里能查到的是新名字）。",
    },
    {
        "id": "mgmt-privileged-access",
        "category": "Management & Governance",
        "name": "Privileged / Managed Access",
        "name-cn": "特权 / 托管访问",
        "confidence": "low",
        "products": {
            "aws": ["AWS IAM Identity Center"],
            "azure": [],
            "gcp": ["Cloud Identity"],
            "alibaba": ["Bastionhost"],
        },
        "notes": "AWS IAM Identity Center is categorized under Security, "
        "Identity, & Compliance (not Management & Governance) in "
        "products-aws.json; referenced here across category boundaries "
        "to match the Managed Access row in cloud-compare-en-new.md. "
        "Azure AD Privileged Identity Management doesn't appear in "
        "products-azure.json — left empty. GCP's Cloud Identity is also "
        "referenced in mgmt-organization-governance under a different "
        "functional lens.",
        "notes-cn": "AWS IAM Identity Center 在 products-aws.json 里被"
        "划分到 Security, Identity, & Compliance 分类，不是 Management "
        "& Governance，这里按 cloud-compare-en-new.md 的 Managed Access "
        "行跨分类引用。文档给的 Azure AD Privileged Identity Management "
        "在 products-azure.json 里查不到，保持留空。GCP 的 Cloud "
        "Identity 在 mgmt-organization-governance 分组里也被引用了，属于"
        "同一产品横跨两种功能定位。",
    },
    {
        "id": "mgmt-cost-management",
        "category": "Management & Governance",
        "name": "Cost Management",
        "name-cn": "成本管理",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Billing and Cost Management"],
            "azure": [],
            "gcp": ["Cloud Billing"],
        },
        "notes": "AWS Billing and Cost Management is categorized under "
        "Cloud Financial Management (not Management & Governance) in "
        "products-aws.json — it's the renamed/consolidated successor to "
        "what cloud-compare-en-new.md calls \"AWS Cost Explorer\", which "
        "no longer appears under that name. Azure Cost Management "
        "doesn't appear in products-azure.json — left empty. GCP's "
        "Cloud Billing is also referenced in mgmt-account-management "
        "under a different functional lens.",
        "notes-cn": "AWS Billing and Cost Management 在 products-aws.json"
        "里被划分到 Cloud Financial Management 分类，不是 Management & "
        "Governance——它是 cloud-compare-en-new.md 里写的\"AWS Cost "
        "Explorer\"改名/整合后的产品，那个旧名字已经查不到了。Azure Cost "
        "Management 在 products-azure.json 里查不到，保持留空。GCP 的 "
        "Cloud Billing 在 mgmt-account-management 分组里也被引用了，属于"
        "同一产品横跨两种功能定位。",
    },
    {
        "id": "mgmt-managed-grafana",
        "category": "Management & Governance",
        "name": "Managed Grafana Dashboards",
        "name-cn": "托管 Grafana 仪表板",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Managed Grafana"],
            "azure": ["Azure Managed Grafana"],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. GCP has no separately branded managed-Grafana "
        "product in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。GCP 在这份数据里没有单独品牌化的托管 Grafana 产品。",
    },
    {
        "id": "mgmt-managed-prometheus",
        "category": "Management & Governance",
        "name": "Managed Prometheus Monitoring",
        "name-cn": "托管 Prometheus 监控",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Managed Service for Prometheus"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. Azure/GCP fold Prometheus-compatible metrics "
        "into their broader Monitor/Cloud Monitoring products rather "
        "than offering a separately branded managed-Prometheus product "
        "in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 把兼容 Prometheus 的指标能力并进了更宽泛的 "
        "Monitor/Cloud Monitoring 产品里，在这份数据里没有单独品牌化的"
        "托管 Prometheus 产品。",
    },
    {
        "id": "mgmt-sustainability",
        "category": "Management & Governance",
        "name": "Sustainability / Carbon Footprint Reporting",
        "name-cn": "可持续发展 / 碳足迹报告",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Sustainability"],
            "azure": [],
            "gcp": ["Carbon Footprint"],
            "alibaba": ["Energy Expert"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. Azure has no separately branded carbon-footprint "
        "reporting product in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure 在这份数据里没有单独品牌化的碳足迹报告产品。",
    },
    {
        "id": "mgmt-resource-health",
        "category": "Management & Governance",
        "name": "Resource / Service Health Dashboard",
        "name-cn": "资源 / 服务健康仪表板",
        "confidence": "low",
        "products": {
            "aws": ["AWS Health"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Resource Health / Service Health "
        "Monitoring rows in cloud-compare-en-new.md (document lists "
        "Azure Service Health and GCP Cloud Status, neither of which "
        "appears as a standalone product in this data set).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Resource Health / "
        "Service Health Monitoring 行（文档给的 Azure Service Health、"
        "GCP Cloud Status 在这份数据里都不是独立产品条目）。",
    },
    {
        "id": "mgmt-resource-visualization",
        "category": "Management & Governance",
        "name": "Resource Visualization",
        "name-cn": "资源可视化",
        "confidence": "low",
        "products": {
            "aws": ["AWS Resource Groups"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Cloud Architect Design Tools (CADT)"],
        },
        "notes": "Matches the Resource Visualization row in "
        "cloud-compare-en-new.md (document lists Azure Resource Graph "
        "and GCP Asset Inventory, neither of which appears as a "
        "standalone product in this data set under that name).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Resource "
        "Visualization 行（文档给的 Azure Resource Graph、GCP Asset "
        "Inventory 在这份数据里都查不到对应名字的独立产品）。",
    },
    # ---------------- Machine Learning ----------------
    {
        "id": "ml-foundation-model-service",
        "category": "Machine Learning",
        "name": "Foundation Model Service",
        "name-cn": "基础模型服务",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Bedrock"],
            "azure": ["Azure OpenAI in Foundry Models"],
            "gcp": ["Gemini Enterprise Agent Platform"],
            "alibaba": ["Model Studio"],
        },
        "notes": "Matches the AI Base Model Service row in "
        "cloud-compare-en-new.md (document lists Azure OpenAI Service, "
        "renamed/restructured into Azure OpenAI in Foundry Models under "
        "Microsoft's AI Foundry branding). GCP's side is filled by "
        "Gemini Enterprise Agent Platform — the current branding of the "
        "platform formerly known as Vertex AI, which provides access to "
        "the Gemini foundation models. Alibaba Cloud Model Studio is the "
        "GenAI foundation-model platform (Qwen etc.), the direct "
        "counterpart to Bedrock / Azure OpenAI.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 AI Base Model "
        "Service 行（文档给的 Azure OpenAI Service 已经在微软 AI Foundry"
        "品牌下重组为 Azure OpenAI in Foundry Models）。GCP 一侧由 "
        "Gemini Enterprise Agent Platform 补上——即原 Vertex AI 平台的"
        "现品牌，提供 Gemini 系列基础模型。阿里云 Model Studio 是生成式 "
        "AI 基础模型平台（通义千问等），与 Bedrock / Azure OpenAI "
        "直接对应。",
    },
    {
        "id": "ml-nlp",
        "category": "Machine Learning",
        "name": "Natural Language Processing",
        "name-cn": "自然语言处理",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Comprehend"],
            "azure": ["Azure Language in Foundry Tools"],
            "gcp": ["Cloud Natural Language API"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "ml-predictive-analysis",
        "category": "Machine Learning",
        "name": "Predictive Analysis / Forecasting",
        "name-cn": "预测分析",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Forecast"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Predictive Analysis row in "
        "cloud-compare-en-new.md; the document lists no standalone "
        "Azure/GCP forecasting product either (Azure's is a sub-feature "
        "of its Cognitive Services, not separately documented in "
        "products-azure.json).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Predictive Analysis "
        "行，文档里 Azure/GCP 一侧也没有独立的预测分析产品（Azure 那边是"
        "认知服务的子功能，没有在 products-azure.json 里单独立项）。",
    },
    {
        "id": "ml-dialog-chatbot",
        "category": "Machine Learning",
        "name": "Conversational Agent / Chatbot",
        "name-cn": "对话机器人",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Lex"],
            "azure": ["Azure AI Bot Service"],
            "gcp": ["Dialogflow CX", "Dialogflow ES"],
            "alibaba": ["Intelligent Service Robot"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "ml-computer-vision",
        "category": "Machine Learning",
        "name": "Computer Vision / Image Recognition",
        "name-cn": "计算机视觉 / 图像识别",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Rekognition"],
            "azure": ["Azure Vision in Foundry Tools", "Azure AI Custom Vision"],
            "gcp": ["Cloud Vision API", "Vision API Product Search"],
            "alibaba": ["Image Search"],
        },
        "notes": "Consolidates the document's separate Computer Vision "
        "and Image Recognition rows — both AWS Rekognition and the "
        "Azure/GCP vision products cover general-purpose image/video "
        "analysis without a meaningful product-level distinction in "
        "this data set.",
        "notes-cn": "把文档里 Computer Vision 和 Image Recognition 两行"
        "合并了——AWS Rekognition 以及 Azure/GCP 的视觉类产品覆盖的都是"
        "通用图像/视频分析能力，在这份数据里没有能撑起两个独立分组的"
        "产品级区分。",
    },
    {
        "id": "ml-personalized-recommendation",
        "category": "Machine Learning",
        "name": "Personalized Recommendation",
        "name-cn": "个性化推荐",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Personalize"],
            "azure": ["Azure AI Personalizer"],
            "gcp": [],
            "alibaba": ["AIRec"],
        },
        "notes": "Matches the Personalized Recommendation row in "
        "cloud-compare-en-new.md. The document's GCP counterpart, "
        "Recommendations AI, doesn't appear under that name in "
        "products-gcp.json (GCP's Recommender product is a broader "
        "cost/resource-optimization advisor — see mgmt-best-practices-"
        "advisor — not a customer-facing recommendation engine, so it "
        "isn't reused here).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Personalized "
        "Recommendation 行。文档给的 GCP 对应产品 Recommendations AI 在 "
        "products-gcp.json 里查不到这个名字（GCP 的 Recommender 是更"
        "宽泛的成本/资源优化建议工具——见 mgmt-best-practices-advisor，"
        "不是面向终端用户的推荐引擎，所以这里不复用它）。",
    },
    {
        "id": "ml-text-to-speech",
        "category": "Machine Learning",
        "name": "Text-to-Speech",
        "name-cn": "文本转语音",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Polly"],
            "azure": [],
            "gcp": ["Cloud Text-to-Speech"],
            "alibaba": ["Intelligent Speech Interaction"],
        },
        "notes": "Matches the Text-to-Speech row in "
        "cloud-compare-en-new.md; the document's Azure counterpart is a "
        "Cognitive Services sub-feature not separately documented in "
        "products-azure.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Text-to-Speech 行；"
        "文档给的 Azure 对应产品是认知服务的子功能，没有在 "
        "products-azure.json 里单独立项。",
    },
    {
        "id": "ml-document-understanding",
        "category": "Machine Learning",
        "name": "Document Understanding / Extraction",
        "name-cn": "文档理解 / 提取",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Textract"],
            "azure": ["Azure Document Intelligence in Foundry Tools"],
            "gcp": ["Document AI"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "ml-platform",
        "category": "Machine Learning",
        "name": "End-to-End Machine Learning Platform",
        "name-cn": "端到端机器学习平台",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon SageMaker AI"],
            "azure": ["Azure Machine Learning"],
            "gcp": ["Gemini Enterprise Agent Platform"],
            "alibaba": ["Machine Learning Platform For AI"],
        },
        "notes": "Matches the Machine Learning Platform row (and the "
        "related ML Model Registry/Pipeline/Feature Store/Deployment/"
        "Monitoring rows, which all point to the same three platform "
        "products in cloud-compare-en-new.md) — consolidated into one "
        "group rather than five near-duplicates. GCP's side is filled by "
        "Gemini Enterprise Agent Platform, the current branding of the "
        "platform formerly known as Vertex AI — an end-to-end platform "
        "for building, deploying and governing ML/AI models and agents.",
        "notes-cn": "对应 Machine Learning Platform 行（以及文档里指向"
        "同样三个平台产品的 ML Model Registry/Pipeline/Feature Store/"
        "Deployment/Monitoring 几行，这里合并成一个分组而不是拆五个高度"
        "重复的分组）。GCP 一侧由 Gemini Enterprise Agent Platform "
        "补上，即原 Vertex AI 平台的现品牌——覆盖 ML/AI 模型与 Agent "
        "构建、部署、治理全生命周期的端到端平台。",
    },
    {
        "id": "ml-speech-recognition",
        "category": "Machine Learning",
        "name": "Speech Recognition",
        "name-cn": "语音识别",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Transcribe"],
            "azure": [],
            "gcp": ["Cloud Speech-to-Text"],
            "alibaba": ["Intelligent Speech Interaction"],
        },
        "notes": "Matches the Speech Recognition row in "
        "cloud-compare-en-new.md; the document's Azure counterpart is a "
        "Cognitive Services sub-feature not separately documented in "
        "products-azure.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Speech Recognition "
        "行；文档给的 Azure 对应产品是认知服务的子功能，没有在 "
        "products-azure.json 里单独立项。",
    },
    {
        "id": "ml-translation",
        "category": "Machine Learning",
        "name": "Language Translation",
        "name-cn": "语言翻译",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Translate"],
            "azure": ["Azure Translator in Foundry Tools"],
            "gcp": ["Cloud Translation"],
            "alibaba": ["Machine Translation"],
        },
        "notes": "",
        "notes-cn": "",
    },
    # ---------------- Security, Identity, & Compliance ----------------
    {
        "id": "sec-iam-core",
        "category": "Security, Identity, & Compliance",
        "name": "Core Identity & Access Management",
        "name-cn": "核心身份与访问管理",
        "confidence": "high",
        "products": {
            "aws": ["AWS Identity and Access Management"],
            "azure": ["Microsoft Entra ID (formerly Azure AD)"],
            "gcp": ["Identity and Access Management (IAM)"],
            "alibaba": ["Resource Access Management"],
        },
        "notes": "Matches the Identity Access Management row in "
        "cloud-compare-en-new.md.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Identity Access "
        "Management 行。",
    },
    {
        "id": "sec-customer-identity",
        "category": "Security, Identity, & Compliance",
        "name": "Customer / App Identity (CIAM)",
        "name-cn": "客户 / 应用身份认证（CIAM）",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Cognito"],
            "azure": ["Microsoft Entra External ID"],
            "gcp": ["Identity Platform"],
            "alibaba": ["IDaaS"],
        },
        "notes": "Matches the Identity Authentication Service / External "
        "Identity Management rows in cloud-compare-en-new.md (document "
        "lists Azure AD B2C and Firebase Authentication, both since "
        "renamed/restructured — the current equivalents in this data "
        "set are Microsoft Entra External ID and Identity Platform).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Identity "
        "Authentication Service / External Identity Management 行"
        "（文档给的 Azure AD B2C、Firebase Authentication 都已经改名/"
        "重组，这份数据里对应的现名是 Microsoft Entra External ID 和 "
        "Identity Platform）。",
    },
    {
        "id": "sec-directory-service",
        "category": "Security, Identity, & Compliance",
        "name": "Managed Directory Service",
        "name-cn": "托管目录服务",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Directory Service"],
            "azure": ["Microsoft Entra ID (formerly Azure AD)"],
            "gcp": [],
        },
        "notes": "Matches the Directory Service row in "
        "cloud-compare-en-new.md; the document's GCP counterpart, Cloud "
        "Identity, is already referenced elsewhere (see "
        "mgmt-organization-governance) under a broader "
        "identity/organization-management lens rather than this "
        "narrower AD-compatible-directory sense, so it isn't repeated "
        "here.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Directory Service "
        "行；文档给的 GCP 对应产品 Cloud Identity 已经在别处引用了（见"
        "mgmt-organization-governance），那边取的是更宽泛的身份/组织"
        "管理含义，不是这里「兼容 AD 的托管目录」这个更窄的场景，这里就"
        "不重复引用了。",
    },
    {
        "id": "sec-threat-detection",
        "category": "Security, Identity, & Compliance",
        "name": "Threat Detection",
        "name-cn": "威胁检测",
        "confidence": "high",
        "products": {
            "aws": ["Amazon GuardDuty"],
            "azure": ["Microsoft Defender for Cloud"],
            "gcp": ["Security Command Center"],
            "alibaba": ["Security Center"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "sec-vulnerability-assessment",
        "category": "Security, Identity, & Compliance",
        "name": "Vulnerability Assessment",
        "name-cn": "漏洞评估",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Inspector"],
            "azure": ["Microsoft Defender for Cloud"],
            "gcp": ["Security Command Center"],
        },
        "notes": "Microsoft Defender for Cloud and Security Command "
        "Center are broad unified security products that also cover "
        "threat detection (sec-threat-detection) — reused here since "
        "neither Azure nor GCP has a separately branded vulnerability-"
        "scanning-only product in this data set.",
        "notes-cn": "Microsoft Defender for Cloud 和 Security Command "
        "Center 是覆盖面很广的统一安全产品，威胁检测那组（"
        "sec-threat-detection）也在用——这里复用是因为 Azure/GCP 在这份"
        "数据里都没有单独品牌化的、只做漏洞扫描的产品。",
    },
    {
        "id": "sec-investigation-siem",
        "category": "Security, Identity, & Compliance",
        "name": "Security Investigation / SIEM",
        "name-cn": "安全调查 / SIEM",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Detective"],
            "azure": ["Microsoft Sentinel"],
            "gcp": ["Security Command Center"],
        },
        "notes": "Matches the Security Investigation Service / Security "
        "Center / Security Monitoring rows in cloud-compare-en-new.md "
        "(consolidated — they all point to the same three products). "
        "GCP's dedicated SIEM product, Chronicle, doesn't appear in "
        "products-gcp.json under that name — Security Command Center is "
        "used instead, reused across several groups.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Security "
        "Investigation Service / Security Center / Security Monitoring "
        "几行（合并成一组，因为都指向同样三个产品）。GCP 专门的 SIEM "
        "产品 Chronicle 没有以这个名字出现在 products-gcp.json 里，改用"
        "在多个分组里复用的 Security Command Center 代替。",
    },
    {
        "id": "sec-data-privacy-dlp",
        "category": "Security, Identity, & Compliance",
        "name": "Data Privacy / Loss Prevention",
        "name-cn": "数据隐私 / 防泄露",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Macie"],
            "azure": ["Azure Information Protection"],
            "gcp": ["Sensitive Data Protection"],
            "alibaba": ["Sensitive Data Discovery & Protection"],
        },
        "notes": "cloud-compare-en-new.md lists GCP's product as Cloud "
        "DLP, which Google has since rebranded to Sensitive Data "
        "Protection (the name found in products-gcp.json).",
        "notes-cn": "cloud-compare-en-new.md 给 GCP 填的是 Cloud DLP，"
        "Google 已经把它改名为 Sensitive Data Protection（"
        "products-gcp.json 里能查到的是新名字）。",
    },
    {
        "id": "sec-fine-grained-authorization",
        "category": "Security, Identity, & Compliance",
        "name": "Fine-Grained Authorization for Custom Apps",
        "name-cn": "自定义应用的细粒度授权",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Verified Permissions"],
            "azure": [],
            "gcp": ["Identity and Access Management (IAM)"],
        },
        "notes": "Matches the Permission Verification Service row in "
        "cloud-compare-en-new.md (document lists Azure RBAC / Cloud "
        "IAM, but Azure RBAC is a built-in feature of Entra ID rather "
        "than a separately documented product, so it doesn't appear in "
        "products-azure.json — left empty). GCP's IAM is reused from "
        "sec-iam-core, since GCP doesn't have an app-level fine-grained "
        "authorization product distinct from its core IAM.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Permission "
        "Verification Service 行（文档给的 Azure RBAC 是 Entra ID 内置"
        "的功能，不是单独立项的产品，没有出现在 products-azure.json 里，"
        "保持留空）。GCP 一侧复用了 sec-iam-core 里的 IAM，因为 GCP 没有"
        "区别于核心 IAM 的应用级细粒度授权产品。",
    },
    {
        "id": "sec-compliance-audit",
        "category": "Security, Identity, & Compliance",
        "name": "Compliance Reporting & Auditing",
        "name-cn": "合规报告与审计",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Artifact", "AWS Audit Manager"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Compliance Reporting Service / Audit "
        "Management Service rows in cloud-compare-en-new.md (document "
        "lists Azure Policy for both, already referenced in "
        "mgmt-config-policy under its primary configuration-governance "
        "role — not repeated here since it's a fairly indirect fit for "
        "\"compliance reporting\" specifically; GCP's Compliance Reports "
        "doesn't appear as a standalone product in this data set).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Compliance "
        "Reporting Service / Audit Management Service 行（文档两行都给"
        "了 Azure Policy，但它已经在 mgmt-config-policy 里以「配置治理」"
        "这个主要角色被引用过，对「合规报告」这个更具体的场景贴合度一般，"
        "这里不重复引用；GCP 的 Compliance Reports 在这份数据里不是"
        "独立产品）。",
    },
    {
        "id": "sec-certificate-management",
        "category": "Security, Identity, & Compliance",
        "name": "Certificate Management (Public & Private CA)",
        "name-cn": "证书管理（公有 / 私有 CA）",
        "confidence": "high",
        "products": {
            "aws": ["AWS Certificate Manager", "AWS Private Certificate Authority"],
            "azure": ["Azure Key Vault"],
            "gcp": ["Certificate Authority Service"],
            "alibaba": ["Certificate Management Service(Original SSL Certificate)"],
        },
        "notes": "Consolidates the document's separate Certificate "
        "Management Service and Private Certificate Authority rows — "
        "both AWS products and their Azure/GCP counterparts are the "
        "same across the two rows in cloud-compare-en-new.md.",
        "notes-cn": "把文档里 Certificate Management Service 和 Private "
        "Certificate Authority 两行合并了——这两行在 "
        "cloud-compare-en-new.md 里对应的 Azure/GCP 产品是一样的。",
    },
    {
        "id": "sec-hsm",
        "category": "Security, Identity, & Compliance",
        "name": "Hardware Security Module (HSM)",
        "name-cn": "硬件安全模块（HSM）",
        "confidence": "high",
        "products": {
            "aws": ["AWS CloudHSM"],
            "azure": ["Azure Cloud HSM"],
            "gcp": ["Cloud HSM"],
            "alibaba": ["Data Encryption Service"],
        },
        "notes": "AWS CloudHSM is categorized under Cryptography & PKI "
        "(not Security, Identity, & Compliance) in products-aws.json; "
        "referenced here across category boundaries to match the "
        "Hardware Security Module row in cloud-compare-en-new.md.",
        "notes-cn": "AWS CloudHSM 在 products-aws.json 里被划分到 "
        "Cryptography & PKI 分类，不是 Security, Identity, & "
        "Compliance，这里按 cloud-compare-en-new.md 的 Hardware Security "
        "Module 行跨分类引用。",
    },
    {
        "id": "sec-key-management",
        "category": "Security, Identity, & Compliance",
        "name": "Key Management Service (KMS)",
        "name-cn": "密钥管理服务（KMS）",
        "confidence": "high",
        "products": {
            "aws": ["AWS Key Management Service"],
            "azure": ["Azure Key Vault"],
            "gcp": ["Cloud Key Management Service"],
            "alibaba": ["Key Management Service"],
        },
        "notes": "AWS Key Management Service is categorized under "
        "Cryptography & PKI (not Security, Identity, & Compliance) in "
        "products-aws.json; referenced here across category boundaries "
        "to match the Key Management Service row in "
        "cloud-compare-en-new.md. Azure Key Vault is reused from "
        "sec-certificate-management, since Azure bundles key/secret/"
        "certificate management into one product.",
        "notes-cn": "AWS Key Management Service 在 products-aws.json 里"
        "被划分到 Cryptography & PKI 分类，不是 Security, Identity, & "
        "Compliance，这里按 cloud-compare-en-new.md 的 Key Management "
        "Service 行跨分类引用。Azure Key Vault 在 "
        "sec-certificate-management 里也被引用了，因为 Azure 把密钥/"
        "密码/证书管理都打包进了同一个产品。",
    },
    {
        "id": "sec-secret-management",
        "category": "Security, Identity, & Compliance",
        "name": "Secret Management",
        "name-cn": "密钥（凭据）管理",
        "confidence": "high",
        "products": {
            "aws": ["AWS Secrets Manager"],
            "azure": ["Azure Key Vault"],
            "gcp": ["Secret Manager"],
        },
        "notes": "Azure Key Vault is reused again here (also covers "
        "certificate and encryption-key management) since Azure doesn't "
        "split these into separately branded products the way AWS does.",
        "notes-cn": "Azure Key Vault 在这里再次被复用（同时也覆盖证书和"
        "加密密钥管理），因为 Azure 没有像 AWS 那样把这些拆成单独品牌化"
        "的产品。",
    },
    {
        "id": "sec-firewall-management",
        "category": "Security, Identity, & Compliance",
        "name": "Firewall Policy Management",
        "name-cn": "防火墙策略管理",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Firewall Manager"],
            "azure": ["Azure Firewall Manager"],
            "gcp": ["Google Cloud Armor"],
        },
        "notes": "GCP has no separately branded centralized firewall-"
        "policy-management product distinct from Cloud Armor itself in "
        "this data set.",
        "notes-cn": "GCP 在这份数据里没有独立于 Cloud Armor 本身的、"
        "单独品牌化的集中式防火墙策略管理产品。",
    },
    {
        "id": "sec-network-firewall",
        "category": "Security, Identity, & Compliance",
        "name": "Network Firewall",
        "name-cn": "网络防火墙",
        "confidence": "high",
        "products": {
            "aws": ["AWS Network Firewall"],
            "azure": ["Azure Firewall"],
            "gcp": ["Google Cloud Armor"],
            "alibaba": ["Cloud Firewall"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "sec-ddos-protection",
        "category": "Security, Identity, & Compliance",
        "name": "DDoS Protection",
        "name-cn": "DDoS 防护",
        "confidence": "high",
        "products": {
            "aws": ["AWS Shield"],
            "azure": ["Azure DDoS Protection"],
            "gcp": ["Google Cloud Armor"],
            "alibaba": ["Anti-DDoS"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "sec-waf",
        "category": "Security, Identity, & Compliance",
        "name": "Web Application Firewall (WAF)",
        "name-cn": "Web 应用防火墙（WAF）",
        "confidence": "high",
        "products": {
            "aws": ["AWS WAF"],
            "azure": ["Azure Web Application Firewall"],
            "gcp": ["Google Cloud Armor"],
            "alibaba": ["Web Application Firewall"],
        },
        "notes": "Google Cloud Armor is reused across "
        "sec-firewall-management / sec-network-firewall / "
        "sec-ddos-protection / sec-waf because GCP consolidates network "
        "firewalling, DDoS mitigation, and WAF capabilities into one "
        "product, whereas AWS and (mostly) Azure split them into "
        "separate ones.",
        "notes-cn": "Google Cloud Armor 在 sec-firewall-management / "
        "sec-network-firewall / sec-ddos-protection / sec-waf 几个分组"
        "里都被复用了，因为 GCP 把网络防火墙、DDoS 防护和 WAF 能力都"
        "打包进了同一个产品，而 AWS 和（大部分）Azure 把它们拆成了独立"
        "产品。",
    },
    {
        "id": "sec-resource-sharing",
        "category": "Security, Identity, & Compliance",
        "name": "Cross-Account Resource Sharing",
        "name-cn": "跨账户资源共享",
        "confidence": "low",
        "products": {
            "aws": ["AWS Resource Access Manager"],
            "azure": [],
            "gcp": ["Identity and Access Management (IAM)"],
        },
        "notes": "Matches the Resource Access Management row in "
        "cloud-compare-en-new.md (document lists Azure RBAC, which "
        "isn't a separately documented product — left empty). GCP's "
        "IAM is reused from sec-iam-core.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Resource Access "
        "Management 行（文档给的 Azure RBAC 不是单独立项的产品，保持"
        "留空）。GCP 一侧复用了 sec-iam-core 里的 IAM。",
    },
    {
        "id": "sec-payment-cryptography",
        "category": "Security, Identity, & Compliance",
        "name": "Payment Cryptography",
        "name-cn": "支付加密",
        "confidence": "low",
        "products": {
            "aws": ["AWS Payment Cryptography"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No Azure/GCP product with this narrow "
        "payment-industry-specific focus was found in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有这种聚焦支付行业的窄场景"
        "产品。",
    },
    {
        "id": "sec-incident-response",
        "category": "Security, Identity, & Compliance",
        "name": "Managed Security Incident Response",
        "name-cn": "托管安全事件响应",
        "confidence": "low",
        "products": {
            "aws": ["AWS Security Incident Response"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Managed Security Service"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No standalone managed-incident-response product "
        "with human CIRT assistance was found for Azure/GCP in this "
        "data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有查到提供人工 CIRT 协助的独立"
        "托管事件响应产品。",
    },
    # ---------------- Analytics ----------------
    {
        "id": "analytics-interactive-query",
        "category": "Analytics",
        "name": "Interactive Query Analysis",
        "name-cn": "交互式查询分析",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Athena"],
            "azure": ["Azure Synapse Analytics"],
            "gcp": ["BigQuery"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "analytics-search-service",
        "category": "Analytics",
        "name": "Managed Search Service",
        "name-cn": "托管搜索服务",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon CloudSearch"],
            "azure": ["Azure AI Search"],
            "gcp": [],
            "alibaba": ["Elasticsearch"],
        },
        "notes": "Matches the Search Service row in "
        "cloud-compare-en-new.md (document lists Azure Cognitive "
        "Search, since renamed/restructured into Azure AI Search under "
        "Microsoft's AI Foundry branding). GCP's Cloud Search doesn't "
        "appear as a standalone product in products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Search Service 行"
        "（文档给的 Azure Cognitive Search 已经改名重组为 Azure AI "
        "Search）。GCP 的 Cloud Search 在 products-gcp.json 里不是独立"
        "产品。",
    },
    {
        "id": "analytics-data-governance",
        "category": "Analytics",
        "name": "Data Governance",
        "name-cn": "数据治理",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon DataZone"],
            "azure": ["Microsoft Purview"],
            "gcp": [],
            "alibaba": ["Dataphin"],
        },
        "notes": "Matches the Data Governance row in "
        "cloud-compare-en-new.md; GCP's Dataplex doesn't appear as a "
        "standalone product in products-gcp.json — a known gap in this "
        "data source (see references/gcp.md), similar to the missing "
        "Vertex AI / Pub/Sub entries.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Data Governance 行；"
        "GCP 的 Dataplex 在 products-gcp.json 里不是独立产品——这份数据"
        "源的已知缺口（见 references/gcp.md），和缺失的 Vertex AI / "
        "Pub/Sub 是同一类问题。",
    },
    {
        "id": "analytics-big-data-processing",
        "category": "Analytics",
        "name": "Big Data Processing (Hadoop/Spark)",
        "name-cn": "大数据处理（Hadoop/Spark）",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon EMR"],
            "azure": ["HDInsight"],
            "gcp": ["Managed Service for Apache Spark"],
            "alibaba": ["E-MapReduce"],
        },
        "notes": "Matches the Big Data Processing row in "
        "cloud-compare-en-new.md. GCP's entry is Managed Service for "
        "Apache Spark — the renamed successor of Cloud Dataproc.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Big Data Processing "
        "行；GCP 一侧对应的产品是 Managed Service for Apache Spark，"
        "即原 Cloud Dataproc 的更名继任者。",
    },
    {
        "id": "analytics-stream-processing",
        "category": "Analytics",
        "name": "Real-Time Stream Processing",
        "name-cn": "实时流处理",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Kinesis"],
            "azure": ["Azure Stream Analytics"],
            "gcp": ["Cloud Dataflow"],
            "alibaba": ["Realtime Compute for Apache Flink"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "analytics-stream-delivery",
        "category": "Analytics",
        "name": "Streaming Data Delivery",
        "name-cn": "流数据投递",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Data Firehose"],
            "azure": ["Event Grid"],
            "gcp": ["Cloud Dataflow"],
            "alibaba": ["DataHub"],
        },
        "notes": "Matches the Data Stream Transfer row in "
        "cloud-compare-en-new.md (document lists Azure Event Hubs, "
        "which doesn't appear in products-azure.json under that exact "
        "name — used Event Grid instead as the closest managed event/"
        "stream ingestion product found; the fit is approximate). Cloud "
        "Dataflow is reused from analytics-stream-processing since GCP "
        "doesn't split stream delivery from stream processing the way "
        "AWS does.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Data Stream "
        "Transfer 行（文档给的 Azure Event Hubs 在 products-azure.json "
        "里查不到这个确切名字，改用能找到的、定位最接近的托管事件/流"
        "接入产品 Event Grid 代替，贴合度是近似的）。Cloud Dataflow 在"
        "analytics-stream-processing 里也被引用了，因为 GCP 没有像 AWS"
        "那样把流投递和流处理拆成两个产品。",
    },
    {
        "id": "analytics-stream-analytics-engine",
        "category": "Analytics",
        "name": "Stream Analytics Engine",
        "name-cn": "流分析引擎",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Managed Service for Apache Flink"],
            "azure": ["Azure Stream Analytics"],
            "gcp": ["Cloud Dataflow"],
        },
        "notes": "Matches the Stream Analytics row in "
        "cloud-compare-en-new.md; AWS's product was renamed from "
        "\"Kinesis Data Analytics\" to \"Amazon Managed Service for "
        "Apache Flink\". Azure Stream Analytics and GCP Cloud Dataflow "
        "are reused from the other streaming groups since neither "
        "vendor splits stream ingestion/processing/analytics into as "
        "many distinct products as AWS does.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Stream Analytics "
        "行；AWS 这个产品是从「Kinesis Data Analytics」改名成"
        "「Amazon Managed Service for Apache Flink」的。Azure Stream "
        "Analytics 和 GCP Cloud Dataflow 在别的流处理分组里也被引用了，"
        "因为两家都没有像 AWS 那样把流接入/处理/分析拆成这么多独立产品。",
    },
    {
        "id": "analytics-managed-kafka",
        "category": "Analytics",
        "name": "Managed Apache Kafka",
        "name-cn": "托管 Apache Kafka",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Managed Streaming for Apache Kafka"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Message Queue for Apache Kafka"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No separately branded managed-Kafka product was "
        "found for Azure/GCP in this data set (Azure Event Hubs offers "
        "a Kafka-compatible endpoint as a feature rather than a "
        "distinct product).",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有单独品牌化的托管 Kafka 产品"
        "（Azure Event Hubs 提供兼容 Kafka 的接入点，但那是一项功能，不是"
        "独立产品）。",
    },
    {
        "id": "analytics-opensearch",
        "category": "Analytics",
        "name": "Managed OpenSearch",
        "name-cn": "托管 OpenSearch",
        "confidence": "low",
        "products": {
            "aws": ["Amazon OpenSearch Service"],
            "azure": [],
            "gcp": [],
            "alibaba": ["OpenSearch"],
        },
        "notes": "Matches the Search and Analytics Engine row in "
        "cloud-compare-en-new.md (document lists Azure OpenSearch "
        "Service, which doesn't appear in products-azure.json — the "
        "document itself also lists no GCP counterpart).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Search and "
        "Analytics Engine 行（文档给的 Azure OpenSearch Service 在 "
        "products-azure.json 里查不到；文档自己给 GCP 一侧也是空的）。",
    },
    {
        "id": "analytics-data-warehouse",
        "category": "Analytics",
        "name": "Cloud Data Warehouse",
        "name-cn": "云数据仓库",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Redshift"],
            "azure": ["Azure Synapse Analytics"],
            "gcp": ["BigQuery"],
            "alibaba": ["MaxCompute", "Hologres", "AnalyticDB for MySQL", "AnalyticDB for PostgreSQL", "ApsaraDB for ClickHouse"],
        },
        "notes": "Azure Synapse Analytics and BigQuery are reused from "
        "analytics-interactive-query since Azure/GCP don't split "
        "interactive query analysis from data warehousing into separate "
        "products the way AWS does (Athena vs. Redshift).",
        "notes-cn": "Azure Synapse Analytics 和 BigQuery 在 "
        "analytics-interactive-query 里也被引用了，因为 Azure/GCP 没有"
        "像 AWS（Athena 对 Redshift）那样把交互式查询分析和数据仓库拆成"
        "两个产品。",
    },
    {
        "id": "analytics-etl",
        "category": "Analytics",
        "name": "ETL / Data Integration Service",
        "name-cn": "ETL / 数据集成服务",
        "confidence": "high",
        "products": {
            "aws": ["AWS Glue"],
            "azure": ["Azure Data Factory"],
            "gcp": ["Cloud Data Fusion"],
            "alibaba": ["DataWorks", "Data Integration"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "analytics-data-exploration",
        "category": "Analytics",
        "name": "Ad-Hoc Data Exploration",
        "name-cn": "即席数据探索",
        "confidence": "low",
        "products": {
            "aws": [],
            "azure": ["Azure Data Explorer"],
            "gcp": [],
        },
        "notes": "Matches the Data Exploration Service row in "
        "cloud-compare-en-new.md; the document lists no AWS/GCP "
        "counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Data Exploration "
        "Service 行，文档里 AWS/GCP 一侧也是空的。",
    },
    {
        "id": "analytics-open-datasets",
        "category": "Analytics",
        "name": "Curated Open Datasets",
        "name-cn": "精选开放数据集",
        "confidence": "low",
        "products": {
            "aws": [],
            "azure": ["Azure Open Datasets"],
            "gcp": [],
        },
        "notes": "Matches the Open Datasets row in "
        "cloud-compare-en-new.md; the document's GCP counterpart, "
        "Google Cloud Public Datasets, doesn't appear as a standalone "
        "product in products-gcp.json, and the document lists no AWS "
        "counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Open Datasets 行；"
        "文档给的 GCP 对应产品 Google Cloud Public Datasets 在 "
        "products-gcp.json 里不是独立产品，文档自己给 AWS 一侧也是空的。",
    },
    {
        "id": "analytics-data-lake-analytics",
        "category": "Analytics",
        "name": "Data Lake Analytics / Governance",
        "name-cn": "数据湖分析与治理",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Lake Formation"],
            "azure": ["Data Lake Analytics"],
            "gcp": [],
            "alibaba": ["Data Lake Formation"],
        },
        "notes": "Matches the Data Lake Analytics row in "
        "cloud-compare-en-new.md (document lists GCP's counterpart as "
        "plain Cloud Storage, but that's the object-storage layer — see "
        "analytics-data-lake-storage — not an analytics/governance layer "
        "on top of a lake the way Lake Formation is, so it isn't reused "
        "here).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Data Lake Analytics "
        "行（文档给 GCP 一侧填的是普通的 Cloud Storage，但那是对象存储层"
        "——见 analytics-data-lake-storage，不是 Lake Formation 这种建在"
        "数据湖之上的分析/治理层，这里不复用）。",
    },
    {
        "id": "analytics-data-lake-storage",
        "category": "Analytics",
        "name": "Data Lake Storage",
        "name-cn": "数据湖存储",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Simple Storage Service"],
            "azure": ["Azure Data Lake Storage"],
            "gcp": ["Cloud Storage"],
        },
        "notes": "Amazon S3 and Cloud Storage are reused from "
        "serverless-object-storage (Serverless category) — same "
        "products, different functional lens (general object storage "
        "vs. purpose-built data lake storage for analytics workloads).",
        "notes-cn": "Amazon S3 和 Cloud Storage 在 "
        "serverless-object-storage 分组（Serverless 分类）里也被引用了"
        "——同一个产品，不同的功能定位（通用对象存储 vs. 面向分析"
        "工作负载的数据湖存储）。",
    },
    {
        "id": "analytics-data-pipeline",
        "category": "Analytics",
        "name": "Data Pipeline Orchestration",
        "name-cn": "数据管道编排",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Data Pipeline"],
            "azure": ["Azure Data Factory"],
            "gcp": ["Cloud Dataflow"],
        },
        "notes": "Azure Data Factory and Cloud Dataflow are reused from "
        "analytics-etl / analytics-stream-processing since neither "
        "vendor has a product distinct from ETL/stream-processing for "
        "this narrower \"periodic pipeline orchestration\" use case that "
        "AWS Data Pipeline targets.",
        "notes-cn": "Azure Data Factory 和 Cloud Dataflow 在 "
        "analytics-etl / analytics-stream-processing 分组里也被引用了，"
        "因为两家都没有针对 AWS Data Pipeline 这种「周期性管道编排」窄"
        "场景的独立产品，用的还是各自的 ETL/流处理产品。",
    },
    {
        "id": "analytics-bi-visualization",
        "category": "Analytics",
        "name": "Business Intelligence & Data Visualization",
        "name-cn": "商业智能与数据可视化",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Quick"],
            "azure": ["Power BI"],
            "gcp": ["Looker"],
            "alibaba": ["Quick BI", "DataV"],
        },
        "notes": "AWS's product was renamed from \"Amazon QuickSight\" to "
        "\"Amazon Quick\"; GCP's is Looker rather than the "
        "cloud-compare-en-new.md-listed \"Looker Studio\", which doesn't "
        "appear under that name in products-gcp.json.",
        "notes-cn": "AWS 这个产品是从「Amazon QuickSight」改名成"
        "「Amazon Quick」的；GCP 一侧用的是 Looker，不是 "
        "cloud-compare-en-new.md 里写的「Looker Studio」（后者在 "
        "products-gcp.json 里查不到这个名字）。",
    },
    {
        "id": "analytics-data-sharing",
        "category": "Analytics",
        "name": "Third-Party / Cross-Org Data Sharing",
        "name-cn": "第三方 / 跨组织数据共享",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Data Exchange"],
            "azure": ["Azure Data Share"],
            "gcp": [],
        },
        "notes": "Matches the Data Sharing row in "
        "cloud-compare-en-new.md; GCP's Analytics Hub doesn't appear as "
        "a standalone product in products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Data Sharing 行；"
        "GCP 的 Analytics Hub 在 products-gcp.json 里不是独立产品。",
    },
    {
        "id": "analytics-data-catalog",
        "category": "Analytics",
        "name": "Data Catalog",
        "name-cn": "数据目录",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Glue"],
            "azure": ["Microsoft Purview"],
            "gcp": ["Knowledge Catalog"],
        },
        "notes": "Matches the Data Catalog row in cloud-compare-en-new.md "
        "(document lists AWS Glue Data Catalog specifically, which "
        "isn't separately documented from AWS Glue itself in "
        "products-aws.json, and Azure Purview, since renamed to "
        "Microsoft Purview). Both AWS Glue and Microsoft Purview are "
        "reused from analytics-etl / analytics-data-governance under "
        "this narrower cataloging lens.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Data Catalog 行"
        "（文档specifically 给的是 AWS Glue Data Catalog，但它在 "
        "products-aws.json 里没有和 AWS Glue 本身分开单独立项；Azure "
        "Purview 已经改名 Microsoft Purview）。AWS Glue 和 Microsoft "
        "Purview 分别在 analytics-etl / analytics-data-governance 里也"
        "被引用了，这里是「数据目录」这个更窄的功能定位。",
    },
    {
        "id": "analytics-clean-rooms",
        "category": "Analytics",
        "name": "Data Clean Room",
        "name-cn": "数据清洁室",
        "confidence": "low",
        "products": {
            "aws": ["AWS Clean Rooms"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No separately branded data-clean-room product "
        "was found for Azure/GCP in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有单独品牌化的数据清洁室产品。",
    },
    {
        "id": "analytics-entity-resolution",
        "category": "Analytics",
        "name": "Entity Resolution / Record Linking",
        "name-cn": "实体解析 / 记录关联",
        "confidence": "low",
        "products": {
            "aws": ["AWS Entity Resolution"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No separately branded entity-resolution product "
        "was found for Azure/GCP in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有单独品牌化的实体解析产品。",
    },
    {
        "id": "analytics-financial-data-workspace",
        "category": "Analytics",
        "name": "Financial Industry Data Workspace",
        "name-cn": "金融行业数据工作空间",
        "confidence": "low",
        "products": {
            "aws": ["Amazon FinSpace"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No industry-specific financial-data workspace "
        "product was found for Azure/GCP in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有面向金融行业的专属数据工作"
        "空间产品。",
    },
    {
        "id": "analytics-saas-integration",
        "category": "Analytics",
        "name": "No-Code SaaS Data Integration",
        "name-cn": "无代码 SaaS 数据集成",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon AppFlow"],
            "azure": ["Logic Apps"],
            "gcp": ["Cloud Data Fusion"],
        },
        "notes": "Matches the Application Integration Service row in "
        "cloud-compare-en-new.md. AWS tags AppFlow under its own "
        "Analytics category rather than Application Integration; Azure "
        "Logic Apps and GCP Cloud Data Fusion are reused from "
        "serverless-workflow-orchestration / analytics-etl under this "
        "narrower no-code SaaS-connector lens.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Application "
        "Integration Service 行。AWS 把 AppFlow 归到了自己的 Analytics "
        "分类而不是 Application Integration；Azure Logic Apps 和 GCP "
        "Cloud Data Fusion 分别在 serverless-workflow-orchestration / "
        "analytics-etl 里也被引用了，这里是「无代码 SaaS 连接器」这个"
        "更窄的功能定位。",
    },
    {
        "id": "analytics-unified-workspace",
        "category": "Analytics",
        "name": "Unified Data & AI Workspace",
        "name-cn": "统一数据与 AI 工作空间",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon SageMaker"],
            "azure": ["Azure Databricks"],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. \"Amazon SageMaker\" (distinct from \"Amazon "
        "SageMaker AI\", which is the ML-specific platform referenced in "
        "ml-platform) has been repositioned as a broader unified data, "
        "analytics, and AI workspace, similar in spirit to Azure "
        "Databricks. No GCP counterpart with this same broad framing "
        "was found in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。「Amazon SageMaker」（区别于 ml-platform 分组里引用的、"
        "专注机器学习的「Amazon SageMaker AI」）已经被重新定位成一个更"
        "宽泛的统一数据、分析与 AI 工作空间，定位上和 Azure Databricks "
        "比较接近。GCP 在这份数据里没有查到同样宽泛定位的对应产品。",
    },
    # ---------------- Networking & Content Delivery ----------------
    {
        "id": "net-cdn",
        "category": "Networking & Content Delivery",
        "name": "Content Delivery Network (CDN)",
        "name-cn": "内容分发网络（CDN）",
        "confidence": "high",
        "products": {
            "aws": ["Amazon CloudFront"],
            "azure": ["Azure Content Delivery Network"],
            "gcp": ["Cloud CDN"],
            "alibaba": ["Alibaba Cloud CDN", "Dynamic Content Delivery Network", "Secure Content Delivery"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "net-dns",
        "category": "Networking & Content Delivery",
        "name": "DNS Service",
        "name-cn": "DNS 服务",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Route 53"],
            "azure": ["Azure DNS"],
            "gcp": ["Cloud DNS"],
            "alibaba": ["Alibaba Cloud DNS", "Alibaba Cloud PrivateZone", "EMAS HTTPDNS"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "net-domain-registration",
        "category": "Networking & Content Delivery",
        "name": "Domain Registration & WHOIS",
        "name-cn": "域名注册与 WHOIS 查询",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Route 53"],
            "azure": [],
            "gcp": ["Cloud Domains"],
            "alibaba": ["Domains", "WHOIS"],
        },
        "notes": "Matches the Domain Registration and Domain Whois rows in "
        "cloud-compare-en-new.md. AWS Route 53 covers both DNS hosting "
        "(net-dns) and domain registration; Azure App Service Domains is "
        "not catalogued as a standalone product in products-azure.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Domain Registration "
        "与 Domain Whois 行。AWS Route 53 同时覆盖 DNS 托管（net-dns）"
        "与域名注册；Azure App Service Domains 在 products-azure.json 里"
        "不是独立产品。",
    },
    {
        "id": "net-vpc",
        "category": "Networking & Content Delivery",
        "name": "Virtual Private Cloud",
        "name-cn": "虚拟私有云",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Virtual Private Cloud"],
            "azure": ["Azure Virtual Network"],
            "gcp": ["Virtual Private Cloud"],
            "alibaba": ["Virtual Private Cloud"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "net-service-mesh",
        "category": "Networking & Content Delivery",
        "name": "Service Mesh",
        "name-cn": "服务网格",
        "confidence": "low",
        "products": {
            "aws": ["AWS App Mesh"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Alibaba Cloud Service Mesh"],
        },
        "notes": "Matches the Service Mesh row in cloud-compare-en-new.md "
        "(document lists Azure Service Fabric Mesh and GCP Traffic "
        "Director, neither of which appears as a standalone product in "
        "this data set).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Service Mesh 行"
        "（文档给的 Azure Service Fabric Mesh、GCP Traffic Director 在"
        "这份数据里都不是独立产品）。",
    },
    {
        "id": "net-vpn",
        "category": "Networking & Content Delivery",
        "name": "VPN Connectivity",
        "name-cn": "VPN 连接",
        "confidence": "high",
        "products": {
            "aws": ["AWS Virtual Private Network"],
            "azure": ["Azure VPN Gateway"],
            "gcp": ["Cloud VPN"],
            "alibaba": ["VPN Gateway"],
        },
        "notes": "Consolidates the document's separate VPN Client and "
        "Site-to-Site VPN rows — AWS documents a single unified "
        "\"AWS Virtual Private Network\" product covering both in this "
        "data set, rather than the two separate Client VPN / "
        "Site-to-Site VPN products the document lists.",
        "notes-cn": "把文档里 VPN Client 和 Site-to-Site VPN 两行合并"
        "了——这份数据里 AWS 用一个统一的「AWS Virtual Private Network」"
        "产品覆盖了这两种场景，不是文档写的 Client VPN / Site-to-Site "
        "VPN 两个独立产品。",
    },
    {
        "id": "net-service-discovery",
        "category": "Networking & Content Delivery",
        "name": "Service Discovery",
        "name-cn": "服务发现",
        "confidence": "low",
        "products": {
            "aws": ["AWS Cloud Map"],
            "azure": ["Azure App Configuration"],
            "gcp": [],
        },
        "notes": "Matches the Service Discovery row in "
        "cloud-compare-en-new.md, but Azure App Configuration is "
        "primarily an app-settings store, not a dedicated service-"
        "discovery product — a loose fit per the document's own "
        "pairing. GCP's Cloud Service Directory doesn't appear as a "
        "standalone product in products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Service Discovery "
        "行，但 Azure App Configuration 本质是应用配置存储，不是专门的"
        "服务发现产品，贴合度一般，这里沿用文档自己的配对。GCP 的 Cloud "
        "Service Directory 在 products-gcp.json 里不是独立产品。",
    },
    {
        "id": "net-dedicated-connection",
        "category": "Networking & Content Delivery",
        "name": "Dedicated Private Connection",
        "name-cn": "专用连接",
        "confidence": "high",
        "products": {
            "aws": ["AWS Direct Connect"],
            "azure": ["Azure ExpressRoute"],
            "gcp": ["Cloud Interconnect"],
            "alibaba": ["Express Connect"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "net-global-accelerator",
        "category": "Networking & Content Delivery",
        "name": "Global Application Accelerator",
        "name-cn": "全球加速器",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Global Accelerator"],
            "azure": ["Azure Front Door"],
            "gcp": [],
            "alibaba": ["Global Accelerator"],
        },
        "notes": "Matches the Global Accelerator row in "
        "cloud-compare-en-new.md; GCP's Premium Tier Networking doesn't "
        "appear as a standalone product in products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Global Accelerator "
        "行；GCP 的 Premium Tier Networking 在 products-gcp.json 里不是"
        "独立产品。",
    },
    {
        "id": "net-private-connection",
        "category": "Networking & Content Delivery",
        "name": "Private Service Connection",
        "name-cn": "私有服务连接",
        "confidence": "low",
        "products": {
            "aws": [],
            "azure": ["Azure Private Link"],
            "gcp": [],
            "alibaba": ["PrivateLink"],
        },
        "notes": "Matches the Private Connection row in "
        "cloud-compare-en-new.md (document lists AWS PrivateLink, which "
        "doesn't appear anywhere in products-aws.json under that name — "
        "a genuine gap in this data source; GCP's Private Service "
        "Connect also doesn't appear as a standalone product).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Private Connection "
        "行（文档给的 AWS PrivateLink 在 products-aws.json 里完全查不到"
        "这个名字——这份数据源真实存在的缺口；GCP 的 Private Service "
        "Connect 也不是独立产品）。",
    },
    {
        "id": "net-load-balancing",
        "category": "Networking & Content Delivery",
        "name": "Load Balancing",
        "name-cn": "负载均衡",
        "confidence": "high",
        "products": {
            "aws": ["Elastic Load Balancing"],
            "azure": ["Azure Load Balancer"],
            "gcp": ["Cloud Load Balancing"],
            "alibaba": ["Server Load Balancer"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "net-monitoring-diagnostics",
        "category": "Networking & Content Delivery",
        "name": "Network Monitoring & Diagnostics",
        "name-cn": "网络监控与诊断",
        "confidence": "medium",
        "products": {
            "aws": [],
            "azure": ["Azure Network Watcher"],
            "gcp": ["Network Intelligence Center"],
            "alibaba": ["Network Intelligence Service (NIS)"],
        },
        "notes": "Matches the Network Monitoring / Network Analysis rows "
        "in cloud-compare-en-new.md (document lists AWS Network Manager "
        "/ Network Insights, neither of which is tagged under "
        "Networking & Content Delivery in products-aws.json or found "
        "elsewhere under those names — left empty).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Network Monitoring "
        "/ Network Analysis 行（文档给的 AWS Network Manager / Network "
        "Insights 在 products-aws.json 里没有被划入 Networking & "
        "Content Delivery 分类，也没有查到这两个名字，保持留空）。",
    },
    {
        "id": "net-traffic-management",
        "category": "Networking & Content Delivery",
        "name": "Global Traffic Management",
        "name-cn": "全球流量管理",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Global Accelerator"],
            "azure": ["Azure Traffic Manager"],
            "gcp": ["Cloud Load Balancing"],
            "alibaba": ["Global Traffic Manager"],
        },
        "notes": "AWS Global Accelerator and Cloud Load Balancing are "
        "reused from net-global-accelerator / net-load-balancing since "
        "neither AWS nor GCP has a product distinct from those two for "
        "this narrower DNS-based traffic-routing use case that Azure "
        "Traffic Manager targets.",
        "notes-cn": "AWS Global Accelerator 和 Cloud Load Balancing 在"
        "net-global-accelerator / net-load-balancing 分组里也被引用了，"
        "因为 AWS 和 GCP 都没有针对 Azure Traffic Manager 这种基于 DNS "
        "的流量路由窄场景的独立产品。",
    },
    {
        "id": "net-hub-spoke-connectivity",
        "category": "Networking & Content Delivery",
        "name": "Hub-and-Spoke Network Connectivity",
        "name-cn": "中心辐射型网络连接",
        "confidence": "medium",
        "products": {
            "aws": [],
            "azure": ["Azure Virtual WAN"],
            "gcp": ["Network Connectivity Center"],
            "alibaba": ["Cloud Enterprise Network", "Smart Access Gateway"],
        },
        "notes": "Matches the Wide Area Network Service / Transit "
        "Gateway / Network Connectivity Center rows in "
        "cloud-compare-en-new.md (document lists AWS Cloud WAN / "
        "Transit Gateway, neither of which is tagged under Networking & "
        "Content Delivery in products-aws.json or found elsewhere under "
        "those names — left empty). Alibaba Cloud has two entries here: "
        "Cloud Enterprise Network is the hub, Smart Access Gateway is "
        "the SD-WAN edge appliance feeding into it.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Wide Area Network "
        "Service / Transit Gateway / Network Connectivity Center 几行"
        "（文档给的 AWS Cloud WAN / Transit Gateway 在 products-aws.json"
        "里没有被划入 Networking & Content Delivery 分类，也没有查到"
        "这两个名字，保持留空）。阿里云在此有两条产品线：Cloud "
        "Enterprise Network 是中心，Smart Access Gateway 是接入它的 "
        "SD-WAN 边缘设备。",
    },
    {
        "id": "net-zero-trust-remote-access",
        "category": "Networking & Content Delivery",
        "name": "Zero-Trust / VPN-less Remote Access",
        "name-cn": "零信任 / 无 VPN 远程访问",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Verified Access"],
            "azure": ["Azure Bastion"],
            "gcp": ["Identity-Aware Proxy"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md "
        "under this framing, but effectively matches the document's "
        "Bastion Service row (AWS Systems Manager Session Manager | "
        "Azure Bastion | Identity-Aware Proxy) — AWS Systems Manager "
        "Session Manager isn't separately documented in "
        "products-aws.json, so the more recently introduced AWS "
        "Verified Access (same \"secure access without a VPN\" goal) is "
        "used instead.",
        "notes-cn": "cloud-compare-en-new.md 没有直接对应这个框架的行，"
        "但实质上对应的是文档的 Bastion Service 行（AWS Systems Manager "
        "Session Manager | Azure Bastion | Identity-Aware Proxy）——AWS "
        "Systems Manager Session Manager 没有在 products-aws.json 里"
        "单独立项，改用目标同样是「无需 VPN 安全访问」的、更新的 AWS "
        "Verified Access 代替。",
    },
    {
        "id": "net-application-recovery",
        "category": "Networking & Content Delivery",
        "name": "Application Disaster Recovery Traffic Control",
        "name-cn": "应用灾难恢复流量控制",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Application Recovery Controller (ARC)"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No separately branded product for this narrow "
        "DR-traffic-shifting use case was found for Azure/GCP in this "
        "data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有针对这种「灾难恢复流量切换」"
        "窄场景的单独品牌化产品。",
    },
    {
        "id": "net-service-connectivity-lattice",
        "category": "Networking & Content Delivery",
        "name": "Application-Layer Service Networking",
        "name-cn": "应用层服务组网",
        "confidence": "low",
        "products": {
            "aws": ["Amazon VPC Lattice"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. VPC Lattice is a newer AWS product with no clear "
        "distinct counterpart found for Azure/GCP in this data set "
        "(closest concept is service mesh — see net-service-mesh — but "
        "Lattice's application-layer, VPC-spanning approach isn't quite "
        "the same thing).",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。VPC Lattice 是 AWS 较新的产品，在这份数据里没有找到清晰"
        "对应的 Azure/GCP 产品（概念上最接近服务网格——见 "
        "net-service-mesh，但 Lattice 这种跨 VPC 的应用层组网方式和"
        "服务网格并不完全是一回事）。",
    },
    # ---------------- Business Applications ----------------
    # 这个分类整体覆盖偏弱：Azure/GCP 各自的办公协作套件
    # （Microsoft 365、Google Workspace）是独立于 azure.microsoft.com /
    # docs.cloud.google.com 之外的产品线，压根没有被这两份数据源抓到
    # （Teams、SharePoint、Exchange Online、Power Apps、Google Meet、
    # Google Drive、AppSheet 等都查不到），所以这个分类下很多分组天然
    # 只有 AWS 一侧，不是抓漏了。
    {
        "id": "bizapp-collaboration-communication",
        "category": "Business Applications",
        "name": "Meetings & Team Collaboration",
        "name-cn": "会议与团队协作",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Chime"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Dedicated DingTalk"],
        },
        "notes": "Matches the Collaboration Communication row in "
        "cloud-compare-en-new.md (document lists Microsoft Teams and "
        "Google Meet, both part of the Microsoft 365 / Google Workspace "
        "product lines that this data set's Azure/GCP sources don't "
        "cover — see the category-level note above).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Collaboration "
        "Communication 行（文档给的 Microsoft Teams、Google Meet 都属于"
        "这份数据的 Azure/GCP 数据源覆盖不到的 Microsoft 365 / Google "
        "Workspace 产品线——见上面的分类级别说明）。",
    },
    {
        "id": "bizapp-call-center",
        "category": "Business Applications",
        "name": "Cloud Contact Center",
        "name-cn": "云联络中心",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Connect Customer"],
            "azure": ["Azure Communication Services"],
            "gcp": [],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "bizapp-customer-interaction",
        "category": "Business Applications",
        "name": "Multichannel Customer Interaction",
        "name-cn": "多渠道客户互动",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Pinpoint"],
            "azure": ["Azure Communication Services"],
            "gcp": [],
        },
        "notes": "Azure Communication Services is reused from "
        "bizapp-call-center since Azure bundles contact-center and "
        "marketing-communication capabilities into one CPaaS product "
        "rather than splitting them like AWS does.",
        "notes-cn": "Azure Communication Services 在 bizapp-call-center "
        "里也被引用了，因为 Azure 把联络中心和营销通信能力打包进了同一个"
        "CPaaS 产品，不像 AWS 拆成了不同产品。",
    },
    {
        "id": "bizapp-email-service",
        "category": "Business Applications",
        "name": "Transactional Email Service",
        "name-cn": "事务性邮件服务",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Simple Email Service"],
            "azure": ["Azure Communication Services"],
            "gcp": [],
            "alibaba": ["Direct Mail"],
        },
        "notes": "Matches the Email Service row in "
        "cloud-compare-en-new.md; Azure Communication Services (reused "
        "again) also covers email sending, though it isn't a dedicated "
        "email-specific product the way SES is, so confidence is low.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Email Service 行；"
        "Azure Communication Services（再次复用）也支持发送邮件，但它"
        "不是像 SES 那样专门的邮件产品，所以 confidence 标低。",
    },
    {
        "id": "bizapp-realtime-communication-sdk",
        "category": "Business Applications",
        "name": "Real-Time Communication SDK (CPaaS)",
        "name-cn": "实时通信 SDK（CPaaS）",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Chime SDK"],
            "azure": ["Azure Communication Services"],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. Azure Communication Services is reused a third "
        "time — it's fundamentally a CPaaS product spanning call "
        "center, marketing messaging, email, and embeddable real-time "
        "communication, all of which AWS splits into distinct products.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure Communication Services 在这里第三次被复用——它本质"
        "上是一个横跨联络中心、营销消息、邮件和可嵌入实时通信能力的 "
        "CPaaS 产品，AWS 把这些拆成了不同的产品。",
    },
    {
        "id": "bizapp-enterprise-email-calendar",
        "category": "Business Applications",
        "name": "Enterprise Email & Calendar",
        "name-cn": "企业邮箱与日历",
        "confidence": "low",
        "products": {
            "aws": ["Amazon WorkMail"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Alibaba Mail"],
        },
        "notes": "Matches the Enterprise Email row in "
        "cloud-compare-en-new.md (document lists Exchange Online and "
        "Google Workspace, both outside this data set's Azure/GCP "
        "sources — see the category-level note above).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Enterprise Email "
        "行（文档给的 Exchange Online、Google Workspace 都在这份数据的 "
        "Azure/GCP 数据源覆盖范围之外——见上面的分类级别说明）。",
    },
    {
        "id": "bizapp-low-code-platform",
        "category": "Business Applications",
        "name": "Low-Code Internal App Platform",
        "name-cn": "低代码内部应用平台",
        "confidence": "low",
        "products": {
            "aws": ["AWS App Studio"],
            "azure": [],
            "gcp": [],
            "alibaba": ["YiDA"],
        },
        "notes": "Matches the Low-Code Platform row in "
        "cloud-compare-en-new.md (document lists Power Apps and "
        "AppSheet, both outside this data set's Azure/GCP sources — "
        "see the category-level note above). AWS App Studio is also "
        "tagged under Developer Tools and Machine Learning in "
        "products-aws.json; referenced here under its low-code-platform "
        "role.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Low-Code Platform "
        "行（文档给的 Power Apps、AppSheet 都在这份数据的 Azure/GCP "
        "数据源覆盖范围之外——见上面的分类级别说明）。AWS App Studio 在 "
        "products-aws.json 里同时也被划入 Developer Tools 和 Machine "
        "Learning 分类，这里按它的低代码平台角色引用。",
    },
    {
        "id": "bizapp-app2person-messaging",
        "category": "Business Applications",
        "name": "Application-to-Person Messaging",
        "name-cn": "应用到个人消息通知",
        "confidence": "low",
        "products": {
            "aws": [
                "AWS End User Messaging Push",
                "AWS End User Messaging SMS",
                "AWS End User Messaging Social",
            ],
            "azure": [],
            "gcp": [],
            "alibaba": ["Short Message Service", "ChatAPP"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined, consolidating AWS's three channel-specific "
        "products (push/SMS/WhatsApp) into one group. No equivalent "
        "product was found for Azure/GCP in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟，把 AWS 按渠道拆分的三个产品（推送/短信/WhatsApp）合并成"
        "一组。Azure/GCP 在这份数据里都没有找到对应产品。",
    },
    {
        "id": "bizapp-supply-chain",
        "category": "Business Applications",
        "name": "Supply Chain Management",
        "name-cn": "供应链管理",
        "confidence": "low",
        "products": {
            "aws": ["AWS Supply Chain"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Supply Chain Management row in "
        "cloud-compare-en-new.md; the document lists no Azure/GCP "
        "counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Supply Chain "
        "Management 行，文档里 Azure/GCP 一侧也是空的。",
    },
    {
        "id": "bizapp-e2e-encrypted-comms",
        "category": "Business Applications",
        "name": "End-to-End Encrypted Enterprise Communication",
        "name-cn": "端到端加密企业通信",
        "confidence": "low",
        "products": {
            "aws": ["AWS Wickr"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Encryption Communication row in "
        "cloud-compare-en-new.md; the document lists no Azure/GCP "
        "counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Encryption "
        "Communication 行，文档里 Azure/GCP 一侧也是空的。",
    },
    {
        "id": "bizapp-saas-data-aggregation",
        "category": "Business Applications",
        "name": "SaaS Data Aggregation & Security",
        "name-cn": "SaaS 数据聚合与安全",
        "confidence": "low",
        "products": {
            "aws": ["AWS AppFabric"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No equivalent SaaS-management-aggregation "
        "product was found for Azure/GCP in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有找到对应的 SaaS 聚合管理"
        "产品。",
    },
    # ---------------- Migration & Transfer ----------------
    {
        "id": "mig-app-discovery",
        "category": "Migration & Transfer",
        "name": "Application Discovery",
        "name-cn": "应用发现",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Application Discovery Service"],
            "azure": ["Azure Migrate"],
            "gcp": [],
        },
        "notes": "Matches the Application Discovery Service row in "
        "cloud-compare-en-new.md; GCP's Cloud Asset Inventory (already "
        "referenced under mgmt-cloud-asset-inventory) is a general "
        "resource inventory, not a migration-discovery product, so it "
        "isn't reused here.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Application "
        "Discovery Service 行；GCP 的 Cloud Asset Inventory（已经在 "
        "mgmt-cloud-asset-inventory 里引用过）是通用资源清单，不是迁移"
        "发现产品，这里不复用。",
    },
    {
        "id": "mig-mainframe-modernization",
        "category": "Migration & Transfer",
        "name": "Mainframe Modernization",
        "name-cn": "大型机现代化改造",
        "confidence": "low",
        "products": {
            "aws": ["AWS Mainframe Modernization"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Mainframe Modernization row in "
        "cloud-compare-en-new.md; the document lists no Azure/GCP "
        "counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Mainframe "
        "Modernization 行，文档里 Azure/GCP 一侧也是空的。",
    },
    {
        "id": "mig-migration-center",
        "category": "Migration & Transfer",
        "name": "Migration Tracking Hub",
        "name-cn": "迁移跟踪中心",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Migration Hub"],
            "azure": ["Azure Migrate"],
            "gcp": [],
            "alibaba": ["Cloud Migration Hub"],
        },
        "notes": "Azure Migrate is reused from mig-app-discovery since "
        "Azure bundles discovery and migration tracking into one "
        "unified platform rather than splitting them like AWS does.",
        "notes-cn": "Azure Migrate 在 mig-app-discovery 里也被引用了，"
        "因为 Azure 把发现和迁移跟踪打包进了同一个统一平台，不像 AWS "
        "拆成了不同产品。",
    },
    {
        "id": "mig-data-transfer-device",
        "category": "Migration & Transfer",
        "name": "Physical Data Transfer Appliance",
        "name-cn": "物理数据传输设备",
        "confidence": "high",
        "products": {
            "aws": ["AWS Data Transfer Terminal"],
            "azure": ["Azure Data Box"],
            "gcp": ["Transfer Appliance"],
            "alibaba": ["Data Transport"],
        },
        "notes": "Matches the Data Transfer Device row in "
        "cloud-compare-en-new.md; AWS's product was renamed from the "
        "\"Snow Family\" to \"AWS Data Transfer Terminal\".",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Data Transfer "
        "Device 行；AWS 这个产品是从「Snow Family」改名成「AWS Data "
        "Transfer Terminal」的。",
    },
    {
        "id": "mig-file-transfer",
        "category": "Migration & Transfer",
        "name": "Managed File Transfer (SFTP/FTPS/FTP)",
        "name-cn": "托管文件传输（SFTP/FTPS/FTP）",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Transfer Family"],
            "azure": ["Azure Files"],
            "gcp": [],
        },
        "notes": "Matches the File Transfer row in "
        "cloud-compare-en-new.md; GCP's Cloud Storage SFTP doesn't "
        "appear as a standalone product in products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 File Transfer 行；"
        "GCP 的 Cloud Storage SFTP 在 products-gcp.json 里不是独立"
        "产品。",
    },
    {
        "id": "mig-data-sync",
        "category": "Migration & Transfer",
        "name": "Online Data Transfer & Sync",
        "name-cn": "在线数据传输与同步",
        "confidence": "medium",
        "products": {
            "aws": ["AWS DataSync"],
            "azure": ["Azure Data Box"],
            "gcp": ["Storage Transfer Service"],
        },
        "notes": "Matches the Data Transfer & Synchronization row in "
        "cloud-compare-en-new.md (document also lists Azure File Sync "
        "for Azure, which doesn't appear in products-azure.json — Azure "
        "Data Box, reused from mig-data-transfer-device, is the closest "
        "available match, though it's physical-appliance-based rather "
        "than online).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Data Transfer & "
        "Synchronization 行（文档给 Azure 一侧还列了 Azure File Sync，"
        "但它没有出现在 products-azure.json 里——改用 "
        "mig-data-transfer-device 里也引用过的 Azure Data Box 作为"
        "最接近的替代，尽管它是物理设备而不是在线传输）。",
    },
    {
        "id": "mig-schema-conversion",
        "category": "Migration & Transfer",
        "name": "Database Schema Conversion",
        "name-cn": "数据库模式转换",
        "confidence": "low",
        "products": {
            "aws": ["AWS Schema Conversion Tool"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No standalone schema-conversion product was "
        "found for Azure/GCP in this data set (the capability is "
        "usually bundled into their database migration services).",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有独立的模式转换产品（这项能力"
        "通常被打包进了它们各自的数据库迁移服务里）。",
    },
    {
        "id": "mig-ai-transformation",
        "category": "Migration & Transfer",
        "name": "Agentic AI-Powered Transformation",
        "name-cn": "智能体 AI 驱动的转型改造",
        "confidence": "low",
        "products": {
            "aws": ["AWS Transform"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. AWS Transform is a newer agentic-AI product with "
        "no clear distinct counterpart found for Azure/GCP in this "
        "data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。AWS Transform 是较新的智能体 AI 产品，在这份数据里没有"
        "找到清晰对应的 Azure/GCP 产品。",
    },
    {
        "id": "mig-app-migration-modernization",
        "category": "Migration & Transfer",
        "name": "Application Migration & Modernization",
        "name-cn": "应用迁移与现代化改造",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Transform MGN"],
            "azure": ["Azure Migrate"],
            "gcp": [],
        },
        "notes": "Matches the Application Migration Service row in "
        "cloud-compare-en-new.md; AWS's product was renamed from "
        "\"AWS Application Migration Service (MGN)\" to \"AWS Transform "
        "MGN\". Azure Migrate is reused a third time from "
        "mig-app-discovery / mig-migration-center. GCP's \"Migrate for "
        "Compute Engine\" doesn't appear as a standalone product in "
        "products-gcp.json — another instance of this data source's "
        "known gaps for well-known GCP products.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Application "
        "Migration Service 行；AWS 这个产品是从「AWS Application "
        "Migration Service (MGN)」改名成「AWS Transform MGN」的。Azure "
        "Migrate 在 mig-app-discovery / mig-migration-center 里也被"
        "第三次引用了。GCP 的「Migrate for Compute Engine」在 "
        "products-gcp.json 里不是独立产品——又一个这份数据源对知名 GCP "
        "产品覆盖不全的例子。",
    },
    # ---------------- Media Services ----------------
    # Azure Media Services 已经被微软在 2024 年正式退役，所以这个分类下
    # 大部分分组 Azure 一侧都会是空的——不是数据源漏抓，是产品本身没了。
    {
        "id": "media-video-transcoding",
        "category": "Media Services",
        "name": "Video Transcoding",
        "name-cn": "视频转码",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Elemental MediaConvert"],
            "azure": [],
            "gcp": ["Transcoder API"],
            "alibaba": ["ApsaraVideo for Media Processing"],
        },
        "notes": "Matches the Media Transcoding / Video Transcoding rows "
        "in cloud-compare-en-new.md (document lists Azure Media "
        "Services, which Microsoft officially retired in 2024 — it "
        "doesn't appear in products-azure.json because the product no "
        "longer exists, not because of a data-source gap).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Media Transcoding /"
        "Video Transcoding 行（文档给的 Azure Media Services 微软已经在"
        "2024 年正式退役——它不在 products-azure.json 里是因为产品本身"
        "已经没有了，不是数据源漏抓）。",
    },
    {
        "id": "media-live-streaming",
        "category": "Media Services",
        "name": "Live Video Streaming",
        "name-cn": "直播视频流",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Elemental MediaLive"],
            "azure": [],
            "gcp": ["Live Stream API"],
            "alibaba": ["ApsaraVideo Live"],
        },
        "notes": "Matches the Live Streaming row in "
        "cloud-compare-en-new.md; same retired-Azure-Media-Services "
        "situation as media-video-transcoding.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Live Streaming 行；"
        "和 media-video-transcoding 一样是 Azure Media Services 已退役"
        "的情况。",
    },
    {
        "id": "media-interactive-live-video",
        "category": "Media Services",
        "name": "Interactive Live Video Streaming",
        "name-cn": "互动直播视频",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Interactive Video Service"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Real-Time Streaming"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No equivalent low-latency interactive-streaming "
        "product was found for Azure/GCP in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在这份数据里都没有找到对应的低延迟互动直播"
        "产品。",
    },
    {
        "id": "media-live-video-workflow",
        "category": "Media Services",
        "name": "Live Video Workflow (Transport, Origination, Ad Insertion)",
        "name-cn": "直播视频工作流（传输/源发起/广告插入）",
        "confidence": "low",
        "products": {
            "aws": [
                "AWS Elemental MediaConnect",
                "AWS Elemental MediaPackage",
                "AWS Elemental MediaTailor",
            ],
            "azure": [],
            "gcp": [],
            "alibaba": ["ApsaraVideo VOD"],
        },
        "notes": "Consolidates three distinct doc rows (the AWS side of "
        "each already has no living Azure/GCP counterpart in this data "
        "set) into one group rather than three empty-sided ones. AWS "
        "breaks the live-video pipeline into separate transport/"
        "packaging/ad-monetization products; no equivalent breakdown "
        "was found for Azure/GCP.",
        "notes-cn": "把文档里三个独立的行合并成一组（这几行的 AWS 一侧"
        "在这份数据里都没有存活的 Azure/GCP 对应产品），不拆成三个空侧"
        "分组。AWS 把直播视频链路拆成了传输/打包/广告变现几个独立产品，"
        "Azure/GCP 在这份数据里都没有找到对应的拆分。",
    },
    {
        "id": "media-specialized-tools",
        "category": "Media Services",
        "name": "Specialized Media Production Tools",
        "name-cn": "专业媒体制作工具",
        "confidence": "low",
        "products": {
            "aws": [
                "AWS Deadline Cloud",
                "AWS Elemental Inference",
                "AWS Elemental On-Premises",
                "AWS Cloud Digital Interface SDK",
            ],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart rows in cloud-compare-en-new.md; "
        "self-defined, consolidating four niche/specialized AWS media-"
        "production products (rendering, ML-on-video, on-prem encoding, "
        "uncompressed video interfaces) with no Azure/GCP counterparts "
        "found in this data set into one group rather than four "
        "single-sided ones.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出这几行，按产品"
        "定位自拟，把四个小众/专业化的 AWS 媒体制作产品（渲染、视频机器"
        "学习推理、本地编码、非压缩视频接口）合并成一组，而不是拆成四个"
        "单边分组——Azure/GCP 在这份数据里都没有找到对应产品。",
    },
    # ---------------- Internet of Things (IoT) ----------------
    # GCP 已经在 2023 年正式退役了 Cloud IoT Core（连带其他 IoT 相关产品），
    # products-gcp.json 里也确实一个 IoT 产品都没有——这个分类下 GCP 一侧
    # 全部留空是真实情况，不是数据源漏抓。
    {
        "id": "iot-core-connectivity",
        "category": "Internet of Things (IoT)",
        "name": "IoT Device Connectivity & Data Ingestion",
        "name-cn": "IoT 设备连接与数据接入",
        "confidence": "high",
        "products": {
            "aws": ["AWS IoT Core"],
            "azure": ["Azure IoT Hub"],
            "gcp": [],
            "alibaba": ["IoT Platform", "AliwareMQ for IoT"],
        },
        "notes": "Consolidates the IoT Core Service / IoT Data Analysis / "
        "IoT Event Processing rows in cloud-compare-en-new.md, which all "
        "point to the same AWS IoT Core / Azure IoT Hub pairing. GCP's "
        "Cloud IoT Core was officially retired by Google in 2023, so it "
        "correctly doesn't appear in products-gcp.json.",
        "notes-cn": "合并了 cloud-compare-en-new.md 的 IoT Core Service /"
        "IoT Data Analysis / IoT Event Processing 几行（都指向同样的 "
        "AWS IoT Core / Azure IoT Hub 配对）。GCP 的 Cloud IoT Core 已经"
        "在 2023 年被 Google 正式退役，所以 products-gcp.json 里确实"
        "查不到，不是抓漏了。",
    },
    {
        "id": "iot-device-management",
        "category": "Internet of Things (IoT)",
        "name": "IoT Device Fleet Management",
        "name-cn": "IoT 设备批量管理",
        "confidence": "medium",
        "products": {
            "aws": ["AWS IoT Device Management"],
            "azure": ["Azure IoT Hub"],
            "gcp": [],
        },
        "notes": "Azure IoT Hub is reused from iot-core-connectivity "
        "since Azure bundles device management into the same hub "
        "product rather than splitting it out like AWS does.",
        "notes-cn": "Azure IoT Hub 在 iot-core-connectivity 里也被引用"
        "了，因为 Azure 把设备管理打包进了同一个 Hub 产品，不像 AWS 拆成"
        "了独立产品。",
    },
    {
        "id": "iot-device-security",
        "category": "Internet of Things (IoT)",
        "name": "IoT Device Security",
        "name-cn": "IoT 设备安全",
        "confidence": "low",
        "products": {
            "aws": ["AWS IoT Device Defender"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the IoT Device Security row in "
        "cloud-compare-en-new.md; the document's Azure IoT Security "
        "doesn't appear as a standalone product in products-azure.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 IoT Device "
        "Security 行；文档给的 Azure IoT Security 在 products-azure.json"
        "里不是独立产品。",
    },
    {
        "id": "iot-edge-computing",
        "category": "Internet of Things (IoT)",
        "name": "IoT Edge Computing",
        "name-cn": "IoT 边缘计算",
        "confidence": "high",
        "products": {
            "aws": ["AWS IoT Greengrass"],
            "azure": ["Azure IoT Edge"],
            "gcp": [],
            "alibaba": ["Link IoT Edge"],
        },
        "notes": "Matches the Edge Computing row in "
        "cloud-compare-en-new.md; GCP's Cloud IoT Edge was retired "
        "alongside Cloud IoT Core.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Edge Computing 行；"
        "GCP 的 Cloud IoT Edge 和 Cloud IoT Core 一起被退役了。",
    },
    {
        "id": "iot-industrial-central",
        "category": "Internet of Things (IoT)",
        "name": "Industrial IoT / Fleet Onboarding",
        "name-cn": "工业物联网 / 设备接入平台",
        "confidence": "medium",
        "products": {
            "aws": ["AWS IoT SiteWise"],
            "azure": ["Azure IoT Central"],
            "gcp": [],
        },
        "notes": "Matches the Industrial IoT row in "
        "cloud-compare-en-new.md.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Industrial IoT 行。",
    },
    {
        "id": "iot-digital-twin",
        "category": "Internet of Things (IoT)",
        "name": "Digital Twin",
        "name-cn": "数字孪生",
        "confidence": "high",
        "products": {
            "aws": ["AWS IoT TwinMaker"],
            "azure": ["Azure Digital Twins"],
            "gcp": [],
        },
        "notes": "Matches the Digital Twin row in "
        "cloud-compare-en-new.md; the document's GCP counterpart, "
        "Supply Chain Twin, is a narrower vertical-specific product not "
        "found in products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Digital Twin 行；"
        "文档给的 GCP 对应产品 Supply Chain Twin 是更窄的垂直行业产品，"
        "在 products-gcp.json 里查不到。",
    },
    {
        "id": "iot-vehicle-data",
        "category": "Internet of Things (IoT)",
        "name": "Connected Vehicle Data Platform",
        "name-cn": "车联网数据平台",
        "confidence": "low",
        "products": {
            "aws": ["AWS IoT FleetWise"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Vehicle Network Service row in "
        "cloud-compare-en-new.md; the document lists no Azure/GCP "
        "counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Vehicle Network "
        "Service 行，文档里 Azure/GCP 一侧也是空的。",
    },
    {
        "id": "iot-rtos",
        "category": "Internet of Things (IoT)",
        "name": "Real-Time Operating System for Microcontrollers",
        "name-cn": "微控制器实时操作系统",
        "confidence": "low",
        "products": {
            "aws": ["FreeRTOS"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Real-time Operating System row in "
        "cloud-compare-en-new.md (document lists Azure RTOS, which "
        "doesn't appear in products-azure.json).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Real-time "
        "Operating System 行（文档给的 Azure RTOS 在 "
        "products-azure.json 里查不到）。",
    },
    {
        "id": "iot-hardware-connectivity",
        "category": "Internet of Things (IoT)",
        "name": "IoT Hardware Connectivity Enablement",
        "name-cn": "IoT 硬件联网使能",
        "confidence": "low",
        "products": {
            "aws": ["AWS IoT ExpressLink", "AWS IoT Wireless"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart rows in cloud-compare-en-new.md; "
        "self-defined, consolidating two AWS products focused on "
        "getting physical devices securely connected (a pre-certified "
        "connectivity module, and LoRaWAN/Sidewalk wireless "
        "connectivity) into one group. No Azure/GCP counterparts were "
        "found in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出这两行，按产品"
        "定位自拟，把两个聚焦「让物理设备安全联网」的 AWS 产品（预认证"
        "联网模组、LoRaWAN/Sidewalk 无线连接）合并成一组。Azure/GCP 在"
        "这份数据里都没有找到对应产品。",
    },
    # ---------------- Storage ----------------
    {
        "id": "storage-block",
        "category": "Storage",
        "name": "Block Storage",
        "name-cn": "块存储",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Elastic Block Store"],
            "azure": ["Azure Disk Storage"],
            "gcp": ["Persistent Disk"],
            "alibaba": ["Elastic Block Storage"],
        },
        "notes": "cloud-compare-en-new.md lists Azure Managed Disks for "
        "Azure — Microsoft has since renamed this product line to Azure "
        "Disk Storage (the name found in products-azure.json).",
        "notes-cn": "cloud-compare-en-new.md 给 Azure 一侧填的是 Azure "
        "Managed Disks，微软已经把这条产品线改名为 Azure Disk Storage"
        "（products-azure.json 里能查到的是新名字）。",
    },
    {
        "id": "storage-file-system",
        "category": "Storage",
        "name": "Managed File System (NFS/SMB)",
        "name-cn": "托管文件系统（NFS/SMB）",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Elastic File System", "Amazon FSx"],
            "azure": ["Azure Files"],
            "gcp": ["Filestore"],
            "alibaba": ["Apsara File Storage NAS"],
        },
        "notes": "Consolidates the document's separate File Storage "
        "Service and File System Service rows — both AWS products (EFS "
        "for NFS, FSx for a broader range of file system types) map to "
        "the same Azure Files / GCP Filestore pairing in "
        "cloud-compare-en-new.md.",
        "notes-cn": "把文档里 File Storage Service 和 File System "
        "Service 两行合并了——AWS 这两个产品（EFS 面向 NFS，FSx 覆盖更"
        "多种文件系统类型）在 cloud-compare-en-new.md 里对应的都是同样的"
        "Azure Files / GCP Filestore 配对。",
    },
    {
        "id": "storage-object",
        "category": "Storage",
        "name": "Object Storage",
        "name-cn": "对象存储",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Simple Storage Service"],
            "azure": ["Azure Blob Storage"],
            "gcp": ["Cloud Storage"],
            "alibaba": ["Object Storage Service"],
        },
        "notes": "Same three products already referenced under "
        "serverless-object-storage (Serverless) and "
        "analytics-data-lake-storage (Analytics) — this is the plain "
        "\"object storage\" functional lens that matches AWS's own "
        "Storage category tag on S3.",
        "notes-cn": "和 serverless-object-storage（Serverless 分类）、"
        "analytics-data-lake-storage（Analytics 分类）里引用的是同样"
        "三个产品——这里是最基础的「对象存储」功能定位，对应 AWS 自己给 "
        "S3 打的 Storage 分类标签。",
    },
    {
        "id": "storage-archive",
        "category": "Storage",
        "name": "Archive Storage",
        "name-cn": "归档存储",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Glacier"],
            "azure": ["Archive Storage"],
            "gcp": [],
        },
        "notes": "Matches the Archive Storage Service row in "
        "cloud-compare-en-new.md; GCP's Cloud Storage Archive is a "
        "storage class within Cloud Storage rather than a separately "
        "documented product in products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Archive Storage "
        "Service 行；GCP 的 Cloud Storage Archive 是 Cloud Storage 里的"
        "一个存储类别，不是 products-gcp.json 里单独立项的产品。",
    },
    {
        "id": "storage-backup",
        "category": "Storage",
        "name": "Backup Service",
        "name-cn": "备份服务",
        "confidence": "high",
        "products": {
            "aws": ["AWS Backup"],
            "azure": ["Azure Backup"],
            "gcp": ["Backup and DR"],
            "alibaba": ["Hybrid Backup Recovery", "Database Backup"],
        },
        "notes": "",
        "notes-cn": "",
    },
    {
        "id": "storage-disaster-recovery",
        "category": "Storage",
        "name": "Application Disaster Recovery",
        "name-cn": "应用容灾恢复",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Elastic Disaster Recovery"],
            "azure": ["Azure Site Recovery"],
            "gcp": [],
        },
        "notes": "Matches the Disaster Recovery Service row in "
        "cloud-compare-en-new.md; the document lists no GCP counterpart "
        "either (GCP's Backup and DR, reused from storage-backup, "
        "covers backup/recovery of data and workloads rather than "
        "full application-level DR orchestration the way this row "
        "means it).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Disaster Recovery "
        "Service 行，文档里 GCP 一侧也是空的（GCP 的 Backup and DR，"
        "在 storage-backup 里也引用了，覆盖的是数据/工作负载的备份恢复，"
        "不是这一行说的完整应用级容灾编排）。",
    },
    {
        "id": "storage-edge-transfer-appliance",
        "category": "Storage",
        "name": "Edge Compute & Data Transfer Appliance",
        "name-cn": "边缘计算与数据传输设备",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Snowball Edge"],
            "azure": ["Azure Data Box"],
            "gcp": ["Transfer Appliance"],
        },
        "notes": "AWS Snowball Edge is a distinct product from "
        "\"AWS Data Transfer Terminal\" (referenced in "
        "mig-data-transfer-device under Migration & Transfer) — Edge "
        "additionally offers on-device edge compute, not just physical "
        "data transport. Azure Data Box and GCP Transfer Appliance are "
        "reused since neither vendor splits the two use cases into "
        "separate products.",
        "notes-cn": "AWS Snowball Edge 和「AWS Data Transfer Terminal」"
        "（在 Migration & Transfer 分类的 mig-data-transfer-device 里"
        "引用）是两个不同的产品——Edge 额外提供设备上的边缘计算能力，不"
        "只是物理数据搬运。Azure Data Box 和 GCP Transfer Appliance 在"
        "这里复用，因为两家都没有把这两种场景拆成独立产品。",
    },
    {
        "id": "storage-gateway",
        "category": "Storage",
        "name": "Hybrid Storage Gateway",
        "name-cn": "混合存储网关",
        "confidence": "low",
        "products": {
            "aws": ["AWS Storage Gateway"],
            "azure": [],
            "gcp": [],
            "alibaba": ["Cloud Storage Gateway"],
        },
        "notes": "Matches the Storage Gateway Service row in "
        "cloud-compare-en-new.md (document lists Azure Storage Gateway, "
        "which doesn't appear in products-azure.json, and GCP's Storage "
        "Transfer Service, already referenced elsewhere under a "
        "cloud-to-cloud transfer lens rather than this on-premises "
        "hybrid-gateway sense, so it isn't reused here).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Storage Gateway "
        "Service 行（文档给的 Azure Storage Gateway 在 "
        "products-azure.json 里查不到；GCP 的 Storage Transfer "
        "Service 已经在别处以「跨云传输」的定位引用过，和这里「本地"
        "混合网关」的含义不是一回事，这里不复用）。",
    },
    # ---------------- Containers ----------------
    {
        "id": "containers-image-repository",
        "category": "Containers",
        "name": "Container Image Repository",
        "name-cn": "容器镜像仓库",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Elastic Container Registry"],
            "azure": ["Azure Container Registry"],
            "gcp": ["Artifact Registry"],
            "alibaba": ["Container Registry"],
        },
        "notes": "GCP's Artifact Registry is reused from "
        "devtools-artifact-repository — Google consolidated its "
        "container-image registry into the same general-purpose "
        "artifact manager rather than keeping a container-specific "
        "product.",
        "notes-cn": "GCP 的 Artifact Registry 在 "
        "devtools-artifact-repository 里也被引用了——Google 把容器镜像"
        "仓库并进了同一个通用制品管理器，没有保留单独的容器专属产品。",
    },
    {
        "id": "containers-run-service",
        "category": "Containers",
        "name": "Managed Container Runtime",
        "name-cn": "托管容器运行服务",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Elastic Container Service"],
            "azure": ["Azure Container Instances"],
            "gcp": ["Cloud Run"],
        },
        "notes": "Azure Container Instances and Cloud Run are reused "
        "from compute-paas-app-hosting / serverless-containers under "
        "this narrower \"run containers without Kubernetes\" lens.",
        "notes-cn": "Azure Container Instances 和 Cloud Run 在"
        "compute-paas-app-hosting / serverless-containers 里也被引用"
        "了，这里是「不用 Kubernetes 直接运行容器」这个更窄的功能定位。",
    },
    {
        "id": "containers-orchestration",
        "category": "Containers",
        "name": "Managed Kubernetes Orchestration",
        "name-cn": "托管 Kubernetes 编排",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Elastic Kubernetes Service"],
            "azure": ["Azure Kubernetes Service (AKS)"],
            "gcp": ["Google Kubernetes Engine documentation"],
            "alibaba": ["Container Service for Kubernetes", "ACK One"],
        },
        "notes": "Azure Kubernetes Service is reused from the Compute "
        "category's unmapped-tracking (it's tagged Compute in "
        "products-azure.json) under this dedicated container-"
        "orchestration lens.",
        "notes-cn": "Azure Kubernetes Service 在 products-azure.json 里"
        "自己的分类标签是 Compute，这里是它专门的容器编排功能定位。",
    },
    {
        "id": "containers-managed-openshift",
        "category": "Containers",
        "name": "Managed Red Hat OpenShift",
        "name-cn": "托管 Red Hat OpenShift",
        "confidence": "high",
        "products": {
            "aws": ["Red Hat OpenShift Service on AWS"],
            "azure": ["Azure Red Hat OpenShift"],
            "gcp": [],
        },
        "notes": "No GCP-managed OpenShift offering was found in this "
        "data set.",
        "notes-cn": "GCP 在这份数据里没有找到托管 OpenShift 产品。",
    },
    {
        "id": "containers-migration-tool",
        "category": "Containers",
        "name": "Application Containerization Tool",
        "name-cn": "应用容器化迁移工具",
        "confidence": "low",
        "products": {
            "aws": ["AWS App2Container"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Containerization Tool row in "
        "cloud-compare-en-new.md; the document lists no Azure/GCP "
        "counterpart either.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Containerization "
        "Tool 行，文档里 Azure/GCP 一侧也是空的。",
    },
    # ---------------- Cryptography & PKI ----------------
    {
        "id": "crypto-tools-and-signing",
        "category": "Cryptography & PKI",
        "name": "Crypto Tools & Code Signing",
        "name-cn": "加密工具与代码签名",
        "confidence": "low",
        "products": {
            "aws": ["AWS Crypto Tools", "AWS Signer"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. AWS Crypto Tools is a developer-focused crypto "
        "library/SDK family, and AWS Signer is a managed code-signing "
        "service for Lambda and IoT — they are grouped together here "
        "as the two Cryptography & PKI entries that aren't already "
        "cross-referenced from sec-certificate-management / sec-hsm / "
        "sec-key-management. No Azure/GCP product with this exact "
        "scope was found in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。AWS Crypto Tools 是面向开发者的密码学库/SDK 家族，AWS "
        "Signer 是面向 Lambda 与 IoT 的托管代码签名服务——两者都不是"
        " sec-certificate-management / sec-hsm / sec-key-management "
        "已交叉引用的那 4 个产品，因此合并为一个分组。Azure/GCP 在这份"
        "数据里都没有查到完全对应的产品。",
    },
    # ---------------- Application Integration ----------------
    {
        "id": "appint-managed-airflow",
        "category": "Application Integration",
        "name": "Managed Apache Airflow",
        "name-cn": "托管 Apache Airflow",
        "confidence": "high",
        "products": {
            "aws": ["Amazon MWAA"],
            "azure": [],
            "gcp": ["Managed Service for Apache Airflow"],
        },
        "notes": "Matches the Workflow Management row in "
        "cloud-compare-en-new.md (document lists the GCP product as "
        "'Cloud Composer', which appears in products-gcp.json under "
        "the name 'Managed Service for Apache Airflow'). Azure has "
        "no managed-Airflow offering in this data set (the document "
        "leaves the Azure column blank).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Workflow Management "
        "行（文档给的 GCP 产品名是 Cloud Composer，在 products-gcp.json "
        "里实际叫 Managed Service for Apache Airflow）。Azure 一侧在此"
        "数据集中没有托管 Airflow 产品（文档对应列也是空白）。",
    },
    {
        "id": "appint-legacy-workflow-orchestration",
        "category": "Application Integration",
        "name": "Legacy Workflow Orchestration",
        "name-cn": "传统工作流编排",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Simple Workflow Service"],
            "azure": ["Logic Apps"],
            "gcp": ["Workflows"],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. Amazon SWF is AWS's legacy workflow service "
        "(AWS now recommends Step Functions for new applications). "
        "Azure Logic Apps and GCP Workflows occupy the same general "
        "'coordinate work across distributed components' category "
        "but are modern low-code/serverless offerings, not strict "
        "equivalents — hence the low confidence.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Amazon SWF 是 AWS 的传统工作流服务（AWS 官方推荐新应用"
        "改用 Step Functions）。Azure Logic Apps 与 GCP Workflows 同属"
        "「跨分布式组件协调工作」这个大类，但都是现代化的低代码/无服务器"
        "产品，并非严格等价——因此置信度为低。",
    },
    {
        "id": "appint-b2b-edi",
        "category": "Application Integration",
        "name": "B2B EDI Data Interchange",
        "name-cn": "B2B EDI 数据交换",
        "confidence": "low",
        "products": {
            "aws": ["AWS B2B Data Interchange"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. No Azure/GCP product specifically branded for "
        "EDI-based B2B transaction exchange was found in this data "
        "set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Azure/GCP 在此数据集中没有单独品牌化的、面向 EDI B2B 交易"
        "交换的产品。",
    },
    # ---------------- Front-End Web & Mobile ----------------
    {
        "id": "frontend-location-service",
        "category": "Front-End Web & Mobile",
        "name": "Location Service",
        "name-cn": "位置服务",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Location Service"],
            "azure": ["Azure Maps"],
            "gcp": [],
        },
        "notes": "Matches the Location Service row in "
        "cloud-compare-en-new.md. GCP's Maps Platform doesn't appear "
        "as a standalone product in products-gcp.json — a known gap "
        "in this data source (see references/gcp.md).",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Location Service 行。"
        "GCP 的 Maps Platform 在 products-gcp.json 里不是独立产品——"
        "这份数据源的已知缺口（见 references/gcp.md）。",
    },
    {
        "id": "frontend-mobile-web-dev-platform",
        "category": "Front-End Web & Mobile",
        "name": "Mobile & Web App Development Platform",
        "name-cn": "移动与 Web 应用开发平台",
        "confidence": "high",
        "products": {
            "aws": ["AWS Amplify"],
            "azure": ["Static Web Apps"],
            "gcp": [],
            "alibaba": ["mPaaS"],
        },
        "notes": "Matches the Mobile and Web Application Development row "
        "in cloud-compare-en-new.md. GCP's Firebase doesn't appear as "
        "a standalone product in products-gcp.json — a known gap in "
        "this data source. Azure Static Web Apps is also referenced "
        "from compute-paas-app-hosting, since its positioning "
        "overlaps both categories.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Mobile and Web "
        "Application Development 行。GCP 的 Firebase 在 products-gcp.json "
        "里不是独立产品——这份数据源的已知缺口。Azure Static Web Apps 在"
        " compute-paas-app-hosting 分组里也被引用，因为它的定位横跨两个"
        "品类。",
    },
    {
        "id": "frontend-mobile-app-testing",
        "category": "Front-End Web & Mobile",
        "name": "Mobile App Testing on Real Devices",
        "name-cn": "真机移动应用测试",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Device Farm"],
            "azure": ["Azure DevTest Labs"],
            "gcp": [],
            "alibaba": ["EMAS Mobile Testing"],
        },
        "notes": "Matches the Mobile Application Testing row in "
        "cloud-compare-en-new.md. Azure DevTest Labs is broader in "
        "scope (general dev/test environment provisioning, not "
        "mobile-real-device-specific), hence the medium confidence. "
        "GCP's Firebase Test Lab doesn't appear as a standalone "
        "product in products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Mobile Application "
        "Testing 行。Azure DevTest Labs 定位更宽（通用开发/测试环境"
        "预配，不专门针对移动真机），因此置信度为中。GCP 的 Firebase "
        "Test Lab 在 products-gcp.json 里不是独立产品。",
    },
    {
        "id": "frontend-amplify-mobile-sdks",
        "category": "Front-End Web & Mobile",
        "name": "AWS Amplify Mobile SDKs",
        "name-cn": "AWS Amplify 移动 SDK",
        "confidence": "low",
        "products": {
            "aws": [
                "AWS Amplify (AWS Mobile SDK for Android)",
                "AWS AmplifyiOS (AWS Mobile SDK for iOS)",
                "AWS Mobile SDK for Unity",
            ],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. These are the platform-specific AWS Amplify "
        "SDKs (Android / iOS / Unity) — they ship as separate "
        "products in products-aws.json but are really one SDK family, "
        "so they're grouped together here. No Azure/GCP product with "
        "the same scope was found in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。这三条都是 AWS Amplify 的平台专属 SDK（Android / iOS / "
        "Unity）——它们在 products-aws.json 里被拆成独立产品，但实际"
        "同属一个 SDK 家族，这里合并为一个分组。Azure/GCP 在此数据集中"
        "没有同范围的产品。",
    },
    {
        "id": "frontend-silk-browser",
        "category": "Front-End Web & Mobile",
        "name": "Cloud-Accelerated Mobile Browser",
        "name-cn": "云加速移动浏览器",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Silk"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. Amazon Silk is AWS's cloud-accelerated mobile "
        "browser (splitting rendering between the device and EC2) — "
        "a unique product category with no Azure/GCP equivalent in "
        "this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Amazon Silk 是 AWS 的云加速移动浏览器（渲染工作在设备与"
        " EC2 之间分摊）——品类独特，Azure/GCP 在此数据集中没有对应"
        "产品。",
    },
    # ---------------- General Reference ----------------
    {
        "id": "genref-support-plan",
        "category": "General Reference",
        "name": "Cloud Support Plan",
        "name-cn": "云支持计划",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Support"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Support Management row in "
        "cloud-compare-en-new.md. The document lists Azure Support "
        "and Google Cloud Support as counterparts, but neither "
        "appears as a standalone product in products-azure.json / "
        "products-gcp.json — both vendors document their support "
        "plans outside the product catalog pages this data set was "
        "scraped from.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Support Management "
        "行。文档给出的对应产品是 Azure Support 和 Google Cloud Support，"
        "但两者都未作为独立产品出现在 products-azure.json / "
        "products-gcp.json 里——这两家厂商把支持计划文档放在本数据集"
        "抓取来源（产品目录页）之外。",
    },
    {
        "id": "genref-aws-docs-and-references",
        "category": "General Reference",
        "name": "AWS Documentation & Reference Pages",
        "name-cn": "AWS 文档与参考页面",
        "confidence": "low",
        "products": {
            "aws": [
                "AWS Diagnostic Tools",
                "AWS Glossary",
                "AWS Lifecycle changes",
                "AWS Security Credentials",
                "AWS Service Endpoints",
                "Service Quotas reference",
                "Tagging AWS Resources",
            ],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. These entries appear in products-aws.json as "
        "'products' but are really documentation/reference pages "
        "(glossary, endpoints list, tagging guide, etc.), not "
        "standalone cloud services — grouped together here so the "
        "category has zero truly-unmapped entries. No Azure/GCP "
        "analog exists at this granularity.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。这些条目在 products-aws.json 里被当作「产品」列出，但"
        "本质上都是文档/参考页面（术语表、端点列表、打标签指南等），"
        "不是独立的云服务——合并为一个分组，让该分类的 trulyUnmapped "
        "清零。Azure/GCP 在此颗粒度上没有可比对的同类条目。",
    },
    # ---------------- End User Computing ----------------
    {
        "id": "euc-virtual-desktop",
        "category": "End User Computing",
        "name": "Virtual Desktop Infrastructure (VDI)",
        "name-cn": "虚拟桌面基础设施（VDI）",
        "confidence": "high",
        "products": {
            "aws": ["Amazon WorkSpaces", "Amazon WorkSpaces Core"],
            "azure": ["Azure Virtual Desktop"],
            "gcp": [],
            "alibaba": ["Elastic Desktop Service"],
        },
        "notes": "Matches the Virtual Desktop row in "
        "cloud-compare-en-new.md. WorkSpaces Core is the bare VDI "
        "control plane for third-party brokers; it shares the "
        "WorkSpaces brand and the same use case as WorkSpaces, so "
        "both sit in this group. GCP has no first-party VDI "
        "offering in this data set.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Virtual Desktop 行。"
        "WorkSpaces Core 是面向第三方代理的裸 VDI 控制面，与 WorkSpaces "
        "同品牌同场景，因此两者归入同一分组。GCP 在此数据集中没有"
        "第一方 VDI 产品。",
    },
    {
        "id": "euc-app-streaming",
        "category": "End User Computing",
        "name": "Application Streaming",
        "name-cn": "应用流式传输",
        "confidence": "high",
        "products": {
            "aws": ["Amazon WorkSpaces Applications"],
            "azure": ["Azure Virtual Desktop"],
            "gcp": [],
        },
        "notes": "Matches the Application Streaming row in "
        "cloud-compare-en-new.md (document lists the AWS product "
        "under its former name 'Amazon AppStream 2.0'; "
        "products-aws.json now calls it 'Amazon WorkSpaces "
        "Applications'). Azure Virtual Desktop covers both full-"
        "desktop and per-app streaming, so it's reused from "
        "euc-virtual-desktop. GCP has no first-party app-streaming "
        "offering in this data set.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Application "
        "Streaming 行（文档中该 AWS 产品使用旧名 Amazon AppStream 2.0，"
        "products-aws.json 现在叫 Amazon WorkSpaces Applications）。"
        "Azure Virtual Desktop 同时覆盖完整桌面和单应用流式传输，因此"
        "从 euc-virtual-desktop 复用。GCP 在此数据集中没有第一方应用"
        "流式传输产品。",
    },
    {
        "id": "euc-secure-browser",
        "category": "End User Computing",
        "name": "Secure Enterprise Browser",
        "name-cn": "安全企业浏览器",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon WorkSpaces Secure Browser"],
            "azure": ["Azure Virtual Desktop"],
            "gcp": [],
        },
        "notes": "Matches the Web Virtual Desktop row in "
        "cloud-compare-en-new.md (document lists the AWS product "
        "as 'Amazon WorkSpaces Web'; products-aws.json calls it "
        "'Amazon WorkSpaces Secure Browser'). Azure Virtual Desktop "
        "provides browser-based access to internal resources, so "
        "it's reused here as the closest counterpart.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Web Virtual Desktop "
        "行（文档给的 AWS 产品名是 Amazon WorkSpaces Web，"
        "products-aws.json 里实际叫 Amazon WorkSpaces Secure "
        "Browser）。Azure Virtual Desktop 提供基于浏览器的内部资源"
        "访问，是最接近的对应产品，在此复用。",
    },
    {
        "id": "euc-remote-display-protocol",
        "category": "End User Computing",
        "name": "Remote Display Protocol",
        "name-cn": "远程显示协议",
        "confidence": "low",
        "products": {
            "aws": ["Amazon DCV"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. Amazon DCV is a high-performance remote "
        "display protocol for graphics-intensive workloads — a "
        "narrower scope than full VDI. No Azure/GCP product with "
        "this exact focus was found in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。Amazon DCV 是面向图形密集型工作负载的高性能远程显示协议，"
        "比完整 VDI 范围更窄。Azure/GCP 在此数据集中没有同焦点的产品。",
    },
    {
        "id": "euc-thin-client-device",
        "category": "End User Computing",
        "name": "Thin Client Device",
        "name-cn": "瘦客户端设备",
        "confidence": "low",
        "products": {
            "aws": ["Amazon WorkSpaces Thin Client"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. A first-party AWS hardware device for "
        "accessing WorkSpaces. No Azure/GCP hardware thin client "
        "was found in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出此行，按产品定位"
        "自拟。这是 AWS 第一方用于访问 WorkSpaces 的硬件设备。Azure/"
        "GCP 在此数据集中没有对应的硬件瘦客户端。",
    },
    # ---------------- Customer Enablement Services ----------------
    {
        "id": "custenable-aws-services-portfolio",
        "category": "Customer Enablement Services",
        "name": "AWS Customer Enablement Portfolio",
        "name-cn": "AWS 客户赋能服务组合",
        "confidence": "low",
        "products": {
            "aws": [
                "AWS Incident Detection and Response",
                "AWS IQ",
                "AWS Managed Services",
                "AWS Professional Services",
                "AWS re:Post Private",
                "AWS Training and Certification",
            ],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart rows in cloud-compare-en-new.md; "
        "self-defined. These are AWS-branded professional services, "
        "managed operations, training, and expert-marketplace "
        "offerings. Azure and GCP have analogous programs (Microsoft "
        "Consulting Services, Google Cloud Professional Services, "
        "etc.) but they're not catalogued as standalone products in "
        "products-azure.json / products-gcp.json. Grouped together "
        "as a single AWS-only portfolio entry.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出对应行，按产品定位"
        "自拟。这些都是 AWS 品牌下的专业服务、托管运维、培训和专家市场"
        "类产品。Azure 与 GCP 有类似的项目（Microsoft Consulting "
        "Services、Google Cloud Professional Services 等），但它们并未"
        "作为独立产品列入 products-azure.json / products-gcp.json。"
        "此处合并为一条 AWS 专属组合条目。",
    },
    # ---------------- AWS Management Console ----------------
    {
        "id": "console-genai-assistant",
        "category": "AWS Management Console",
        "name": "Generative AI Console Assistant",
        "name-cn": "生成式 AI 控制台助手",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon Q"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Intelligent Assistant row in "
        "cloud-compare-en-new.md — the document leaves the Azure "
        "and GCP columns blank for this row. Microsoft's Copilot "
        "for Azure and Google Cloud's Gemini for Cloud exist but "
        "neither appears as a standalone product in "
        "products-azure.json / products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Intelligent "
        "Assistant 行——文档此行 Azure 与 GCP 列均留空。Microsoft "
        "Copilot for Azure 与 Google Cloud 的 Gemini for Cloud 实际"
        "存在，但都未作为独立产品出现在 products-azure.json / "
        "products-gcp.json 里。",
    },
    {
        "id": "console-access-tools",
        "category": "AWS Management Console",
        "name": "Console Access Tools",
        "name-cn": "控制台访问工具",
        "confidence": "low",
        "products": {
            "aws": ["AWS Console Mobile Application", "AWS Sign-In"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart rows in cloud-compare-en-new.md; "
        "self-defined. The Console Mobile App and Sign-In help page "
        "are AWS-specific console access surfaces. Azure and GCP "
        "have equivalent capabilities (Azure mobile app, Google "
        "Cloud Console sign-in) but neither is catalogued as a "
        "standalone product in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出对应行，按产品"
        "定位自拟。Console Mobile App 与 Sign-In 帮助页都是 AWS 专属"
        "的控制台访问入口。Azure 与 GCP 有等价能力（Azure 移动应用、"
        "Google Cloud Console 登录），但都未作为独立产品列入此数据集。",
    },
    # ---------------- Cloud Financial Management ----------------
    {
        "id": "finmgmt-pricing-and-savings-tools",
        "category": "Cloud Financial Management",
        "name": "Pricing & Savings Tools",
        "name-cn": "定价与节省工具",
        "confidence": "low",
        "products": {
            "aws": [
                "AWS Flat-Rate Plans",
                "AWS Pricing Calculator",
                "Savings Plans",
            ],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart rows in cloud-compare-en-new.md; "
        "self-defined. These are AWS-specific pricing / discount "
        "instruments (calculator, flat-rate bundles, Savings Plans). "
        "Azure and GCP have analogous capabilities (Azure Pricing "
        "Calculator, Azure Reservations / Azure Savings Plan for "
        "Compute, GCP Committed Use Discounts) but none are "
        "catalogued as standalone products in products-azure.json / "
        "products-gcp.json. Grouped together here as a single "
        "AWS-only portfolio entry.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出对应行，按产品"
        "定位自拟。这些都是 AWS 特有的定价/折扣工具（成本估算器、"
        "固定费率套餐、Savings Plans）。Azure 与 GCP 有类似能力"
        "（Azure Pricing Calculator、Azure Reservations / Azure "
        "Savings Plan for Compute、GCP Committed Use Discounts），"
        "但都未作为独立产品列入 products-azure.json / products-gcp."
        "json。此处合并为一条 AWS 专属组合条目。",
    },
    # ---------------- Game Development ----------------
    {
        "id": "game-server-hosting-and-streaming",
        "category": "Game Development",
        "name": "Game Server Hosting & Streaming",
        "name-cn": "游戏服务器托管与串流",
        "confidence": "medium",
        "products": {
            "aws": ["Amazon GameLift Servers", "Amazon GameLift Streams"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Game Server Hosting row in "
        "cloud-compare-en-new.md (document lists the AWS product as "
        "'Amazon GameLift'; products-aws.json now splits it into "
        "'GameLift Servers' and 'GameLift Streams'). The document "
        "lists Azure PlayFab as the Azure counterpart, but PlayFab "
        "doesn't appear in products-azure.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Game Server "
        "Hosting 行（文档给的 AWS 产品名是 Amazon GameLift，"
        "products-aws.json 现在拆成了 GameLift Servers 和 GameLift "
        "Streams 两个产品）。文档给的 Azure 对应产品是 Azure PlayFab，"
        "但该产品未列入 products-azure.json。",
    },
    {
        "id": "game-engine",
        "category": "Game Development",
        "name": "Game Engine",
        "name-cn": "游戏引擎",
        "confidence": "low",
        "products": {
            "aws": ["Amazon Lumberyard"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. Lumberyard is AWS's free cross-platform 3D "
        "game engine (upstreamed to Open 3D Engine in 2021; AWS no "
        "longer ships binaries). No Azure/GCP first-party game "
        "engine appears in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出对应行，按产品"
        "定位自拟。Lumberyard 是 AWS 免费的跨平台 3D 游戏引擎（2021 年"
        "已上游至 Open 3D Engine，AWS 不再发布二进制）。Azure/GCP 在此"
        "数据集中没有第一方游戏引擎。",
    },
    # ---------------- Blockchain ----------------
    {
        "id": "blockchain-managed-node",
        "category": "Blockchain",
        "name": "Managed Blockchain Node",
        "name-cn": "托管区块链节点",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Managed Blockchain"],
            "azure": [],
            "gcp": ["Blockchain Node Engine"],
            "alibaba": ["Blockchain as a Service"],
        },
        "notes": "Matches the Blockchain Platform row in "
        "cloud-compare-en-new.md. The document lists the (now-"
        "retired) Azure Blockchain Service for Azure and leaves GCP "
        "blank — both are outdated. Azure Blockchain Service is no "
        "longer in products-azure.json (retired 2021); GCP's "
        "Blockchain Node Engine is the current first-party managed-"
        "blockchain-node offering and is used here as the GCP "
        "counterpart.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Blockchain "
        "Platform 行。文档给的 Azure 对应产品是已停用的 Azure "
        "Blockchain Service，GCP 列留空——两处信息均已过时。Azure "
        "Blockchain Service 已不在 products-azure.json 里（2021 年停"
        "用）；GCP 当前的第一方托管区块链节点产品是 Blockchain Node "
        "Engine，这里用作 GCP 一侧的对应。",
    },
    {
        "id": "blockchain-deployment-templates",
        "category": "Blockchain",
        "name": "Blockchain Deployment Templates",
        "name-cn": "区块链部署模板",
        "confidence": "low",
        "products": {
            "aws": ["AWS Blockchain Templates"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. AWS Blockchain Templates are CloudFormation-"
        "based quick-start templates for self-hosting open-source "
        "blockchain frameworks on EC2/ECS — a deployment-mechanism "
        "offering, not a managed blockchain service.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出对应行，按产品"
        "定位自拟。AWS Blockchain Templates 是基于 CloudFormation 的"
        "快速启动模板，用于在 EC2/ECS 上自托管开源区块链框架——属于"
        "部署机制产品，不是托管区块链服务。",
    },
    # ---------------- Quantum Computing ----------------
    {
        "id": "quantum-computing-platform",
        "category": "Quantum Computing",
        "name": "Quantum Computing Platform",
        "name-cn": "量子计算平台",
        "confidence": "high",
        "products": {
            "aws": ["Amazon Braket"],
            "azure": ["Azure Quantum"],
            "gcp": [],
        },
        "notes": "Matches the Quantum Computing Platform row in "
        "cloud-compare-en-new.md. The document lists Google Quantum "
        "AI as the GCP counterpart, but it doesn't appear as a "
        "standalone product in products-gcp.json.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Quantum Computing "
        "Platform 行。文档给的 GCP 对应产品是 Google Quantum AI，但该"
        "产品未作为独立产品列入 products-gcp.json。",
    },
    # ---------------- Satellite ----------------
    {
        "id": "satellite-ground-station",
        "category": "Satellite",
        "name": "Satellite Ground Station as a Service",
        "name-cn": "卫星地面站即服务",
        "confidence": "medium",
        "products": {
            "aws": ["AWS Ground Station"],
            "azure": [],
            "gcp": [],
        },
        "notes": "Matches the Satellite Ground Station Service row in "
        "cloud-compare-en-new.md. The document lists Azure Orbital "
        "as the Azure counterpart, but Orbital was retired and no "
        "longer appears in products-azure.json. GCP has no first-"
        "party ground-station offering in this data set.",
        "notes-cn": "对应 cloud-compare-en-new.md 的 Satellite Ground "
        "Station Service 行。文档给的 Azure 对应产品是 Azure Orbital，"
        "但 Orbital 已停用，不再列入 products-azure.json。GCP 在此数据"
        "集中没有第一方地面站产品。",
    },
    # ---------------- Partner Central ----------------
    {
        "id": "partner-central-portal",
        "category": "Partner Central",
        "name": "Partner Program Portal",
        "name-cn": "合作伙伴计划门户",
        "confidence": "low",
        "products": {
            "aws": ["AWS Partner Central"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. AWS Partner Central is the portal for AWS "
        "Partner Network (APN) membership. Azure (Microsoft AI "
        "Cloud Partner Program) and GCP (Google Cloud Partner "
        "Advantage) have analogous partner-program portals, but "
        "neither is catalogued as a standalone product in this "
        "data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出对应行，按产品"
        "定位自拟。AWS Partner Central 是 AWS Partner Network（APN）"
        "会员的门户。Azure（Microsoft AI Cloud Partner Program）与 "
        "GCP（Google Cloud Partner Advantage）有类似的合作伙伴计划"
        "门户，但都未作为独立产品列入此数据集。",
    },
    # ---------------- Compute HPC ----------------
    {
        "id": "hpc-research-portal",
        "category": "Compute HPC",
        "name": "Research Collaboration Portal",
        "name-cn": "科研协作门户",
        "confidence": "low",
        "products": {
            "aws": ["Research and Engineering Studio on AWS"],
            "azure": [],
            "gcp": [],
        },
        "notes": "No direct counterpart row in cloud-compare-en-new.md; "
        "self-defined. Research and Engineering Studio on AWS is a "
        "portal-builder for HPC/research collaboration environments "
        "on AWS. No Azure/GCP product with this exact focus was "
        "found in this data set.",
        "notes-cn": "cloud-compare-en-new.md 未单独列出对应行，按产品"
        "定位自拟。Research and Engineering Studio on AWS 是面向 AWS 上"
        " HPC/科研协作环境的门户构建工具。Azure/GCP 在此数据集中没有同"
        "焦点的产品。",
    },
]


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "product"


def load_products(vendor):
    with open(SOURCE_FILES[vendor], encoding="utf-8") as f:
        data = json.load(f)
    return {p["name"]: p for p in data["products"]}


def resolve(name, index, vendor, group_id, require_translation=True):
    product = index.get(name)
    if product is None:
        raise ValueError(
            f"分组 {group_id!r} 引用的 {vendor} 产品 {name!r} 在 "
            f"{SOURCE_FILES[vendor]} 里不存在，检查是不是名字打错了，或者"
            f"数据源更新后产品改名/下线了"
        )
    description_cn = DESCRIPTION_CN.get(vendor, {}).get(name)
    if description_cn is None:
        if require_translation:
            # GROUPS 里精心配对的产品是这份数据真正有价值的部分，翻译质量
            # 要求严格：漏填直接报错，不允许生成缺中文的记录。
            raise ValueError(
                f"分组 {group_id!r} 引用的 {vendor} 产品 {name!r} 在 "
                f"DESCRIPTION_CN 里没有对应的中文描述翻译，补一条再重跑"
            )
        # unmapped 兜底扫描覆盖的是全部三份数据源的产品（跑一次就有
        # 七百多条），这里不强制要求中文翻译——先保证"这个产品有没有被
        # 收进 product-mapping.json"这个更硬的完整性要求，翻译可以后续
        # 慢慢补（补上之后这里会自动读到，不用改代码）。
        description_cn = None
    return {
        "name": product["name"],
        "link": product["link"],
        "description": product["description"],
        "description-cn": description_cn,
    }


def build():
    indexes = {vendor: load_products(vendor) for vendor in SOURCE_FILES}

    # 把每个产品的 categories 字段 canonical 化，避免同一个产品
    # 因为 AWS 叫 "Machine Learning"、Azure 叫 "AI + machine learning"
    # 而被算成两个分类。预处理一次，后面所有按分类的统计都用归一后的。
    canonical_categories_by_vendor = {}
    for vendor, idx in indexes.items():
        canonical_categories_by_vendor[vendor] = {
            name: sorted({canonical_category(c) for c in p["categories"]})
            for name, p in idx.items()
        }

    referenced_by_category = {}  # {(category, vendor): set(names)}
    referenced_globally = {vendor: set() for vendor in SOURCE_FILES}  # 不分类，只看有没有被任何分组引用过
    resolved_groups = []

    for group in GROUPS:
        # GROUPS 里的 category 也走一遍 canonical——容错写法：如果将来
        # 有人误把 Azure/GCP 风格的原始名写进 GROUPS，会被自动归到主名，
        # 不会在输出里出现一个"只有一条分组"的伪分类。
        category = canonical_category(group["category"])
        resolved_products = {}
        for vendor in SOURCE_FILES:
            names = group["products"].get(vendor, [])
            resolved_products[vendor] = [
                resolve(name, indexes[vendor], vendor, group["id"]) for name in names
            ]
            referenced_by_category.setdefault((category, vendor), set()).update(names)
            referenced_globally[vendor].update(names)

        resolved_groups.append(
            {
                "id": group["id"],
                "category": category,
                "category-cn": CATEGORY_LABELS_CN.get(category, ""),
                "name": group["name"],
                "name-cn": group["name-cn"],
                "confidence": group["confidence"],
                "products": resolved_products,
                "notes": group.get("notes", ""),
                "notes-cn": group.get("notes-cn", ""),
            }
        )

    # unmapped 里很容易出现"看着没覆盖，其实已经被别的分类下的分组引用了"
    # 的情况——比如 AWS Lambda 同时挂了 Compute 和 Serverless 两个分类，
    # 只被 serverless-functions 分组引用，在 Compute 分类下按老逻辑算就会
    # 显示成"没人管"，但实际上它已经在映射表里了。这里按分类统计的同时，
    # 再拆一份"是否被任何分组引用过"，避免这种误导。
    #
    # pilot_categories 是 GROUPS 里实际做过精细跨云配对的分类（目前只有
    # AWS 风格的 Compute/Database/Serverless 三个）；all_categories 是三份
    # 数据里出现过的全部分类名（AWS 自己的 30 个、加上 Azure/GCP 各自的
    # 命名，彼此不需要对齐成同一套词表）。unmapped 统计要覆盖
    # all_categories，不能只看 pilot_categories，否则还没做精细分组的
    # 分类里的产品会完全从 product-mapping.json 里消失，不满足"每个产品
    # 都要在这份文件里有体现"的要求。
    pilot_categories = sorted({canonical_category(g["category"]) for g in GROUPS})
    all_categories = sorted(
        set().union(
            *(set(cats) for cats in canonical_categories_by_vendor.values() for cats in cats.values())
        )
    )
    unmapped = {}
    for category in all_categories:
        unmapped[category] = {}
        for vendor in SOURCE_FILES:
            referenced = referenced_by_category.get((category, vendor), set())
            all_in_category = [
                name
                for name, cats in canonical_categories_by_vendor[vendor].items()
                if category in cats
            ]
            leftover = sorted(set(all_in_category) - referenced)

            truly_unmapped_names = [n for n in leftover if n not in referenced_globally[vendor]]
            mapped_under_other_category = [
                n for n in leftover if n in referenced_globally[vendor]
            ]

            # 真正没找到跨云对应关系的产品，也包成和 groups 里一样的形状，
            # 只是当前厂商之外的 products.<vendor> 都是空数组——这样前端
            # 不用为"已配对"和"暂未配对"两种情况写两套渲染逻辑，都当成
            # 一行来处理就行，category/name 直接用这个产品自己在源数据里
            # 的分类和名字，不用我们另外去发明一个分组名。
            #
            # name-cn 故意留空字符串：这些条目的 name 就是产品官方名（如
            # "Amazon EC2"、"Azure Virtual Machines"），按 SKILL.md 的规则
            # 产品官方名称不翻译；空字符串标记"没有人工起过中文显示名"，
            # 前端 transform.js 会自动 fallback 到英文 name 显示，不会出
            # 现空白。不要在这里填一个翻译后的中文名——那会混淆"分组名
            # （可以翻译）"和"产品官方名（不翻译）"的边界。
            truly_unmapped_entries = [
                {
                    "id": f"unmapped-{vendor}-{slugify(name)}",
                    "category": category,
                    "category-cn": CATEGORY_LABELS_CN.get(category, ""),
                    "name": name,
                    "name-cn": "",
                    "confidence": "none",
                    "products": {
                        v: (
                            [
                                resolve(
                                    name,
                                    indexes[vendor],
                                    vendor,
                                    f"unmapped:{category}",
                                    require_translation=False,
                                )
                            ]
                            if v == vendor
                            else []
                        )
                        for v in SOURCE_FILES
                    },
                    "notes": "No confirmed cross-cloud counterpart found yet.",
                    "notes-cn": "尚未找到确认的跨云对应产品。",
                }
                for name in truly_unmapped_names
            ]

            unmapped[category][vendor] = {
                "trulyUnmapped": truly_unmapped_entries,
                "mappedUnderOtherCategory": mapped_under_other_category,
            }

    return {
        "pilotCategories": pilot_categories,
        "allCategories": all_categories,
        "groups": resolved_groups,
        "unmapped": unmapped,
    }


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
    result = build()

    output = {
        "taxonomy": "aws",
        "generatedAt": datetime.date.today().isoformat(),
        "pilotCategories": result["pilotCategories"],
        "allCategories": result["allCategories"],
        "categoryLabels-cn": CATEGORY_LABELS_CN,
        "note": "GROUPS currently only has curated cross-cloud pairings "
        "for the Compute / Database / Serverless categories (see "
        "pilotCategories) — extend GROUPS as needed for the rest. "
        "Matches were cross-checked against the manually maintained "
        "cloud-compare-en-new.md in the repo root. allCategories lists "
        "every category name that actually appears across the three "
        "products-*.json files (AWS's own taxonomy plus Azure's and "
        "GCP's, which use different category names for the same "
        "concepts) — unmapped is computed against this full list, so "
        "every product from every vendor is represented in this file "
        "somewhere, either inside a curated group or as a single-vendor "
        "entry under unmapped.<category>.<vendor>.trulyUnmapped. "
        "Group-level category/name/notes and each product's description "
        "are provided in both English and a \"-cn\" suffixed Chinese "
        "translation for language switching in the UI; official product "
        "names and links are not translated. In `unmapped`, a product "
        "may look uncovered under one category but actually already be "
        "referenced by a group under a different category (a product "
        "can carry multiple category tags) — such items are listed "
        "under `mappedUnderOtherCategory` rather than `trulyUnmapped`.",
        "note-cn": "GROUPS 目前只对 Compute / Database / Serverless 三个"
        "分类做过精细的跨云配对（见 pilotCategories），其余分类还需要"
        "按需扩展 GROUPS。匹配关系参考了仓库根目录下人工维护的"
        "cloud-compare-en-new.md 做交叉校验。allCategories 列出了三份"
        "products-*.json 里实际出现过的全部分类名（AWS 自己的分类体系，"
        "加上 Azure、GCP 各自对同一概念的不同叫法）——unmapped 是按这份"
        "完整分类清单统计的，所以不管精细分组做没做到，每个厂商的每个"
        "产品都会在这份文件里有体现：要么在某个 groups 分组里，要么以"
        "单厂商条目的形式出现在 unmapped.<category>.<vendor>.trulyUnmapped"
        "里。分组层级的 category/name/notes 及每条产品的 description 都"
        "同时提供英文原文和 -cn 后缀的中文翻译，供页面切换语种显示；产品"
        "官方名称和链接不做翻译。`unmapped` 里有些产品看着在某个分类下"
        "没被覆盖，实际上是已经被别的分类下的分组引用了（一个产品可以"
        "同时挂多个分类），这类条目放在 mappedUnderOtherCategory 里，不算"
        "trulyUnmapped。",
        "groups": result["groups"],
        "unmapped": result["unmapped"],
    }

    write_json_with_diff(args.output, output, operation="跨云产品映射重建")

    truly_unmapped_count = sum(
        len(v["trulyUnmapped"]) for cat in result["unmapped"].values() for v in cat.values()
    )
    covered_elsewhere_count = sum(
        len(v["mappedUnderOtherCategory"])
        for cat in result["unmapped"].values()
        for v in cat.values()
    )
    print(
        f"生成 {len(result['groups'])} 个映射分组，试点分类："
        f"{', '.join(result['pilotCategories'])}；覆盖全部 "
        f"{len(result['allCategories'])} 个分类的完整性检查：真正没有被"
        f"任何分组覆盖的产品共 {truly_unmapped_count} 个，另有 "
        f"{covered_elsewhere_count} 个看起来像没覆盖、实际上已经在别的"
        f"分类下被引用了（按分类/厂商列在 "
        f"unmapped.<category>.<vendor>.trulyUnmapped / "
        f".mappedUnderOtherCategory 里）。已写入 {args.output}"
    )


if __name__ == "__main__":
    main()
