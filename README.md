# English Buddy

A Claude Code plugin that helps you improve your English by automatically checking grammar and tracking your progress.

## Features

- **Automatic Grammar Checking**: Every English message you send is analyzed for grammar, spelling, and style issues
- **Smart Filtering**: Skips code, commands, Chinese text, and technical content
- **Dual Storage**: Corrections saved to both SQLite (for stats) and Obsidian (for review)
- **macOS Notifications**: Get instant feedback with clickable notifications
- **Progress Tracking**: Daily, weekly, and all-time statistics with ASCII charts

## Installation

### Development Mode

```bash
claude --plugin-dir ~/code/my/english-buddy
```

### Permanent Installation

```bash
ln -s ~/code/my/english-buddy ~/.claude/plugins/english-buddy
```

Then enable in Claude Code settings or restart Claude Code.

## Commands

| Command | Description |
|---------|-------------|
| `/english-buddy:summary` | Today's corrections summary |
| `/english-buddy:week` | Weekly progress report |
| `/english-buddy:stats` | Detailed statistics with charts |

## How It Works

```
┌─────────────────────────────────────────────┐
│  You send an English message                │
│           ↓                                 │
│  Hook triggers check_grammar.py             │
│           ↓                                 │
│  Claude Haiku analyzes grammar              │
│           ↓                                 │
│  If errors found:                           │
│    → Save to SQLite (stats)                 │
│    → Save to Obsidian (daily log)           │
│    → Show macOS notification                │
└─────────────────────────────────────────────┘
```

## Data Storage

### SQLite Database
`~/.english-buddy/data.sqlite`

Stores structured data for statistics:
- Corrections with timestamps
- Errors by category (spelling, grammar, style, vocabulary)
- Daily aggregated stats

### Obsidian Markdown
`~/obsidian/learning/english/YYYY-MM-DD.md`

Human-readable daily logs with:
- Original text
- Corrections and explanations
- Better expressions
- Chinese summaries

## Requirements

- macOS (for notifications)
- Python 3.8+
- Claude Code 1.0.33+
- `anthropic` Python package (for API calls)
- `terminal-notifier` (optional, for better notifications)

```bash
pip install anthropic
brew install terminal-notifier
```

## Configuration

The plugin uses your existing `ANTHROPIC_API_KEY` from:
- Environment variable, or
- `~/.claude/.env` file

## Example Output

### Daily Summary
```
📊 Daily Summary - 2026-01-14
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total corrections: 8
  • Spelling:   2
  • Grammar:    5
  • Style:      1

📝 Most common mistakes today:
  1. "waht" → "what" (3x)
  2. "I has" → "I have" (2x)
```

### Statistics
```
📊 English Learning Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Error Distribution
━━━━━━━━━━━━━━━━━━
Spelling    ████████ 25%
Grammar     ████████████████ 50%
Style       ████ 15%
Vocabulary  ███ 10%
```

## License

MIT

## Author

0xhardman
