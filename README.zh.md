# Enterprise Hub MCP Skill

这是 `enterprise-hub-mcp` 的独立 Codex skill 仓库，用来指导 Codex 或其他员工自有 agent 通过 MCP 安全使用 企业资料中枢。

这个仓库只包含 skill，不包含 企业资料中枢 API、worker、数据库、Qdrant 或 MCP server 实现。服务实现仍来自主项目 `YinXiaoyu-1998/SME_DATA_CENTER`。

## 当前产品面

企业资料中枢当前是 Phase 3 检索/数据底座：

- evidence 文档：`upload_evidence_document` → indexing → `get_evidence_document_status` / `search_document_evidence`
- structured 数据：`upload_structured_dataset` → MySQL import → `get_import_status` / `list_structured_datasets` / `query_structured_dataset`

它不是员工直接对话的 AI agent，不生成最终业务答案，不生成报表/dashboard，不执行 Skill Directory 条目，也不允许 agent 绕过 API 直读 MySQL、Qdrant、storage、session 文件或 token。

旧的普通文档上传、搜索、详情、下载、归档流程已移除。

## 仓库内容

```text
skills/enterprise-hub-mcp/
  SKILL.md
  agents/openai.yaml
```

## 安装到 Codex

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YinXiaoyu-1998/enterprise-hub-mcp-skill \
  --path skills/enterprise-hub-mcp
```

安装后重启 Codex 或新开 thread，skill 才会重新加载。

## 主项目前置条件

本地默认主项目路径：

```text
/Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER
```

主项目准备：

```sh
cd /Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER
npm install
MYSQL_PORT=3307 npm run runtime:compose:up
DATABASE_URL='mysql://enterprise_hub:enterprise_hub_local_password@localhost:3307/enterprise_hub' npm run db:generate
DATABASE_URL='mysql://enterprise_hub:enterprise_hub_local_password@localhost:3307/enterprise_hub' npm run db:migrate
DATABASE_URL='mysql://enterprise_hub:enterprise_hub_local_password@localhost:3307/enterprise_hub' npm run db:seed
npm run qdrant:init
```

## Codex MCP 配置

推荐使用 `mcp-bootup`，让本地 MCP server 启动 API、worker loop 和 MCP stdio server：

```toml
[mcp_servers.enterprise-hub]
command = "bash"
args = ["-lc", "cd /Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER && npm run --silent mcp-bootup"]
startup_timeout_sec = 120

[mcp_servers.enterprise-hub.env]
ENTERPRISE_HUB_MCP_SESSION_FILE = "/Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER/.data/enterprise-hub-mcp/session.json"
```

不要在配置里写生产 token、password、API key、OSS credential 或 service account。

## 推荐 Codex 提示词

```text
Use $enterprise-hub-mcp with the local-development profile.
Log in as baoli.manager@example.com with sessionName "baoli".
List labels.
Upload/search/query through the Phase 3 evidence or structured tools only.
Do not print raw tokens, do not ask for production credentials, and do not claim inaccessible data exists.
```

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

## 本地验证流程

最小 evidence 验证：

1. 登录 `baoli.manager@example.com`，sessionName 用 `baoli`。
2. 调 `enterprise_hub_list_labels`，选择 `store:baoli`。
3. 调 `upload_evidence_document` 上传一个本地 MD/TXT/DOCX。
4. 调 `get_evidence_document_status`，等待 document active 且 index ready。
5. 调 `search_document_evidence`，返回 evidence chunks；不要生成最终答案。

最小 structured 验证：

1. 登录 `baoli.manager@example.com`。
2. 调 `upload_structured_dataset` 上传主项目的 `fixtures/structured/dishes-valid.csv`，dataset 为 `dishes`，带 `store:baoli`。
3. 调 `get_import_status`。
4. 调 `list_structured_datasets`。
5. 调 `query_structured_dataset` 做受控只读查询；不要发送 SQL。

权限隔离验证：

1. 登录 `suzhou.manager@example.com`，sessionName 用 `suzhou`。
2. 搜索或查询同一 Baoli 内容。
3. 预期没有可见结果，也不泄露标题、文件名、行数、source metadata 或存在性。

自动 smoke：

```sh
cd /Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER
MYSQL_PORT=3307 npm run test:mcp
```

## 安全边界

- 所有非 health 数据访问必须通过 MCP tools 和后端 HTTP API authorization。
- 不要让 agent 直读 MySQL、Qdrant、storage、session 文件或 token。
- 不要让 agent 发送 raw SQL、公式、window function、join、delete/update/insert/DDL 或自然语言 query generation 指令。
- 不要让 agent 生成最终业务结论、报表或 dashboard。
- 不要上传真实客户导出、第三方下载数据或公司机密文件，除非用户明确授权该具体文件。
- 不要声称不可见数据存在。
- `staging-remote` 和 `production` 目前只是占位 profile；没有批准配置前不要发明 endpoint、token flow、域名或 TLS 设置。

## 故障排查

| 现象                                       | 处理方式                                     |
| ------------------------------------------ | -------------------------------------------- |
| Codex 里看不到 `enterprise-hub` MCP server | 重启 Codex，或检查 `~/.codex/config.toml`    |
| Codex 里看不到 `$enterprise-hub-mcp` skill | 确认安装目录存在后重启 Codex                 |
| MCP tools 未暴露                           | 说明 MCP 未连接；不要 fallback 到 CLI/API    |
| tool 调用连接失败                          | 说明服务不可用；只有用户要求时才检查本地启动 |
| 登录返回 `EMPLOYEE_NOT_FOUND`              | 重新 seed 本地数据库，确认 API 使用同一 DB   |
| evidence 上传后搜索为空                    | 先查 `get_evidence_document_status`          |
| structured import 失败                     | 返回服务 validation errors，不要本地改表     |
| Suzhou 搜不到 Baoli 数据                   | 这是预期权限隔离结果                         |

## 相关仓库

- 主项目：`YinXiaoyu-1998/SME_DATA_CENTER`
- 本 skill repo：`YinXiaoyu-1998/enterprise-hub-mcp-skill`
