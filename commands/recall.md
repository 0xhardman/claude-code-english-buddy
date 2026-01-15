---
description: Retry failed grammar checks due to network issues
allowed-tools: [Bash]
---

# Recall - Retry Failed Grammar Checks

Run the recall script to retry any grammar checks that failed due to network issues:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/recall.py
```

This script will:
- Load any failed grammar checks from the retry queue
- Retry each one (with 1 additional retry on failure)
- Save successful results to Obsidian and the database
- Notify you of the outcome via macOS notification
- Clear successful items from the queue
