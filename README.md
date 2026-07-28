# Enterprise Hub MCP Skill

The official runbook for employee-owned agents to install and use the Enterprise Hub remote MCP
launcher. It uses browser login and the official service origin
`https://api.smedatacenter.xyz`; employees never give passwords, tokens, or authorization codes to
an agent.

This repository contains only skill and client-connection guidance. It never operates the
Enterprise Hub API, database, Qdrant, storage, Docker, worker, cloud resources, or deployment.
Those service responsibilities remain in
[SME_DATA_CENTER](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER).

> Live-service status: `enterprise-hub-mcp-launcher@0.1.0`, browser login, and the public HTTPS MCP
> boundary are deployed together in staging. Real employee login and authorization are still
> required; Windows desktop acceptance remains a release gate.

## Install The Skill

Clone or download this repository, then install the skill to the canonical current-user skill
directory. Do not default to `~/.codex/skills`.

| Platform         | Canonical target                                  |
| ---------------- | ------------------------------------------------- |
| macOS/Linux-like | `~/.agents/skills/enterprise-hub-mcp`             |
| Windows          | `%USERPROFILE%\.agents\skills\enterprise-hub-mcp` |

macOS/Linux-like shell:

```sh
mkdir -p "$HOME/.agents/skills"
SKILL_TARGET="$HOME/.agents/skills/enterprise-hub-mcp"
if [ -e "$SKILL_TARGET" ]; then
  mv "$SKILL_TARGET" "$SKILL_TARGET.bak.$(date +%Y%m%d%H%M%S)"
fi
cp -R skills/enterprise-hub-mcp "$SKILL_TARGET"
```

Windows PowerShell:

```powershell
$SkillRoot = Join-Path $env:USERPROFILE ".agents\skills"
$SkillTarget = Join-Path $SkillRoot "enterprise-hub-mcp"
New-Item -ItemType Directory -Force -Path $SkillRoot | Out-Null
if (Test-Path $SkillTarget) {
  Move-Item $SkillTarget "$SkillTarget.bak.$(Get-Date -Format yyyyMMddHHmmss)"
}
Copy-Item -Recurse "skills\enterprise-hub-mcp" $SkillTarget
```

Restart Codex or open a new task after installation so the skill list refreshes.

## Official Launcher

The only approved launcher package is `enterprise-hub-mcp-launcher@0.1.0`. Never use npm
`latest`, an unpinned version, or launcher self-update.

Run `node --version` and `npm --version` first. Node.js **22 or newer** and a working npm are
required. If Node.js is absent or its major version is below 22, install/upgrade it for the current
user before installing the launcher.

| Platform | Current-user package directory                                          |
| -------- | ----------------------------------------------------------------------- |
| macOS    | `~/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/` |
| Windows  | `%LOCALAPPDATA%\\Enterprise Hub\\launcher\\versions\\0.1.0\\`           |

An authorized employee-owned agent installs or repairs it idempotently:

```sh
npm install --prefix "<launcher-directory>" --save-exact enterprise-hub-mcp-launcher@0.1.0
```

The agent must run the exact platform self-check before claiming success:

```sh
ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz \
  "$HOME/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/node_modules/.bin/enterprise-hub-mcp-launcher" self-check
```

```powershell
$env:ENTERPRISE_HUB_BASE_URL = "https://api.smedatacenter.xyz"
& "$env:LOCALAPPDATA\Enterprise Hub\launcher\versions\0.1.0\node_modules\.bin\enterprise-hub-mcp-launcher.cmd" self-check
```

Self-check returns only safe machine-readable fields:
`ok`, `launcherVersion`, `serviceOrigin`, `platform`,
`secureStore.{available,durableCredentialPresent}`,
`server.{reachable,metadataCompatible,minimumLauncherVersion,recommendedLauncherVersion,recommendedUpdateAvailable}`,
and `mcp.handshake` (`ok`, `not_authenticated`, or `unavailable`). The launcher never self-updates.
An approved update uses a new exact versioned directory, changes only the invoking agent's MCP
launcher path, and preserves the operating-system secure session.

## Configuration And Login

Configure Enterprise Hub as a **local stdio launcher**, not as a direct remote HTTP/OAuth server.
The launcher connects to `https://api.smedatacenter.xyz`, opens the system browser for login, and
keeps its durable credential only in macOS Keychain or Windows Credential Manager. Configuration,
environment variables, command arguments, files, logs, and chat must never contain passwords,
tokens, authorization codes, raw headers, or OAuth secrets.

The complete stdio launch tuple is fixed. It has one `serve` argument and one non-secret
environment value—do not add a working directory, another environment variable, or a credential.

