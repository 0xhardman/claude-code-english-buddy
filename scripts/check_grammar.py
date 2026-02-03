#!/usr/bin/env python3
"""
Grammar Checker Script for English Buddy.
Called by UserPromptSubmit hook to check English grammar.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from config import get_data_dir, get_obsidian_dir, get_retry_queue_max, is_notification_enabled


def get_retry_queue_path() -> Path:
    """Get the retry queue file path from config."""
    return get_data_dir() / "retry_queue.json"


def get_last_check_path() -> Path:
    """Get the last check file path from config."""
    return get_data_dir() / "last_check.json"


def save_last_check(user_prompt: str, analysis: dict, notification_message: str):
    """Save the last successful check for recall."""
    last_check_path = get_last_check_path()
    last_check_path.parent.mkdir(parents=True, exist_ok=True)
    with open(last_check_path, 'w') as f:
        json.dump({
            "prompt": user_prompt,
            "analysis": analysis,
            "notification": notification_message,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)


def save_to_retry_queue(user_prompt: str, reason: str):
    """Save a failed message to retry queue for later recall using atomic writes."""
    queue_path = get_retry_queue_path()
    queue_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing queue
    queue = []
    if queue_path.exists():
        try:
            with open(queue_path, 'r') as f:
                queue = json.load(f)
        except (json.JSONDecodeError, IOError):
            queue = []

    # Add new item
    queue.append({
        "prompt": user_prompt,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    })

    # Keep only last N items (from config) to prevent unbounded growth
    max_items = get_retry_queue_max()
    queue = queue[-max_items:]

    # Atomic write: write to temp file first, then rename
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            dir=queue_path.parent,
            delete=False,
            suffix='.tmp'
        ) as tmp:
            json.dump(queue, tmp, indent=2, ensure_ascii=False)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.rename(tmp.name, queue_path)
    except Exception:
        # Fallback to direct write if atomic write fails
        with open(queue_path, 'w') as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)

from language_detect import should_check_grammar
from claude_api import analyze_grammar
from obsidian import save_correction as save_to_obsidian
from db import save_correction as save_to_db


def send_notification(title: str, message: str):
    """Send macOS system notification using terminal-notifier."""
    # Check if notifications are enabled in config
    if not is_notification_enabled():
        return

    # Find terminal-notifier in PATH
    terminal_notifier = shutil.which('terminal-notifier')

    if terminal_notifier:
        try:
            # Get today's Obsidian file path for click action
            date_str = datetime.now().strftime("%Y-%m-%d")
            obsidian_file = get_obsidian_dir() / f"{date_str}.md"

            subprocess.run(
                [
                    terminal_notifier,
                    '-title', title,
                    '-message', message,
                    '-group', 'english-buddy',
                    '-sender', 'com.apple.Terminal',
                    '-execute', f"open '{obsidian_file}'"
                ],
                capture_output=True,
                timeout=5
            )
            return
        except Exception as e:
            print(f"Notification error: {e}", file=sys.stderr)

    # Fallback to osascript
    try:
        subprocess.run([
            'osascript', '-e',
            f'display notification "{message}" with title "{title}"'
        ], capture_output=True, timeout=5)
    except Exception:
        pass


def main():
    """Main entry point for UserPromptSubmit hook."""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        user_prompt = input_data.get('prompt', '') or input_data.get('user_prompt', '')
        transcript_path = input_data.get('transcript_path')

        # Check if we should analyze this text
        if not should_check_grammar(user_prompt):
            print(json.dumps({}), file=sys.stdout)
            sys.exit(0)

        # Call Claude API for analysis (with conversation context)
        analysis = analyze_grammar(user_prompt, transcript_path=transcript_path)

        if analysis is None:
            # API call failed, save to retry queue
            save_to_retry_queue(user_prompt, "API call failed")
            print(json.dumps({}), file=sys.stdout)
            sys.exit(0)

        if analysis:
            # Skip if marked as technical content
            if analysis.get('skipped'):
                print(json.dumps({}), file=sys.stdout)
                sys.exit(0)

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

                # Build notification message
                notif_parts = []
                if errors:
                    for err in errors[:2]:  # Max 2 errors in notification
                        notif_parts.append(f"「{err['original']}」→「{err['correction']}」")
                if analysis.get('better_expression') and not notif_parts:
                    better = analysis['better_expression']
                    if len(better) > 50:
                        better = better[:47] + "..."
                    notif_parts.append(f"Better: {better}")

                if notif_parts:
                    notif_message = " | ".join(notif_parts)
                    send_notification("English Buddy", notif_message)
                    save_last_check(user_prompt, analysis, notif_message)

        # Output empty JSON to stdout (hook response)
        print(json.dumps({}), file=sys.stdout)

    except Exception as e:
        # Log error but don't block the conversation
        print(f"Grammar check error: {e}", file=sys.stderr)
        # Save to retry queue if we have user_prompt
        try:
            if user_prompt:
                save_to_retry_queue(user_prompt, str(e))
        except NameError:
            pass
        print(json.dumps({}), file=sys.stdout)

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
