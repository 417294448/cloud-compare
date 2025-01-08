# 国内主流云厂商产品对照表

## 目录
- [计算](#计算)
- [容器](#容器) 
- [存储](#存储)
- [数据库](#数据库)
- [网络](#网络)
- [安全](#安全)
- [中间件](#中间件)
- [数据分析与大数据](#数据分析与大数据)
- [人工智能](#人工智能)
- [开发工具](#开发工具)
- [企业应用](#企业应用)
- [物联网](#物联网)
- [视频服务](#视频服务)
- [视频及媒体服务](#视频及媒体服务)
- [数据迁移](#数据迁移)
- [运维管理](#运维管理)
- [解决方案](#解决方案)
- [云通信](#云通信)
- [监控与运维](#监控与运维)
- [媒体处理](#媒体处理)
- [区块链](#区块链)
- [边缘计算](#边缘计算)
- [微服务与API](#微服务与api)
- [云原生中间件](#云原生中间件)
- [云通信增值服务](#云通信增值服务)
- [数据治理](#数据治理)
- [混合云管理](#混合云管理)
- [安全合规](#安全合规)
- [数据智能](#数据智能)
- [云网络优化](#云网络优化)
- [云原生DevOps](#云原生devops)
- [云原生IoT](#云原生iot)

## 计算

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 弹性计算服务器 | 云服务器 ECS | 云服务器 CVM | 弹性云服务器 ECS | 云服务器 BCC | 弹性云主机 | Amazon EC2 |
| 轻量应用服务器 | 轻量应用服务器 SWAS  | 轻量应用服务器 | 轻量应用服务器 | - | 轻量型云主机 | Amazon Lightsail |
| GPU云服务器 | GPU计算型实例 | GPU 云服务器 | GPU加速云服务器 | GPU云服务器 | GPU云主机 | Amazon EC2 P3/P4 |
| 弹性裸金属服务器 | 弹性裸金属服务器 EBM  | 裸金属云服务器 CPM | 裸金属服务器 BMS | 太行·弹性裸金属服务器 | 物理机 | Amazon EC2 Bare Metal |
| 专有宿主机 | 专有宿主机 DDH | 专用宿主机 CDH | 专属主机 DeH | - | 专属服务器 | Amazon EC2 Dedicated Hosts |
| 弹性伸缩 | 弹性伸缩 ESS | 弹性伸缩 AS | 弹性伸缩 AS | 弹性伸缩 | 弹性伸缩服务 | Amazon EC2 Auto Scaling |
| Serverless | 函数计算 FC  | 云函数 SCF | 函数工作流 FunctionGraph | 函数计算 CFC | 函数计算 | AWS Lambda |
| FPGA计算 | FPGA计算服务 FaaS  | FPGA云服务器 | FPGA加速云服务器 | - | - | Amazon EC2 F1 |
| 异构计算 | 异构计算服务 HCS  | 异构计算 | 智能异构云服务器 | 异构计算 | - | AWS Inferentia |
| 弹性高性能计算 | 弹性高性能计算 E-HPC  | 高性能计算 HPC | HPC解决方案 | 高性能计算 HPC | 高性能计算 | AWS ParallelCluster |
| 自动化助手 | - | 自动化助手 | - | - | - | - |

## 容器

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 容器服务 | 容器服务 ACK  | 容器服务 TKE | 云容器引擎 CCE | 容器引擎 CCE | 云容器引擎 | Amazon EKS |
| Serverless 容器 | Serverless 容器服务 ASK | Serverless 容器服务 EKS | 云容器实例 CCI | 容器实例 BCI | Serverless容器引擎 | AWS Fargate |
| 容器镜像服务 | 容器镜像服务 ACR | 容器镜像服务 TCR | 容器镜像服务 SWR | 容器镜像服务 | 容器镜像服务 | Amazon ECR |
| 服务网格 | 服务网格 ASM | 服务网格 TCM | 云服务网格 CSM | 服务网格 | 应用服务网格 | AWS App Mesh |
| 容器镜像加速 | - | 容器镜像加速 | - | - | - | - |

## 存储

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 对象存储 | 对象存储 OSS | 对象存储 COS | 对象存储服务 OBS | 对象存储 BOS | 对象存储 OOS | Amazon S3 |
| 块存储 | 块存储 EBS | 云硬盘 CBS | 云硬盘 EVS | 云硬盘 CDS | 云硬盘 EVS | Amazon EBS |
| 文件存储 | 文件存储 NAS | 文件存储 CFS | 弹性文件服务 EFS | 文件存储 BFS | 文件存储 NAS | Amazon EFS |
| 归档存储 | 归档存储 | 归档存储 CAS | 对象存储服务 OBS | 归档存储 BAS | 归档存储 | Amazon Glacier |
| 混合云存储 | 混合云存储阵列 | 存储网关 CSG | 存储容灾服务 SDRS | 存储网关 | 存储网关 | AWS Storage Gateway |
| 智能数据湖存储 | 智能数据湖存储 HDLS | - | 数据湖存储 DLS | - | - | Amazon S3 Lake Formation |
| 文件存储 CPFS | 文件存储 CPFS | - | 并行文件系统 | - | - | Amazon FSx |
| 存储容量单位包 | 存储容量单位包 SCU | 存储资源包 | 存储包 | 存储资源包 | 存储包 | AWS Savings Plans |
| 云盘备份服务 | 快照 | 快照 | 云备份 CBR | 快照 | 快照 | Amazon EBS Snapshots |
| 混合备份服务 | 混合云备份服务 HBR | 云备份 CBackup | 云备份 CBR | 混合云备份 | 混合云备份 | AWS Backup |
| 分布式文件系统 | 分布式文件系统 CPFS | 文件存储 CFS Turbo | 并行文件系统 | - | - | Amazon FSx for Lustre |
| 对象存储网关 | 对象存储网关 CSG | 存储网关 CSG | 存储网关 SGW | 存储网关 | 存储网关 | AWS Storage Gateway |
| 智能分层存储 | OSS智能分层 | COS智能分层 | OBS智能分层 | - | - | S3 Intelligent-Tiering |
| 数据万象 | - | 数据万象 | - | - | - | - |

## 数据库

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 关系型数据库 MySQL | 云数据库 RDS MySQL | 云数据库 TencentDB for MySQL | 云数据库 RDS MySQL | 云数据库 BaiduDB for MySQL | 云数据库 MySQL | Amazon RDS for MySQL |
| 关系型数据库 PostgreSQL | 云数据库 RDS PostgreSQL | 云数据库 PostgreSQL | 云数据库 PostgreSQL | 云数据库 PostgreSQL | 云数据库 PostgreSQL | Amazon RDS for PostgreSQL |
| 关系型数据库 SQL Server | 云数据库 RDS SQL Server | 云数据库 SQL Server | 云数据库 SQL Server | 云数据库 SQL Server | 云数据库 SQL Server | Amazon RDS for SQL Server |
| 云原生关系型数据库 | 云原生数据库 PolarDB | 云原生数据库 TDSQL-C | 云数据库 GaussDB | - | - | Amazon Aurora |
| 分布式数据库 | 分布式数据库 PolarDB-X | 分布式数据库 TDSQL | 分布式数据库服务 GaussDB | - | - | Amazon Aurora |
| NoSQL数据库 | 云数据库 MongoDB 版 | 云数据库 MongoDB | 文档数据库服务 DDS | 文档数据库 MongoDB | 云数据库 MongoDB | Amazon DocumentDB |
| 内存数据库 | 云数据库 Tair（兼容 Redis） | 云数据库 Redis | 分布式缓存服务 DCS、GaussDB(for Redis) | 云数据库 Redis | 云数据库 Redis | Amazon ElastiCache |
| 时序数据库 | 时序数据库 TSDB | 时序数据库 CTSDB | 时序数据库服务 | - | - | Amazon Timestream |
| 图数据库 | 图数据库 GDB | 图数据库 TGraph | 图数据库服务 GaussDB | - | - | Amazon Neptune |
| 时空数据库 | 时空数据库 Ganos | - | GaussDB(for Geo) | - | - | Amazon TimeStream |
| 数据库代理 | 数据库代理 DProxy | 数据库智能管家 DBbrain | 数据库代理 | - | - | Amazon RDS Proxy |
| 数据库自治服务 | 数据库自治服务 DAS | 数据库智能管家 DBbrain | 数据库治理服务 | - | - | Amazon RDS Proxy |
| 数据库网关 | 数据库网关 DG | 数据库代理 | 数据库网关 | - | - | Amazon RDS Proxy |
| 数据库备份 | 数据库备份服务 DBS | 数据库备份 CDB | 数据库备份服务 | 数据库备份 | 数据库备份 | AWS Backup |
| 数据库智能管家 | - | 数据库智能管家 DBbrain | - | - | - | - |
| 轻量数据库 | - | 轻量数据库 | - | - | - | - |

## 网络

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 负载均衡 | 负载均衡 SLB | 负载均衡 CLB | 弹性负载均衡 ELB | 负载均衡 BLB | 负载均衡 LB | Elastic Load Balancing |
| 专有网络 | 专有网络 VPC | 私有网络 VPC | 虚拟私有云 VPC | 私有网络 VPC | 虚拟私有云 VPC | Amazon VPC |
| CDN | CDN | 内容分发网络 CDN | 内容分发网络 CDN | 内容分发网络 CDN | CDN | Amazon CloudFront |
| VPN网关 | VPN网关 | VPN连接 VPC | VPN网关 VGW | VPN网关 | VPN网关 | AWS VPN |
| NAT网关 | NAT网关 | NAT网关 | NAT网关 | NAT网关 | NAT网关 | AWS NAT Gateway |
| 全球加速 | 全球加速 GA | 全球应用加速 GAAP | 全球加速 GA | - | - | AWS Global Accelerator |
| 云企业网 | 云企业网 CEN | 云联网 CCN | 云连接 CC | 云企业网 | 企业级专网 | AWS Transit Gateway |
| 私网连接 | 私网连接 PrivateLink | 私有连接 | 私网连接 VPC Endpoint | 私网连接 | 私网连接 | AWS PrivateLink |
| 服务网格数据平面 | ASM数据平面 | TCM数据平面 | CSM数据平面 | - | - | AWS App Mesh |
| 容器网络 | 容器服务网络 CNI | 容器网络 CNI | 容器网络 CNI | 容器网络 | 容器网络 | Amazon VPC CNI |
| 网络流日志 | - | 网络流日志 | - | - | - | - |
| Anycast公网加速 | - | Anycast 公网加速 | - | - | - | - |

## 安全

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| DDoS防护 | DDoS高防 | DDoS 防护 | Anti-DDoS流量清洗 | DDoS高防 | DDoS防护 | AWS Shield |
| Web应用防火墙 | Web应用防火墙 WAF | Web应用防火墙 WAF | Web应用防火墙 WAF | Web应用防火墙 WAF | Web应用防火墙 | AWS WAF |
| 云安全中心 | 云安全中心 | 云安全中心 | 主机安全服务 HSS | 主机安全 | 云安全中心 | Amazon GuardDuty |
| 密钥管理 | 密钥管理服务 KMS | 密钥管理系统 KMS | 数据加密服务 DEW | 密钥管理服务 KMS | 密钥管理服务 | AWS KMS |
| 堡垒机 | 堡垒机 | 堡垒机 | 云堡垒机 CBH | 堡垒机 | 堡垒机 | AWS Systems Manager Session Manager |
| 数据安全中心 | 数据安全中心 DSC | 数据安全中心 DSC | 数据安全中心 DSC | 数据安全中心 | 数据安全中心 | Amazon Macie |
| 云安全态势管理 | 云安全态势管理 | 安全运营中心 SOC | 态势感知 SA | 安全中心 | 态势感知 | AWS Security Hub |
| 加密服务 | 加密服务 HSM | 云加密机 HSM | 数据加密服务 DEW | 加密服务 | 加密服务 | AWS CloudHSM |
| 证书服务 | SSL证书 | SSL证书 | SSL证书管理 | SSL证书 | SSL证书 | AWS Certificate Manager |
| 容器安全服务 | 容器安全服务 | 容器安全服务 | 容器安全服务 | 容器安全 | 容器安全 | Amazon ECS Security |
| 云原生防火墙 | 云防火墙 | 云防火墙 | 云防火墙 | 云防火墙 | 云防火墙 | AWS Network Firewall |
| 密码管理服务 | 凭据管家 | 凭据管理系统 | 凭据管理服务 | 密钥管理 | 密钥管理 | AWS Secrets Manager |
| 漏洞扫描 | 漏洞扫描 | 漏洞扫描服务 | 漏洞扫描服务 | 漏洞扫描 | 漏洞扫描 | Amazon Inspector |
| 小程序安全加速 | - | 小程序安全加速 | - | - | - | - |
| API安全 | - | API安全 | - | - | - | - |
| BOT流量管理 | - | BOT流量管理 | - | - | - | - |

## 中间件

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 消息队列 | 消息队列 RocketMQ | 消息队列 CKafka | 分布式消息服务 DMS | 消息队列 BMQ | 消息队列服务 | Amazon MQ |
| 应用服务网格 | 服务网格 ASM | 服务网格 TCM | 应用服务网格 ASM | 服务网格 | 服务网格 | AWS App Mesh |
| API网关 | API网关 | API网关 | API网关服务 APIG | API网关 | API网关 | Amazon API Gateway |
| 企业级分布式服务 | 企业级分布式应用服务 EDAS | 微服务平台 TSF | 应用管理与运维平台 ServiceStage | 微服务引擎 | 微服务平台 | AWS App Runner |
| 分布式任务调度 | 分布式任务调度 SchedulerX | 分布式任务调度 | 分布式任务调度服务 | 分布式任务调度 | 分布式调度服务 | Amazon Managed Workflows |
| 事件总线 | 事件总线 EventBridge | 事件总线 EventBridge | 应用魔方 | 事件中心 | 事件总线 | Amazon EventBridge |
| 配置管理 | 应用配置管理 ACM | 配置中心 | 应用参数配置服务 | 配置服务 | 配置中心 | AWS AppConfig |

## 数据分析与大数据

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 大数据计算 | MaxCompute（原ODPS） | 云数据仓库 CDW | 数据湖探索 DLI | BDL数据湖 | 大数据平台 | Amazon EMR |
| 实时计算 | 实时计算 Flink版 | 流计算 Oceanus | 实时流计算服务 CS | 流式计算 | 流计算服务 | Amazon Kinesis |
| 数据湖 | 数据湖构建 Data Lake Formation | 数据湖计算 DLC | 数据湖治理中心 LakeFormation | 数据湖 | 数据湖 | AWS Lake Formation |
| 可视化大屏 | DataV数据可视化 | 腾讯云图 | 数据可视化 DLV | 数据可视化 Sugar | 数据可视化 | Amazon QuickSight |
| 数据可视化 | 智能商业分析 Quick BI | 腾讯云图 | DataArts Studio | 数据可视化 Sugar | 数据可视化 | Amazon QuickSight |
| 智能推荐 | 智能推荐 AIRec | 推荐系统 | 推荐系统服务 | 智能推荐 | 智能推荐 | Amazon Personalize |
| 实时数仓 | 实时数仓 Hologres | 云数据仓库 | GaussDB(DWS) | - | 实时数仓 | Amazon Redshift |
| 数据开发 | 大数据开发治理平台 DataWorks | 数据开发平台 | DataArts Studio | 数据工厂 | 数据开发 | AWS Glue |
| 数据湖分析 | Data Lake Analytics (DLA) | 数据湖分析 | 数据湖探索 | 数据湖分析 | 数据湖分析 | Amazon Athena |
| 数据仓库 | 云原生数据仓库 AnalyticDB | 云数据仓库 | GaussDB(DWS) | - | 数据仓库 | Amazon Redshift |
| 实时数据集成 | 数据集成 Data Integration | 数据集成 | 数据集成服务 | 数据集成 | 数据集成 | AWS Glue |
| 智能数据建设与治理 | 智能数据建设与治理 Dataphin | - | - | - | - | - |

## 人工智能

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 机器学习平台 | 人工智能平台 PAI | 腾讯云 TI 平台 | ModelArts | BML机器学习 | 机器学习平台 | Amazon SageMaker |
| 语音识别 | 智能语音交互 | 语音识别 | 语音识别服务 SIS | 语音识别 ASR | 语音识别 | Amazon Transcribe |
| 人脸识别 | 人脸人体视觉智能开放平台 | 人脸识别 | 人脸识别服务 Face | 人脸识别 | 人脸识别 | Amazon Rekognition |
| 自然语言处理 | 自然语言处理 NLP | 自然语言处理 | 自然语言处理基础服务 NLP | 自然语言处理 NLP | 自然语言处理 | Amazon Comprehend |
| 大模型服务 | 通义大模型 | 混元大模型 | 盘古大模型 | 文心大模型 | - | Amazon Bedrock |
| 智能对话机器人 | 智能对话机器人 | 智能客服 | 智能对话机器人 | 智能对话平台 UNIT | 智能客服 | Amazon Lex |
| 机器学习可视化 | PAI-DSW | TI-ONE | ModelArts-Notebook | BML-Notebook | - | Amazon SageMaker Studio |
| 向量检索服务 | 向量检索服务 Proxima | 向量数据库 | 向量检索服务 | 向量检索引擎 | - | Amazon Kendra |
| AI开发平台 | PAI-DSW | TI-ONE | ModelArts | BML | AI开发平台 | SageMaker Studio |
| 模型训练 | PAI-Training | TI-Training | ModelArts-Training | BML-Training | 模型训练 | SageMaker Training |
| 模型服务 | PAI-EAS | TI-EMS | ModelArts-Serving | BML-Serving | 模型服务 | SageMaker Endpoints |
| AI推理加速 | PAI-Inference | TI-Inference | ModelArts-Inference | - | - | AWS Inferentia |
| 智能翻译 | - | 腾讯同传 | - | - | - | - |
| 智能数智人 | - | 腾讯智能数智人 | - | - | - | - |
| 大模型知识引擎 | - | 大模型知识引擎 | - | - | - | - |
| 大模型图像创作引擎 | - | 大模型图像创作引擎 | - | - | - | - |
| 大模型视频创作引擎 | - | 大模型视频创作引擎 | - | - | - | - |

## 开发工具

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 云IDE | Cloud Shell | Cloud Studio | CloudIDE | Cloud IDE | 云IDE | AWS Cloud9 |
| DevOps | 云效 | CODING DevOps | 软件开发生产线 CloudPipeline | DevOps平台 | DevOps平台 | AWS CodeStar |
| 应用监控 | ARMS | 应用性能监控 APM | 应用性能管理 APM | 应用性能监控 APM | 应用性能监控 | Amazon CloudWatch |
| 日志服务 | 日志服务 SLS | 日志服务 CLS | 日志服务 LTS | 日志服务 BLS | 日志服务 | Amazon CloudWatch Logs |
| 云原生应用平台 | 云原生应用平台 ACAP | 云原生应用平台 | 云原生应用平台 | 云原生平台 | 云原生平台 | AWS App Runner |
| 应用托管 | 轻量应用服务器 | 应用托管平台 | 应用管理服务 | 应用引擎 | 应用托管 | AWS Elastic Beanstalk |

## 企业应用

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 邮件推送 | 邮件推送 | 邮件推送 | 消息通知服务 SMN | 邮件推送 | 邮件服务 | Amazon SES |
| 短信服务 | 短信服务 | 短信 SMS | 消息通知服务 SMN | 短信服务 | 短信服务 | Amazon SNS |
| 区块链服务 | 区块链服务 BaaS | 区块链服务 TBaaS | 区块链服务 BCS | 区块链服务 | 区块链服务 | Amazon Managed Blockchain |

## 物联网

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 物联网平台 | 物联网平台 IoT Platform | 物联网通信 IoT Hub | 设备接入服务 IoTDA | 物联网核心套件 IoT Core | 物联网平台 | AWS IoT Core |
| 物联网边缘计算 | 物联网边缘计算 | 物联网边缘计算 IoT Edge | 智能边缘平台 IEF | 物联网边缘计算 BEC | 边缘计算 | AWS IoT Greengrass |

## 视频及媒体服务

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 视频点播 | 视频点播 | 云点播 VOD | 视频点播服务 VOD | 视频点播 VOD | 视频点播 | Amazon Video on Demand |
| 视频直播 | 视频直播 | 云直播 CSS | 视频直播服务 Live | 视频直播 LSS | 视频直播 | Amazon Interactive Video Service |
| 实时音视频 | 音视频通信 RTC | 实时音视频 TRTC | 实时音视频服务 RTC | 音视频服务 RTC | 实时音视频 | Amazon Chime SDK |
| 媒体处理 | 媒体处理 MPS | 媒体处理 MPS | 媒体处理服务 MPC | 媒体处理 MCP | 媒体处理 | AWS Elemental MediaConvert |
| 智能媒体管理 | 智能媒体管理 IMM | 数字媒体 | 媒体资产管理 | 智能媒体服务 | 媒体管理 | AWS Elemental MediaStore |
| 音视频转码 | 音视频转码 | 音视频转码 | 音视频转码服务 | 音视频转码 | 转码服务 | AWS Elemental MediaLive |
| 云导播台 | - | 云导播台 | - | - | - | - |
| 智能创作 | - | 智能创作 | - | - | - | - |
| 云智绘 | - | 腾讯云智绘 | - | - | - | - |

## 数据迁移

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 数据传输 | 数据传输服务 DTS | 数据传输服务 DTS | 数据复制服务 DRS | 数据传输服务 | 数据传输服务 | AWS Database Migration Service |
| 离线迁移 | 闪电立方 | 迁移服务平台 MSP | 主机迁移服务 SMS | 主机迁移 | 主机迁移服务 | AWS Migration Hub |
| 在线迁移 | 服务器迁移中心 SMC | 云服务器迁移 | 主机迁移服务 SMS | 在线迁移 | 在线迁移 | AWS Application Migration Service |

## 运维管理

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 云管理与治理 | 云管家 | 云管理平台 TStack | 云管理中心 | 云管理平台 | 云管理平台 | AWS Control Tower |
| 资源编排 | 资源编排服务 ROS | 资源编排 TIC | 资源模板服务 RTS | 资源编排 | 资源编排 | AWS CloudFormation |
| 标签管理 | 标签管理 | 标签 | 标签管理服务 TMS | 标签管理 | 标签管理 | AWS Resource Groups & Tag Editor |
| 配额中心 | 配额中心 | 配额管理 | 配额中心 | 配额管理 | 配额管理 | Service Quotas |

## 解决方案

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 混合云解决方案 | 混合云解决方案 | 混合云解决方案 | 混合云解决方案 | 混合云解决方案 | 混合云解决方案 | AWS Outposts |
| 数字化转型 | 数字化转型解决方案 | 数字化转型方案 | 数字化转型方案 | 智能云解决方案 | 数字化转型方案 | AWS Digital Transformation |
| 行业解决方案 | 行业云解决方案 | 行业解决方案 | 行业云解决方案 | 行业解决方案 | 行业云方案 | AWS Industry Solutions |

## 云通信

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 语音通信 | 语音服务 | 语音消息 | 语音通话 | 智能语音 | 语音通信 | Amazon Connect |
| 号码隐私保护 | 号码隐私保护 | 号码保护 | 隐私保护通话 | 号码隐私保护 | 号码保护 | - |
| 通信网络 | 云通信网络 | 云联网 | 云专线 | 云专线 | 专线服务 | AWS Direct Connect |

## 监控与运维

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 运维编排 | 运维编排服务 OOS | 自动化助手 TAT | 云自动化服务 | 运维编排 | 运维编排 | AWS Systems Manager |
| 访问控制 | 访问控制 RAM | 访问管理 CAM | 统一身份认证服务 IAM | 访问控制 | 访问控制 | AWS IAM |
| 成本管理 | 成本管理 | 费用中心 | 成本管理 | 成本管理 | 成本管理 | AWS Cost Explorer |
| 应用监控 | 云监控 CMS | 云监控 CM | 应用运维管理 AOM | 云监控 | 云监控 | Amazon CloudWatch |
| 基础设施监控 | 云监控 CMS | 云监控 CM | 云监控服务 CES | 云监控 | 云监控 | Amazon CloudWatch |
| 日志监控 | 日志服务 SLS | 日志服务 CLS | 日志服务 LTS | 日志服务 | 日志服务 | Amazon CloudWatch Logs |
| 链路追踪 | 链路追踪 Xtrace | 分布式追踪 | 应用性能管理 APM | 分布式追踪 | 链路追踪 | AWS X-Ray |
| 应用性能监控 | ARMS | 应用性能监控 APM | 应用性能管理 APM | APM | APM | Amazon CloudWatch |
| 智能运维平台 | AIOPS | 智能运维平台 | 智能运维服务 | 智能运维 | 智能运维 | Amazon DevOps Guru |
| 监控告警 | 云监控告警 | 监控告警 | 应用运维监控 | 监控告警 | 监控告警 | Amazon CloudWatch |
| 日志分析 | 日志分析服务 | 日志分析 | 日志分析服务 | 日志分析 | 日志分析 | Amazon CloudWatch Logs Insights |
| 运维大盘 | 运维大盘 | 云监控大盘 | 监控面板 | 监控大盘 | 运维大盘 | Amazon CloudWatch Dashboard |


## 区块链

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 区块链平台 | 区块链服务 BaaS | 区块链服务 TBaaS | 区块链服务 BCS | 区块链引擎 BBE | 区块链平台 | Amazon Managed Blockchain |
| 联盟链 | 区块链联盟链 | 联盟链 | 联盟链服务 | 超级链 | 联盟链 | Amazon Quantum Ledger Database |
| 智能合约 | 智能合约 | 智能合约 | 智能合约服务 | 智能合约 | 智能合约 | AWS Blockchain Templates |
| 区块链数据服务 | - | 区块链数据服务 | - | - | - | - |
| 可信计算 | - | 可信计算 | - | - | - | - |

## 边缘计算

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 边缘节点服务 | 边缘节点服务 ENS | 边缘计算机器 ECM | 智能边缘云 IEC | 边缘计算节点 | 边缘节点 | AWS Wavelength |
| 边缘实例 | 边缘实例 | 边缘实例 | 边缘实例 | 边缘实例 | 边缘实例 | AWS Outposts |
| 边缘存储 | 边缘存储 | 边缘存储 | 边缘存储 | 边缘存储 | 边缘存储 | AWS Storage Gateway |

## 微服务与API

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 微服务注册配置中心 | 应用配置管理 ACM | 微服务注册中心 TSF | 应用服务网格 CSE | 微服务引擎 | 服务注册中心 | AWS App Mesh |
| 分布式事务 | 分布式事务服务 DTX | 分布式事务 DTF | 分布式事务服务 DTS | - | - | Amazon QLDB |
| API开发管理 | API开发管理 | API开发管理 | API Explorer | API管理 | API管理平台 | AWS API Gateway |

## 云原生中间件

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 微服务引擎 | 微服务引擎 MSE | 微服务引擎 TSE | 微服务引擎 CSE | 微服务引擎 | 微服务引擎 | AWS App Mesh |
| 消息队列Kafka | 消息队列Kafka | 消息队列Kafka | 分布式消息服务Kafka | 消息队列Kafka | 消息队列Kafka | Amazon MSK |
| 消息队列MQTT | 微消息队列MQTT | 消息队列MQTT | IoT消息队列 | 物联网消息队列 | 物联网消息队列 | AWS IoT Core |

## 云通信增值服务

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 智能联络中心 | 智能联络中心 | 云呼叫中心 | 云呼叫中心 | 智能客服 | 云呼叫中心 | Amazon Connect |
| 号码认证服务 | 号码认证服务 | 号码认证 | 号码认证服务 | - | 号码认证 | - |
| 语音验证码 | 语音验证码 | 语音验证码 | 语音验证码 | 语音验证码 | 语音验证码 | Amazon Pinpoint |

## 数据治理

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 数据资产管理 | 数据资产管理 | 数据资产中心 | 数据资产管理服务 | 数据资产管理 | 数据资产管理 | AWS Glue Data Catalog |
| 数据质量管理 | 数据质量 DQC | 数据质量管理 | 数据质量管理 | 数据质量管理 | 数据质量管理 | AWS Glue DataBrew |
| 数据安全治理 | 敏感数据保护 | 数据安全治理 | 数据安全中心 | 数据安全治理 | 数据安全治理 | Amazon Macie |
| 数据建模 | 数据建模 | 数据建模工具 | 数据建模服务 | 数据建模 | - | AWS Database Migration Service |

## 混合云管理

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 混合云控制台 | 混合云管理平台 | 混合云管理平台 | 云管理中心 | 混合云管理 | 混合云管理平台 | AWS Systems Manager |
| 云连接器 | 云连接器 | 云连接器 | 云专线 | 专线接入 | 云专线 | AWS Direct Connect |
| 多云管理 | 多云管理平台 | 多云管理 | 多云管理服务 | - | 多云管理 | AWS Control Tower |
| 云灾备 | 混合云容灾 | 云灾备 | 云容灾服务 | 容灾服务 | 灾备服务 | AWS Elastic Disaster Recovery |

## 安全合规

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 等保合规 | 等保合规 | 等保合规 | 等保合规服务 | 等保合规 | 等保合规 | AWS Artifact |
| 隐私计算 | 隐私计算服务 | 隐私计算 | 隐私计算服务 | 隐私计算平台 | 隐私计算 | AWS Clean Rooms |
| 合规审计 | 操作审计 ActionTrail | 云审计 CloudAudit | 云审计服务 CTS | 操作审计 | 操作审计 | AWS CloudTrail |
| 风险识别 | 云安全中心 | 安全中心 | 企业主机安全 | 安全中心 | 安全中心 | Amazon Inspector |

## 数据智能

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 智能对话分析 | 智能对话分析 | 智能对话分析 | 会话分析服务 | 智能会话分析 | 会话分析 | Amazon Contact Lens |
| 智能文档处理 | 智能文档服务 | 文字识别 OCR | 文字识别服务 | 文字识别 OCR | 文档识别 | Amazon Textract |
| 智能搜索 | 开放搜索 OpenSearch | 云搜 TCS | 云搜索服务 CSS | 智能搜索 | 智能搜索 | Amazon OpenSearch |
| 知识图谱 | DataV知识图谱 | 知识图谱 | 知识图谱服务 | 知识图谱 | 知识图谱 | Amazon Neptune |


## 云网络优化

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 智能路由 | 智能接入网关 SAG | SD-WAN 接入服务 | 软件定义广域网 SD-WAN | 智能接入 | SD-WAN | AWS Cloud WAN |
| 网络质量监控 | 网络质量监控 | 网络分析 | 网络质量监控 | 网络监控 | 网络监控 | Amazon VPC Flow Logs |
| 流量调度 | 全局流量管理 GTM | 智能解析 DNS | 云解析服务 DNS | 智能DNS | 智能DNS | Amazon Route 53 |
| 网络加速 | 全站加速 DCDN | 全站加速网络 ECDN | 全站加速服务 DCDN | 全站加速 | 全站加速 | Amazon CloudFront |


## 云原生DevOps

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| 持续集成/交付 | 云效 FLOW | CODING CI/CD | CloudPipeline | DevOps平台 | DevOps平台 | AWS CodePipeline |
| 制品管理 | 云效制品仓库 | CODING 制品库 | 软件仓库 | 制品仓库 | 制品仓库 | AWS CodeArtifact |
| 代码扫描 | 云效代码扫描 | 代码分析 | 代码检查 | 代码分析 | 代码检查 | Amazon CodeGuru |
| 配置管理 | 配置管理 ACM | 配置平台 | 配置管理 | 配置中心 | 配置管理 | AWS AppConfig |

## 云原生IoT

| 服务类型 | 阿里云 | 腾讯云 | 华为云 | 百度云 | 天翼云 | AWS |
|---------|--------|--------|--------|---------|---------|-----|
| IoT设备管理 | IoT物联网平台 | IoT Explorer | IoT设备接入 | IoT Core | IoT平台 | AWS IoT Core |
| IoT边缘计算 | Link Edge | IoT Edge | IEF | IoT Edge | 边缘计算 | AWS IoT Greengrass |
| IoT数据分析 | IoT数据分析 | IoT数据分析 | IoT数据分析 | IoT分析 | IoT分析 | AWS IoT Analytics |
| IoT安全服务 | IoT安全服务 | IoT安全服务 | IoT安全服务 | IoT安全 | IoT安全 | AWS IoT Device Defender |
