"""
Obsidian file operations for English Buddy.
Saves grammar corrections to daily markdown files.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional


# Default Obsidian path
OBSIDIAN_PATH = Path.home() / "obsidian" / "learning" / "english"


def get_obsidian_path() -> Path:
    """Get the Obsidian path, creating if needed."""
    OBSIDIAN_PATH.mkdir(parents=True, exist_ok=True)
    return OBSIDIAN_PATH


def get_daily_file_path(target_date: Optional[str] = None) -> Path:
    """Get path to daily markdown file."""
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")
    return get_obsidian_path() / f"{target_date}.md"


def save_correction(
    user_message: str,
    analysis: dict,
    target_date: Optional[str] = None
):
    """
    Append correction record to Obsidian daily file.

    Args:
        user_message: Original user message
        analysis: Analysis dict from Claude API
        target_date: Optional date string (YYYY-MM-DD), defaults to today
    """
    file_path = get_daily_file_path(target_date)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Use extracted user_text if available
    display_text = analysis.get('user_text') or user_message

    lines = []
    lines.append(f"\n## {timestamp}\n")
    lines.append(f"**Original:** {display_text}\n")

    if analysis.get('has_errors') and analysis.get('errors'):
        lines.append("\n**Errors:**")
        for err in analysis['errors']:
            category = err.get('category', 'grammar')
            lines.append(f"- \"{err['original']}\" → \"{err['correction']}\" ({err.get('explanation', '')} [{category}])")
        lines.append("")

    if analysis.get('better_expression'):
        lines.append(f"\n**Better:** {analysis['better_expression']}\n")

    if analysis.get('summary'):
        lines.append(f"\n> {analysis['summary']}\n")

    lines.append("\n---")

    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return True
    except Exception as e:
        print(f"Failed to save to Obsidian: {e}", file=__import__('sys').stderr)
        return False


def read_daily_file(target_date: Optional[str] = None) -> str:
    """Read the daily markdown file content."""
    file_path = get_daily_file_path(target_date)
    if file_path.exists():
        return file_path.read_text(encoding='utf-8')
    return ""


if __name__ == "__main__":
    # Test
    print(f"Obsidian path: {get_obsidian_path()}")
    print(f"Today's file: {get_daily_file_path()}")
    print(f"Content preview: {read_daily_file()[:200]}...")
