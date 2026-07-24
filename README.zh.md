# Enterprise Hub MCP Skill

这是员工自有 agent 安装和使用 Enterprise Hub 远程 MCP launcher 的正式运行手册。它使用
浏览器登录和正式服务地址 `https://api.smedatacenter.xyz`；员工绝不通过 agent 提供密码、token
或授权码。

本仓库只包含 skill 与 MCP 客户端连接说明；不操作 Enterprise Hub 的 API、数据库、Qdrant、
storage、Docker、worker、云资源或部署。服务职责仍属于主项目
[SME_DATA_CENTER](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER)。

> Cutover 前状态：这是已批准的正式目标手册，不代表浏览器登录 launcher、npm 包或公开 MCP
> 边界已经上线。当前实现和 cutover 工作以主仓库记录为准。

## 安装 Skill

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YinXiaoyu-1998/enterprise-hub-mcp-skill \
  --path skills/enterprise-hub-mcp
```

安装后重启 Codex 或新开任务，使 skill 列表刷新。

## 正式 Launcher

唯一批准的 launcher 包是 `enterprise-hub-mcp-launcher@0.1.0`。禁止使用 npm `latest`、
未固定版本或 launcher 自更新。

| 平台    | 当前 OS 用户的包目录                                                    |
| ------- | ----------------------------------------------------------------------- |
| macOS   | `~/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/` |
| Windows | `%LOCALAPPDATA%\\Enterprise Hub\\launcher\\versions\\0.1.0\\`           |

经授权的员工自有 agent 用以下命令幂等安装或修复：

```sh
npm install --prefix "<launcher-directory>" --save-exact enterprise-hub-mcp-launcher@0.1.0
```

agent 必须先运行已安装 launcher 的无凭证自检，才能声明安装成功。launcher 不会自更新。批准
更新时使用新的精确版本目录，只改调用该 agent 的 MCP launcher 路径，并保留操作系统安全会话。

## 配置与登录

把 Enterprise Hub 配置成**本地 stdio launcher**，不要配置成直连远程 HTTP/OAuth 服务。launcher
连接 `https://api.smedatacenter.xyz`、打开系统浏览器供员工登录，并只在 macOS Keychain 或 Windows
Credential Manager 中保存 durable credential。配置、环境变量、命令参数、文件、日志和聊天内容
不得包含密码、token、授权码、原始 header 或 OAuth secret。

完整 stdio launch tuple 是固定的：只有一个 `serve` 参数和一个非秘密环境变量；不得添加工作目录、
其他环境变量或任何凭证。

| 平台    | Command                                                                                                              | Args    | Env                                                     |
| ------- | -------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------- |
| macOS   | `~/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/node_modules/.bin/enterprise-hub-mcp-launcher` | `serve` | `ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz` |
| Windows | `%LOCALAPPDATA%\\Enterprise Hub\\launcher\\versions\\0.1.0\\node_modules\\.bin\\enterprise-hub-mcp-launcher.cmd`     | `serve` | `ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz` |

修改 MCP 客户端前，先检查现有配置并创建带时间戳的备份。只添加或替换它的 `enterprise-hub`
stdio entry，保留所有无关 server 与设置。

- Codex：使用当前安装版 Codex 的 MCP 配置机制配置固定版本 launcher，然后 reload/restart Codex
  并确认工具发现。如果无法从已安装的帮助或配置中确定受支持的位置/语法，应报告这个明确阻塞，
  不要猜测或覆盖配置文件。
- OpenClaw：新 entry 用 `openclaw mcp add`，最小幂等替换用 `openclaw mcp set`，再以
  `openclaw mcp doctor enterprise-hub --probe` 验证。macOS 的 add 形式是
  `openclaw mcp add enterprise-hub --command "$HOME/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/node_modules/.bin/enterprise-hub-mcp-launcher" --arg serve --env ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz`。
  不要用 `openclaw mcp login` 或 `openclaw mcp logout`：它们管理 OpenClaw 的直连 HTTP OAuth
  store，而 Enterprise Hub 的浏览器登录和安全存储由 launcher 管理。
- 其他 agent：采取受保护的自适应发现——检查产品 help 与当前配置、先备份、只加固定本地 stdio
  entry 并验证握手。不要破坏性猜测，也不要配置直连 OAuth。

认证状态未知时调用 `enterprise_hub_auth_status`。若返回 `authentication_required`，调用
`enterprise_hub_login`，只请员工在浏览器页面完成登录。成功后只重试原业务操作一次。仅在员工
要求退出时调用 `enterprise_hub_logout`；它会让同一 OS 用户安全存储下的所有本地 Enterprise Hub
agent 退出。

## 安全使用

- 可见组织、标签和资源完全由后端授权决定，不依赖客户端过滤。不得传入组织 ID，也不得推断
  隐藏数据。
- 只读取用户选择上传文件的精确原始字节；传 inline bytes，不传本地路径。不得规范化或重建内容。
- 可轮询状态，但不得启动 worker 或操作服务基础设施。
- 仅对完全相同的导入重放复用 structured-import idempotency key。import-status 404 只能视为
  不可见或不存在。
- 对同一 query/filter/limit 原样使用 evidence cursor。`INVALID_CURSOR` 时重新开始；
  `CURSOR_EXPIRED` 时说明已过期，且只有员工仍想继续才重新搜索。
- Skill Directory 只列出元数据；不得执行条目，也不得生成报告/dashboard。

## 生命周期

单 agent 移除时，备份该 agent 配置并只删它的 `enterprise-hub` entry。共享退出使用
`enterprise_hub_logout`；服务不可用时，本地安全凭证仍可移除，但远程撤销无法确认。经明确授权
的完全卸载：退出、从可安全发现的本地 agent 中移除 Enterprise Hub entries，并移除当前用户的
launcher 目录和非秘密 state。绝不移除 Node.js/npm、其他 MCP server、Employee Account 或服务端
业务数据。

## 内容

- `skills/enterprise-hub-mcp/SKILL.md`
- `skills/enterprise-hub-mcp/agents/openai.yaml`
