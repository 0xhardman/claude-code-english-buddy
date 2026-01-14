#!/usr/bin/env python3
"""
Statistics Script for English Buddy.
Shows detailed statistics with ASCII charts.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from db import get_daily_stats, get_weekly_stats, get_all_time_stats, get_top_errors
from charts import ascii_bar_chart, ascii_trend_chart, summary_box


def get_last_n_days(n: int = 7) -> list:
    """Get stats for last N days."""
    from db import get_connection, init_db

    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    start_date = (datetime.now() - timedelta(days=n-1)).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT date, total_corrections
        FROM daily_stats
        WHERE date >= ?
        ORDER BY date
    """, (start_date,))

    data = [(row['date'][-5:], row['total_corrections']) for row in cursor.fetchall()]
    conn.close()

    return data


def main():
    """Generate and print statistics with charts."""
    # Get all-time stats
    all_time = get_all_time_stats()
    current_week = get_weekly_stats(weeks_back=0)
    top_errors = get_top_errors(limit=5, days=30)
    trend_data = get_last_n_days(7)

    # Header
    print("\n📊 English Learning Statistics")
    print("━" * 40)

    # All-time summary
    if all_time['total_corrections'] == 0:
        print("\n✨ No data yet! Start writing in English to track your progress.")
        return

    print(f"\n📈 All-Time Summary ({all_time['total_days']} days tracked)")
    print(f"   Total corrections: {all_time['total_corrections']}")

    # Error distribution chart
    print("\n")
    error_data = {
        "Spelling": all_time['spelling_count'],
        "Grammar": all_time['grammar_count'],
        "Style": all_time['style_count'],
        "Vocabulary": all_time['vocabulary_count']
    }
    print(ascii_bar_chart(error_data, "Error Distribution"))

    # Weekly trend chart
    if trend_data:
        print("\n")
        print(ascii_trend_chart(trend_data, "Last 7 Days Trend"))

    # This week's stats
    print("\n")
    week_items = [
        f"Total: {current_week['total_corrections']} corrections",
        f"Spelling: {current_week['spelling_count']}",
        f"Grammar: {current_week['grammar_count']}",
        f"Style: {current_week['style_count']}",
        f"Vocabulary: {current_week['vocabulary_count']}"
    ]
    print(summary_box("This Week", week_items))

    # Top errors (last 30 days)
    if top_errors:
        print("\n📝 Most Common Errors (Last 30 Days)")
        print("━" * 35)
        for i, err in enumerate(top_errors, 1):
            print(f"  {i}. \"{err['original']}\" → \"{err['correction']}\"")
            print(f"     Category: {err['category']}, Count: {err['count']}")

    # Progress indicator
    print("\n")
    avg_daily = all_time['total_corrections'] / max(all_time['total_days'], 1)
    if avg_daily > 0:
        # Lower is better for errors
        goal = 3  # Target: less than 3 errors per day on average
        progress = max(0, min(100, (1 - (avg_daily / 10)) * 100))
        filled = int(progress / 5)
        empty = 20 - filled
        print(f"Improvement Score: [{'█' * filled}{'░' * empty}] {progress:.0f}%")
        print(f"(Based on {avg_daily:.1f} avg daily errors)")

    # Footer
    print("\n" + "━" * 40)
    print("📁 Data: ~/.english-buddy/data.sqlite")
    print("📝 Logs: ~/obsidian/learning/english/")


if __name__ == "__main__":
    main()
