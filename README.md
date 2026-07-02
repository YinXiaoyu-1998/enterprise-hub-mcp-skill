# Enterprise Hub MCP Skill

Standalone Codex skill for using 企业资料中枢 through the local MCP adapter.

The skill teaches an employee-owned agent how to connect to the local
`enterprise-hub` MCP server, authenticate seeded local employees, upload/search/archive
documents, verify Baoli/Suzhou permission isolation, and avoid inventing staging or
production infrastructure.

## Install Into Codex

From any machine with Codex skill installer access:

```sh
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo YinXiaoyu-1998/enterprise-hub-mcp-skill \
  --path skills/enterprise-hub-mcp
```

Restart Codex after installation so the skill list refreshes.

## Local MCP Requirement

This skill expects the 企业资料中枢 repository to be available locally and its MCP server
configured in Codex as `enterprise-hub`, for example:

```toml
[mcp_servers.enterprise-hub]
command = "bash"
args = ["-lc", "cd /path/to/SME_DATA_CENTER && npm run mcp:dev"]
startup_timeout_sec = 120

[mcp_servers.enterprise-hub.env]
ENTERPRISE_HUB_API_URL = "http://127.0.0.1:3000"
ENTERPRISE_HUB_MCP_PROFILE = "local-development"
ENTERPRISE_HUB_MCP_SESSION_FILE = "/path/to/SME_DATA_CENTER/.data/enterprise-hub-mcp/session.json"
```

The API must be started separately. The MCP server is only an adapter over the HTTP API.

## Contents

- `skills/enterprise-hub-mcp/SKILL.md`
- `skills/enterprise-hub-mcp/agents/openai.yaml`

## Safety

Do not commit real tokens, production credentials, real customer exports, or downloaded
third-party data. The skill contains local-development guidance and placeholder remote
profiles only.
