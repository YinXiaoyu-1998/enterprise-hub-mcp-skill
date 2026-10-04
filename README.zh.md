# SMEDC MCP Skill

这是员工自有 agent 安装和使用 SMEDC 远程 MCP launcher 的正式运行手册。SMEDC 是 Small and
Medium Enterprises Data Center 的缩写。它使用浏览器登录和正式服务地址
`https://api.smedatacenter.xyz`；员工绝不通过 agent 提供密码、token 或授权码。

本仓库只包含 skill 与 MCP 客户端连接说明；不操作 SMEDC 的 API、数据库、向量库、storage、
Docker、worker、云资源或部署。

> 在线服务状态：`smedc-mcp-launcher@0.7.1`、浏览器登录和公开 HTTPS MCP 边界是当前打包契约。
> 员工仍需完成真实登录与后端授权。launcher 支持 macOS、Windows 和 Linux；无头 Linux
> 使用同一 Device Authorization 流程，无安全存储时回退为仅内存会话。

## 上传权限

仅启用的 `admin` 可上传证据文档、结构化数据（含进货台账 Delivery Ledger）和检疫证明。
`employee` 无论 clearance 多高都不能上传，但仍可读取符合组织与密级授权的数据。上传工具保持
可见并标为仅管理员可用；已知为 employee 时，agent 不得读取或转换本地文件。launcher 0.7.1
在文件访问前预检查，本地拒绝不产生后端审计。直接 HTTP 上传端点返回 HTTP `403`；
MCP JSON-RPC 传输返回 HTTP `200`，工具结果包含 `isError: true`。两者均携带 `UPLOAD_ADMIN_REQUIRED`、
`File upload requires the admin role.`、`retryable: false`；后端拒绝尽力记录 `file_upload.denied`。
不要重登、重试或提高 clearance 来绕过拒绝。

管理员可明确指定高于自身 clearance 的密级，但不会获得普通读取豁免。分片 create/parts/complete
要求管理员；owner abort 和既有状态、清单、读取规则保留。最低兼容版本与批准安装版本均为
0.6.0；更旧的 launcher 不受支持，并会收到 `LAUNCHER_UPGRADE_REQUIRED`。上传原始文件并报告服务校验错误，核心
skill 不提供特定数据集的转换配方。

## 台账 PDF 能力与服务端切换

[四个归档工具契约](skills/smedc-mcp/references/ledger-pdf-tools.md) 需要正式发布后的 launcher
0.7.1 和已启用归档交付的服务端。0.7.1 已公开发布并独立验证，当前安装 pin 为 0.7.1；
归档交付仍等待服务端切换。
切换后，台账明细与原始 CSV/XLSX 签名关闭；门店/日期聚合和其他数据集继续可用。
上传、照片、PDF 就绪检查和下载协调由独立安装的 delivery-ledger companion 负责；核心 Skill 不在本地生成台账。

## 安装档位

### 仅安装核心

这是默认档位。只安装 `smedc-mcp`，用于 launcher 配置、浏览器登录、文件上传和遵守授权边界的
SMEDC 查询。普通 SMEDC 工作不需要安装任何可选配套 skill，安装或更新核心 skill 时也绝不静默安装
这些配套能力。

### 可选配套