| Platform | Command                                                                                                              | Args    | Env                                                     |
| -------- | -------------------------------------------------------------------------------------------------------------------- | ------- | ------------------------------------------------------- |
| macOS    | `~/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/node_modules/.bin/enterprise-hub-mcp-launcher` | `serve` | `ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz` |
| Windows  | `%LOCALAPPDATA%\\Enterprise Hub\\launcher\\versions\\0.1.0\\node_modules\\.bin\\enterprise-hub-mcp-launcher.cmd`     | `serve` | `ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz` |

Before changing an MCP client, inspect its configuration and make a timestamped backup. Add or
replace only its `enterprise-hub` stdio entry; preserve every unrelated server and setting.

- Codex: use the verified `codex mcp list|get|add|remove` CLI. On macOS, resolve `codex` from PATH
  or use `/Applications/ChatGPT.app/Contents/Resources/codex`; on Windows, resolve `codex.exe`.
  Back up `~/.codex/config.toml` or `%USERPROFILE%\.codex\config.toml` before mutation. Add the
  stdio entry with `codex mcp add --env ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz enterprise-hub -- <platform-launcher-path> serve`.
  Verify with `codex mcp get enterprise-hub --json` and self-check. Repair by removing only a
  mismatched `enterprise-hub` entry and re-adding it; per-agent removal uses
  `codex mcp remove enterprise-hub`, followed by `codex mcp list --json` and an absent `get`.
- OpenClaw: use `openclaw mcp add` for a new stdio entry or `openclaw mcp set` for the smallest
  idempotent replacement, then prove it with `openclaw mcp doctor enterprise-hub --probe`. The
  macOS add form is `openclaw mcp add enterprise-hub --command "$HOME/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/node_modules/.bin/enterprise-hub-mcp-launcher" --arg serve --env ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz`.
  Do not use `openclaw mcp login` or `openclaw mcp logout`: those manage OpenClaw's direct HTTP
  OAuth store, while the Enterprise Hub launcher owns browser login and secure storage.
- Other agents: use guarded adaptive discovery—inspect product help and current config, back up,
  add only the pinned local stdio entry, and validate the handshake. Do not guess destructively or
  configure direct OAuth.

Use `enterprise_hub_auth_status` when authentication state is unknown. On
`authentication_required`, invoke `enterprise_hub_login` and ask the employee only to complete the
browser page. After success, retry the original business operation once. Use
`enterprise_hub_logout` only on an employee's request; it signs out all local Enterprise Hub
agents sharing that OS-user secure store.

## Safe Use

- Backend authorization, not client filtering, determines visible organizations, labels, and
  resources. Do not provide organization IDs or infer hidden data.
- Read only a user-selected upload file's exact bytes; send inline bytes rather than a local path.
  Never normalize or reconstruct content.
- Poll status without starting workers; do not operate service infrastructure.
- Reuse a structured-import idempotency key only for an exact replay. Treat import-status 404 as
  not visible or missing.
- Keep evidence cursors unchanged for the same query/filter/limit. Restart on `INVALID_CURSOR`;
  explain `CURSOR_EXPIRED` and restart only if the employee wants to continue.
- The Skill Directory lists metadata only—do not execute entries or generate reports/dashboards.

## Lifecycle

For per-agent removal, back up that agent's configuration and remove only its `enterprise-hub`
entry. For shared logout, use `enterprise_hub_logout` or run the exact platform command:

```sh
ENTERPRISE_HUB_BASE_URL=https://api.smedatacenter.xyz \
  "$HOME/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/node_modules/.bin/enterprise-hub-mcp-launcher" logout
```

```powershell
$env:ENTERPRISE_HUB_BASE_URL = "https://api.smedatacenter.xyz"
& "$env:LOCALAPPDATA\Enterprise Hub\launcher\versions\0.1.0\node_modules\.bin\enterprise-hub-mcp-launcher.cmd" logout
```

Logout returns only
`{"remoteRevocationConfirmed":<boolean>,"localCredentialRemoved":<boolean>}`, attempts remote
revocation when reachable, and always attempts local deletion. Do not report local logout success
unless `localCredentialRemoved` is true. For complete uninstall with explicit authorization, log
out, remove Enterprise Hub entries from safely discoverable local agents, and remove the
current-user launcher directory and non-secret state. Never remove Node.js/npm, other MCP servers,
the Employee Account, or server-side business data.

## Contents

- `skills/enterprise-hub-mcp/SKILL.md`
- `skills/enterprise-hub-mcp/agents/openai.yaml`
