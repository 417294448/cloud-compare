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
| Interactive Query Analysis | Amazon Athena | Azure Synapse Analytics | BigQuery | Analytics Cloud | Data Lake Analytics | IBM Cloud SQL Query |
| Search Service | Amazon CloudSearch | Azure Cognitive Search | Cloud Search | OCI Search with OpenSearch | OpenSearch | IBM Watson Discovery |
| Data Governance | Amazon DataZone | Microsoft Purview | Dataplex | Data Catalog | DataWorks | IBM Watson Knowledge Catalog |
| Big Data Processing | Amazon EMR | Azure HDInsight | Dataproc | Big Data Service | E-MapReduce | IBM Analytics Engine |
| Real-time Stream Processing | Amazon Kinesis Data Streams | Azure Stream Analytics | Dataflow | Streaming | Realtime Compute | IBM Streaming Analytics |
| Data Stream Transfer | Amazon Kinesis Data Firehose | Azure Event Hubs | Cloud Pub/Sub | Streaming | DataHub | IBM Event Streams |
| Stream Analytics | Amazon Kinesis Data Analytics | Azure Stream Analytics | Dataflow | Streaming Analytics | Realtime Compute | IBM Streaming Analytics |
| Search and Analytics Engine | Amazon OpenSearch Service | Azure OpenSearch Service | - | Search Service | OpenSearch | IBM Watson Discovery |
| Data Warehouse | Amazon Redshift | Azure Synapse Analytics | BigQuery | Autonomous Data Warehouse | MaxCompute | IBM Db2 Warehouse |
| ETL Service | AWS Glue | Azure Data Factory | Cloud Data Fusion | Data Integration | DataWorks | IBM DataStage |
| Data Exploration Service | - | Azure Data Explorer | - | - | - |
| Open Datasets | - | Azure Open Datasets | Google Cloud Public Datasets | - | - |
| Data Lake Analytics | AWS Lake Formation | Azure Data Lake Analytics | Cloud Storage | Data Lake Analytics | Data Lake Analytics | IBM Cloud Object Storage |
| Time Series Analytics | Amazon Timestream | Azure Time Series Insights | Cloud IoT Core | - | Time Series Database | IBM Cloud Databases |
| Data Lake Storage | Amazon S3 | Azure Data Lake Storage | Cloud Storage | Object Storage | Data Lake Storage | IBM Cloud Object Storage |
| Data Pipeline | AWS Data Pipeline | Azure Data Factory | Cloud Dataflow | Data Integration | DataWorks | IBM DataStage |
| Data Visualization & Business Intelligence | Amazon QuickSight | Power BI | Looker Studio | Analytics Cloud | Quick BI | IBM Cognos Analytics |
| Data Sharing | AWS Data Exchange | Azure Data Share | Analytics Hub | - | - | - |
| Anomaly Detection | Amazon Lookout for Metrics | Azure Metrics Advisor | Cloud Monitoring | Anomaly Detection | - | IBM Cloud Monitoring |
| Data Lake Query | Amazon Athena | Azure Synapse Analytics | BigQuery | Analytics Cloud | Data Lake Analytics | IBM Cloud SQL Query |
| Log Service | Amazon CloudWatch Logs | Azure Monitor | Cloud Logging | - | Log Service | IBM Log Analysis |
| Data Quality | AWS Glue DataBrew | Azure Data Factory | Cloud Dataprep | - | - | IBM Watson Knowledge Catalog |
| Data Catalog | AWS Glue Data Catalog | Azure Purview | Data Catalog | - | - | IBM Watson Knowledge Catalog |
| Spark-based analytics | - | Azure Databricks | - | - | - | - |

## 应用集成 (Application Integration)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Application Integration Service | Amazon AppFlow | Azure Logic Apps | Cloud Data Fusion | Integration Cloud Service | Cloud Service Bus | IBM App Connect |
| Event Bus | Amazon EventBridge | Azure Event Grid | Eventarc | Events Service | EventBridge | IBM Event Streams |
| Message & Task Queue | Amazon SQS | Azure Queue Storage | Cloud Tasks | Queue Service | Message Queue | IBM MQ |
| Message Notification Service | Amazon SNS | Azure Notification Hubs | Cloud Pub/Sub | Notifications | Message Service | IBM Event Notifications |
| Message Middleware | Amazon MQ | Azure Service Bus | - | Messaging | Message Queue | IBM MQ |
| Message Queue | Amazon SQS | Azure Queue Storage | Cloud Tasks | Queue Service | Message Queue | IBM MQ |
| Service Bus | Amazon MQ | Azure Service Bus | Pub/Sub | Oracle Integration Cloud | Message Queue | IBM Event Streams |
| GraphQL API Service | AWS AppSync | Azure API Management | Cloud Endpoints | API Gateway | API Gateway | IBM API Connect |
| Workflow Orchestration | AWS Step Functions | Azure Logic Apps | Workflows | Workflow | Serverless Workflow | IBM Cloud Pak for Integration |
| API Gateway | Amazon API Gateway | Azure API Management | Cloud Endpoints, API Gateway | API Gateway | API Gateway | IBM API Connect |
| Workflow Management | Amazon MWAA | - | Cloud Composer | Workflow | - | IBM Cloud Pak for Business Automation |
| Integration Platform | - | Azure Integration Services | Cloud Integration | Integration Cloud | Cloud Integration | IBM Cloud Integration |
| API Design & Testing | - | Azure API Management | Cloud Endpoints | API Gateway | API Gateway | IBM API Connect |
| API Lifecycle Management | - | Azure API Management | Apigee | API Gateway | API Gateway | IBM API Connect |
| Task Scheduling | Amazon EventBridge | Azure Logic Apps | Cloud Scheduler | - | - | IBM Cloud Scheduler |
| Process Automation | AWS Step Functions | Azure Logic Apps | Cloud Workflows | Process Automation | - | IBM Cloud Pak for Business Automation |
| Queue Service | Amazon SQS | Azure Queue Storage | Cloud Tasks | Queue | Message Queue | IBM MQ |
| Enterprise Service Bus | Amazon MQ | Azure Service Bus | - | - | Enterprise Service Bus | IBM App Connect Enterprise |
| Microservices Governance | AWS App Mesh | Azure Service Fabric | - | - | Microservices Engine | IBM Cloud Pak for Integration |
| Flow Control Service | AWS CodePipeline | Azure Pipelines | Cloud Build | - | Flow Control Service | IBM Cloud Continuous Delivery |
| Event Management | Amazon EventBridge | Azure Event Grid | Cloud Pub/Sub | - | EventBridge | IBM Cloud Event Management |
| API Gateway Analytics | - | Azure API Management | API Analytics | - | - | IBM API Connect Analytics |

