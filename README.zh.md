# Enterprise Hub MCP Skill

这是 `enterprise-hub-mcp` 的独立 Codex skill 仓库，用来指导 Codex 或其他员工自有 agent 通过本机 MCP launcher 安全使用企业资料中枢。

本仓库只包含 skill 和 MCP 客户端连接说明；不包含、安装、启动、停止、初始化或维护企业资料中枢 API、worker、数据库、Qdrant、storage 或其他后台服务。服务实现和运维知识归属主项目 [YinXiaoyu-1998/SME_DATA_CENTER](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER)。

## 当前产品面

企业资料中枢当前是 Phase 3 检索/数据底座：

- evidence 文档：`upload_evidence_document` -> indexing -> `get_evidence_document_status` / `search_document_evidence`
- structured 数据：`upload_structured_dataset` -> MySQL import -> `get_import_status` / `list_structured_datasets` / `query_structured_dataset`

它不是员工直接对话的 AI agent，不生成最终业务答案、报表或 dashboard，不执行 Skill Directory 条目，也不允许 agent 绕过 API 直读 MySQL、Qdrant、storage、session 文件或 token。

## 安装到 Codex

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YinXiaoyu-1998/enterprise-hub-mcp-skill \
  --path skills/enterprise-hub-mcp
```

安装后重启 Codex 或新开 thread，skill 才会重新加载。

## 服务前置条件

主服务必须已由服务操作方运行。skill 和 launcher 不得启动、迁移、seed、修复或检查 API、worker、Docker、数据库、Qdrant 或 storage。

本地服务开发与运维流程见主项目的 [README](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/README.md)、[环境变量清单](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/env-inventory.md) 和 [staging 就绪清单](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/staging-readiness.md)。

## Codex MCP 配置

配置本机 launcher；服务端只提供 authenticated Streamable HTTP `POST /mcp`：

```toml
[mcp_servers.enterprise-hub]
command = "npm"
args = ["run", "--silent", "mcp:launcher"]
cwd = "/path/to/SME_DATA_CENTER"
startup_timeout_sec = 120