两个配套 skill 都在
[`YinXiaoyu-1998/smedc-companion-skills`](https://github.com/YinXiaoyu-1998/smedc-companion-skills)
中，并保持为独立安装的 skill：

- `smedc-business-analysis` 生成基于组织名称的经营诊断、周报和月报。
- `smedc-delivery-ledger` 在归档能力发布并启用后，协调服务端定时生成的每日 PDF、ZIP 准备和收货单关联检疫照片操作。

如果尚未安装，agent 可以说明其官方来源并提出安装，但员工必须明确同意安装，或已经明确要求安装这个
具名配套 skill / 全部推荐配套 skill。安装或更新任意一边都不会自动更新另一边。

## 安装 Skill

clone 或下载本仓库后，把 skill 安装到当前用户的 canonical skill 目录。不要默认安装到
`~/.codex/skills`。

| 平台             | Canonical target                         |
| ---------------- | ---------------------------------------- |
| macOS/Linux-like | `~/.agents/skills/smedc-mcp`             |
| Windows          | `%USERPROFILE%\.agents\skills\smedc-mcp` |

让 agent 遵循 [Skill 替换流程](skills/smedc-mcp/references/update-skill.md)：暂存完整目录，
把临时恢复备份放在所有 Skill 发现目录之外，校验文件并确认宿主实际加载的新副本，再删除旧副本和临时备份。
不要覆盖复制已有目录，也不要在 Skill 目录内创建 `.bak` 副本。
需要刷新或重启宿主时，完成该步骤后才能声明新 Skill 已生效。

## 更新 Skill 本体

直接对 agent 说：“帮我更新 smedc-mcp-skill 这个 skill。”新版 skill 同时识别 `smedc-mcp` 和
`smedc-mcp-skill`，会从
[`YinXiaoyu-1998/smedc-mcp-skill`](https://github.com/YinXiaoyu-1998/smedc-mcp-skill)
的默认分支获取最新内容，备份、替换并校验完整 skill 目录，不依赖推荐市场。完成后会报告来源
commit、实际加载路径和清理结果；仍需重载或存在旧副本时，必须报告尚未完成。

只更新 skill 会保留 launcher 和登录会话。升级 launcher 需要用户提出该请求，并使用更新后的官方 skill
所批准的精确版本。agent 仍需具备网络访问、目录写入权限及宿主支持的安装方式。详见
[skill 更新流程](skills/smedc-mcp/references/update-skill.md)。

## 正式 Launcher

唯一批准的 launcher 包是 `smedc-mcp-launcher@0.7.1`。禁止使用 npm `latest`、未固定版本或
launcher 自更新。

先运行 `node --version` 和 `npm --version`。必须使用 Node.js 22 或更高版本并确保 npm 可用。经授权的
员工自有 agent 用以下命令幂等安装或修复：

```sh
npm install --prefix "<launcher-directory>" --save-exact smedc-mcp-launcher@0.7.1
```

使用批准的当前用户 launcher 目录：

| 平台    | Launcher 目录                                                         |
| ------- | --------------------------------------------------------------------- |
| macOS   | `~/Library/Application Support/SMEDC/launcher/versions/0.7.1/`        |
| Windows | `%LOCALAPPDATA%\\SMEDC\\launcher\\versions\\0.7.1\\`                  |
| Linux   | `${XDG_DATA_HOME:-$HOME/.local/share}/SMEDC/launcher/versions/0.7.1/` |

agent 必须运行对应平台的精确自检，才能声明安装成功：

```sh
SMEDC_BASE_URL=https://api.smedatacenter.xyz \
  "$HOME/Library/Application Support/SMEDC/launcher/versions/0.7.1/node_modules/.bin/smedc-mcp-launcher" self-check
```

```powershell
$env:SMEDC_BASE_URL = "https://api.smedatacenter.xyz"
& "$env:LOCALAPPDATA\SMEDC\launcher\versions\0.7.1\node_modules\.bin\smedc-mcp-launcher.cmd" self-check
```

```sh
# Linux
SMEDC_LAUNCHER_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/SMEDC/launcher/versions/0.7.1"
SMEDC_BASE_URL=https://api.smedatacenter.xyz \
  "$SMEDC_LAUNCHER_DIR/node_modules/.bin/smedc-mcp-launcher" self-check
```

self-check 只返回安全的 machine-readable 字段，且 launcher 不会自更新。一般的 SMEDC 更新请求会先
刷新 Skill，再执行完整的[升级清理流程](skills/smedc-mcp/references/upgrade-cleanup.md)：安装并检查批准
版本、切换 MCP 配置、重连并确认实际运行版本、停止旧进程，最后删除旧安装和临时备份。要求清除所有旧版本
时，也要迁移当前用户下可安全发现的其他 SMEDC 接入。保留有效的操作系统安全会话。单独自检成功不能证明
宿主已连接新版。Linux 上
`secureStore.available:false` 是受支持的结果：无头环境不打开本地浏览器，而是返回第一方
登录链接；完成后会话只保存在内存中，launcher 或主机重启后需重新登录。

## 配置与登录

把 SMEDC 配置成本地 stdio launcher，名称为 `smedc`，不要配置成直连远程 HTTP/OAuth 服务。完整 launch
tuple 只有一个 `serve` 参数和一个非秘密环境变量：`SMEDC_BASE_URL=https://api.smedatacenter.xyz`。

修改 MCP 客户端前，先检查现有配置并创建带时间戳的备份。添加或替换它的 `smedc` stdio entry，并删除
授权范围内已核实的重复 SMEDC entry，保留所有无关 server 与设置。

认证状态未知时调用 `smedc_auth_status`。若返回 `authentication_required`，调用 `smedc_login`，只请员工
在浏览器页面完成登录。成功后只重试原业务操作一次。仅在员工要求退出时调用 `smedc_logout`。

员工询问当前登录的是哪个账号时，调用零参数 `smedc_get_current_user`。它返回当前已认证员工的
`displayName`、`email`、`role`、`clearance` 和 `organizationName`。skill 目录工具是
`smedc_list_skills`。

## 内容

- `skills/smedc-mcp/SKILL.md`
- `skills/smedc-mcp/agents/openai.yaml`
- `skills/smedc-mcp/references/update-skill.md`
- `skills/smedc-mcp/references/upgrade-cleanup.md`
- `skills/smedc-mcp/references/ledger-pdf-tools.md`