## 区块链 (Blockchain)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Blockchain Platform | Amazon Managed Blockchain | Azure Blockchain Service (已停用) | - | Blockchain Platform | Blockchain as a Service | IBM Blockchain Platform |
| Distributed Ledger | Amazon QLDB | - | - | - | Blockchain as a Service | IBM Blockchain Platform |

## 业务应用 (Business Applications)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Intelligent Assistant | Amazon Q | - | - | Oracle Intelligent Advisor | Intelligent Speech Interaction | IBM Watson Assistant |
| Collaboration Communication | Amazon Chime | Microsoft Teams | Google Meet | - | DingTalk | IBM Cloud Unified Communications |
| Call Center | Amazon Connect | Azure Communication Services | - | - | Cloud Call Center | IBM Voice Gateway |
| Low-Code Platform | Amazon Honeycode | Power Apps | AppSheet | - | Low-Code Development | IBM Cloud Pak for Business Automation |
| Customer Interaction Service | Amazon Pinpoint | Azure Communication Services | Firebase Cloud Messaging | Digital Assistant | Message Push | IBM Watson Assistant |
| Email Service | Amazon SES | Azure Communication Services | - | Email Delivery | DirectMail | IBM Cloud Email Service |
| Document Collaboration | Amazon WorkDocs | SharePoint | Google Drive | - | Workplace | IBM Cloud Document Services |
| Enterprise Email | Amazon WorkMail | Exchange Online | Google Workspace | - | Alibaba Mail | IBM Cloud Mail |
| Supply Chain Management | AWS Supply Chain | - | - | Logistics Cloud | - | IBM Sterling Supply Chain |
| Encryption Communication | AWS Wickr | - | - | - | - | IBM Cloud Security |
| Enterprise Resource Planning | - | - | - | Fusion Cloud ERP | - | IBM Cloud for SAP |

## 计算服务 (Compute)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Virtual Server | Amazon EC2 | Azure Virtual Machines | Compute Engine | Compute | ECS | IBM Cloud Virtual Servers |
| Auto Scaling | Amazon EC2 Auto Scaling | Azure VM Scale Sets | Managed Instance Groups | Autoscaling | Auto Scaling | IBM Cloud Auto Scale |
| Container Image Repository | Amazon Elastic Container Registry | Azure Container Registry | Artifact Registry | Container Registry | Container Registry | IBM Cloud Container Registry |
| Container Service | Amazon Elastic Container Service | Azure Container Instances | Cloud Run | Container Instances | Container Service | IBM Cloud Container Service |
| Container Orchestration Service | Amazon Elastic Kubernetes Service | Azure Kubernetes Service | Google Kubernetes Engine | Kubernetes Engine (OKE) | ACK | IBM Cloud Kubernetes Service |
| Lightweight Virtual Server | Amazon Lightsail | Azure App Service | App Engine | - | Simple Application Server | IBM Cloud Code Engine |
| Container Application Platform | AWS App Runner | Azure Container Apps | Cloud Run | Container Instance | SAE | IBM Cloud Code Engine |
| Batch Processing | AWS Batch | Azure Batch | Cloud Batch | - | Batch Compute | IBM Cloud Batch Service |
| Application Hosting Platform | AWS Elastic Beanstalk | Azure App Service | App Engine | - | Web App Service | IBM Cloud Foundry |
| Serverless Computing | AWS Lambda | Azure Functions | Cloud Functions | Functions | Function Compute | IBM Cloud Functions |
| Local Region Service | AWS Local Zones | Azure Local Zones | - | - | Edge Node Service | IBM Cloud Satellite |
| Hybrid Cloud Service | AWS Outposts | Azure Stack | Anthos | - | Alibaba Cloud Apsara Stack | IBM Cloud Satellite |
| High-Performance Computing Cluster | AWS ParallelCluster | Azure CycleCloud | Slurm on GCP | - | E-HPC | IBM Spectrum LSF |
| Edge Computing | AWS Wavelength | Azure Edge Zones | Mobile Edge Cloud | - | Edge Computing | IBM Edge Application Manager |

