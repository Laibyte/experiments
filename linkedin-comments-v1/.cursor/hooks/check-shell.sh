#!/bin/bash
# Block dangerous shell commands

read -r payload

# Extract command from JSON
command=$(echo "$payload" | jq -r '.command')

# Dangerous patterns to block (expanded list)
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf \*"
    "rm -rf ~"
    "sudo"
    "chmod -R 777"
    "chmod 777"
    "chown -R"
    "mkfs"
    "dd if="
    "mv.*\/dev\/null"
    "\u003e\/dev\/sda"
    "\u003e \/dev\/sda"
    "wget.*\|.*sh"
    "curl.*\|.*sh"
    ":\(\)\{.*\|\:"
    "fork\(\)"
    "> /dev/"
    "mkfs\."
    "fdisk"
    "parted"
    "shutdown"
    "reboot"
    "init 0"
    "init 6"
    "systemctl.*halt"
    "systemctl.*poweroff"
)

# Check dangerous patterns
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$command" | grep -Eq "$pattern"; then
        jq -n \
            --arg msg "⛔ Blocked dangerous command: $command" \
            '{
                "continue": false,
                "permission": "deny",
                "userMessage": $msg,
                "agentMessage": "This command is blocked for safety. Use safer alternatives or run manually if needed."
            }'
        exit 0
    fi
done

# Allow safe commands
jq -n '{
    "continue": true,
    "permission": "allow"
}'
