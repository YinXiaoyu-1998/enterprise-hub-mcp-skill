# Enterprise Hub MCP Skill

Standalone Codex skill for safely using Enterprise Hub through the local MCP launcher and the service HTTP endpoint.

This repository contains only the skill and MCP-client connection guidance. It does not install, start, stop, initialize, or operate the Enterprise Hub API, worker, database, Qdrant, storage, or any other service. Service implementation and operations belong to [YinXiaoyu-1998/SME_DATA_CENTER](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER).

## Install Into Codex

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YinXiaoyu-1998/enterprise-hub-mcp-skill \
  --path skills/enterprise-hub-mcp
```

Restart Codex after installation so the skill list refreshes.

## Service Prerequisite

A service operator must already provision and operate the API, worker, database, storage, and Qdrant, then provide an approved Enterprise Hub base URL. This skill must report an unavailable connection and must not start or repair the service.

Service development and operations are documented in the main repository [README](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/README.md), [environment inventory](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/env-inventory.md), and [staging readiness checklist](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/staging-readiness.md).

## MCP Launcher Configuration

The MCP launcher lives in the main repository. This configuration starts only that launcher; it does not start API, worker, database, or other services.

```toml
[mcp_servers.enterprise-hub]
command = "npm"
args = ["run", "--silent", "mcp:launcher"]
cwd = "/path/to/SME_DATA_CENTER"
startup_timeout_sec = 120

[mcp_servers.enterprise-hub.env]
ENTERPRISE_HUB_BASE_URL = "http://127.0.0.1:3000"
```

The service exposes authenticated Streamable HTTP at `POST <Enterprise Hub URL>/mcp`. The launcher may use stdio only between the local MCP client and itself. The service has no stdio MCP adapter.

`ENTERPRISE_HUB_BASE_URL` is the only launcher configuration value. Never put a bearer token, password, session file, service account key, or credential in MCP configuration, environment variables, command arguments, files, or skill content.

## Usage Notes

- Do not provide or ask for an organization ID. The service derives organization scope from the authenticated employee and rejects hidden data through backend authorization.
- Evidence search cursors are opaque, short-lived continuation tokens. To fetch the next page, pass `page.nextCursor` back unchanged as `cursor` with the same query, filters, and limit. Restart without a cursor on `INVALID_CURSOR`; on `CURSOR_EXPIRED`, explain the expiry and restart only if the user still wants more results.
- Structured import retries should reuse an `idempotencyKey` only for the exact same file and metadata. Exact replay returns the original persisted `documentId`, `importBatchId`, and storage key instead of duplicating rows or objects.
- `get_import_status` returns the same non-enumerating 404 for nonexistent, cross-org, disabled, or label-inaccessible import batches. Treat it as "not visible or missing" and do not infer hidden batch metadata.

## Contents

- `skills/enterprise-hub-mcp/SKILL.md`
- `skills/enterprise-hub-mcp/agents/openai.yaml`

## Safety

Do not commit real tokens, production credentials, real customer exports, or downloaded third-party data. The skill contains Phase 3 local-development guidance and placeholder remote-service wording only.
