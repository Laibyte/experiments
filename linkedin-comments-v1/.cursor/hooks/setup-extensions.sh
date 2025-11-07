#!/bin/bash
# Auto-install VSCode/Cursor extensions from extensions.json

set -e

# Determine which IDE is being used
CMD=""
IDE_NAME=""
if command -v cursor &> /dev/null; then
  CMD="cursor"
  IDE_NAME="Cursor"
elif command -v code &> /dev/null; then
  CMD="code"
  IDE_NAME="VSCode"
else
  echo "⚠️  Neither 'cursor' nor 'code' command found."
  echo "💡 Extensions must be installed manually from the IDE:"
  echo "   - Open Command Palette (Cmd/Ctrl + Shift + P)"
  echo "   - Search 'Extensions: Show Recommended Extensions'"
  echo "   - Click 'Install All'"
  exit 0
fi

# Find extensions.json file (Cursor can use .cursor/ or .vscode/, VSCode uses .vscode/)
EXTENSIONS_FILE=""
if [ "$IDE_NAME" = "Cursor" ]; then
  # Cursor: prioritize .cursor/extensions.json, fallback to .vscode/extensions.json
  if [ -f ".cursor/extensions.json" ]; then
    EXTENSIONS_FILE=".cursor/extensions.json"
    echo "📦 Installing Cursor extensions from .cursor/extensions.json..."
  elif [ -f ".vscode/extensions.json" ]; then
    EXTENSIONS_FILE=".vscode/extensions.json"
    echo "📦 Installing Cursor extensions from .vscode/extensions.json..."
  else
    echo "❌ No extensions.json found in .cursor/ or .vscode/"
    exit 1
  fi
else
  # VSCode: only use .vscode/extensions.json
  if [ -f ".vscode/extensions.json" ]; then
    EXTENSIONS_FILE=".vscode/extensions.json"
    echo "📦 Installing VSCode extensions from .vscode/extensions.json..."
  else
    echo "❌ No extensions.json found at .vscode/extensions.json"
    exit 1
  fi
fi

# Extract extension IDs from extensions.json using Python
# (jq might not be available yet during initial setup)
EXTENSIONS=$(python3 -c "
import json
import sys

try:
    with open('$EXTENSIONS_FILE', 'r') as f:
        data = json.load(f)
        recommendations = data.get('recommendations', [])
        for ext in recommendations:
            print(ext)
except Exception as e:
    sys.exit(1)
")

if [ -z "$EXTENSIONS" ]; then
  echo "⚠️  No extensions found in $EXTENSIONS_FILE"
  exit 0
fi

# Install each extension
echo ""
echo "Installing extensions:"
INSTALLED=0
FAILED=0

while IFS= read -r extension; do
  echo -n "  - $extension ... "

  # Check if already installed
  if $CMD --list-extensions 2>/dev/null | grep -qi "^$extension$"; then
    echo "✅ already installed"
  else
    # Install extension
    if $CMD --install-extension "$extension" --force > /dev/null 2>&1; then
      echo "✅ installed"
      ((INSTALLED++))
    else
      echo "❌ failed"
      ((FAILED++))
    fi
  fi
done <<< "$EXTENSIONS"

echo ""
if [ $INSTALLED -gt 0 ]; then
  echo "✅ Installed $INSTALLED new extension(s)"
fi

if [ $FAILED -gt 0 ]; then
  echo "⚠️  $FAILED extension(s) failed to install"
  echo "💡 Try installing them manually from the Extensions panel"
fi

echo ""
echo "🎯 Recommended: Restart your IDE to activate all extensions"