[mcp_servers.enterprise-hub.env]
ENTERPRISE_HUB_BASE_URL = "http://127.0.0.1:3000"
```

`ENTERPRISE_HUB_BASE_URL` 是唯一 launcher 配置值。不要在 MCP 配置、环境变量、命令参数、文件或 skill 内容里写 bearer token、password、API key、OSS credential 或 service account。

## 使用注意

- 不要提供或询问组织 ID。组织边界由服务端从当前登录员工推导，隐藏数据由后端授权拒绝。
- Evidence search 的 cursor 是不透明、短期有效的翻页 token。下一页必须沿用相同 query/filter/limit 并原样传回 cursor；遇到 `INVALID_CURSOR` 或 `CURSOR_EXPIRED` 就重新开始搜索。
- 结构化导入只有在同一个文件和同一组 metadata 精确重试时才复用 `idempotencyKey`。精确重放会返回第一次持久化的 `documentId`、`importBatchId` 和 storage key，不会重复写入 rows 或 objects。
- `get_import_status` 对不存在、跨组织、disabled 或标签不可见的批次返回同一种非枚举 404。只能把它当成“不可见或不存在”，不要推断隐藏批次的 metadata。

## 推荐 Codex 提示词

```text
Use $enterprise-hub-mcp.
Configure the Enterprise Hub MCP launcher with this service URL: http://127.0.0.1:3000.
Log in as baoli.manager@example.com with enterprise_hub_login_local.
List labels.
Upload/search/query through the Phase 3 evidence or structured tools only.
Do not print raw tokens, do not ask for production credentials, and do not claim inaccessible data exists.
```

## 当前 MCP Tools

| Tool                           | 用途                                       |
| ------------------------------ | ------------------------------------------ |
| `enterprise_hub_login_local`   | 用 seeded email 登录 launcher 内存 session |
| `enterprise_hub_logout_local`  | 清除 launcher 内存 session                 |
| `enterprise_hub_list_labels`   | 读取可用标签目录                           |
| `enterprise_hub_list_skills`   | 读取已批准 Skill Directory 元数据          |
| `upload_evidence_document`     | 上传 MD/TXT/DOCX evidence 文档             |
| `get_evidence_document_status` | 查询 evidence 文档和索引状态               |
| `search_document_evidence`     | 检索可见 evidence chunks                   |
| `upload_structured_dataset`    | 上传 dishes/business CSV/XLSX 数据集       |
| `get_import_status`            | 查询结构化导入状态                         |
| `list_structured_datasets`     | 查询可用 dataset/字段/operator schema      |
| `query_structured_dataset`     | 执行受控只读结构化 JSON 查询               |

## 验证流程

最小 evidence 验证：

1. 调 `enterprise_hub_login_local` 登录 `baoli.manager@example.com`。
2. 调 `enterprise_hub_list_labels`，选择 `store:baoli`。
3. 调 `upload_evidence_document` 上传一个本地 MD/TXT/DOCX。
4. 调 `get_evidence_document_status`，等待 document active 且 index ready。
5. 调 `search_document_evidence`，返回 evidence chunks；不要生成最终答案。

最小 structured 验证：

1. 调 `enterprise_hub_login_local` 登录 `baoli.manager@example.com`。
2. 调 `upload_structured_dataset` 上传 `dishes` 或 `business` CSV/XLSX，带 `store:baoli`。
3. 调 `get_import_status`。
4. 调 `list_structured_datasets`。
5. 调 `query_structured_dataset` 做受控只读查询；不要发送 SQL。

精确重试：如果同一 structured 文件上传时网络中断，可用原 `idempotencyKey` 重试。返回相同 `documentId` / `importBatchId` / storage key 表示重放成功，不代表重复导入。

Evidence 翻页：如果 `search_document_evidence` 返回非空 cursor，且用户要继续看下一页，用相同 query/filter/limit 原样传回 cursor。不要修改、解码、长期保存或跨员工复用 cursor。

权限隔离验证：

1. 调 `enterprise_hub_login_local` 登录 `suzhou.manager@example.com`。
2. 搜索或查询同一 Baoli 内容。
3. 预期没有可见结果，也不泄露标题、文件名、行数、source metadata 或存在性。

自动 smoke：

```sh
cd /path/to/SME_DATA_CENTER
npm run test:mcp
```

## 安全边界

- 所有非 health 数据访问必须通过 MCP tools 和后端 HTTP API authorization。
- 不要让 agent 直读 MySQL、Qdrant、storage、session 文件或 token。
- 不要让 agent 发送 raw SQL、公式、window function、join、delete/update/insert/DDL 或自然语言 query generation 指令。
- 不要让 agent 生成最终业务结论、报表或 dashboard。
- 不要上传真实客户导出、第三方下载数据或公司机密文件，除非用户明确授权该具体文件。
- `staging-remote` 和 `production` 目前只是占位 profile；没有批准配置前不要发明 endpoint、token flow、域名或 TLS 设置。

## 故障排查

| 现象                                       | 处理方式                                  |
| ------------------------------------------ | ----------------------------------------- |
| Codex 里看不到 `enterprise-hub` MCP server | 重启 Codex，或检查 `~/.codex/config.toml` |
| Codex 里看不到 `$enterprise-hub-mcp` skill | 确认安装目录存在后重启 Codex              |
| MCP tools 未暴露                           | 说明 MCP 未连接；不要 fallback 到 CLI/API |
| tool 调用连接失败                          | 说明服务不可用；不要启动或修复服务        |
| `EMPLOYEE_AUTH_REQUIRED`                   | 请用户核对服务中的已注册 email 并重新登录 |
| evidence 上传后搜索为空                    | 先查 `get_evidence_document_status`       |
| structured import 失败                     | 返回服务 validation errors，不要本地改表  |
| Suzhou 搜不到 Baoli 数据                   | 这是预期权限隔离结果                      |

## 相关仓库

- 主项目：`YinXiaoyu-1998/SME_DATA_CENTER`
- 本 skill repo：`YinXiaoyu-1998/enterprise-hub-mcp-skill`
