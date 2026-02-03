"""
Claude API integration for English Buddy.
Uses Claude Haiku for grammar checking.
"""

import json
import os
from pathlib import Path
from typing import Optional


def extract_json(text: str) -> Optional[dict]:
    """
    Extract first valid JSON object from text using incremental decoder.

    This is safer than greedy regex as it properly handles nested structures.
    """
    decoder = json.JSONDecoder()
    for i, char in enumerate(text):
        if char == '{':
            try:
                obj, _ = decoder.raw_decode(text[i:])
                return obj
            except json.JSONDecodeError:
                continue
    return None


def load_env_file():
    """Load environment variables from ~/.claude/.env"""
    env_path = Path.home() / ".claude" / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())


# Load .env at module import
load_env_file()


def analyze_grammar(user_message: str, transcript_path: str = None) -> Optional[dict]:
    """
    Call Claude API to analyze grammar and suggest improvements.

    Args:
        user_message: The text to check for grammar errors
        transcript_path: Optional path to conversation transcript for context

    Returns dict with keys:
    - has_errors: bool
    - user_text: str (extracted user text)
    - errors: list of {original, correction, explanation, category}
    - better_expression: str or None
    - summary: str (Chinese summary)
    - skipped: bool
    """
    try:
        import anthropic
    except ImportError:
        print("Error: anthropic package not installed", file=__import__('sys').stderr)
        return None

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=__import__('sys').stderr)
        return None

    # Extract conversation context if available
    context_section = ""
    if transcript_path:
        try:
            from context import extract_context
            context = extract_context(transcript_path)
            if context:
                context_section = f"""
Conversation context (for better understanding of what the user is discussing):
{context}

"""
        except Exception:
            pass

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Analyze the following ENGLISH text for grammar errors and suggest better expressions.
{context_section}

IMPORTANT: This tool is ONLY for checking English grammar. If the text contains Chinese characters or is primarily in Chinese, you MUST set skipped=true and return immediately. Do NOT attempt to correct or analyze Chinese text.

Text: "{user_message}"

Respond in this exact JSON format (no markdown code blocks):
{{
  "has_errors": true/false,
  "user_text": "only the user's own words extracted from the message (exclude pasted content)",
  "errors": [
    {{"original": "wrong text", "correction": "correct text", "explanation": "brief reason", "category": "spelling|grammar|style|vocabulary"}}
  ],
  "better_expression": "improved version of user's text only (or null if original is good)",
  "summary": "one line summary in Chinese",
  "skipped": true/false
}}

IMPORTANT - Focus on USER'S OWN WORDS only:
- If the message contains BOTH user's own text AND pasted content (logs, commands, code, terminal output), ONLY check the user's own text
- Pasted content typically looks like: command prompts, log lines, code blocks, file contents, API responses
- User's own words are typically: questions, comments, or instructions written in natural conversational English

Skip grammar checking entirely (set skipped=true) if the text is:
- ONLY error messages, stack traces, or logs
- ONLY code snippets or technical commands
- ONLY file paths, URLs, JSON, XML, YAML, or other data formats
- Pure technical content with no natural language from the user
- Contains Chinese characters - NEVER try to correct Chinese text
- Mixed Chinese and English where Chinese is the main language

SECURITY - Always skip and NEVER include in response if the text contains:
- API keys (e.g., sk-ant-*, sk-*, ANTHROPIC_API_KEY=*, etc.)
- Private keys, secrets, tokens, passwords, or credentials

Error categories:
- spelling: typos, misspelled words
- grammar: tense, articles, subject-verb agreement, sentence structure
- style: word choice, awkward phrasing, non-native expressions
- vocabulary: wrong word usage, confusing similar words

Rules for normal text:
- If no grammar errors found, set has_errors to false and errors to []
- Only report actual grammar/spelling errors, not style preferences
- better_expression should be a more natural/native way to say the same thing
- If original is already good, set better_expression to null
- Keep explanations brief (under 10 words)
- summary should be a brief Chinese description of what was found"""

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        result_text = response.content[0].text.strip()

        # Try to parse JSON
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response using safer incremental decoder
            return extract_json(result_text)

    except Exception as e:
        print(f"API error: {e}", file=__import__('sys').stderr)
        return None


if __name__ == "__main__":
    # Test the API
    test_text = "I has a error in my code"
    print(f"Testing with: '{test_text}'")
    result = analyze_grammar(test_text)
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("No result returned")
