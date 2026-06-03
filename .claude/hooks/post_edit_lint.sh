#!/bin/bash

# Post-edit hook: auto-format Python files after editing
# Triggered after Edit or Write tool modifies a .py file
# Exit code 0 = success (formatting applied), non-zero = format error
# Claude Code passes tool input as JSON on stdin (field: tool_input.file_path)

INPUT=$(cat)
FILE=$(python3 -c "import sys,json; d=json.loads(sys.argv[1]); print(d.get('tool_input',{}).get('file_path',''))" "$INPUT" 2>/dev/null)

if [[ ! "$FILE" =~ \.py$ ]]; then
    exit 0  # Not a Python file, skip
fi

# Check if file exists and is readable
if [[ ! -f "$FILE" ]]; then
    exit 0
fi

# Skip non-source dirs
if [[ "$FILE" =~ __pycache__ ]]; then
    exit 0
fi

# Resolve project root via git to handle any nesting depth
PROJECT_ROOT=$(git -C "$(dirname "$FILE")" rev-parse --show-toplevel 2>/dev/null)
if [[ -z "$PROJECT_ROOT" ]]; then exit 0; fi
cd "$PROJECT_ROOT" || exit 0

# Run ruff format then ruff check --fix on the edited file
if command -v ruff &>/dev/null; then
    ruff format "$FILE" 2>/dev/null
    ruff check --fix "$FILE" 2>/dev/null
    exit 0
fi

# Fallback if ruff not available
exit 0
