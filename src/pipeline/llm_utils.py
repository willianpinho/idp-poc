"""Utilities for parsing LLM responses."""

import json
import re


def parse_json_response(raw: str) -> dict:
    """Parse a JSON response from an LLM, handling markdown code blocks.

    Claude often wraps JSON in ```json ... ``` blocks. This function
    strips those wrappers and parses the JSON content.
    """
    text = raw.strip()

    # Remove markdown code block wrappers
    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    return json.loads(text)