## 容器服务 (Containers)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Containerization Tool | AWS App2Container | - | - | Container Engine | Container Registry | IBM Cloud Container Service |
| Hybrid Container Service | Amazon ECS Anywhere | Azure Arc | Anthos | Container Engine for Kubernetes | ACK Anywhere | IBM Cloud Satellite |
| Hybrid Kubernetes Service | Amazon EKS Anywhere | Azure Arc | Anthos | Container Engine for Kubernetes | ACK Hybrid | IBM Cloud Satellite |
| Kubernetes Distribution | Amazon EKS Distro | Azure Arc | Anthos | - | ACK Distro | IBM Cloud Kubernetes Service |
| Container Development Tool | AWS Copilot | - | - | Cloud Shell | Cloud Shell | IBM Cloud Shell |
| Container Application Management | AWS Proton | - | - | Container Instance | EDAS | IBM Cloud App Management |

## 数据库 (Database)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| High-Performance Relational Database | Amazon Aurora | Azure Database for MySQL/PostgreSQL | Cloud Spanner | Base Database, OCI Database with PostgreSQL | RDS | IBM Db2 on Cloud |
| Document Database | Amazon DocumentDB | Azure Cosmos DB | Cloud Firestore | - | MongoDB Service | IBM Cloudant |
| NoSQL Database | Amazon DynamoDB | Azure Cosmos DB | Cloud Firestore, Cloud Bigtable | NoSQL Database | TableStore | IBM Cloudant |
| Memory Cache | Amazon ElastiCache | Azure Cache for Redis | Memorystore | OCI Cache | ApsaraDB for Redis | IBM Cloud Databases for Redis |
| Wide Column Database | Amazon Keyspaces | Azure Cosmos DB | Cloud Bigtable | - | Lindorm | - |
| Memory Database | Amazon MemoryDB for Redis | Azure Cache for Redis | Memorystore | - | ApsaraDB for Redis | IBM Cloud Databases for Redis |
| Graph Database | Amazon Neptune | Azure Cosmos DB | - | - | Graph Database | IBM Graph |
| Relational Database | Amazon RDS | Azure Database for MySQL/PostgreSQL | Cloud SQL | Base Database | RDS | IBM Cloud Databases |
| Time Series Database | Amazon Timestream | Azure Time Series Insights | - | - | Time Series Database | IBM Cloud Databases |
| Database Migration | AWS Database Migration Service | Azure Database Migration Service | Database Migration Service | Database Migration | Data Transmission Service | IBM Cloud Database Migration |
| Autonomous Database | - | - | - | Autonomous Database | - | - |
| Data Warehouse | Amazon Redshift | Azure Synapse Analytics | BigQuery | Autonomous Data Warehouse | MaxCompute | IBM Db2 Warehouse |

## 开发者工具 (Developer Tools)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Development Collaboration Platform | Amazon CodeCatalyst | Azure DevOps | Cloud Code | Developer Service | - | IBM Cloud DevOps |
| Java Runtime | Amazon Corretto | - | - | - | - | - |
| Developer Lab Environment | AWS Cloud9 | Azure Lab Services | Cloud Workstations | - | - | IBM Cloud Shell |
| Cloud Shell | AWS CloudShell | Azure Cloud Shell | Cloud Shell | Cloud Shell | Cloud Shell | IBM Cloud Shell |
| Resource Management API | AWS Cloud Control API | - | - | - | - | IBM Cloud API |
| Artifact Repository | AWS CodeArtifact | Azure Artifacts | Artifact Registry | Container Registry | Container Registry | IBM Cloud Container Registry |
| Continuous Integration | AWS CodeBuild | Azure Pipelines | Cloud Build | DevOps Build Service | CICD | IBM Cloud Continuous Delivery |
| Continuous Deployment | AWS CodeDeploy | Azure Pipelines | Cloud Deploy | DevOps Deployment Service | CICD | IBM Cloud Continuous Delivery |
| Continuous Delivery | AWS CodePipeline | Azure Pipelines | Cloud Build | DevOps Build Pipeline | - | IBM Cloud Continuous Delivery |
| Development Project Management | AWS CodeStar | Azure DevOps | Cloud Code | - | - | IBM Cloud DevOps |
| Application Performance Monitoring | AWS X-Ray | Azure Application Insights | Cloud Trace | Application Performance Monitoring | ARMS | IBM Cloud Monitoring |
| Load Testing | - | Azure Load Testing | - | - | - | IBM Cloud Load Testing |
| Script Testing | - | Microsoft Playwright Testing | - | - | - | - |
| Code Repository | AWS CodeCommit | Azure Repos | Cloud Source Repositories | DevOps Code Repository | Codeup | IBM Cloud Git Repos |
| Development Metrics | - | Azure DevOps Analytics | - | - | DevOps Analytics | IBM Cloud DevOps Insights |
| Code Analysis & Security | Amazon CodeGuru | Azure DevSecOps, Azure DevOps | Software Supply Chain Security, Cloud Code | - | Code Analysis | IBM Cloud Security, IBM Cloud DevSecOps |
| API Testing | Amazon API Gateway | Azure API Management | Cloud Endpoints | API Gateway | API Gateway | IBM API Connect |

