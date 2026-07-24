# Enterprise Hub MCP Skill

The official runbook for employee-owned agents to install and use the Enterprise Hub remote MCP
launcher. It uses browser login and the official service origin
`https://api.smedatacenter.xyz`; employees never give passwords, tokens, or authorization codes to
an agent.

This repository contains only skill and client-connection guidance. It never operates the
Enterprise Hub API, database, Qdrant, storage, Docker, worker, cloud resources, or deployment.
Those service responsibilities remain in
[SME_DATA_CENTER](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER).

> Pre-cutover status: this is the approved official target runbook. It does not assert that the
> browser-login launcher, npm package, or public MCP boundary is already deployed. The main
> repository records the current implementation and cutover work.

## Install The Skill

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YinXiaoyu-1998/enterprise-hub-mcp-skill \
  --path skills/enterprise-hub-mcp
```

Restart Codex or open a new task after installation so the skill list refreshes.

## Official Launcher

The only approved launcher package is `enterprise-hub-mcp-launcher@0.1.0`. Never use npm
`latest`, an unpinned version, or launcher self-update.

| Platform | Current-user package directory                                          |
| -------- | ----------------------------------------------------------------------- |
| macOS    | `~/Library/Application Support/Enterprise Hub/launcher/versions/0.1.0/` |
| Windows  | `%LOCALAPPDATA%\\Enterprise Hub\\launcher\\versions\\0.1.0\\`           |

An authorized employee-owned agent installs or repairs it idempotently:

```sh
npm install --prefix "<launcher-directory>" --save-exact enterprise-hub-mcp-launcher@0.1.0
```

The agent must use the installed launcher's credential-free self-check before claiming success.
The launcher never self-updates. An approved update uses a new exact versioned directory, changes
only the invoking agent's MCP launcher path, and preserves the operating-system secure session.

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

- Codex: use the installed Codex MCP configuration mechanism for the pinned launcher, then reload
  or restart Codex and confirm tool discovery. If the supported config location/syntax is unclear,
  stop with that narrow blocker rather than editing guessed files.
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
entry. For shared logout, use `enterprise_hub_logout`; if the service is unavailable, local secure
credential removal still completes but remote revocation remains unconfirmed. For complete
uninstall with explicit authorization, log out, remove Enterprise Hub entries from safely
discoverable local agents, and remove the current-user launcher directory and non-secret state.
Never remove Node.js/npm, other MCP servers, the Employee Account, or server-side business data.

## Contents

- `skills/enterprise-hub-mcp/SKILL.md`
- `skills/enterprise-hub-mcp/agents/openai.yaml`
