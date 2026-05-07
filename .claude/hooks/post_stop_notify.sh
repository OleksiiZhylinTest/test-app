#!/bin/bash

# Post-stop hook: notify when Claude finishes responding
# Triggered after Claude's turn ends (Stop event)

echo ""
echo "──────────────────────────────────────"
echo "  Claude finished at $(date '+%H:%M:%S')"
echo "──────────────────────────────────────"