## 最终用户计算 (End User Computing)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Application Streaming | Amazon AppStream 2.0 | Azure Virtual Desktop | - | Desktop Service | Application Streaming | - |
| Virtual Desktop | Amazon WorkSpaces | Azure Virtual Desktop | - | Desktop as a Service | Elastic Desktop Service | IBM Cloud Virtual Desktop |
| Web Virtual Desktop | Amazon WorkSpaces Web | Azure Virtual Desktop | - | Browser Access | Workspace | IBM Cloud Virtual Desktop |

## 前端 Web 和移动 (Front-end Web & Mobile)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Location Service | Amazon Location Service | Azure Maps | Maps Platform | Location Service | Location Service | - |
| Mobile and Web Application Development | AWS Amplify | Azure Static Web Apps | Firebase | APEX | Mobile Development Platform | IBM Mobile Foundation |
| Mobile Application Testing | AWS Device Farm | Azure DevTest Labs | Firebase Test Lab | - | Mobile Testing | IBM Cloud Mobile Testing |

## 游戏开发 (Game Development)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Game Server Hosting | Amazon GameLift | Azure PlayFab | - | Game Development Cloud | Game Service | - |
| Game Backend Service | Amazon GameSparks | Azure PlayFab | - | Game Backend Service | GameShield | - |
| Game Development Toolkit | AWS GameKit | Azure PlayFab | - | - | Game Security | - |

## 物联网 (Internet of Things)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| One-Click IoT | AWS IoT 1-Click | - | - | - | - | - |
| IoT Data Analysis | AWS IoT Analytics | Azure IoT Hub | Cloud IoT Core | OCI IoT Analytics | IoT Analytics | IBM Watson IoT Platform |
| IoT Core Service | AWS IoT Core | Azure IoT Hub | Cloud IoT Core | OCI IoT | IoT Platform | IBM Watson IoT Platform |
| IoT Device Security | AWS IoT Device Defender | Azure IoT Security | Cloud IoT Core | OCI IoT Device Security | - | IBM Watson IoT Platform |
| IoT Device Management | AWS IoT Device Management | Azure IoT Hub | Cloud IoT Core | OCI IoT Device Management | IoT Device Management | IBM Watson IoT Platform |
| IoT Event Processing | AWS IoT Events | Azure IoT Hub | Cloud IoT Core | OCI IoT Events | - | IBM Watson IoT Platform |
| Vehicle Network Service | AWS IoT FleetWise | - | - | - | - | - |
| Edge Computing | AWS IoT Greengrass | Azure IoT Edge | Cloud IoT Edge | - | Link Edge | IBM Edge Computing |
| Robot Management | AWS IoT RoboRunner | - | - | - | - | - |
| Industrial IoT | AWS IoT SiteWise | Azure IoT Central | - | - | - | IBM Maximo |
| Digital Twin | AWS IoT TwinMaker | Azure Digital Twins | Supply Chain Twin | OCI Digital Twin | IoT Studio | IBM Maximo |
| Real-time Operating System | FreeRTOS | Azure RTOS | - | - | - | - |

## 机器学习 (Machine Learning)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| AI Base Model Service | Amazon Bedrock | Azure OpenAI Service | Vertex AI | OCI Language | PAI | IBM Watson Studio |
| Code Intelligence Assistant | Amazon CodeWhisperer | Azure OpenAI Service | Duet AI | - | Tongyi Lingma | IBM Watson Code Assistant |
| Natural Language Processing | Amazon Comprehend | Azure Cognitive Service - Text Analytics | Cloud Natural Language API | OCI Language | NLP | IBM Watson NLP |
| Predictive Analysis | Amazon Forecast | Azure Cognitive Service - Forecasting | - | OCI Forecasting | PAI-AutoLearning | IBM Watson Machine Learning |
| Dialog Robot | Amazon Lex | Azure Bot Service | Cloud Dialogflow | - | Intelligent Service Robot | IBM Watson Assistant |
| Computer Vision | Amazon Lookout for Vision | Azure Computer Vision | Cloud Vision AI | OCI Vision | Vision Intelligence | IBM Watson Visual Recognition |
| Personalized Recommendation | Amazon Personalize | Azure Personalizer | Recommendations AI | - | Machine Learning Platform | IBM Watson Machine Learning |
| Text-to-Speech | Amazon Polly | Azure Cognitive Service - Text-to-Speech | Cloud Text-to-Speech | OCI Speech | Speech Service | IBM Watson Text to Speech |
| Image Recognition | Amazon Rekognition | Azure Computer Vision | Cloud Vision AI | - | Image Search | IBM Watson Visual Recognition |
| Document Understanding | Amazon Textract | Azure Form Recognizer | Cloud Document AI | Document Understanding | - | IBM Watson Discovery |
| Machine Learning Platform | Amazon SageMaker | Azure Machine Learning | Vertex AI | OCI Data Science | PAI-Studio | IBM Watson Studio |
| AI Content Safety | - | Azure AI Content Safety | - | - | - | - |
| AI Document Intelligence | - | Azure AI Document Intelligence | - | - | - | IBM Watson Discovery |
| AI Face Recognition | - | Azure AI Face | - | - | - | IBM Watson Visual Recognition |
| AI Immersive Reader | - | Azure AI Immersive Reader | - | - | - | - |
| AI Video Indexer | - | Azure AI Video Indexer | - | - | - | IBM Watson Media |
| ML Model Registry | Amazon SageMaker | Azure ML | Vertex AI Model Registry | - | PAI-Studio | IBM Watson Studio |
| ML Pipeline | Amazon SageMaker | Azure ML | Vertex AI Pipelines | - | PAI-Studio | IBM Watson Studio |
| ML Feature Store | Amazon SageMaker | Azure ML | Vertex AI Feature Store | - | PAI-Studio | IBM Watson Studio |
| Speech Recognition | Amazon Transcribe | Azure Speech Service | Cloud Speech-to-Text | - | Speech Recognition | IBM Watson Speech to Text |
| Language Translation | Amazon Translate | Azure Translator | Cloud Translation | - | Machine Translation | IBM Watson Language Translator |
| AI Model Deployment | Amazon SageMaker | Azure ML Deployments | Vertex AI | - | PAI-EAS | IBM Watson Machine Learning |
| AI Model Monitoring | Amazon SageMaker | Azure ML Monitoring | Vertex AI | - | PAI-Studio | IBM Watson OpenScale |

