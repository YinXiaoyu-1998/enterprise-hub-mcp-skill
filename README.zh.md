# Enterprise Hub MCP Skill

这是员工自有 agent 安装和使用 Enterprise Hub 远程 MCP launcher 的正式运行手册。它使用
浏览器登录和正式服务地址 `https://api.smedatacenter.xyz`；员工绝不通过 agent 提供密码、token
或授权码。

本仓库只包含 skill 与 MCP 客户端连接说明；不操作 Enterprise Hub 的 API、数据库、Qdrant、
storage、Docker、worker、云资源或部署。服务职责仍属于主项目
[SME_DATA_CENTER](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER)。

> 在线服务状态：`enterprise-hub-mcp-launcher@0.1.0`、浏览器登录和公开 HTTPS MCP 边界已在
> staging 一同部署。员工仍需完成真实登录与授权；Windows 桌面验收仍是发布门。

## 安装 Skill

clone 或下载本仓库后，把 skill 安装到当前用户的 canonical skill 目录。不要默认安装到
`~/.codex/skills`。

| 平台             | Canonical target                                  |
| ---------------- | ------------------------------------------------- |
| macOS/Linux-like | `~/.agents/skills/enterprise-hub-mcp`             |
| Windows          | `%USERPROFILE%\.agents\skills\enterprise-hub-mcp` |

macOS/Linux-like shell：

```sh
mkdir -p "$HOME/.agents/skills"
SKILL_TARGET="$HOME/.agents/skills/enterprise-hub-mcp"
if [ -e "$SKILL_TARGET" ]; then
  mv "$SKILL_TARGET" "$SKILL_TARGET.bak.$(date +%Y%m%d%H%M%S)"
fi
cp -R skills/enterprise-hub-mcp "$SKILL_TARGET"
```

Windows PowerShell：

```powershell
$SkillRoot = Join-Path $env:USERPROFILE ".agents\skills"
$SkillTarget = Join-Path $SkillRoot "enterprise-hub-mcp"
New-Item -ItemType Directory -Force -Path $SkillRoot | Out-Null
if (Test-Path $SkillTarget) {
  Move-Item $SkillTarget "$SkillTarget.bak.$(Get-Date -Format yyyyMMddHHmmss)"
}
Copy-Item -Recurse "skills\enterprise-hub-mcp" $SkillTarget
```

安装后重启 Codex 或新开任务，使 skill 列表刷新。

## 正式 Launcher

唯一批准的 launcher 包是 `enterprise-hub-mcp-launcher@0.1.0`。禁止使用 npm `latest`、
未固定版本或 launcher 自更新。

先运行 `node --version` 和 `npm --version`。必须使用 Node.js **22 或更高版本**并确保 npm 可用。
Node.js 不存在或 major version 小于 22 时，先为当前用户安装/升级，再安装 launcher。

| 平台    | 当前 OS 用户的包目录                                                    |
| ------- | ----------------------------------------------------------------------- |
| macOS   | `~/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/` |
| Windows | `%LOCALAPPDATA%\\Enterprise Hub\\launcher\\versions\\0.1.0\\`           |

经授权的员工自有 agent 用以下命令幂等安装或修复：

```sh
npm install --prefix "<launcher-directory>" --save-exact enterprise-hub-mcp-launcher@0.1.0
```

agent 必须运行对应平台的精确自检，才能声明安装成功：

```sh
ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz \
  "$HOME/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/node_modules/.bin/enterprise-hub-mcp-launcher" self-check
```

```powershell
$env:ENTERPRISE_HUB_BASE_URL = "https://api.smedatacenter.xyz"
& "$env:LOCALAPPDATA\Enterprise Hub\launcher\versions\0.1.0\node_modules\.bin\enterprise-hub-mcp-launcher.cmd" self-check
```

self-check 只返回安全的 machine-readable 字段：`ok`、`launcherVersion`、`serviceOrigin`、
`platform`、`secureStore.{available,durableCredentialPresent}`、
`server.{reachable,metadataCompatible,minimumLauncherVersion,recommendedLauncherVersion,recommendedUpdateAvailable}`
以及 `mcp.handshake`（`ok`、`not_authenticated` 或 `unavailable`）。launcher 不会自更新。批准
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

- Codex：使用已验证的 `codex mcp list|get|add|remove` CLI。macOS 从 PATH 解析 `codex`，不存在时
  使用 `/Applications/ChatGPT.app/Contents/Resources/codex`；Windows 从 PATH 解析
  `codex.exe`。修改前备份 `~/.codex/config.toml` 或
  `%USERPROFILE%\.codex\config.toml`。用
  `codex mcp add --env ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz enterprise-hub -- <platform-launcher-path> serve`
  添加 stdio entry，再用 `codex mcp get enterprise-hub --json` 和 self-check 验证。修复时只删除
  mismatch 的 `enterprise-hub` entry 后重新添加；单 agent 移除使用
  `codex mcp remove enterprise-hub`，然后以 `codex mcp list --json` 和 get absent 验证。
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
`enterprise_hub_logout`，或运行对应平台的精确命令：

```sh
ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz \
  "$HOME/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/node_modules/.bin/enterprise-hub-mcp-launcher" logout
```

```powershell
$env:ENTERPRISE_HUB_BASE_URL = "https://api.smedatacenter.xyz"
& "$env:LOCALAPPDATA\Enterprise Hub\launcher\versions\0.1.0\node_modules\.bin\enterprise-hub-mcp-launcher.cmd" logout
```

logout 只返回
`{"remoteRevocationConfirmed":<boolean>,"localCredentialRemoved":<boolean>}`；远程可达时尝试撤销
session family，并始终尝试删除本地 credential。只有 `localCredentialRemoved` 为 true 时才能报告
本地退出成功。经明确授权的完全卸载：退出、从可安全发现的本地 agent 中移除 Enterprise Hub
entries，并移除当前用户的 launcher 目录和非秘密 state。绝不移除 Node.js/npm、其他 MCP server、
Employee Account 或服务端业务数据。

## 内容

- `skills/enterprise-hub-mcp/SKILL.md`
- `skills/enterprise-hub-mcp/agents/openai.yaml`
