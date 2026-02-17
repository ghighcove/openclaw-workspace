"""Quick fix script - remove emojis from march_historical_collector.py"""

import re

file_path = "G:/ai/openclaw-workspace/automation/march_historical_collector.py"

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace emojis with text
replacements = {
    '❌': '[FAIL]',
    '✅': '[PASS]',
    '⚠️': '[WARNING]',
    '⚠': '[WARNING]',
    '📋': '[TASK]',
    '=' * 60: '=' * 60,  # Already ASCII, safe
}

for emoji, replacement in replacements.items():
    content = content.replace(emoji, replacement)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed emoji characters in {file_path}")
print("Emojis replaced with text equivalents")
