#!/bin/bash

# Pre-edit boundary hook: block edits to Copilot-owned customization surfaces
# Triggered before Edit or Write tool executes
# Exit code 0 = allowed, non-zero = blocked
# Claude Code passes tool input as JSON on stdin

INPUT=$(cat)
FILE=$(python3 -c "import sys,json; d=json.loads(sys.argv[1]); ti=d.get('tool_input',{}); print(ti.get('file_path','') or ti.get('target_file',''))" "$INPUT" 2>/dev/null)

if [[ -z "$FILE" ]]; then
    exit 0
fi

NORMALIZED="${FILE//\\//}"

if [[ "$ALLOW_CROSS_ASSISTANT_CUSTOMIZATION_EDIT" == "1" ]]; then
    exit 0
fi

if [[ "$NORMALIZED" =~ /\.github/(agents|skills|prompts|hooks|instructions)/ ]] || [[ "$NORMALIZED" =~ /\.github/copilot-instructions\.md$ ]]; then
    echo "ERROR: Blocked edit to Copilot-owned customization file: $FILE"
    echo "Claude may only edit Copilot customization files during an explicit cross-tool governance task."
    echo "Set ALLOW_CROSS_ASSISTANT_CUSTOMIZATION_EDIT=1 to allow an intentional one-off edit."
    exit 1
fi

exit 0