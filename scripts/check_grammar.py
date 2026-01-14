#!/usr/bin/env python3
"""
Grammar Checker Script for English Buddy.
Called by UserPromptSubmit hook to check English grammar.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from language_detect import should_check_grammar
from claude_api import analyze_grammar
from obsidian import save_correction as save_to_obsidian
from db import save_correction as save_to_db


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
                '-group', 'english-buddy',
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


def main():
    """Main entry point for UserPromptSubmit hook."""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        user_prompt = input_data.get('prompt', '') or input_data.get('user_prompt', '')

        # Check if we should analyze this text
        if not should_check_grammar(user_prompt):
            print(json.dumps({}), file=sys.stdout)
            sys.exit(0)

        # Call Claude API for analysis
        analysis = analyze_grammar(user_prompt)

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
                    send_notification("English Buddy", " | ".join(notif_parts))

        # Output empty JSON to stdout (hook response)
        print(json.dumps({}), file=sys.stdout)

    except Exception as e:
        # Log error but don't block the conversation
        print(f"Grammar check error: {e}", file=sys.stderr)
        print(json.dumps({}), file=sys.stdout)

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
