#!/usr/bin/env python3
"""
Daily Summary Script for English Buddy.
Shows today's grammar corrections summary.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from db import get_daily_stats, get_daily_corrections, get_top_errors


def main():
    """Generate and print daily summary."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Get today's stats
    stats = get_daily_stats(today)
    corrections = get_daily_corrections(today)
    top_errors = get_top_errors(limit=5, days=1)

    # Header
    print(f"\n📊 Daily Summary - {today}")
    print("━" * 35)

    # Stats overview
    total = stats["total_corrections"]
    if total == 0:
        print("\n✨ No corrections today! Keep practicing!")
        print("\nTip: The more you write in English, the more you'll learn.")
        return

    print(f"\nTotal corrections: {total}")
    print(f"  • Spelling:   {stats['spelling_count']}")
    print(f"  • Grammar:    {stats['grammar_count']}")
    print(f"  • Style:      {stats['style_count']}")
    print(f"  • Vocabulary: {stats['vocabulary_count']}")

    # Top errors
    if top_errors:
        print("\n📝 Most common mistakes today:")
        for i, err in enumerate(top_errors, 1):
            print(f"  {i}. \"{err['original']}\" → \"{err['correction']}\" ({err['count']}x)")

    # Recent corrections
    if corrections:
        print("\n📋 Recent corrections:")
        for corr in corrections[:3]:
            time = corr['timestamp'].split('T')[1][:5] if 'T' in corr['timestamp'] else corr['timestamp'][-5:]
            user_text = corr['user_text'] or corr['original_text']
            if len(user_text) > 50:
                user_text = user_text[:47] + "..."
            print(f"  [{time}] {user_text}")
            for err in corr.get('errors', [])[:2]:
                print(f"         → {err['original']} → {err['correction']}")

    # Footer
    print("\n" + "━" * 35)
    print("📁 Full log: ~/obsidian/learning/english/")


if __name__ == "__main__":
    main()
