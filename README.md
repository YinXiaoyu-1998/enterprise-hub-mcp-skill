# Enterprise Hub MCP Skill

Standalone Codex skill for safely using Enterprise Hub through a configured MCP connection.

This repository contains only the skill and MCP-client connection guidance. It does not install, start, stop, initialize, or operate the Enterprise Hub API, worker, database, Qdrant, storage, or any other service. Service implementation and operations belong to [YinXiaoyu-1998/SME_DATA_CENTER](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER).

## Install Into Codex

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YinXiaoyu-1998/enterprise-hub-mcp-skill \
  --path skills/enterprise-hub-mcp
```

Restart Codex after installation so the skill list refreshes.

## Service Prerequisite

A service operator must already provision and operate the API, worker, database, storage, and Qdrant, then provide an approved `ENTERPRISE_HUB_API_URL`. This skill must report an unavailable connection and must not start or repair the service.

Service development and operations are documented in the main repository [README](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/README.md), [environment inventory](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/env-inventory.md), and [staging readiness checklist](https://github.com/YinXiaoyu-1998/SME_DATA_CENTER/blob/main/docs/implementation/staging-readiness.md).

## MCP Adapter Configuration

The MCP adapter lives in the main repository. This configuration starts only that adapter; it does not start API, worker, database, or other services.

```toml
[mcp_servers.enterprise-hub]
command = "bash"
args = ["-lc", "cd /path/to/SME_DATA_CENTER && npm run --silent mcp:dev"]
startup_timeout_sec = 120

[mcp_servers.enterprise-hub.env]
ENTERPRISE_HUB_API_URL = "https://approved-enterprise-hub-api.example"
ENTERPRISE_HUB_MCP_PROFILE = "local-development"
ENTERPRISE_HUB_MCP_SESSION_FILE = "/path/to/SME_DATA_CENTER/.data/enterprise-hub-mcp/session.json"
```

Do not place production tokens, passwords, API keys, or service-account credentials in client configuration.
