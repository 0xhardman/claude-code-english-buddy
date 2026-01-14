#!/usr/bin/env python3
"""
Weekly Summary Script for English Buddy.
Shows weekly grammar progress and trends.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from db import get_weekly_stats, get_top_errors


def main():
    """Generate and print weekly summary."""
    # Get current week stats
    current_week = get_weekly_stats(weeks_back=0)
    last_week = get_weekly_stats(weeks_back=1)
    top_errors = get_top_errors(limit=5, days=7)

    # Header
    print(f"\n📊 Weekly Summary")
    print(f"   {current_week['week_start']} to {current_week['week_end']}")
    print("━" * 40)

    # Stats overview
    total = current_week["total_corrections"]
    if total == 0:
        print("\n✨ No corrections this week!")
        print("Keep writing in English to track your progress.")
        return

    print(f"\nThis week: {total} corrections")
    print(f"  • Spelling:   {current_week['spelling_count']}")
    print(f"  • Grammar:    {current_week['grammar_count']}")
    print(f"  • Style:      {current_week['style_count']}")
    print(f"  • Vocabulary: {current_week['vocabulary_count']}")

    # Week-over-week comparison
    last_total = last_week["total_corrections"]
    if last_total > 0:
        print(f"\n📈 Week-over-Week Comparison:")
        print(f"   Last week: {last_total} corrections")

        diff = total - last_total
        if diff < 0:
            print(f"   Change: {diff} fewer errors! 🎉")
        elif diff > 0:
            print(f"   Change: +{diff} more errors (more practice!)")
        else:
            print(f"   Change: Same as last week")

        # Category comparison
        for cat in ['spelling', 'grammar', 'style', 'vocabulary']:
            curr = current_week[f'{cat}_count']
            prev = last_week[f'{cat}_count']
            if prev > 0:
                change = ((curr - prev) / prev) * 100
                if abs(change) > 20:
                    arrow = "↓" if change < 0 else "↑"
                    print(f"   {cat.capitalize()}: {arrow} {abs(change):.0f}%")

    # Top errors this week
    if top_errors:
        print("\n📝 Top mistakes this week:")
        for i, err in enumerate(top_errors, 1):
            print(f"  {i}. \"{err['original']}\" → \"{err['correction']}\"")
            print(f"     [{err['category']}] occurred {err['count']} times")

    # Recommendations
    print("\n💡 Focus areas:")
    max_cat = max(
        [('spelling', current_week['spelling_count']),
         ('grammar', current_week['grammar_count']),
         ('style', current_week['style_count']),
         ('vocabulary', current_week['vocabulary_count'])],
        key=lambda x: x[1]
    )
    if max_cat[1] > 0:
        tips = {
            'spelling': "Try typing more slowly and proofreading before sending.",
            'grammar': "Review basic grammar rules: articles, tenses, subject-verb agreement.",
            'style': "Read more native English content to absorb natural expressions.",
            'vocabulary': "Keep a vocabulary journal for commonly confused words."
        }
        print(f"  Your main challenge: {max_cat[0].capitalize()}")
        print(f"  Tip: {tips[max_cat[0]]}")

    # Footer
    print("\n" + "━" * 40)
    print("Run /english-buddy:stats for detailed charts")


if __name__ == "__main__":
    main()
