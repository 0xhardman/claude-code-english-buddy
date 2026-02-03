"""
SQLite database module for English Buddy.
Stores grammar corrections and statistics.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, date
from pathlib import Path
from typing import Optional

from config import get_data_dir


def get_db_path() -> Path:
    """Get the database file path from config."""
    return get_data_dir() / "data.sqlite"


@contextmanager
def get_db_connection():
    """
    Context manager for safe database connection handling.

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # ... operations ...
            conn.commit()
    """
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_connection() -> sqlite3.Connection:
    """Get database connection, creating DB if needed. (Legacy function)"""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Corrections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                original_text TEXT,
                user_text TEXT,
                better_expression TEXT,
                summary TEXT
            )
        """)

        # Errors table (linked to corrections)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                correction_id INTEGER NOT NULL,
                original TEXT,
                correction TEXT,
                explanation TEXT,
                category TEXT,
                FOREIGN KEY (correction_id) REFERENCES corrections(id)
            )
        """)

        # Daily stats (aggregated)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_corrections INTEGER DEFAULT 0,
                spelling_count INTEGER DEFAULT 0,
                grammar_count INTEGER DEFAULT 0,
                style_count INTEGER DEFAULT 0,
                vocabulary_count INTEGER DEFAULT 0
            )
        """)

        conn.commit()


def save_correction(
    original_text: str,
    user_text: str,
    errors: list,
    better_expression: Optional[str],
    summary: Optional[str]
) -> int:
    """
    Save a correction to the database.

    Args:
        original_text: Full original message
        user_text: Extracted user text
        errors: List of error dicts with keys: original, correction, explanation, category
        better_expression: Suggested better expression
        summary: Chinese summary

    Returns:
        correction_id
    """
    init_db()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        # Insert correction
        cursor.execute("""
            INSERT INTO corrections (timestamp, original_text, user_text, better_expression, summary)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, original_text, user_text, better_expression, summary))

        correction_id = cursor.lastrowid

        # Insert errors
        category_counts = {"spelling": 0, "grammar": 0, "style": 0, "vocabulary": 0}
        for error in errors:
            category = error.get("category", "grammar").lower()
            if category not in category_counts:
                category = "grammar"
            category_counts[category] += 1

            cursor.execute("""
                INSERT INTO errors (correction_id, original, correction, explanation, category)
                VALUES (?, ?, ?, ?, ?)
            """, (
                correction_id,
                error.get("original", ""),
                error.get("correction", ""),
                error.get("explanation", ""),
                category
            ))

        # Update daily stats
        today = date.today().isoformat()
        cursor.execute("""
            INSERT INTO daily_stats (date, total_corrections, spelling_count, grammar_count, style_count, vocabulary_count)
            VALUES (?, 1, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                total_corrections = total_corrections + 1,
                spelling_count = spelling_count + ?,
                grammar_count = grammar_count + ?,
                style_count = style_count + ?,
                vocabulary_count = vocabulary_count + ?
        """, (
            today,
            category_counts["spelling"],
            category_counts["grammar"],
            category_counts["style"],
            category_counts["vocabulary"],
            category_counts["spelling"],
            category_counts["grammar"],
            category_counts["style"],
            category_counts["vocabulary"]
        ))

        conn.commit()

    return correction_id


def get_daily_stats(target_date: Optional[str] = None) -> dict:
    """Get statistics for a specific date (default: today)."""
    init_db()
    if target_date is None:
        target_date = date.today().isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM daily_stats WHERE date = ?
        """, (target_date,))

        row = cursor.fetchone()

    if row:
        return dict(row)
    return {
        "date": target_date,
        "total_corrections": 0,
        "spelling_count": 0,
        "grammar_count": 0,
        "style_count": 0,
        "vocabulary_count": 0
    }


def get_daily_corrections(target_date: Optional[str] = None) -> list:
    """Get all corrections for a specific date with their errors."""
    init_db()
    if target_date is None:
        target_date = date.today().isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get corrections for the date
        cursor.execute("""
            SELECT * FROM corrections
            WHERE date(timestamp) = ?
            ORDER BY timestamp DESC
        """, (target_date,))

        corrections = []
        for row in cursor.fetchall():
            correction = dict(row)

            # Get errors for this correction
            cursor.execute("""
                SELECT * FROM errors WHERE correction_id = ?
            """, (correction["id"],))
            correction["errors"] = [dict(e) for e in cursor.fetchall()]
            corrections.append(correction)

    return corrections


def get_weekly_stats(weeks_back: int = 0) -> dict:
    """Get statistics for a specific week."""
    init_db()
    from datetime import timedelta

    # Calculate week start (Monday) and end (Sunday)
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday() + 7 * weeks_back)
    end_of_week = start_of_week + timedelta(days=6)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_corrections,
                SUM(spelling_count) as spelling_count,
                SUM(grammar_count) as grammar_count,
                SUM(style_count) as style_count,
                SUM(vocabulary_count) as vocabulary_count
            FROM daily_stats
            WHERE date BETWEEN ? AND ?
        """, (start_of_week.isoformat(), end_of_week.isoformat()))

        row = cursor.fetchone()

    return {
        "week_start": start_of_week.isoformat(),
        "week_end": end_of_week.isoformat(),
        "total_corrections": row["total_corrections"] or 0,
        "spelling_count": row["spelling_count"] or 0,
        "grammar_count": row["grammar_count"] or 0,
        "style_count": row["style_count"] or 0,
        "vocabulary_count": row["vocabulary_count"] or 0
    }


def get_top_errors(limit: int = 5, days: int = 7) -> list:
    """Get most common errors in the last N days."""
    init_db()
    from datetime import timedelta

    start_date = (date.today() - timedelta(days=days)).isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT original, correction, category, COUNT(*) as count
            FROM errors e
            JOIN corrections c ON e.correction_id = c.id
            WHERE date(c.timestamp) >= ?
            GROUP BY original, correction
            ORDER BY count DESC
            LIMIT ?
        """, (start_date, limit))

        errors = [dict(row) for row in cursor.fetchall()]

    return errors


def get_all_time_stats() -> dict:
    """Get all-time statistics."""
    init_db()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_days,
                SUM(total_corrections) as total_corrections,
                SUM(spelling_count) as spelling_count,
                SUM(grammar_count) as grammar_count,
                SUM(style_count) as style_count,
                SUM(vocabulary_count) as vocabulary_count
            FROM daily_stats
        """)

        row = cursor.fetchone()

    return {
        "total_days": row["total_days"] or 0,
        "total_corrections": row["total_corrections"] or 0,
        "spelling_count": row["spelling_count"] or 0,
        "grammar_count": row["grammar_count"] or 0,
        "style_count": row["style_count"] or 0,
        "vocabulary_count": row["vocabulary_count"] or 0
    }


if __name__ == "__main__":
    # Test the database
    init_db()
    print(f"Database initialized at: {get_db_path()}")
    print(f"Today's stats: {get_daily_stats()}")
