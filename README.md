# SMEDC MCP Skill

The official runbook for employee-owned agents to install and use the SMEDC remote MCP
launcher. SMEDC stands for Small and Medium Enterprises Data Center. It uses browser login and
the official service origin `https://api.smedatacenter.xyz`; employees never give passwords,
tokens, or authorization codes to an agent.

This repository contains only skill and client-connection guidance. It never operates the SMEDC
API, database, vector store, storage, Docker, worker, cloud resources, or deployment.

> Live-service status: `smedc-mcp-launcher@0.6.0`, browser login, and the public HTTPS MCP
> boundary are the current packaging contract. Real employee login and backend authorization are
> still required. The launcher supports macOS, Windows, and Linux; headless Linux uses the same
> Device Authorization flow and falls back to a memory-only session when no secure store exists.

## Upload Permissions

Only active admins can upload evidence, structured datasets (including Delivery Ledger), and
quarantine certificates. Employees at every clearance may read eligible data but cannot upload.
Upload tools remain visible and admin-only; for a known employee role, the agent must not read or
transform the local file. Launcher 0.6.0 preflights before file access; a local denial creates no
backend audit. Direct HTTP upload endpoints return HTTP `403`; MCP JSON-RPC transport returns
HTTP `200` with `isError: true` in the tool result. Both carry `UPLOAD_ADMIN_REQUIRED`, exact message
`File upload requires the admin role.`, and `retryable: false`; backend denials best-effort record
`file_upload.denied`.
Do not re-login, retry, or increase clearance to recover from that denial.

Admins may explicitly classify above their clearance without gaining ordinary read access.
Partition create/parts/complete require admin; owner abort and existing status/manifest/read rules
remain available. Minimum compatible launcher and the approved install pin are both 0.6.0.
Older launchers are unsupported and receive `LAUNCHER_UPGRADE_REQUIRED`. Upload original files and report
service validation errors; this core skill provides no dataset-specific transformations.

## Pending Ledger PDF Capability

The [five archive tool contracts](skills/smedc-mcp/references/ledger-pdf-tools.md) require launcher
0.7.0 once published and service archive delivery enabled. This branch does not publish 0.7.0 or
change the active 0.6.0 installation pin. At cutover, ledger detail and original CSV/XLSX signing
close; supported store/date aggregates and other datasets remain available. Workflow coordination
belongs to the independently installed delivery-ledger companion; the core Skill never generates
local ledgers.

## Installation Profiles

### Core-only install

This is the default profile. Install only `smedc-mcp` for launcher setup, browser login, uploads,
and authorization-safe SMEDC queries. Optional companion skills are not required for ordinary SMEDC
work and are never installed silently by a core install or update.

### Optional companions