## 管理与治理 (Management & Governance)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Account Management | AWS Account Management | Azure Subscription Management | Cloud Billing | Identity and Access Management | Resource Management | IBM Cloud Account Management |
| Application Auto Scaling | AWS Application Auto Scaling | Azure Autoscale | Autoscaling | Autoscaling | Auto Scaling | IBM Cloud Auto Scale |
| Infrastructure as Code | AWS CloudFormation | Azure Resource Manager | Cloud Deployment Manager | Resource Manager | ROS | IBM Cloud Schematics |
| Audit Logs | AWS CloudTrail | Azure Monitor | Cloud Audit Logs | Audit | ActionTrail | IBM Cloud Activity Tracker |
| Monitoring and Observability | AWS CloudWatch | Azure Monitor | Cloud Monitoring | Monitoring | CloudMonitor | IBM Cloud Monitoring |
| Configuration Management | AWS Config | Azure Policy | Security Command Center | Configuration Management | Config | IBM Cloud Security and Compliance Center |
| Multi-Account Management | AWS Control Tower | Azure Landing Zones | - | Compartments | Resource Directory | IBM Cloud Enterprise |
| Management Console | AWS Management Console | Azure Portal | Cloud Console | Cloud Console | Management Console | IBM Cloud Console |
| Organization Management | AWS Organizations | Azure Management Groups | Cloud Identity & Organization | Identity Domains | Resource Management | IBM Cloud Enterprise Management |
| Service Catalog | AWS Service Catalog | Azure Marketplace | Cloud Marketplace | Marketplace | Cloud Marketplace | IBM Cloud Catalog |
| Best Practices Recommendations | AWS Trusted Advisor | Azure Advisor | Recommender | Cloud Advisor | Advisor | IBM Cloud Advisor |
| Cost Management | AWS Cost Explorer | Azure Cost Management | Cloud Billing | Cost Management | Cost Manager | IBM Cloud Cost Management |
| Resource Health | AWS Health Dashboard | Azure Service Health | Cloud Status | Cloud Status | Cloud Monitor | IBM Cloud Status |
| Cloud Asset Inventory | AWS Config | Azure Resource Graph | Cloud Asset Inventory | - | Resource Management | IBM Cloud Security and Compliance |
| Binary Authorization | - | Azure Policy | Binary Authorization | - | Container Registry | IBM Cloud Container Security |
| Advisory Notifications | AWS Security Hub | Azure Security Center | Advisory Notifications | - | Security Center | IBM Cloud Security Advisor |
| Service Health Monitoring | AWS Personal Health Dashboard | Azure Service Health | Cloud Status | - | Cloud Monitor | IBM Cloud System Status |
| Resource Visualization | AWS Resource Groups | Azure Resource Graph | Asset Inventory | - | Resource Management | IBM Cloud Resource Visualization |
| Policy Management | AWS Organizations | Azure Policy | Organization Policy | - | Resource Management | IBM Cloud Security and Compliance |
| Support Management | AWS Support | Azure Support | Google Cloud Support | Support Management | Support | IBM Cloud Support |
| License Management | AWS License Manager | Azure Hybrid Benefit | - | License Manager | - | IBM Cloud License Management |
| Resource Scheduler | AWS Systems Manager | Azure Automation | Cloud Scheduler | Resource Scheduler | - | IBM Cloud Scheduler |
| Security Zones | AWS Control Tower | Azure Security Center | Security Command Center | Security Zones | - | IBM Cloud Security and Compliance Center |
| Bastion Service | AWS Systems Manager Session Manager | Azure Bastion | Identity-Aware Proxy | Bastion | - | IBM Cloud Bastion |
| Managed Access | AWS IAM Identity Center | Azure AD Privileged Identity Management | Cloud Identity | Managed Access | - | IBM Cloud IAM |
| Service Management | - | - | - | - | - | IBM Cloud Service Management |
| Resource Controller | - | - | - | - | - | IBM Cloud Resource Controller |

