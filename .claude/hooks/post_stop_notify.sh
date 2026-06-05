#!/bin/bash

# Post-stop hook: notify when Claude finishes responding and generate token report
# Triggered after Claude's turn ends (Stop event)

stdin_data=$(cat)
if [ -n "$stdin_data" ]; then
  echo "$stdin_data" | python "$CLAUDE_PROJECT_DIR/tools/claude_session_stats.py" 2>/dev/null
fi

echo ""
echo "──────────────────────────────────────"
echo "  Claude finished at $(date '+%H:%M:%S')"
echo "──────────────────────────────────────"
