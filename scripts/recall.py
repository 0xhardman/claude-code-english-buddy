#!/usr/bin/env python3
"""
Recall Script for English Buddy.
Retries failed grammar checks from the retry queue.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from language_detect import should_check_grammar
from claude_api import analyze_grammar
from obsidian import save_correction as save_to_obsidian
from db import save_correction as save_to_db

# Retry queue file path
RETRY_QUEUE_PATH = Path.home() / ".english-buddy" / "retry_queue.json"


def send_notification(title: str, message: str):
    """Send macOS system notification using terminal-notifier."""
    try:
        # Get today's Obsidian file path for click action
        date_str = datetime.now().strftime("%Y-%m-%d")
        obsidian_file = Path.home() / "obsidian" / "learning" / "english" / f"{date_str}.md"

        subprocess.run(
            [
                '/opt/homebrew/bin/terminal-notifier',
                '-title', title,
                '-message', message,
                '-group', 'english-buddy-recall',
                '-sender', 'com.apple.Terminal',
                '-execute', f"open '{obsidian_file}'"
            ],
            capture_output=True,
            timeout=5
        )
    except FileNotFoundError:
        # terminal-notifier not installed, try osascript
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message}" with title "{title}"'
            ], capture_output=True, timeout=5)
        except Exception:
            pass
    except Exception as e:
        print(f"Notification error: {e}", file=sys.stderr)


def load_retry_queue() -> list:
    """Load the retry queue from file."""
    if not RETRY_QUEUE_PATH.exists():
        return []
    try:
        with open(RETRY_QUEUE_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_retry_queue(queue: list):
    """Save the retry queue to file."""
    RETRY_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RETRY_QUEUE_PATH, 'w') as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def process_analysis(user_prompt: str, analysis: dict) -> bool:
    """Process a successful analysis result. Returns True if there were findings."""
    # Skip if marked as technical content
    if analysis.get('skipped'):
        return False

    # Save to Obsidian and SQLite if there are findings
    if analysis.get('has_errors') or analysis.get('better_expression'):
        # Save to Obsidian (markdown)
        save_to_obsidian(user_prompt, analysis)

        # Save to SQLite (for statistics)
        errors = analysis.get('errors', [])
        save_to_db(
            original_text=user_prompt,
            user_text=analysis.get('user_text', user_prompt),
            errors=errors,
            better_expression=analysis.get('better_expression'),
            summary=analysis.get('summary')
        )
        return True
    return False


def main():
    """Main entry point for recall script."""
    queue = load_retry_queue()

    if not queue:
        send_notification("English Buddy Recall", "No failed checks to retry")
        print("No failed checks in retry queue.")
        return

    print(f"Found {len(queue)} failed check(s) to retry...")

    success_count = 0
    still_failed = []
    findings_count = 0

    for item in queue:
        user_prompt = item.get('prompt', '')
        if not user_prompt:
            continue

        print(f"Retrying: {user_prompt[:50]}...")

        # Skip if we shouldn't check this text
        if not should_check_grammar(user_prompt):
            print("  Skipped (not suitable for grammar check)")
            success_count += 1
            continue

        # Try API call (1 retry = 2 total attempts)
        analysis = None
        for attempt in range(2):
            analysis = analyze_grammar(user_prompt)
            if analysis is not None:
                break
            if attempt == 0:
                print("  First attempt failed, retrying in 2 seconds...")
                time.sleep(2)

        if analysis is None:
            print("  Still failed after retry")
            still_failed.append(item)
            continue

        # Process successful analysis
        had_findings = process_analysis(user_prompt, analysis)
        success_count += 1
        if had_findings:
            findings_count += 1
            print("  Success (found issues)")
        else:
            print("  Success (no issues)")

    # Update the queue with only still-failed items
    save_retry_queue(still_failed)

    # Send notification with results
    if still_failed:
        msg = f"Retried {len(queue)}: {success_count} OK, {len(still_failed)} still failed"
    else:
        msg = f"All {success_count} check(s) completed successfully"
        if findings_count > 0:
            msg += f" ({findings_count} with findings)"

    send_notification("English Buddy Recall", msg)
    print(f"\nDone: {msg}")


if __name__ == '__main__':
    main()