## 媒体服务 (Media Services)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Media Transcoding | Amazon Elastic Transcoder | Azure Media Services | Transcoder API | Media Flow | Media Processing | IBM Cloud Video Streaming |
| Video Stream Processing | Amazon Kinesis Video Streams | Azure Media Services | - | Streaming | ApsaraVideo Live | IBM Cloud Video Streaming |
| Video Transcoding | AWS Elemental MediaConvert | Azure Media Services | Transcoder API | - | ApsaraVideo VOD | IBM Cloud Video Streaming |
| Live Streaming | AWS Elemental MediaLive | Azure Media Services | Live Stream API | - | ApsaraVideo Live | IBM Cloud Video Streaming |
| Media Storage | AWS Elemental MediaStore | Azure Media Services | Cloud Storage | Object Storage | ApsaraVideo VOD | IBM Cloud Object Storage |

## 迁移与传输 (Migration & Transfer)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Application Discovery Service | AWS Application Discovery Service | Azure Migrate | Cloud Asset Inventory | Application Migration | - | IBM Cloud Migration |
| Application Migration Service | AWS Application Migration Service | Azure Migrate | Migrate for Compute Engine | Migration Service | - | IBM Cloud Migration |
| Database Migration | AWS Database Migration Service | Azure Database Migration Service | Database Migration Service | Database Migration | Data Transmission Service | IBM Cloud Database Migration |
| Mainframe Modernization | AWS Mainframe Modernization | - | - | Cloud Migration | - | IBM Cloud Modernization |
| Migration Center | AWS Migration Hub | Azure Migrate | - | Migration Hub | - | IBM Cloud Migration |
| Server Migration | AWS Server Migration Service | Azure Migrate | Migrate for Compute Engine | Compute Migration | - | IBM Cloud Migration |
| Data Transfer Device | AWS Snow Family | Azure Data Box | Transfer Appliance | Data Transfer Appliance | - | IBM Cloud Mass Data Migration |
| File Transfer | AWS Transfer Family | Azure Files | Cloud Storage SFTP | - | - | IBM Cloud File Transfer |
| Data Transfer & Synchronization | AWS DataSync | Azure File Sync, Azure Data Box | Storage Transfer Service | Data Transfer Service, Data Transfer | - | IBM Cloud Data Sync, IBM Cloud Mass Data Migration |

## 网络与内容分发 (Networking & Content Delivery)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Content Delivery Network | Amazon CloudFront | Azure CDN | Cloud CDN | Content Delivery Network | CDN | IBM Cloud CDN |
| DNS Service | Amazon Route 53 | Azure DNS | Cloud DNS | DNS | DNS | IBM Cloud DNS Services |
| Virtual Private Cloud | Amazon VPC | Azure Virtual Network | Virtual Private Cloud | Virtual Cloud Network | VPC | IBM Cloud VPC |
| Service Mesh | AWS App Mesh | Azure Service Fabric Mesh | Traffic Director | - | Service Mesh | IBM Cloud Service Mesh |
| VPN Client | AWS Client VPN | Azure VPN Gateway | Cloud VPN | VPN Connect | - | IBM Cloud VPN |
| Service Discovery | AWS Cloud Map | Azure App Configuration | Cloud Service Directory | - | Service Discovery | IBM Cloud Service Discovery |
| Wide Area Network Service | AWS Cloud WAN | Azure Virtual WAN | Network Connectivity Center | - | Smart Access Gateway | - |
| Dedicated Connection | AWS Direct Connect | Azure ExpressRoute | Cloud Interconnect | FastConnect | Express Connect | IBM Cloud Direct Link |
| Global Accelerator | AWS Global Accelerator | Azure Front Door | Premium Tier Networking | - | Global Accelerator | IBM Cloud Internet Services |
| Private 5G Network | AWS Private 5G | Azure Private 5G Core | - | - | Private 5G | IBM Cloud for Telecommunications |
| Private Connection | AWS PrivateLink | Azure Private Link | Private Service Connect | Service Gateway | PrivateLink | IBM Cloud Private Link |
| Site-to-Site VPN | AWS Site-to-Site VPN | Azure VPN Gateway | Cloud VPN | - | VPN Gateway | IBM Cloud VPN |
| Transit Gateway | AWS Transit Gateway | Azure Virtual WAN | Network Connectivity Center | - | Cloud Enterprise Network | IBM Cloud Direct Link |
| Load Balancing | Elastic Load Balancing | Azure Load Balancer | Cloud Load Balancing | Load Balancer | SLB | IBM Cloud Load Balancer |
| DDoS Protection | AWS Shield | Azure DDoS Protection | Cloud Armor | DDoS Protection | Anti-DDoS | IBM Cloud Internet Services |
| Communication Gateway | - | Azure Communications Gateway | - | - | - | - |
| Elastic SAN | - | Azure Elastic SAN | - | - | - | - |
| Fluid Relay | - | Azure Fluid Relay | - | - | - | - |
| NAT Gateway | - | Azure NAT Gateway | - | - | - | IBM Cloud NAT Gateway |
| Network Function Manager | - | Azure Network Function Manager | - | - | - | - |
| SignalR Service | - | Azure SignalR Service | - | - | - | - |
| Web PubSub | - | Azure Web PubSub | - | - | - | - |
| API Gateway Management | Amazon API Gateway | Azure API Management | Cloud Endpoints | API Gateway | API Gateway | IBM API Connect |
| Network Monitoring | AWS Network Manager | Azure Network Watcher | Network Intelligence Center | Network Monitor | Network Analysis | IBM Cloud Flow Logs |
| Network Analysis | AWS Network Insights | Azure Network Watcher | Network Intelligence Center | Network Monitoring | Network Analysis | IBM Cloud Flow Logs |
| Traffic Management | AWS Global Accelerator | Azure Traffic Manager | Cloud Load Balancing | Traffic Management | DCDN | IBM Cloud Internet Services |
| Media CDN | Amazon CloudFront | Azure CDN | Media CDN | - | CDN | IBM Cloud CDN |
| Network Service Tiers | - | Azure ExpressRoute | Network Service Tiers | FastConnect | Express Connect | IBM Cloud Direct Link |
| Global Traffic Management & Acceleration | AWS Global Accelerator | Azure Front Door, Azure Traffic Manager | Premium Tier Networking, Cloud Load Balancing | Traffic Management | Global Accelerator, DCDN, Global Traffic Manager | IBM Cloud Internet Services |
| Network Connectivity Center | AWS Transit Gateway | Azure Virtual WAN | Network Connectivity Center | - | Cloud Enterprise Network | IBM Cloud Direct Link |

