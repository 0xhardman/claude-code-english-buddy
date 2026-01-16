"""
Context extraction module for English Buddy.
Reads Claude Code transcript to provide conversation context.
"""

import json
from pathlib import Path
from typing import Optional


def extract_context(transcript_path: str) -> Optional[str]:
    """
    Extract conversation context from Claude Code transcript.

    Strategy:
    - Include first user message (original task/intent)
    - Include last 3 user messages (recent context)
    - Include last 1 assistant message (current discussion)

    Args:
        transcript_path: Path to the JSONL transcript file

    Returns:
        Formatted context string, or None if unavailable
    """
    if not transcript_path:
        return None

    path = Path(transcript_path)
    if not path.exists():
        return None

    try:
        user_messages = []
        assistant_messages = []

        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    msg_type = entry.get('type')
                    if msg_type == 'user' or msg_type == 'human':
                        content = _extract_text(entry.get('message', {}))
                        # Skip system messages, commands, and very short messages
                        if content and len(content) > 10 and not content.startswith('<'):
                            user_messages.append(_truncate(content, 200))
                    elif msg_type == 'assistant':
                        content = _extract_text(entry.get('message', {}))
                        if content and len(content) > 20:
                            assistant_messages.append(_truncate(content, 150))
                except json.JSONDecodeError:
                    continue

        if not user_messages:
            return None

        # Build context: first user message + recent user messages + last assistant
        context_lines = []

        # First user message (original task) - if we have more than 3 messages
        if len(user_messages) > 3:
            context_lines.append(f"- Original task: {user_messages[0]}")

        # Last 3 user messages (excluding current prompt which is last)
        recent_user = user_messages[-4:-1] if len(user_messages) > 1 else []
        for msg in recent_user:
            context_lines.append(f"- User: {msg}")

        # Last assistant message (current discussion context)
        if assistant_messages:
            context_lines.append(f"- Assistant: {assistant_messages[-1]}")

        return "\n".join(context_lines) if context_lines else None

    except Exception:
        return None


def _extract_text(message: dict) -> str:
    """Extract text content from a message object."""
    if isinstance(message, str):
        return message

    content = message.get('content', '')
    if isinstance(content, str):
        return content

    # Handle list of content blocks
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, str):
                texts.append(block)
            elif isinstance(block, dict):
                if block.get('type') == 'text':
                    texts.append(block.get('text', ''))
        return ' '.join(texts)

    return ''


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max length."""
    text = text.replace('\n', ' ').strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + '...'


if __name__ == "__main__":
    # Test with a sample transcript path
    import sys
    if len(sys.argv) > 1:
        context = extract_context(sys.argv[1])
        if context:
            print("Extracted context:")
            print(context)
        else:
            print("No context extracted")
    else:
        print("Usage: python3 context.py <transcript_path>")
