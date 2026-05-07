#!/bin/bash

# Pre-bash safety hook: block destructive operations that are too risky to run
# Triggered before Bash tool executes
# Exit code 0 = safe to execute, non-zero = blocked
# Claude Code passes tool input as JSON on stdin (field: tool_input.command)

INPUT=$(cat)
COMMAND=$(python3 -c "import sys,json; d=json.loads(sys.argv[1]); print(d.get('tool_input',{}).get('command',''))" "$INPUT" 2>/dev/null)

# Strip cmd /c and powershell -Command wrappers so inner commands are checked
STRIPPED="$COMMAND"
if [[ "$STRIPPED" =~ ^cmd[[:space:]]+/[cC][[:space:]]+(.*) ]]; then
    STRIPPED="${BASH_REMATCH[1]}"
elif [[ "$STRIPPED" =~ ^powershell[[:space:]].*-[Cc]ommand[[:space:]]+(.*) ]]; then
    STRIPPED="${BASH_REMATCH[1]}"
fi

# Dangerous patterns to block
BLOCKED_PATTERNS=(
    "git reset --hard"
    "git checkout --"
    "rm -rf"
    "git clean -f"
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if [[ "$STRIPPED" =~ $pattern ]]; then
        echo "ERROR: Blocked destructive operation: $pattern"
        echo "This operation requires explicit user confirmation."
        exit 1
    fi
done

# Block all force pushes regardless of argument order (--force, -f, --force-with-lease)
if [[ "$STRIPPED" =~ ^git[[:space:]]+push ]] && \
   [[ "$STRIPPED" =~ (--force|--force-with-lease|-f)([[:space:]]|$) ]]; then
    echo "ERROR: Blocked force push: $STRIPPED"
    echo "Force pushing rewrites remote history. Requires explicit user approval."
    exit 1
fi

# Allow everything else
exit 0