## 安全、身份与合规 (Security, Identity & Compliance)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Identity Authentication Service | Amazon Cognito | Azure Active Directory B2C | Firebase Authentication | Identity Cloud Service | IDaaS | IBM Cloud IAM |
| Security Investigation Service | Amazon Detective | Azure Sentinel | Security Command Center | Cloud Guard | Security Center | IBM Cloud Security Advisor |
| Threat Detection Service | Amazon GuardDuty | Azure Defender | Security Command Center | Cloud Guard | Security Center | IBM Cloud Security Advisor |
| Security Assessment Service | Amazon Inspector | Azure Defender | Security Command Center | Cloud Guard | Security Center | IBM Cloud Security and Compliance Center |
| Data Privacy Service | Amazon Macie | Azure Information Protection | Cloud DLP | Data Safe | Sensitive Data Discovery | IBM Cloud Data Shield |
| Permission Verification Service | Amazon Verified Permissions | Azure RBAC | Cloud IAM | - | - | IBM Cloud IAM |
| Compliance Reporting Service | AWS Artifact | Azure Policy | Compliance Reports | - | - | IBM Cloud Security and Compliance Center |
| Audit Management Service | AWS Audit Manager | Azure Policy | Security Command Center | - | - | IBM Cloud Security and Compliance Center |
| Certificate Management Service | AWS Certificate Manager | Azure Key Vault | Certificate Authority Service | - | - | IBM Cloud Certificate Manager |
| Hardware Security Module | AWS CloudHSM | Azure Dedicated HSM | Cloud HSM | - | - | IBM Cloud HSM |
| Directory Service | AWS Directory Service | Azure Active Directory | Cloud Identity | - | - | IBM Cloud Directory Service |
| Firewall Management | AWS Firewall Manager | Azure Firewall Manager | Cloud Armor | - | - | IBM Cloud Internet Services |
| Identity Access Management | AWS IAM | Azure Active Directory | Cloud IAM | Identity and Access Management | RAM | IBM Cloud IAM |
| Identity Center | AWS Identity Center | Azure Active Directory | Cloud Identity | - | - | IBM Cloud IAM |
| Key Management Service | AWS KMS | Azure Key Vault | Cloud KMS | Key Management | KMS | IBM Key Protect |
| Network Firewall | AWS Network Firewall | Azure Firewall | Cloud Armor | - | Cloud Firewall | IBM Cloud Internet Services |
| Private Certificate Authority | AWS Private Certificate Authority | Azure Key Vault | Certificate Authority Service | - | - | IBM Cloud Certificate Manager |
| Resource Access Management | AWS Resource Access Manager | Azure RBAC | Cloud IAM | - | - | IBM Cloud IAM |
| Secret Management | AWS Secrets Manager | Azure Key Vault | Secret Manager | - | - | IBM Cloud Secrets Manager |
| Security Center | AWS Security Hub | Azure Sentinel | Security Command Center | - | - | IBM Cloud Security Advisor |
| DDoS Protection | AWS Shield | Azure DDoS Protection | Cloud Armor | DDoS Protection | Anti-DDoS | IBM Cloud Internet Services |
| Web Application Firewall | AWS WAF | Azure Web Application Firewall | Cloud Armor | Web Application Firewall | WAF | IBM Cloud Internet Services |
| Security Monitoring | AWS Security Hub | Azure Sentinel | Security Command Center | - | - | IBM Cloud Security Advisor |
| Vulnerability Scanning | Amazon Inspector | Azure Defender | Security Command Center | - | - | IBM Cloud Security Advisor |
| Security Posture Management | AWS Security Hub | Microsoft Defender for Cloud | Security Command Center | Cloud Guard | Security Center | IBM Cloud Security and Compliance Center |
| Zero Trust Security | - | Azure Zero Trust | BeyondCorp | - | Zero Trust Security | IBM Cloud Security Zero Trust |
| Cloud Asset Inventory | AWS Config | Azure Resource Graph | Cloud Asset Inventory | - | Resource Management | IBM Cloud Security and Compliance |
| Binary Authorization | - | Azure Policy | Binary Authorization | - | Container Registry | IBM Cloud Container Security |
| Advisory Notifications | AWS Security Hub | Azure Security Center | Advisory Notifications | - | Security Center | IBM Cloud Security Advisor |
| Confidential Computing | AWS Nitro Enclaves | Azure Confidential Computing | Confidential Computing | - | Security Center | IBM Cloud Hyper Protect Services |
| Security Information Management | Amazon Security Lake | Azure Sentinel | Chronicle | - | Security Center | IBM Cloud Security Insights |
| External Identity Management | Amazon Cognito | Azure External ID | Identity Platform | - | IDaaS | IBM Cloud IAM |
| Anti-Bot Service | AWS WAF | Azure Web Application Firewall | Cloud Armor | - | Anti-Bot Service | IBM Cloud Internet Services |
| SSL Certificate Service | AWS Certificate Manager | Azure App Service Certificates | - | - | SSL Certificates Service | IBM Cloud Certificate Manager |
| Cloud Security Scanner | Amazon Inspector | Azure Defender | Security Scanner | - | Cloud Security Scanner | IBM Cloud Security Advisor |

