# Enterprise Hub MCP Skill

这是 `enterprise-hub-mcp` 的独立 Codex skill 仓库，用来指导 Codex 或其他员工自有 agent 通过本地 MCP server 安全使用 企业资料中枢。

这个仓库只包含 skill，不包含 企业资料中枢 API、worker、数据库、MCP server 实现。MCP server 仍然来自主项目 `SME_DATA_CENTER`。

## 这个 skill 做什么

- 指导 agent 连接本地 `enterprise-hub` MCP server。
- 指导 agent 使用 seeded 本地员工登录，例如 `baoli.manager@example.com`。
- 指导 agent 通过 MCP 上传、查询、下载 URL、归档资料。
- 指导 agent 验证 Baoli/Suzhou 的权限隔离。
- 阻止 agent 发明 staging/production endpoint、域名、token flow 或云资源配置。
- 阻止 agent 绕过 API 直接读 MySQL、本地 storage、session 文件或 token。

它不是报表生成器、dashboard 服务、skill 执行平台，也不会把 企业资料中枢 变成员工直接对话的 AI agent。

## 仓库内容

```text
skills/enterprise-hub-mcp/
  SKILL.md
  agents/openai.yaml
```

## 安装到 Codex

在已登录 GitHub 且能访问这个 private repo 的机器上运行：

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YinXiaoyu-1998/enterprise-hub-mcp-skill \
  --path skills/enterprise-hub-mcp
```

安装后重启 Codex，新的 skill 才会出现在可用 skill 列表中。

如果你在本机已经手动安装过，也可以确认目录存在：

```sh
ls ~/.codex/skills/enterprise-hub-mcp
```

## 前置条件

使用这个 skill 前，需要先有主项目：

```text
/Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER
```

主项目需要完成：

```sh
npm install
MYSQL_PORT=3307 docker compose up -d mysql
DATABASE_URL='mysql://enterprise_hub:enterprise_hub_local_password@localhost:3307/enterprise_hub' npm run db:generate
DATABASE_URL='mysql://enterprise_hub:enterprise_hub_local_password@localhost:3307/enterprise_hub' npm run db:seed
```

然后单独启动 API：

```sh
cd /Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER
DATABASE_URL='mysql://enterprise_hub:enterprise_hub_local_password@localhost:3307/enterprise_hub' \
STORAGE_DRIVER=local \
LOCAL_STORAGE_ROOT=.data/storage \
JWT_SECRET=replace-with-local-development-secret \
PORT=3000 \
npm run api:dev
```

## Codex MCP 配置

在 `~/.codex/config.toml` 中配置本地 MCP server：

```toml
[mcp_servers.enterprise-hub]
command = "bash"
args = ["-lc", "cd /Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER && npm run mcp:dev"]
startup_timeout_sec = 120

[mcp_servers.enterprise-hub.env]
ENTERPRISE_HUB_API_URL = "http://127.0.0.1:3000"
ENTERPRISE_HUB_MCP_PROFILE = "local-development"
ENTERPRISE_HUB_MCP_SESSION_FILE = "/Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER/.data/enterprise-hub-mcp/session.json"
```

验证 Codex 已读到 MCP server：

```sh
/Applications/Codex.app/Contents/Resources/codex mcp list
```

列表中应该能看到 `enterprise-hub`，状态为 `enabled`。

## 推荐 Codex 提示词

在一个新的 Codex thread 中使用：

```text
Use $enterprise-hub-mcp with the local-development profile to run the local 企业资料中枢 MCP human-test flow. Do not print raw tokens, do not ask for production credentials, and do not claim inaccessible documents exist.
```

如果 Codex 还没有识别到 `$enterprise-hub-mcp`，请重启 Codex。

## 常用 MCP tool

| Tool                                       | 用途                                 |
| ------------------------------------------ | ------------------------------------ |
| `enterprise_hub_login_dev`                 | 用 seeded email 登录本地 dev session |
| `enterprise_hub_list_labels`               | 读取可用标签目录                     |
| `enterprise_hub_upload_document`           | 上传本地文件到资料中枢               |
| `enterprise_hub_get_document_status`       | 查询上传/处理状态                    |
| `enterprise_hub_search_documents`          | 搜索当前员工可见的 active 资料       |
| `enterprise_hub_get_document`              | 读取可见资料元数据                   |
| `enterprise_hub_get_document_download_url` | 获取可见资料下载 URL                 |
| `enterprise_hub_archive_document`          | 归档资料                             |
| `enterprise_hub_list_skills`               | 读取已批准 Skill Directory 元数据    |

## 本地验证流程

最小验证路径：

1. 用 `enterprise_hub_login_dev` 登录 `baoli.manager@example.com`，sessionName 用 `baoli`。
2. 调用 `enterprise_hub_list_labels`，确认有 `store:baoli`。
3. 调用 `enterprise_hub_upload_document` 上传主项目里的 synthetic fixture：

   ```text
   /Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER/fixtures/baoli-june-meituan.csv
   ```

4. 在主项目运行一次 worker：

   ```sh
   cd /Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER
   DATABASE_URL='mysql://enterprise_hub:enterprise_hub_local_password@localhost:3307/enterprise_hub' \
   STORAGE_DRIVER=local \
   LOCAL_STORAGE_ROOT=.data/storage \
   npm run worker:once
   ```

5. 用 Baoli session 搜索，应能看到 active 资料。
6. 用 `suzhou.manager@example.com` 登录 sessionName `suzhou`。
7. 用 Suzhou session 搜索同一关键词，应看不到 Baoli 资料。
8. 用 Baoli session 归档资料，普通搜索不应再返回这份资料。

也可以在主项目直接跑自动 smoke：

```sh
cd /Users/xiaoyuyin/Desktop/YXY_DEV/SME_DATA_CENTER
MYSQL_PORT=3307 npm run test:mcp
```

## 安全边界

- 不要提交真实 token、生产凭据、service account、真实客户导出或第三方下载数据。
- 不要让 agent 直接读取 MySQL、本地 storage 或 session 文件。
- 不要让 agent 声称不可见资料“存在但无权访问”；对不可见资料只能报告没有可见结果。
- 不要在 local-development 中要求生产密码、OSS 配置、线上 MySQL 或域名。
- `staging-remote` 和 `production` 目前只是占位 profile；没有批准配置前不要发明 endpoint 或 token flow。

## 故障排查

| 现象                                       | 处理方式                                          |
| ------------------------------------------ | ------------------------------------------------- |
| Codex 里看不到 `enterprise-hub` MCP server | 重启 Codex，或检查 `~/.codex/config.toml`         |
| Codex 里看不到 `$enterprise-hub-mcp` skill | 确认安装目录存在后重启 Codex                      |
| MCP 启动提示缺少 `ENTERPRISE_HUB_API_URL`  | 检查 MCP env 配置                                 |
| tool 调用连接失败                          | 先启动主项目 API，并确认端口是 `3000`             |
| 登录返回 `EMPLOYEE_NOT_FOUND`              | 重新 seed 本地数据库，确认 API 使用同一 DB        |
| 上传后搜索不到                             | 先运行 `npm run worker:once`，等状态变成 `active` |
| Suzhou 搜不到 Baoli 资料                   | 这是预期权限隔离结果                              |

## 相关仓库

- 主项目：`YinXiaoyu-1998/SME_DATA_CENTER`
- 本 skill repo：`YinXiaoyu-1998/enterprise-hub-mcp-skill`
