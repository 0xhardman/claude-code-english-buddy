"""
Language detection utilities for English Buddy.
Detects English vs Chinese text to filter messages.
"""

import re


def contains_english(text: str) -> bool:
    """Check if text contains English letters (at least 2 consecutive letters)."""
    english_pattern = re.compile(r'[a-zA-Z]{2,}')
    return bool(english_pattern.search(text))


def is_pure_chinese(text: str) -> bool:
    """Check if text is pure Chinese (no English words)."""
    # Remove punctuation, numbers, whitespace
    cleaned = re.sub(r'[\s\d\W]+', '', text)
    if not cleaned:
        return True
    # Check if all remaining chars are CJK
    for char in cleaned:
        if '\u4e00' <= char <= '\u9fff':  # CJK Unified Ideographs
            continue
        elif 'a' <= char.lower() <= 'z':
            return False
    return True


def is_primarily_chinese(text: str) -> bool:
    """
    Check if text is primarily Chinese (>30% Chinese characters).
    Used to skip mixed Chinese/English where Chinese is the main language.
    """
    chinese_count = 0
    english_count = 0

    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # CJK Unified Ideographs
            chinese_count += 1
        elif 'a' <= char.lower() <= 'z':
            english_count += 1

    # If no letters at all, skip
    if chinese_count + english_count == 0:
        return True

    # Skip if Chinese characters are more than 30% of all letters
    return chinese_count > (chinese_count + english_count) * 0.3


def should_check_grammar(text: str) -> bool:
    """
    Determine if text should be checked for grammar.

    Returns False if:
    - Text is empty
    - Text starts with / (slash command)
    - Text is pure Chinese
    - Text is primarily Chinese (>30% Chinese)
    - Text has no English content
    - Text is too short (< 3 words)
    """
    if not text or not text.strip():
        return False

    # Skip slash commands (e.g., /english-buddy:stats)
    if text.strip().startswith('/'):
        return False

    if is_pure_chinese(text):
        return False

    if is_primarily_chinese(text):
        return False

    if not contains_english(text):
        return False

    # Skip very short messages
    words = text.split()
    if len(words) < 3:
        return False

    return True


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("Hello world today", True),  # 3 words, should check
        ("Hello world", False),  # Too short (< 3 words)
        ("你好世界", False),
        ("I want to improve my English", True),
        ("我想学习 Python", False),  # Primarily Chinese
        ("Hi", False),  # Too short
        ("npm install package", True),  # 3 words
        ("这是一个测试", False),
        ("/english-buddy:stats", False),  # Slash command
        ("/commit", False),  # Slash command
    ]

    for text, expected in test_cases:
        result = should_check_grammar(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> {result} (expected {expected})")