## 存储服务 (Storage)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Block Storage Service | Amazon EBS | Azure Managed Disks | Persistent Disk | Block Volume | Block Storage | IBM Cloud Block Storage |
| File Storage Service | Amazon EFS | Azure Files | Filestore | File Storage | NAS | IBM Cloud File Storage |
| File System Service | Amazon FSx | Azure Files | Filestore | - | NAS | IBM Cloud File Storage |
| Object Storage Service | Amazon S3 | Azure Blob Storage | Cloud Storage | Object Storage | OSS | IBM Cloud Object Storage |
| Archive Storage Service | Amazon S3 Glacier | Azure Archive Storage | Cloud Storage Archive | Archive Storage | OSS Archive | IBM Cloud Object Storage Archive |
| Backup Service | AWS Backup | Azure Backup | Backup and DR Service | Backup Service | Hybrid Backup Recovery | IBM Cloud Backup |
| Disaster Recovery Service | AWS Elastic Disaster Recovery | Azure Site Recovery | - | - | Hybrid Disaster Recovery | IBM Cloud Disaster Recovery |
| Data Transfer Device | AWS Snow Family | Azure Data Box | Transfer Appliance | Data Transfer Appliance | - | IBM Cloud Mass Data Migration |
| Storage Gateway Service | AWS Storage Gateway | Azure Storage Gateway | Storage Transfer Service | - | Storage Gateway | IBM Cloud Storage Gateway |
| HPC Cache | - | Azure HPC Cache | - | - | - | - |
| Managed Lustre | - | Azure Managed Lustre | - | - | - | - |
| NetApp Storage | - | Azure NetApp Files | - | - | - | - |
| Queue Storage | - | Azure Queue Storage | - | - | - | IBM Cloud Messages for RabbitMQ |
| Storage Lifecycle Management | S3 Lifecycle | Azure Storage Lifecycle | Object Lifecycle Management | Object Lifecycle Management | OSS Lifecycle | IBM Cloud Object Storage Lifecycle |
| Storage Performance | Amazon EBS io2 | Azure Ultra Disk | Persistent Disk | Block Volume | ESSD | IBM Cloud Block Storage |

## 量子计算 (Quantum Technologies)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Quantum Computing Platform | Amazon Braket | Azure Quantum | Google Quantum AI | Quantum Computing | Quantum Computing Platform | IBM Quantum |

## 机器人技术 (Robotics)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Robot Management Service | AWS IoT RoboRunner | - | - | - | Robot Service | - |
| Robot Development Platform | AWS RoboMaker | - | Cloud Robotics Core | - | Robot Development Platform | - |

## 卫星 (Satellite)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Satellite Ground Station Service | AWS Ground Station | Azure Orbital | - | - | Satellite Connection | - |

## 混合与多云 (Hybrid + Multicloud)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Hybrid Management Service | AWS Outposts | Azure Arc | Anthos | - | Alibaba Cloud Apsara Stack | IBM Cloud Satellite |
| Edge Kubernetes | - | Azure Kubernetes Service Edge Essentials | - | - | - | IBM Edge Computing |
| Operator Service | - | Azure Operator Nexus | - | - | - | - |
| Operator Insights | - | Azure Operator Insights | - | - | - | - |

## 域名注册 (Domain Registration)

| Service Type | AWS | Azure | GCP | OCI | Alibaba Cloud | IBM Cloud |
|---------|-----|-------|-----|-----|---------------|-----------|
| Domain Registration Service | Amazon Route 53 Domains | Azure App Service Domains | Cloud Domains | - | Domains | IBM Cloud Domains |
| Domain Management | Amazon Route 53 | Azure DNS | Cloud Domains | DNS | Domains | IBM Cloud DNS Services |
| Domain Transfer | Amazon Route 53 | Azure App Service Domains | Cloud Domains | - | Domains | IBM Cloud Domains |
| Domain Privacy Protection | Amazon Route 53 | Azure App Service Domains | Cloud Domains | - | Domain Privacy | IBM Cloud Domains |
| Domain Auto-renewal | Amazon Route 53 | Azure App Service Domains | Cloud Domains | - | Domains | IBM Cloud Domains |
| Domain Whois Service | Amazon Route 53 | Azure App Service Domains | Cloud Domains | - | Domain Whois | IBM Cloud Domains |