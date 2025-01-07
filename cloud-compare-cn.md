各云厂商产品数量统计：
| 云服务商 | 产品大类数量 | 具体产品/服务数量 |
|----------|--------------|-------------------|
| AWS | 23 | 200+ |
| Azure | 22 | 200+ |
| GCP | 19 | 150+ |

我将尽可能详尽地列出主要云服务的竞品关系。为了便于阅读，我会按照服务类别分多个表格展示。

1. 计算服务

| 服务类型 | AWS | Azure | GCP |
|----------|-----|-------|-----|
| 虚拟机 | EC2 | Virtual Machines | Compute Engine |
| 容器服务 | EKS | AKS | GKE |
| 容器注册表 | ECR | Container Registry | Container Registry |
| 无服务器计算 | Lambda | Azure Functions | Cloud Functions |
| 容器实例 | Fargate | Container Instances | Cloud Run |
| 批处理 | Batch | Batch | Cloud Batch |
| 弹性编排 | Auto Scaling | VM Scale Sets | Instance Groups |

2. 存储服务

| 服务类型 | AWS | Azure | GCP |
|----------|-----|-------|-----|
| 对象存储 | S3 | Blob Storage | Cloud Storage |
| 文件存储 | EFS | Files | Filestore |
| 块存储 | EBS | Managed Disks | Persistent Disk |
| 归档存储 | Glacier | Archive Storage | Archive Storage |
| 混合存储 | Storage Gateway | StorSimple | Storage Transfer Service |
| 备份服务 | Backup | Backup | Backup and DR |

3. 数据库服务

| 服务类型 | AWS | Azure | GCP |
|----------|-----|-------|-----|
| 关系型数据库 | RDS | Azure SQL Database | Cloud SQL |
| NoSQL文档数据库 | DynamoDB | Cosmos DB | Firestore |
| 内存数据库 | ElastiCache | Cache for Redis | Memorystore |
| 时序数据库 | Timestream | Time Series Insights | Cloud Bigtable |
| 图数据库 | Neptune | Cosmos DB Graph API | - |
| 数据仓库 | Redshift | Synapse Analytics | BigQuery |
| 数据迁移 | Database Migration Service | Database Migration Service | Database Migration Service |

4. 网络服务

| 服务类型 | AWS | Azure | GCP |
|----------|-----|-------|-----|
| 虚拟网络 | VPC | Virtual Network | VPC |
| CDN | CloudFront | Azure CDN | Cloud CDN |
| DNS服务 | Route 53 | DNS | Cloud DNS |
| 负载均衡 | ELB | Load Balancer | Cloud Load Balancing |
| VPN服务 | VPN Gateway | VPN Gateway | Cloud VPN |
| 专线服务 | Direct Connect | ExpressRoute | Cloud Interconnect |
| 防火墙 | Network Firewall | Azure Firewall | Cloud Armor |

5. 安全与身份

| 服务类型 | AWS | Azure | GCP |
|----------|-----|-------|-----|
| 身份认证 | IAM | Azure Active Directory | Cloud IAM |
| 密钥管理 | KMS | Key Vault | Cloud KMS |
| 证书服务 | Certificate Manager | App Service Certificates | Certificate Authority Service |
| 安全评估 | Inspector | Security Center | Security Command Center |
| WAF | WAF | WAF | Cloud Armor |
| DDoS防护 | Shield | DDoS Protection | Cloud Armor |

6. 开发者工具

| 服务类型 | AWS | Azure | GCP |
|----------|-----|-------|-----|
| CI/CD | CodePipeline | DevOps | Cloud Build |
| 代码仓库 | CodeCommit | DevOps Repos | Cloud Source Repositories |
| API网关 | API Gateway | API Management | Cloud Endpoints/API Gateway |
| 开发工具 | Cloud9 | DevOps | Cloud Code |
| 监控服务 | CloudWatch | Azure Monitor | Cloud Monitoring |
| 日志服务 | CloudWatch Logs | Log Analytics | Cloud Logging |

7. AI/ML服务

| 服务类型 | AWS | Azure | GCP |
|----------|-----|-------|-----|
| 机器学习平台 | SageMaker | Azure Machine Learning | Vertex AI |
| 语音服务 | Polly/Transcribe | Cognitive Speech Services | Cloud Speech-to-Text |
| 视觉服务 | Rekognition | Computer Vision | Cloud Vision AI |
| 自然语言处理 | Comprehend | Text Analytics | Cloud Natural Language |
| 翻译服务 | Translate | Translator | Cloud Translation |
| 对话机器人 | Lex | Bot Service | Dialogflow |

8. 分析服务

| 服务类型 | AWS | Azure | GCP |
|----------|-----|-------|-----|
| 数据湖 | Lake Formation | Data Lake Storage | Cloud Storage |
| 流处理 | Kinesis | Stream Analytics | Dataflow |
| ETL服务 | Glue | Data Factory | Cloud Data Fusion |
| 分析查询 | Athena | Data Explorer | BigQuery |
| 可视化 | QuickSight | Power BI | Looker |

9. 集成服务

| 服务类型 | AWS | Azure | GCP |
|----------|-----|-------|-----|
| 消息队列 | SQS | Service Bus | Cloud Pub/Sub |
| 事件总线 | EventBridge | Event Grid | Cloud Scheduler |
| 通知服务 | SNS | Notification Hubs | Cloud Pub/Sub |
| 工作流服务 | Step Functions | Logic Apps | Workflows |
| API管理 | API Gateway | API Management | Apigee |

注意事项：
此列表并非详尽无遗，仅包含主要服务
某些服务可能跨越多个类别
部分服务的功能范围和定位可能略有差异
各云服务商可能有独特的服务没有直接对应的竞品
服务名称和功能会随时间更新变化