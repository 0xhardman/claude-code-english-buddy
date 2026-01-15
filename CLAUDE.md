# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

English Buddy is a Claude Code plugin that automatically checks English grammar in user messages, tracks corrections in SQLite and Obsidian, and provides learning analytics.

## Development Setup

```bash
# Install dependencies
pip install anthropic
brew install terminal-notifier  # Optional, for macOS notifications

# Run in development mode
claude --plugin-dir ./english-buddy
```

Environment: Set `ANTHROPIC_API_KEY` in environment or `~/.claude/.env`

## Testing Individual Components

```bash
python3 lib/claude_api.py      # Test grammar API
python3 lib/db.py              # Test database operations
python3 lib/language_detect.py # Test language detection
python3 lib/charts.py          # Test ASCII chart generation
```

## Architecture

### Execution Flow

```
User message → UserPromptSubmit hook → check_grammar.py
    → language_detect.py (filter non-English/short text)
    → claude_api.py (Claude Haiku analysis)
    → Success: db.py + obsidian.py + notification
    → Failure: save to retry_queue.json
```

### Key Modules

- **lib/claude_api.py**: Claude 3.5 Haiku API calls, returns JSON with errors/corrections
- **lib/db.py**: SQLite operations (`~/.english-buddy/data.sqlite`), tables: corrections, errors, daily_stats
- **lib/obsidian.py**: Markdown logs (`~/obsidian/learning/english/YYYY-MM-DD.md`)
- **lib/language_detect.py**: Filters Chinese text, short messages, non-English content
- **lib/charts.py**: ASCII bar/trend charts for terminal display

### Scripts

- **check_grammar.py**: Hook handler, reads stdin JSON, returns empty JSON to stdout
- **daily_summary.py**: `/english-buddy:summary` command
- **weekly_summary.py**: `/english-buddy:week` command
- **stats.py**: `/english-buddy:stats` command with ASCII charts
- **recall.py**: `/english-buddy:recall` - retry failed checks or re-notify last success

### Data Files

- `~/.english-buddy/data.sqlite` - Statistics database
- `~/.english-buddy/retry_queue.json` - Failed checks queue (max 50 items)
- `~/.english-buddy/last_check.json` - Last successful check for recall
- `~/obsidian/learning/english/` - Daily markdown logs

## Plugin Configuration

- `hooks/hooks.json`: UserPromptSubmit hook triggers check_grammar.py (15s timeout)
- `.claude-plugin/plugin.json`: Plugin metadata
- `commands/*.md`: Command definitions for Claude Code

## Key Design Patterns

1. **Dual Storage**: SQLite for analytics, Obsidian for human-readable logs
2. **Graceful Degradation**: Failed checks saved to retry queue, non-blocking returns
3. **Smart Filtering**: Skip Chinese text, short messages, technical content
4. **Notification Fallback**: terminal-notifier → osascript → silent
