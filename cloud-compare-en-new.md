# 国际主流云厂商产品对照表

## 目录 （Catalog）
- [分析服务 (Analytics)](#分析服务-analytics)
- [应用集成 (Application Integration)](#应用集成-application-integration)
- [区块链 (Blockchain)](#区块链-blockchain)
- [业务应用 (Business Applications)](#业务应用-business-applications)
- [计算服务 (Compute)](#计算服务-compute)
- [容器服务 (Containers)](#容器服务-containers)
- [数据库 (Database)](#数据库-database)
- [开发者工具 (Developer Tools)](#开发者工具-developer-tools)
- [最终用户计算 (End User Computing)](#最终用户计算-end-user-computing)
- [前端 Web 和移动 (Front-end Web & Mobile)](#前端-web-和-移动-front-end-web--mobile)
- [游戏开发 (Game Development)](#游戏开发-game-development)
- [物联网 (Internet of Things)](#物联网-internet-of-things)
- [机器学习 (Machine Learning)](#机器学习-machine-learning)
- [管理与治理 (Management & Governance)](#管理与治理-management--governance)
- [媒体服务 (Media Services)](#媒体服务-media-services)
- [迁移与传输 (Migration & Transfer)](#迁移与传输-migration--transfer)
- [网络与内容分发 (Networking & Content Delivery)](#网络与内容分发-networking--content-delivery)
- [安全、身份与合规 (Security, Identity & Compliance)](#安全身份与合规-security-identity--compliance)
- [存储服务 (Storage)](#存储服务-storage)
- [量子计算 (Quantum Technologies)](#量子计算-quantum-technologies)
- [机器人技术 (Robotics)](#机器人技术-robotics)
- [卫星 (Satellite)](#卫星-satellite)
- [混合与多云 (Hybrid + Multicloud)](#混合与多云-hybrid--multicloud)
- [域名注册 (Domain Registration)](#域名注册-domain-registration)

## 分析服务 (Analytics)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Interactive Query Analysis <br>交互式查询分析 | Amazon Athena | Azure Synapse Analytics | BigQuery | Analytics Cloud | Data Lake Analytics | IBM Cloud SQL Query |
| Search Service <br>搜索服务 | Amazon CloudSearch | Azure Cognitive Search | Cloud Search | OCI Search with OpenSearch | OpenSearch | IBM Watson Discovery |
| Data Governance <br>数据治理 | Amazon DataZone | Microsoft Purview | Dataplex | Data Catalog | DataWorks | IBM Watson Knowledge Catalog |
| Big Data Processing <br>大数据处理 | Amazon EMR | Azure HDInsight | Dataproc | Big Data Service | E-MapReduce | IBM Analytics Engine |
| Real-time Stream Processing <br>实时流处理 | Amazon Kinesis Data Streams | Azure Stream Analytics | Dataflow | Streaming | Realtime Compute | IBM Streaming Analytics |
| Data Stream Transfer <br>数据流传输 | Amazon Kinesis Data Firehose | Azure Event Hubs | Cloud Pub/Sub | Streaming | DataHub | IBM Event Streams |
| Stream Analytics <br>流分析 | Amazon Kinesis Data Analytics | Azure Stream Analytics | Dataflow | Streaming Analytics | Realtime Compute | IBM Streaming Analytics |
| Search and Analytics Engine <br>搜索与分析引擎 | Amazon OpenSearch Service | Azure OpenSearch Service | - | Search Service | OpenSearch | IBM Watson Discovery |
| Data Warehouse <br>数据仓库 | Amazon Redshift | Azure Synapse Analytics | BigQuery | Autonomous Data Warehouse | MaxCompute | IBM Db2 Warehouse |
| ETL Service <br>ETL服务 | AWS Glue | Azure Data Factory | Cloud Data Fusion | Data Integration | DataWorks | IBM DataStage |
| Data Exploration Service <br>数据探索服务 | - | Azure Data Explorer | - | - | - |
| Open Datasets <br>开放数据集 | - | Azure Open Datasets | Google Cloud Public Datasets | - | - |
| Data Lake Analytics <br>数据湖分析 | AWS Lake Formation | Azure Data Lake Analytics | Cloud Storage | Data Lake Analytics | Data Lake Analytics | IBM Cloud Object Storage |
| Time Series Analytics <br>时序分析 | Amazon Timestream | Azure Time Series Insights | Cloud IoT Core | - | Time Series Database | IBM Cloud Databases |
| Data Lake Storage <br>数据湖存储 | Amazon S3 | Azure Data Lake Storage | Cloud Storage | Object Storage | Data Lake Storage | IBM Cloud Object Storage |
| Data Pipeline <br>数据管道 | AWS Data Pipeline | Azure Data Factory | Cloud Dataflow | Data Integration | DataWorks | IBM DataStage |
| Data Visualization & Business Intelligence <br>数据可视化与商业智能 | Amazon QuickSight | Power BI | Looker Studio | Analytics Cloud | Quick BI | IBM Cognos Analytics |
| Data Sharing <br>数据共享 | AWS Data Exchange | Azure Data Share | Analytics Hub | - | - | - |
| Anomaly Detection <br>异常检测 | Amazon Lookout for Metrics | Azure Metrics Advisor | Cloud Monitoring | Anomaly Detection | - | IBM Cloud Monitoring |
| Data Lake Query <br>数据湖查询 | Amazon Athena | Azure Synapse Analytics | BigQuery | Analytics Cloud | Data Lake Analytics | IBM Cloud SQL Query |
| Log Service <br>日志服务 | Amazon CloudWatch Logs | Azure Monitor | Cloud Logging | - | Log Service | IBM Log Analysis |
| Data Quality <br>数据质量 | AWS Glue DataBrew | Azure Data Factory | Cloud Dataprep | - | - | IBM Watson Knowledge Catalog |
| Data Catalog <br>数据目录 | AWS Glue Data Catalog | Azure Purview | Data Catalog | - | - | IBM Watson Knowledge Catalog |
| Spark-based analytics <br>基于Spark的分析 | - | Azure Databricks | - | - | - | - |

## 应用集成 (Application Integration)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Application Integration Service <br>应用集成服务 | Amazon AppFlow | Azure Logic Apps | Cloud Data Fusion | Integration Cloud Service | Cloud Service Bus | IBM App Connect |
| Event Bus <br>事件总线 | Amazon EventBridge | Azure Event Grid | Eventarc | Events Service | EventBridge | IBM Event Streams |
| Message & Task Queue <br>消息与任务队列 | Amazon SQS | Azure Queue Storage | Cloud Tasks | Queue Service | Message Queue | IBM MQ |
| Message Notification Service <br>消息通知服务 | Amazon SNS | Azure Notification Hubs | Cloud Pub/Sub | Notifications | Message Service | IBM Event Notifications |
| Message Middleware <br>消息中间件 | Amazon MQ | Azure Service Bus | - | Messaging | Message Queue | IBM MQ |
| Message Queue <br>消息队列 | Amazon SQS | Azure Queue Storage | Cloud Tasks | Queue Service | Message Queue | IBM MQ |
| Service Bus <br>服务总线 | Amazon MQ | Azure Service Bus | Pub/Sub | Oracle Integration Cloud | Message Queue | IBM Event Streams |
| GraphQL API Service <br>GraphQL API服务 | AWS AppSync | Azure API Management | Cloud Endpoints | API Gateway | API Gateway | IBM API Connect |
| Workflow Orchestration <br>工作流编排 | AWS Step Functions | Azure Logic Apps | Workflows | Workflow | Serverless Workflow | IBM Cloud Pak for Integration |
| API Gateway <br>API网关 | Amazon API Gateway | Azure API Management | Cloud Endpoints, API Gateway | API Gateway | API Gateway | IBM API Connect |
| Workflow Management <br>工作流管理 | Amazon MWAA | - | Cloud Composer | Workflow | - | IBM Cloud Pak for Business Automation |
| Integration Platform <br>集成平台 | - | Azure Integration Services | Cloud Integration | Integration Cloud | Cloud Integration | IBM Cloud Integration |
| API Design & Testing <br>API设计与测试 | - | Azure API Management | Cloud Endpoints | API Gateway | API Gateway | IBM API Connect |
| API Lifecycle Management <br>API生命周期管理 | - | Azure API Management | Apigee | API Gateway | API Gateway | IBM API Connect |
| Task Scheduling <br>任务调度 | Amazon EventBridge | Azure Logic Apps | Cloud Scheduler | - | - | IBM Cloud Scheduler |
| Process Automation <br>流程自动化 | AWS Step Functions | Azure Logic Apps | Cloud Workflows | Process Automation | - | IBM Cloud Pak for Business Automation |
| Queue Service <br>队列服务 | Amazon SQS | Azure Queue Storage | Cloud Tasks | Queue | Message Queue | IBM MQ |
| Enterprise Service Bus <br>企业服务总线 | Amazon MQ | Azure Service Bus | - | - | Enterprise Service Bus | IBM App Connect Enterprise |
| Microservices Governance <br>微服务治理 | AWS App Mesh | Azure Service Fabric | - | - | Microservices Engine | IBM Cloud Pak for Integration |
| Flow Control Service <br>流量控制服务 | AWS CodePipeline | Azure Pipelines | Cloud Build | - | Flow Control Service | IBM Cloud Continuous Delivery |
| Event Management <br>事件管理 | Amazon EventBridge | Azure Event Grid | Cloud Pub/Sub | - | EventBridge | IBM Cloud Event Management |
| API Gateway Analytics <br>API网关分析 | - | Azure API Management | API Analytics | - | - | IBM API Connect Analytics |

## 区块链 (Blockchain)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Blockchain Platform <br>区块链平台 | Amazon Managed Blockchain | Azure Blockchain Service (已停用) | - | Blockchain Platform | Blockchain as a Service | IBM Blockchain Platform |
| Distributed Ledger <br>分布式账本 | Amazon QLDB | - | - | - | Blockchain as a Service | IBM Blockchain Platform |

## 业务应用 (Business Applications)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Intelligent Assistant <br>智能助手 | Amazon Q | - | - | Oracle Intelligent Advisor | Intelligent Speech Interaction | IBM Watson Assistant |
| Collaboration Communication <br>协作通信 | Amazon Chime | Microsoft Teams | Google Meet | - | DingTalk | IBM Cloud Unified Communications |
| Call Center <br>呼叫中心 | Amazon Connect | Azure Communication Services | - | - | Cloud Call Center | IBM Voice Gateway |
| Low-Code Platform <br>低代码平台 | Amazon Honeycode | Power Apps | AppSheet | - | Low-Code Development | IBM Cloud Pak for Business Automation |
| Customer Interaction Service <br>客户互动服务 | Amazon Pinpoint | Azure Communication Services | Firebase Cloud Messaging | Digital Assistant | Message Push | IBM Watson Assistant |
| Email Service <br>电子邮件服务 | Amazon SES | Azure Communication Services | - | Email Delivery | DirectMail | IBM Cloud Email Service |
| Document Collaboration <br>文档协作 | Amazon WorkDocs | SharePoint | Google Drive | - | Workplace | IBM Cloud Document Services |
| Enterprise Email <br>企业邮箱 | Amazon WorkMail | Exchange Online | Google Workspace | - | Alibaba Mail | IBM Cloud Mail |
| Supply Chain Management <br>供应链管理 | AWS Supply Chain | - | - | Logistics Cloud | - | IBM Sterling Supply Chain |
| Encryption Communication <br>加密通信 | AWS Wickr | - | - | - | - | IBM Cloud Security |
| Enterprise Resource Planning <br>企业资源规划 | - | - | - | Fusion Cloud ERP | - | IBM Cloud for SAP |

## 计算服务 (Compute)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Virtual Server <br>虚拟服务器 | Amazon EC2 | Azure Virtual Machines | Compute Engine | Compute | ECS | IBM Cloud Virtual Servers |
| Auto Scaling <br>自动扩缩容 | Amazon EC2 Auto Scaling | Azure VM Scale Sets | Managed Instance Groups | Autoscaling | Auto Scaling | IBM Cloud Auto Scale |
| Container Image Repository <br>容器镜像仓库 | Amazon Elastic Container Registry | Azure Container Registry | Artifact Registry | Container Registry | Container Registry | IBM Cloud Container Registry |
| Container Service <br>容器服务 | Amazon Elastic Container Service | Azure Container Instances | Cloud Run | Container Instances | Container Service | IBM Cloud Container Service |
| Container Orchestration Service <br>容器编排服务 | Amazon Elastic Kubernetes Service | Azure Kubernetes Service | Google Kubernetes Engine | Kubernetes Engine (OKE) | ACK | IBM Cloud Kubernetes Service |
| Lightweight Virtual Server <br>轻量级虚拟服务器 | Amazon Lightsail | Azure App Service | App Engine | - | Simple Application Server | IBM Cloud Code Engine |
| Container Application Platform <br>容器应用平台 | AWS App Runner | Azure Container Apps | Cloud Run | Container Instance | SAE | IBM Cloud Code Engine |
| Batch Processing <br>批处理 | AWS Batch | Azure Batch | Cloud Batch | - | Batch Compute | IBM Cloud Batch Service |
| Application Hosting Platform <br>应用托管平台 | AWS Elastic Beanstalk | Azure App Service | App Engine | - | Web App Service | IBM Cloud Foundry |
| Serverless Computing <br>无服务器计算 | AWS Lambda | Azure Functions | Cloud Functions | Functions | Function Compute | IBM Cloud Functions |
| Local Region Service <br>本地化区域服务 | AWS Local Zones | Azure Local Zones | - | - | Edge Node Service | IBM Cloud Satellite |
| Hybrid Cloud Service <br>混合云服务 | AWS Outposts | Azure Stack | Anthos | - | Alibaba Cloud Apsara Stack | IBM Cloud Satellite |
| High-Performance Computing Cluster <br>高性能计算集群 | AWS ParallelCluster | Azure CycleCloud | Slurm on GCP | - | E-HPC | IBM Spectrum LSF |
| Edge Computing <br>边缘计算 | AWS Wavelength | Azure Edge Zones | Mobile Edge Cloud | - | Edge Computing | IBM Edge Application Manager |

## 容器服务 (Containers)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Containerization Tool <br>容器化工具 | AWS App2Container | - | - | Container Engine | Container Registry | IBM Cloud Container Service |
| Hybrid Container Service <br>混合容器服务 | Amazon ECS Anywhere | Azure Arc | Anthos | Container Engine for Kubernetes | ACK Anywhere | IBM Cloud Satellite |
| Hybrid Kubernetes Service <br>混合Kubernetes服务 | Amazon EKS Anywhere | Azure Arc | Anthos | Container Engine for Kubernetes | ACK Hybrid | IBM Cloud Satellite |
| Kubernetes Distribution <br>Kubernetes发行版 | Amazon EKS Distro | Azure Arc | Anthos | - | ACK Distro | IBM Cloud Kubernetes Service |
| Container Development Tool <br>容器开发工具 | AWS Copilot | - | - | Cloud Shell | Cloud Shell | IBM Cloud Shell |
| Container Application Management <br>容器应用管理 | AWS Proton | - | - | Container Instance | EDAS | IBM Cloud App Management |

## 数据库 (Database)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| High-Performance Relational Database <br>高性能关系型数据库 | Amazon Aurora | Azure Database for MySQL/PostgreSQL | Cloud Spanner | Base Database, OCI Database with PostgreSQL | RDS | IBM Db2 on Cloud |
| Document Database <br>文档数据库 | Amazon DocumentDB | Azure Cosmos DB | Cloud Firestore | - | MongoDB Service | IBM Cloudant |
| NoSQL Database <br>NoSQL数据库 | Amazon DynamoDB | Azure Cosmos DB | Cloud Firestore, Cloud Bigtable | NoSQL Database | TableStore | IBM Cloudant |
| Memory Cache <br>内存缓存 | Amazon ElastiCache | Azure Cache for Redis | Memorystore | OCI Cache | ApsaraDB for Redis | IBM Cloud Databases for Redis |
| Wide Column Database <br>宽列数据库 | Amazon Keyspaces | Azure Cosmos DB | Cloud Bigtable | - | Lindorm | - |
| Memory Database <br>内存数据库 | Amazon MemoryDB for Redis | Azure Cache for Redis | Memorystore | - | ApsaraDB for Redis | IBM Cloud Databases for Redis |
| Graph Database <br>图数据库 | Amazon Neptune | Azure Cosmos DB | - | - | Graph Database | IBM Graph |
| Relational Database <br>关系型数据库 | Amazon RDS | Azure Database for MySQL/PostgreSQL | Cloud SQL | Base Database | RDS | IBM Cloud Databases |
| Time Series Database <br>时序数据库 | Amazon Timestream | Azure Time Series Insights | - | - | Time Series Database | IBM Cloud Databases |
| Database Migration <br>数据库迁移 | AWS Database Migration Service | Azure Database Migration Service | Database Migration Service | Database Migration | Data Transmission Service | IBM Cloud Database Migration |
| Autonomous Database <br>自治数据库 | - | - | - | Autonomous Database | - | - |
| Data Warehouse <br>数据仓库 | Amazon Redshift | Azure Synapse Analytics | BigQuery | Autonomous Data Warehouse | MaxCompute | IBM Db2 Warehouse |

## 开发者工具 (Developer Tools)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Development Collaboration Platform <br>开发协作平台 | Amazon CodeCatalyst | Azure DevOps | Cloud Code | Developer Service | - | IBM Cloud DevOps |
| Java Runtime <br>Java运行时 | Amazon Corretto | - | - | - | - | - |
| Developer Lab Environment <br>开发者实验室环境 | AWS Cloud9 | Azure Lab Services | Cloud Workstations | - | - | IBM Cloud Shell |
| Cloud Shell <br>云Shell | AWS CloudShell | Azure Cloud Shell | Cloud Shell | Cloud Shell | Cloud Shell | IBM Cloud Shell |
| Resource Management API <br>资源管理API | AWS Cloud Control API | - | - | - | - | IBM Cloud API |
| Artifact Repository <br>制品库 | AWS CodeArtifact | Azure Artifacts | Artifact Registry | Container Registry | Container Registry | IBM Cloud Container Registry |
| Continuous Integration <br>持续集成 | AWS CodeBuild | Azure Pipelines | Cloud Build | DevOps Build Service | CICD | IBM Cloud Continuous Delivery |
| Continuous Deployment <br>持续部署 | AWS CodeDeploy | Azure Pipelines | Cloud Deploy | DevOps Deployment Service | CICD | IBM Cloud Continuous Delivery |
| Continuous Delivery <br>持续交付 | AWS CodePipeline | Azure Pipelines | Cloud Build | DevOps Build Pipeline | - | IBM Cloud Continuous Delivery |
| Development Project Management <br>开发项目管理 | AWS CodeStar | Azure DevOps | Cloud Code | - | - | IBM Cloud DevOps |
| Application Performance Monitoring <br>应用性能监控 | AWS X-Ray | Azure Application Insights | Cloud Trace | Application Performance Monitoring | ARMS | IBM Cloud Monitoring |
| Load Testing <br>负载测试 | - | Azure Load Testing | - | - | - | IBM Cloud Load Testing |
| Script Testing <br>脚本测试 | - | Microsoft Playwright Testing | - | - | - | - |
| Code Repository <br>代码仓库 | AWS CodeCommit | Azure Repos | Cloud Source Repositories | DevOps Code Repository | Codeup | IBM Cloud Git Repos |
| Development Metrics <br>开发指标 | - | Azure DevOps Analytics | - | - | DevOps Analytics | IBM Cloud DevOps Insights |
| Code Analysis & Security <br>代码分析与安全 | Amazon CodeGuru | Azure DevSecOps, Azure DevOps | Software Supply Chain Security, Cloud Code | - | Code Analysis | IBM Cloud Security, IBM Cloud DevSecOps |
| API Testing <br>API测试 | Amazon API Gateway | Azure API Management | Cloud Endpoints | API Gateway | API Gateway | IBM API Connect |

## 最终用户计算 (End User Computing)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Application Streaming <br>应用流式传输 | Amazon AppStream 2.0 | Azure Virtual Desktop | - | Desktop Service | Application Streaming | - |
| Virtual Desktop <br>虚拟桌面 | Amazon WorkSpaces | Azure Virtual Desktop | - | Desktop as a Service | Elastic Desktop Service | IBM Cloud Virtual Desktop |
| Web Virtual Desktop <br>Web虚拟桌面 | Amazon WorkSpaces Web | Azure Virtual Desktop | - | Browser Access | Workspace | IBM Cloud Virtual Desktop |

## 前端 Web 和移动 (Front-end Web & Mobile)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Location Service <br>定位服务 | Amazon Location Service | Azure Maps | Maps Platform | Location Service | Location Service | - |
| Mobile and Web Application Development <br>移动和Web应用开发 | AWS Amplify | Azure Static Web Apps | Firebase | APEX | Mobile Development Platform | IBM Mobile Foundation |
| Mobile Application Testing <br>移动应用测试 | AWS Device Farm | Azure DevTest Labs | Firebase Test Lab | - | Mobile Testing | IBM Cloud Mobile Testing |

## 游戏开发 (Game Development)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Game Server Hosting <br>游戏服务器托管 | Amazon GameLift | Azure PlayFab | - | Game Development Cloud | Game Service | - |
| Game Backend Service <br>游戏后端服务 | Amazon GameSparks | Azure PlayFab | - | Game Backend Service | GameShield | - |
| Game Development Toolkit <br>游戏开发工具包 | AWS GameKit | Azure PlayFab | - | - | Game Security | - |

## 物联网 (Internet of Things)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| One-Click IoT <br>一键物联网 | AWS IoT 1-Click | - | - | - | - | - |
| IoT Data Analysis <br>物联网数据分析 | AWS IoT Analytics | Azure IoT Hub | Cloud IoT Core | OCI IoT Analytics | IoT Analytics | IBM Watson IoT Platform |
| IoT Core Service <br>物联网核心服务 | AWS IoT Core | Azure IoT Hub | Cloud IoT Core | OCI IoT | IoT Platform | IBM Watson IoT Platform |
| IoT Device Security <br>物联网设备安全 | AWS IoT Device Defender | Azure IoT Security | Cloud IoT Core | OCI IoT Device Security | - | IBM Watson IoT Platform |
| IoT Device Management <br>物联网设备管理 | AWS IoT Device Management | Azure IoT Hub | Cloud IoT Core | OCI IoT Device Management | IoT Device Management | IBM Watson IoT Platform |
| IoT Event Processing <br>物联网事件处理 | AWS IoT Events | Azure IoT Hub | Cloud IoT Core | OCI IoT Events | - | IBM Watson IoT Platform |
| Vehicle Network Service <br>车载网络服务 | AWS IoT FleetWise | - | - | - | - | - |
| Edge Computing <br>边缘计算 | AWS IoT Greengrass | Azure IoT Edge | Cloud IoT Edge | - | Link Edge | IBM Edge Computing |
| Robot Management <br>机器人管理 | AWS IoT RoboRunner | - | - | - | - | - |
| Industrial IoT <br>工业物联网 | AWS IoT SiteWise | Azure IoT Central | - | - | - | IBM Maximo |
| Digital Twin <br>数字孪生 | AWS IoT TwinMaker | Azure Digital Twins | Supply Chain Twin | OCI Digital Twin | IoT Studio | IBM Maximo |
| Real-time Operating System <br>实时操作系统 | FreeRTOS | Azure RTOS | - | - | - | - |

## 机器学习 (Machine Learning)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| AI Base Model Service <br>AI基础模型服务 | Amazon Bedrock | Azure OpenAI Service | Vertex AI | OCI Language | PAI | IBM Watson Studio |
| Code Intelligence Assistant <br>代码智能助手 | Amazon CodeWhisperer | Azure OpenAI Service | Duet AI | - | Tongyi Lingma | IBM Watson Code Assistant |
| Natural Language Processing <br>自然语言处理 | Amazon Comprehend | Azure Cognitive Service - Text Analytics | Cloud Natural Language API | OCI Language | NLP | IBM Watson NLP |
| Predictive Analysis <br>预测分析 | Amazon Forecast | Azure Cognitive Service - Forecasting | - | OCI Forecasting | PAI-AutoLearning | IBM Watson Machine Learning |
| Dialog Robot <br>对话机器人 | Amazon Lex | Azure Bot Service | Cloud Dialogflow | - | Intelligent Service Robot | IBM Watson Assistant |
| Computer Vision <br>计算机视觉 | Amazon Lookout for Vision | Azure Computer Vision | Cloud Vision AI | OCI Vision | Vision Intelligence | IBM Watson Visual Recognition |
| Personalized Recommendation <br>个性化推荐 | Amazon Personalize | Azure Personalizer | Recommendations AI | - | Machine Learning Platform | IBM Watson Machine Learning |
| Text-to-Speech <br>文本转语音 | Amazon Polly | Azure Cognitive Service - Text-to-Speech | Cloud Text-to-Speech | OCI Speech | Speech Service | IBM Watson Text to Speech |
| Image Recognition <br>图像识别 | Amazon Rekognition | Azure Computer Vision | Cloud Vision AI | - | Image Search | IBM Watson Visual Recognition |
| Document Understanding <br>文档理解 | Amazon Textract | Azure Form Recognizer | Cloud Document AI | Document Understanding | - | IBM Watson Discovery |
| Machine Learning Platform <br>机器学习平台 | Amazon SageMaker | Azure Machine Learning | Vertex AI | OCI Data Science | PAI-Studio | IBM Watson Studio |
| AI Content Safety <br>AI内容安全 | - | Azure AI Content Safety | - | - | - | - |
| AI Document Intelligence <br>AI文档智能 | - | Azure AI Document Intelligence | - | - | - | IBM Watson Discovery |
| AI Face Recognition <br>AI人脸识别 | - | Azure AI Face | - | - | - | IBM Watson Visual Recognition |
| AI Immersive Reader <br>AI沉浸式阅读器 | - | Azure AI Immersive Reader | - | - | - | - |
| AI Video Indexer <br>AI视频索引器 | - | Azure AI Video Indexer | - | - | - | IBM Watson Media |
| ML Model Registry <br>ML模型注册表 | Amazon SageMaker | Azure ML | Vertex AI Model Registry | - | PAI-Studio | IBM Watson Studio |
| ML Pipeline <br>ML管道 | Amazon SageMaker | Azure ML | Vertex AI Pipelines | - | PAI-Studio | IBM Watson Studio |
| ML Feature Store <br>ML特征商店 | Amazon SageMaker | Azure ML | Vertex AI Feature Store | - | PAI-Studio | IBM Watson Studio |
| Speech Recognition <br>语音识别 | Amazon Transcribe | Azure Speech Service | Cloud Speech-to-Text | - | Speech Recognition | IBM Watson Speech to Text |
| Language Translation <br>语言翻译 | Amazon Translate | Azure Translator | Cloud Translation | - | Machine Translation | IBM Watson Language Translator |
| AI Model Deployment <br>AI模型部署 | Amazon SageMaker | Azure ML Deployments | Vertex AI | - | PAI-EAS | IBM Watson Machine Learning |
| AI Model Monitoring <br>AI模型监控 | Amazon SageMaker | Azure ML Monitoring | Vertex AI | - | PAI-Studio | IBM Watson OpenScale |

## 管理与治理 (Management & Governance)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Account Management <br>账户管理 | AWS Account Management | Azure Subscription Management | Cloud Billing | Identity and Access Management | Resource Management | IBM Cloud Account Management |
| Application Auto Scaling <br>应用自动扩缩容 | AWS Application Auto Scaling | Azure Autoscale | Autoscaling | Autoscaling | Auto Scaling | IBM Cloud Auto Scale |
| Infrastructure as Code <br>基础设施即代码 | AWS CloudFormation | Azure Resource Manager | Cloud Deployment Manager | Resource Manager | ROS | IBM Cloud Schematics |
| Audit Logs <br>审计日志 | AWS CloudTrail | Azure Monitor | Cloud Audit Logs | Audit | ActionTrail | IBM Cloud Activity Tracker |
| Monitoring and Observability <br>监控与可观测性 | AWS CloudWatch | Azure Monitor | Cloud Monitoring | Monitoring | CloudMonitor | IBM Cloud Monitoring |
| Configuration Management <br>配置管理 | AWS Config | Azure Policy | Security Command Center | Configuration Management | Config | IBM Cloud Security and Compliance Center |
| Multi-Account Management <br>多账户管理 | AWS Control Tower | Azure Landing Zones | - | Compartments | Resource Directory | IBM Cloud Enterprise |
| Management Console <br>管理控制台 | AWS Management Console | Azure Portal | Cloud Console | Cloud Console | Management Console | IBM Cloud Console |
| Organization Management <br>组织管理 | AWS Organizations | Azure Management Groups | Cloud Identity & Organization | Identity Domains | Resource Management | IBM Cloud Enterprise Management |
| Service Catalog <br>服务目录 | AWS Service Catalog | Azure Marketplace | Cloud Marketplace | Marketplace | Cloud Marketplace | IBM Cloud Catalog |
| Best Practices Recommendations <br>最佳实践建议 | AWS Trusted Advisor | Azure Advisor | Recommender | Cloud Advisor | Advisor | IBM Cloud Advisor |
| Cost Management <br>成本管理 | AWS Cost Explorer | Azure Cost Management | Cloud Billing | Cost Management | Cost Manager | IBM Cloud Cost Management |
| Resource Health <br>资源健康 | AWS Health Dashboard | Azure Service Health | Cloud Status | Cloud Status | Cloud Monitor | IBM Cloud Status |
| Cloud Asset Inventory <br>云资产清单 | AWS Config | Azure Resource Graph | Cloud Asset Inventory | - | Resource Management | IBM Cloud Security and Compliance |
| Binary Authorization <br>二进制授权 | - | Azure Policy | Binary Authorization | - | Container Registry | IBM Cloud Container Security |
| Advisory Notifications <br>咨询通知 | AWS Security Hub | Azure Security Center | Advisory Notifications | - | Security Center | IBM Cloud Security Advisor |
| Service Health Monitoring <br>服务健康监控 | AWS Personal Health Dashboard | Azure Service Health | Cloud Status | - | Cloud Monitor | IBM Cloud System Status |
| Resource Visualization <br>资源可视化 | AWS Resource Groups | Azure Resource Graph | Asset Inventory | - | Resource Management | IBM Cloud Resource Visualization |
| Policy Management <br>策略管理 | AWS Organizations | Azure Policy | Organization Policy | - | Resource Management | IBM Cloud Security and Compliance |
| Support Management <br>支持管理 | AWS Support | Azure Support | Google Cloud Support | Support Management | Support | IBM Cloud Support |
| License Management <br>许可证管理 | AWS License Manager | Azure Hybrid Benefit | - | License Manager | - | IBM Cloud License Management |
| Resource Scheduler <br>资源调度器 | AWS Systems Manager | Azure Automation | Cloud Scheduler | Resource Scheduler | - | IBM Cloud Scheduler |
| Security Zones <br>安全区域 | AWS Control Tower | Azure Security Center | Security Command Center | Security Zones | - | IBM Cloud Security and Compliance Center |
| Bastion Service <br>跳板服务 | AWS Systems Manager Session Manager | Azure Bastion | Identity-Aware Proxy | Bastion | - | IBM Cloud Bastion |
| Managed Access <br>托管访问 | AWS IAM Identity Center | Azure AD Privileged Identity Management | Cloud Identity | Managed Access | - | IBM Cloud IAM |
| Service Management <br>服务管理 | - | - | - | - | - | IBM Cloud Service Management |
| Resource Controller <br>资源控制器 | - | - | - | - | - | IBM Cloud Resource Controller |

## 媒体服务 (Media Services)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Media Transcoding <br>媒体转码 | Amazon Elastic Transcoder | Azure Media Services | Transcoder API | Media Flow | Media Processing | IBM Cloud Video Streaming |
| Video Stream Processing <br>视频流处理 | Amazon Kinesis Video Streams | Azure Media Services | - | Streaming | ApsaraVideo Live | IBM Cloud Video Streaming |
| Video Transcoding <br>视频转码 | AWS Elemental MediaConvert | Azure Media Services | Transcoder API | - | ApsaraVideo VOD | IBM Cloud Video Streaming |
| Live Streaming <br>直播 | AWS Elemental MediaLive | Azure Media Services | Live Stream API | - | ApsaraVideo Live | IBM Cloud Video Streaming |
| Media Storage <br>媒体存储 | AWS Elemental MediaStore | Azure Media Services | Cloud Storage | Object Storage | ApsaraVideo VOD | IBM Cloud Object Storage |

## 迁移与传输 (Migration & Transfer)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Application Discovery Service <br>应用发现服务 | AWS Application Discovery Service | Azure Migrate | Cloud Asset Inventory | Application Migration | - | IBM Cloud Migration |
| Application Migration Service <br>应用迁移服务 | AWS Application Migration Service | Azure Migrate | Migrate for Compute Engine | Migration Service | - | IBM Cloud Migration |
| Database Migration <br>数据库迁移 | AWS Database Migration Service | Azure Database Migration Service | Database Migration Service | Database Migration | Data Transmission Service | IBM Cloud Database Migration |
| Mainframe Modernization <br>大型机现代化 | AWS Mainframe Modernization | - | - | Cloud Migration | - | IBM Cloud Modernization |
| Migration Center <br>迁移中心 | AWS Migration Hub | Azure Migrate | - | Migration Hub | - | IBM Cloud Migration |
| Server Migration <br>服务器迁移 | AWS Server Migration Service | Azure Migrate | Migrate for Compute Engine | Compute Migration | - | IBM Cloud Migration |
| Data Transfer Device <br>数据传输设备 | AWS Snow Family | Azure Data Box | Transfer Appliance | Data Transfer Appliance | - | IBM Cloud Mass Data Migration |
| File Transfer <br>文件传输 | AWS Transfer Family | Azure Files | Cloud Storage SFTP | - | - | IBM Cloud File Transfer |
| Data Transfer & Synchronization <br>数据传输与同步 | AWS DataSync | Azure File Sync, Azure Data Box | Storage Transfer Service | Data Transfer Service, Data Transfer | - | IBM Cloud Data Sync, IBM Cloud Mass Data Migration |

## 网络与内容分发 (Networking & Content Delivery)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Content Delivery Network <br>内容分发网络 | Amazon CloudFront | Azure CDN | Cloud CDN | Content Delivery Network | CDN | IBM Cloud CDN |
| DNS Service <br>DNS服务 | Amazon Route 53 | Azure DNS | Cloud DNS | DNS | DNS | IBM Cloud DNS Services |
| Virtual Private Cloud <br>虚拟私有云 | Amazon VPC | Azure Virtual Network | Virtual Private Cloud | Virtual Cloud Network | VPC | IBM Cloud VPC |
| Service Mesh <br>服务网格 | AWS App Mesh | Azure Service Fabric Mesh | Traffic Director | - | Service Mesh | IBM Cloud Service Mesh |
| VPN Client <br>VPN客户端 | AWS Client VPN | Azure VPN Gateway | Cloud VPN | VPN Connect | - | IBM Cloud VPN |
| Service Discovery <br>服务发现 | AWS Cloud Map | Azure App Configuration | Cloud Service Directory | - | Service Discovery | IBM Cloud Service Discovery |
| Wide Area Network Service <br>广域网服务 | AWS Cloud WAN | Azure Virtual WAN | Network Connectivity Center | - | Smart Access Gateway | - |
| Dedicated Connection <br>专线连接 | AWS Direct Connect | Azure ExpressRoute | Cloud Interconnect | FastConnect | Express Connect | IBM Cloud Direct Link |
| Global Accelerator <br>全球加速器 | AWS Global Accelerator | Azure Front Door | Premium Tier Networking | - | Global Accelerator | IBM Cloud Internet Services |
| Private 5G Network <br>私有5G网络 | AWS Private 5G | Azure Private 5G Core | - | - | Private 5G | IBM Cloud for Telecommunications |
| Private Connection <br>私有连接 | AWS PrivateLink | Azure Private Link | Private Service Connect | Service Gateway | PrivateLink | IBM Cloud Private Link |
| Site-to-Site VPN <br>站点到站点VPN | AWS Site-to-Site VPN | Azure VPN Gateway | Cloud VPN | - | VPN Gateway | IBM Cloud VPN |
| Transit Gateway <br>传输网关 | AWS Transit Gateway | Azure Virtual WAN | Network Connectivity Center | - | Cloud Enterprise Network | IBM Cloud Direct Link |
| Load Balancing <br>负载均衡 | Elastic Load Balancing | Azure Load Balancer | Cloud Load Balancing | Load Balancer | SLB | IBM Cloud Load Balancer |
| DDoS Protection <br>DDoS防护 | AWS Shield | Azure DDoS Protection | Cloud Armor | DDoS Protection | Anti-DDoS | IBM Cloud Internet Services |
| Communication Gateway <br>通信网关 | - | Azure Communications Gateway | - | - | - | - |
| Elastic SAN <br>弹性SAN | - | Azure Elastic SAN | - | - | - | - |
| Fluid Relay <br>流体中继 | - | Azure Fluid Relay | - | - | - | - |
| NAT Gateway <br>NAT网关 | - | Azure NAT Gateway | - | - | - | IBM Cloud NAT Gateway |
| Network Function Manager <br>网络功能管理器 | - | Azure Network Function Manager | - | - | - | - |
| SignalR Service <br>SignalR服务 | - | Azure SignalR Service | - | - | - | - |
| Web PubSub <br>Web PubSub | - | Azure Web PubSub | - | - | - | - |
| API Gateway Management <br>API网关管理 | Amazon API Gateway | Azure API Management | Cloud Endpoints | API Gateway | API Gateway | IBM API Connect |
| Network Monitoring <br>网络监控 | AWS Network Manager | Azure Network Watcher | Network Intelligence Center | Network Monitor | Network Analysis | IBM Cloud Flow Logs |
| Network Analysis <br>网络分析 | AWS Network Insights | Azure Network Watcher | Network Intelligence Center | Network Monitoring | Network Analysis | IBM Cloud Flow Logs |
| Traffic Management <br>流量管理 | AWS Global Accelerator | Azure Traffic Manager | Cloud Load Balancing | Traffic Management | DCDN | IBM Cloud Internet Services |
| Media CDN <br>媒体CDN | Amazon CloudFront | Azure CDN | Media CDN | - | CDN | IBM Cloud CDN |
| Network Service Tiers <br>网络服务层 | - | Azure ExpressRoute | Network Service Tiers | FastConnect | Express Connect | IBM Cloud Direct Link |
| Global Traffic Management & Acceleration <br>全球流量管理与加速 | AWS Global Accelerator | Azure Front Door, Azure Traffic Manager | Premium Tier Networking, Cloud Load Balancing | Traffic Management | Global Accelerator, DCDN, Global Traffic Manager | IBM Cloud Internet Services |
| Network Connectivity Center <br>网络连接中心 | AWS Transit Gateway | Azure Virtual WAN | Network Connectivity Center | - | Cloud Enterprise Network | IBM Cloud Direct Link |

## 安全、身份与合规 (Security, Identity & Compliance)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Identity Authentication Service <br>身份认证服务 | Amazon Cognito | Azure Active Directory B2C | Firebase Authentication | Identity Cloud Service | IDaaS | IBM Cloud IAM |
| Security Investigation Service <br>安全调查服务 | Amazon Detective | Azure Sentinel | Security Command Center | Cloud Guard | Security Center | IBM Cloud Security Advisor |
| Threat Detection Service <br>威胁检测服务 | Amazon GuardDuty | Azure Defender | Security Command Center | Cloud Guard | Security Center | IBM Cloud Security Advisor |
| Security Assessment Service <br>安全评估服务 | Amazon Inspector | Azure Defender | Security Command Center | Cloud Guard | Security Center | IBM Cloud Security and Compliance Center |
| Data Privacy Service <br>数据隐私服务 | Amazon Macie | Azure Information Protection | Cloud DLP | Data Safe | Sensitive Data Discovery | IBM Cloud Data Shield |
| Permission Verification Service <br>权限验证服务 | Amazon Verified Permissions | Azure RBAC | Cloud IAM | - | - | IBM Cloud IAM |
| Compliance Reporting Service <br>合规报告服务 | AWS Artifact | Azure Policy | Compliance Reports | - | - | IBM Cloud Security and Compliance Center |
| Audit Management Service <br>审计管理服务 | AWS Audit Manager | Azure Policy | Security Command Center | - | - | IBM Cloud Security and Compliance Center |
| Certificate Management Service <br>证书管理服务 | AWS Certificate Manager | Azure Key Vault | Certificate Authority Service | - | - | IBM Cloud Certificate Manager |
| Hardware Security Module <br>硬件安全模块 | AWS CloudHSM | Azure Dedicated HSM | Cloud HSM | - | - | IBM Cloud HSM |
| Directory Service <br>目录服务 | AWS Directory Service | Azure Active Directory | Cloud Identity | - | - | IBM Cloud Directory Service |
| Firewall Management <br>防火墙管理 | AWS Firewall Manager | Azure Firewall Manager | Cloud Armor | - | - | IBM Cloud Internet Services |
| Identity Access Management <br>身份访问管理 | AWS IAM | Azure Active Directory | Cloud IAM | Identity and Access Management | RAM | IBM Cloud IAM |
| Identity Center <br>身份中心 | AWS Identity Center | Azure Active Directory | Cloud Identity | - | - | IBM Cloud IAM |
| Key Management Service <br>密钥管理服务 | AWS KMS | Azure Key Vault | Cloud KMS | Key Management | KMS | IBM Key Protect |
| Network Firewall <br>网络防火墙 | AWS Network Firewall | Azure Firewall | Cloud Armor | - | Cloud Firewall | IBM Cloud Internet Services |
| Private Certificate Authority <br>私有证书颁发机构 | AWS Private Certificate Authority | Azure Key Vault | Certificate Authority Service | - | - | IBM Cloud Certificate Manager |
| Resource Access Management <br>资源访问管理 | AWS Resource Access Manager | Azure RBAC | Cloud IAM | - | - | IBM Cloud IAM |
| Secret Management <br>密钥管理 | AWS Secrets Manager | Azure Key Vault | Secret Manager | - | - | IBM Cloud Secrets Manager |
| Security Center <br>安全中心 | AWS Security Hub | Azure Sentinel | Security Command Center | - | - | IBM Cloud Security Advisor |
| DDoS Protection <br>DDoS防护 | AWS Shield | Azure DDoS Protection | Cloud Armor | DDoS Protection | Anti-DDoS | IBM Cloud Internet Services |
| Web Application Firewall <br>Web应用防火墙 | AWS WAF | Azure Web Application Firewall | Cloud Armor | Web Application Firewall | WAF | IBM Cloud Internet Services |
| Security Monitoring <br>安全监控 | AWS Security Hub | Azure Sentinel | Security Command Center | - | - | IBM Cloud Security Advisor |
| Vulnerability Scanning <br>漏洞扫描 | Amazon Inspector | Azure Defender | Security Command Center | - | - | IBM Cloud Security Advisor |
| Security Posture Management <br>安全态势管理 | AWS Security Hub | Microsoft Defender for Cloud | Security Command Center | Cloud Guard | Security Center | IBM Cloud Security and Compliance Center |
| Zero Trust Security <br>零信任安全 | - | Azure Zero Trust | BeyondCorp | - | Zero Trust Security | IBM Cloud Security Zero Trust |
| Cloud Asset Inventory <br>云资产清单 | AWS Config | Azure Resource Graph | Cloud Asset Inventory | - | Resource Management | IBM Cloud Security and Compliance |
| Binary Authorization <br>二进制授权 | - | Azure Policy | Binary Authorization | - | Container Registry | IBM Cloud Container Security |
| Advisory Notifications <br>咨询通知 | AWS Security Hub | Azure Security Center | Advisory Notifications | - | Security Center | IBM Cloud Security Advisor |
| Confidential Computing <br>机密计算 | AWS Nitro Enclaves | Azure Confidential Computing | Confidential Computing | - | Security Center | IBM Cloud Hyper Protect Services |
| Security Information Management <br>安全信息管理 | Amazon Security Lake | Azure Sentinel | Chronicle | - | Security Center | IBM Cloud Security Insights |
| External Identity Management <br>外部身份管理 | Amazon Cognito | Azure External ID | Identity Platform | - | IDaaS | IBM Cloud IAM |
| Anti-Bot Service <br>反机器人服务 | AWS WAF | Azure Web Application Firewall | Cloud Armor | - | Anti-Bot Service | IBM Cloud Internet Services |
| SSL Certificate Service <br>SSL证书服务 | AWS Certificate Manager | Azure App Service Certificates | - | - | SSL Certificates Service | IBM Cloud Certificate Manager |
| Cloud Security Scanner <br>云安全扫描器 | Amazon Inspector | Azure Defender | Security Scanner | - | Cloud Security Scanner | IBM Cloud Security Advisor |

## 存储服务 (Storage)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Block Storage Service <br>块存储服务 | Amazon EBS | Azure Managed Disks | Persistent Disk | Block Volume | Block Storage | IBM Cloud Block Storage |
| File Storage Service <br>文件存储服务 | Amazon EFS | Azure Files | Filestore | File Storage | NAS | IBM Cloud File Storage |
| File System Service <br>文件系统服务 | Amazon FSx | Azure Files | Filestore | - | NAS | IBM Cloud File Storage |
| Object Storage Service <br>对象存储服务 | Amazon S3 | Azure Blob Storage | Cloud Storage | Object Storage | OSS | IBM Cloud Object Storage |
| Archive Storage Service <br>归档存储服务 | Amazon S3 Glacier | Azure Archive Storage | Cloud Storage Archive | Archive Storage | OSS Archive | IBM Cloud Object Storage Archive |
| Backup Service <br>备份服务 | AWS Backup | Azure Backup | Backup and DR Service | Backup Service | Hybrid Backup Recovery | IBM Cloud Backup |
| Disaster Recovery Service <br>灾难恢复服务 | AWS Elastic Disaster Recovery | Azure Site Recovery | - | - | Hybrid Disaster Recovery | IBM Cloud Disaster Recovery |
| Data Transfer Device <br>数据传输设备 | AWS Snow Family | Azure Data Box | Transfer Appliance | Data Transfer Appliance | - | IBM Cloud Mass Data Migration |
| Storage Gateway Service <br>存储网关服务 | AWS Storage Gateway | Azure Storage Gateway | Storage Transfer Service | - | Storage Gateway | IBM Cloud Storage Gateway |
| HPC Cache <br>HPC缓存 | - | Azure HPC Cache | - | - | - | - |
| Managed Lustre <br>托管Lustre | - | Azure Managed Lustre | - | - | - | - |
| NetApp Storage <br>NetApp存储 | - | Azure NetApp Files | - | - | - | - |
| Queue Storage <br>队列存储 | - | Azure Queue Storage | - | - | - | IBM Cloud Messages for RabbitMQ |
| Storage Lifecycle Management <br>存储生命周期管理 | S3 Lifecycle | Azure Storage Lifecycle | Object Lifecycle Management | Object Lifecycle Management | OSS Lifecycle | IBM Cloud Object Storage Lifecycle |
| Storage Performance <br>存储性能 | Amazon EBS io2 | Azure Ultra Disk | Persistent Disk | Block Volume | ESSD | IBM Cloud Block Storage |

## 量子计算 (Quantum Technologies)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Quantum Computing Platform <br>量子计算平台 | Amazon Braket | Azure Quantum | Google Quantum AI | Quantum Computing | Quantum Computing Platform | IBM Quantum |

## 机器人技术 (Robotics)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Robot Management Service <br>机器人管理服务 | AWS IoT RoboRunner | - | - | - | Robot Service | - |
| Robot Development Platform <br>机器人开发平台 | AWS RoboMaker | - | Cloud Robotics Core | - | Robot Development Platform | - |

## 卫星 (Satellite)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Satellite Ground Station Service <br>卫星地面站服务 | AWS Ground Station | Azure Orbital | - | - | Satellite Connection | - |

## 混合与多云 (Hybrid + Multicloud)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Hybrid Management Service <br>混合管理服务 | AWS Outposts | Azure Arc | Anthos | - | Alibaba Cloud Apsara Stack | IBM Cloud Satellite |
| Edge Kubernetes <br>边缘Kubernetes | - | Azure Kubernetes Service Edge Essentials | - | - | - | IBM Edge Computing |
| Operator Service <br>运营商服务 | - | Azure Operator Nexus | - | - | - | - |
| Operator Insights <br>运营商洞察 | - | Azure Operator Insights | - | - | - | - |

## 域名注册 (Domain Registration)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Domain Registration Service <br>域名注册服务 | Amazon Route 53 Domains | Azure App Service Domains | Cloud Domains | - | Domains | IBM Cloud Domains |
| Domain Management <br>域名管理 | Amazon Route 53 | Azure DNS | Cloud Domains | DNS | Domains | IBM Cloud DNS Services |
| Domain Transfer <br>域名转移 | Amazon Route 53 | Azure App Service Domains | Cloud Domains | - | Domains | IBM Cloud Domains |
| Domain Privacy Protection <br>域名隐私保护 | Amazon Route 53 | Azure App Service Domains | Cloud Domains | - | Domain Privacy | IBM Cloud Domains |
| Domain Auto-renewal <br>域名自动续费 | Amazon Route 53 | Azure App Service Domains | Cloud Domains | - | Domains | IBM Cloud Domains |
| Domain Whois Service <br>域名Whois服务 | Amazon Route 53 | Azure App Service Domains | Cloud Domains | - | Domain Whois | IBM Cloud Domains |
