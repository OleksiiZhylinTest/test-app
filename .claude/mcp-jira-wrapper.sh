#!/bin/bash

# MCP wrapper: loads project .env and starts the Jira MCP server
# Used by settings.local.json mcpServers.jira-mcp

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: .env not found at $ENV_FILE" >&2
    exit 1
fi

# Load .env (skip comments and blank lines)
set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

# Derive host from JIRA_URL (strip protocol and trailing path)
JIRA_HOST=$(echo "$JIRA_URL" | sed 's|https\?://||' | sed 's|/.*||')

if [[ -z "$JIRA_HOST" || -z "$JIRA_EMAIL" || -z "$JIRA_API_TOKEN" ]]; then
    echo "ERROR: JIRA_URL, JIRA_EMAIL, or JIRA_API_TOKEN not set in .env" >&2
    exit 1
fi

exec npx --yes "@anthropic-ai/jira-mcp@latest" \
    --host "$JIRA_HOST" \
    --email "$JIRA_EMAIL" \
    --api-token "$JIRA_API_TOKEN"
