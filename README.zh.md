# Enterprise Hub MCP Skill

这是 `enterprise-hub-mcp` 的独立 Codex skill 仓库，用来指导 Codex 或其他员工自有 agent 通过 MCP 安全使用企业资料中枢。

本仓库只包含 skill 和 MCP 客户端连接说明；不包含、安装、启动、停止、初始化或维护企业资料中枢 API、worker、数据库、Qdrant、storage 或其他后台服务。服务实现和运维知识归属主项目 [YinXiaoyu-1998/SME_DATA_CENTER](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER)。

## 当前产品面

企业资料中枢当前是 Phase 3 检索/数据底座：

- evidence 文档：`upload_evidence_document` → indexing → `get_evidence_document_status` / `search_document_evidence`
- structured 数据：`upload_structured_dataset` → MySQL import → `get_import_status` / `list_structured_datasets` / `query_structured_dataset`

它不是员工直接对话的 AI agent，不生成最终业务答案、报表或 dashboard，不执行 Skill Directory 条目，也不允许 agent 绕过 API 直读 MySQL、Qdrant、storage、session 文件或 token。

## 安装到 Codex

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YinXiaoyu-1998/enterprise-hub-mcp-skill \
  --path skills/enterprise-hub-mcp
```

安装后重启 Codex 或新开 thread，skill 才会重新加载。

## 服务前置条件

服务运营方必须先部署或运行 API、worker、数据库、存储和 Qdrant，并向 MCP 使用者提供已批准的 `ENTERPRISE_HUB_API_URL`。本 skill 不能也不会执行安装服务、启动 Docker、迁移或 seed 数据库、初始化 Qdrant、运行 worker 或修复服务等操作。

本地服务开发与运维流程见主项目的 [README](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/README.md)、[环境变量清单](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/env-inventory.md) 和 [staging 就绪清单](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/staging-readiness.md)。

## Codex MCP 配置

MCP adapter 位于主项目工作目录中。下面的命令只启动 MCP stdio adapter；它不会启动或管理 API、worker、数据库或其他服务。配置前，确认 `ENTERPRISE_HUB_API_URL` 已由服务运营方提供且可访问。

```toml
[mcp_servers.enterprise-hub]
command = "bash"
args = ["-lc", "cd /path/to/SME_DATA_CENTER && npm run --silent mcp:dev"]
startup_timeout_sec = 120

[mcp_servers.enterprise-hub.env]
ENTERPRISE_HUB_API_URL = "https://approved-enterprise-hub-api.example"
ENTERPRISE_HUB_MCP_PROFILE = "local-development"
ENTERPRISE_HUB_MCP_SESSION_FILE = "/path/to/SME_DATA_CENTER/.data/enterprise-hub-mcp/session.json"
```

不要在配置里写生产 token、password、API key、OSS credential 或 service account。

## 当前 MCP Tools

| Tool                           | 用途                                  |
| ------------------------------ | ------------------------------------- |
| `enterprise_hub_login_dev`     | 用 seeded email 登录本地 dev session  |
| `enterprise_hub_list_labels`   | 读取可用标签目录                      |
| `enterprise_hub_list_skills`   | 读取已批准 Skill Directory 元数据     |
| `upload_evidence_document`     | 上传 MD/TXT/DOCX evidence 文档        |
| `get_evidence_document_status` | 查询 evidence 文档和索引状态          |
| `search_document_evidence`     | 检索可见 evidence chunks              |
| `upload_structured_dataset`    | 上传 dishes/business CSV/XLSX 数据集  |
| `get_import_status`            | 查询结构化导入状态                    |
| `list_structured_datasets`     | 查询可用 dataset/字段/operator schema |
| `query_structured_dataset`     | 执行受控只读结构化 JSON 查询          |

## 故障处理

| 现象                                       | 处理方式                                                     |
| ------------------------------------------ | ------------------------------------------------------------ |
| Codex 里看不到 `enterprise-hub` MCP server | 检查 MCP 客户端配置并重启 Codex。                            |
| MCP tools 未暴露或 tool 调用连接失败       | 报告服务未连接或不可用；不要启动、修复或修改任何服务。       |
| 登录返回 `EMPLOYEE_NOT_FOUND`              | 报告该服务当前没有此开发身份；不要 seed 或修改数据库。       |
| evidence 上传后搜索为空                    | 调 `get_evidence_document_status` 并报告服务返回的索引状态。 |
| structured import 失败                     | 返回服务 validation errors，不要本地改表。                   |

## 安全边界

- 所有非 health 数据访问必须通过 MCP tools 和后端 HTTP API authorization。
- 不要让 agent 直读 MySQL、Qdrant、storage、session 文件或 token。
- 不要让 agent 发送 raw SQL、公式、window function、join、delete/update/insert/DDL 或自然语言 query generation 指令。
- 不要让 agent 生成最终业务结论、报表或 dashboard。
- 不要上传真实客户导出、第三方下载数据或公司机密文件，除非用户明确授权该具体文件。
- `staging-remote` 和 `production` 目前只是占位 profile；没有批准配置前不要发明 endpoint、token flow、域名或 TLS 设置。
