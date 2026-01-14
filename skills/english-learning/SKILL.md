---
name: english-learning
description: Use when user asks about English progress, grammar learning, correction statistics, or wants to review their mistakes. Triggers on phrases like "how is my English", "my grammar mistakes", "show my progress", "English learning stats", "what errors do I make".
---

# English Learning Assistant

This skill helps users track and improve their English writing through the English Buddy plugin.

## When to Use

Activate this skill when the user:
- Asks about their English learning progress
- Wants to see grammar correction statistics
- Mentions grammar mistakes or errors
- Asks for improvement suggestions
- Wants to review what they've learned

## Available Commands

Suggest these commands based on what the user needs:

### `/english-buddy:summary`
**Best for:** Quick check of today's activity
- Shows today's correction count
- Lists errors by category
- Displays most common mistakes today

### `/english-buddy:week`
**Best for:** Weekly progress review
- Shows week's total corrections
- Compares with last week
- Provides personalized improvement tips

### `/english-buddy:stats`
**Best for:** Detailed analytics
- All-time statistics
- Visual charts (error distribution, trends)
- Most frequent errors over 30 days
- Overall improvement score

## Data Locations

- **Statistics database:** `~/.english-buddy/data.sqlite`
- **Daily logs:** `~/obsidian/learning/english/YYYY-MM-DD.md`

## How It Works

The English Buddy plugin automatically:
1. Checks English text when you send messages
2. Uses Claude Haiku to identify grammar errors
3. Saves corrections to both SQLite and Obsidian
4. Sends macOS notifications for immediate feedback

## Example Responses

When user asks "How's my English learning going?":
> Let me check your English learning progress. You can run `/english-buddy:summary` for today's stats or `/english-buddy:week` for weekly progress.

When user asks "What grammar mistakes do I make most?":
> Run `/english-buddy:stats` to see your most common errors and overall improvement trends.
