#!/bin/bash
# Final checks when agent task completes
# Integrates with pre-commit for quality checks

read -r payload

status=$(echo "$payload" | jq -r '.status' 2>/dev/null || echo "unknown")

# Log completion
echo "$(date +%Y-%m-%d\ %H:%M:%S) - Task completed with status: $status" >> .cursor/hooks.log

# Check if pre-commit is available
if ! command -v poetry &> /dev/null; then
  echo "⚠️  Poetry not found. Skipping quality checks."
  exit 0
fi

# Check if in a poetry project
if [ ! -f "pyproject.toml" ]; then
  echo "⚠️  Not in a poetry project. Skipping quality checks."
  exit 0
fi

echo "🔍 Running quality checks via pre-commit..."

# Run pre-commit checks (fast checks only, no commit needed)
# This gives immediate feedback without requiring a commit
if poetry run pre-commit run --all-files 2>&1 | grep -q "Failed"; then
  echo ""
  echo "⚠️  Pre-commit checks found issues."
  echo "💡 Fix them with: poetry run poe lint-fix && poetry run poe format"
  echo "💡 Or run: make lint-fix && make format"
else
  echo "✅ All quality checks passed!"
fi

# Show notification (macOS only)
if command -v osascript &> /dev/null; then
  osascript -e 'display notification "Agent task completed" with title "Cursor" sound name "Glass"' 2>/dev/null
fi

exit 0