Both companions live in
[`YinXiaoyu-1998/smedc-companion-skills`](https://github.com/YinXiaoyu-1998/smedc-companion-skills)
and remain independently installed skills:

- `smedc-business-analysis` generates organization-backed operating diagnoses, weekly reports, and
  monthly reports.
- `smedc-delivery-ledger` coordinates server daily PDF refresh, ZIP preparation, and receipt-linked
  quarantine-certificate photo operations when the archive capability is released and enabled.

If a companion is absent, an agent may identify the official source and offer to install it, but the
employee must explicitly authorize that installation or request the named companion or all
recommended companions. Installing or updating either repository does not update the other.

## Install The Skill

Clone or download this repository, then install the skill to the canonical current-user skill
directory. Do not default to `~/.codex/skills`.

| Platform         | Canonical target                         |
| ---------------- | ---------------------------------------- |
| macOS/Linux-like | `~/.agents/skills/smedc-mcp`             |
| Windows          | `%USERPROFILE%\.agents\skills\smedc-mcp` |

Ask the agent to follow the [skill replacement procedure](skills/smedc-mcp/references/update-skill.md):
stage the complete directory, keep temporary recovery copies outside all skill discovery roots,
verify file contents and the host's loaded copy, then remove obsolete duplicates and temporary
backups. Do not overlay an existing directory or create `.bak` copies inside a skill root.
If the host needs a reload/restart, complete that step before claiming the installed skill is active.

## Update The Skill

Ask your agent: "Update the smedc-mcp-skill skill." The installed skill recognizes both `smedc-mcp`
and `smedc-mcp-skill`, retrieves the latest default-branch revision from
[`YinXiaoyu-1998/smedc-mcp-skill`](https://github.com/YinXiaoyu-1998/smedc-mcp-skill), and backs up,
replaces, and verifies its complete skill directory. A marketplace listing is not required. The
agent reports the source commit, loaded installation path, and cleanup result; pending host
reloads or obsolete copies are reported as incomplete.

Updating the skill alone preserves the launcher and login session. A launcher upgrade requires a
launcher or general SMEDC update request and uses the exact pin in the refreshed official skill. Network/write access and
the host's supported installation mechanism are still required. See the
[update procedure](skills/smedc-mcp/references/update-skill.md).

## Official Launcher

The only approved launcher package is `smedc-mcp-launcher@0.6.0`. Never use npm `latest`, an
unpinned version, or launcher self-update.

Run `node --version` and `npm --version` first. Node.js 22 or newer and a working npm are required.
An authorized employee-owned agent installs or repairs it idempotently:

```sh
npm install --prefix "<launcher-directory>" --save-exact smedc-mcp-launcher@0.6.0
```

Use the approved current-user launcher directory:

| Platform | Launcher directory                                                    |
| -------- | --------------------------------------------------------------------- |
| macOS    | `~/Library/Application Support/SMEDC/launcher/versions/0.6.0/`        |
| Windows  | `%LOCALAPPDATA%\\SMEDC\\launcher\\versions\\0.6.0\\`                  |
| Linux    | `${XDG_DATA_HOME:-$HOME/.local/share}/SMEDC/launcher/versions/0.6.0/` |

The agent must run the exact platform self-check before claiming success:

```sh
SMEDC_BASE_URL=https://api.smedatacenter.xyz \
  "$HOME/Library/Application Support/SMEDC/launcher/versions/0.6.0/node_modules/.bin/smedc-mcp-launcher" self-check
```

```powershell
$env:SMEDC_BASE_URL = "https://api.smedatacenter.xyz"
& "$env:LOCALAPPDATA\SMEDC\launcher\versions\0.6.0\node_modules\.bin\smedc-mcp-launcher.cmd" self-check
```

```sh
# Linux
SMEDC_LAUNCHER_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/SMEDC/launcher/versions/0.6.0"
SMEDC_BASE_URL=https://api.smedatacenter.xyz \
  "$SMEDC_LAUNCHER_DIR/node_modules/.bin/smedc-mcp-launcher" self-check
```

Self-check returns only safe machine-readable fields and never self-updates. A general SMEDC
update refreshes the skill and follows the required
[upgrade and cleanup procedure](skills/smedc-mcp/references/upgrade-cleanup.md): prepare the
approved launcher, switch MCP entries, reconnect and verify the running version, stop old
processes, then remove superseded installations and temporary backups. Requests to remove all
old versions also migrate safely discoverable current-user SMEDC integrations. Preserve valid
operating-system secure sessions. A standalone self-check is not proof of the host connection.
On Linux, `secureStore.available:false` is supported:
the launcher returns the first-party login link instead of opening a local browser when headless,
keeps the resulting session in memory only, and requires login again after launcher or host restart.

## Configuration And Login

Configure SMEDC as a local stdio launcher named `smedc`, not as a direct remote HTTP/OAuth server.
The complete launch tuple has one `serve` argument and one non-secret environment value:
`SMEDC_BASE_URL=https://api.smedatacenter.xyz`.

Before changing an MCP client, inspect its configuration and make a timestamped backup. Add or
replace its `smedc` stdio entry and remove verified duplicate SMEDC entries within the requested
scope; preserve every unrelated server and setting.

Use `smedc_auth_status` when authentication state is unknown. On `authentication_required`, invoke
`smedc_login` and ask the employee only to complete the browser page. After success, retry the
original business operation once. Use `smedc_logout` only on an employee's request.

When an employee asks which account is active, use the zero-input `smedc_get_current_user` tool. It
returns the authenticated employee's `displayName`, `email`, `role`, `clearance`, and
`organizationName`. The skill directory tool is `smedc_list_skills`.

## Contents

- `skills/smedc-mcp/SKILL.md`
- `skills/smedc-mcp/agents/openai.yaml`
- `skills/smedc-mcp/references/update-skill.md`
- `skills/smedc-mcp/references/upgrade-cleanup.md`
- `skills/smedc-mcp/references/ledger-pdf-tools.md`
