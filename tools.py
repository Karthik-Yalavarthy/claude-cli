"""
Tool implementations and schemas for the research-assistant CLI.

Each tool has two parts:
1. A Python function that does the actual work.
2. A schema dict that tells Claude the tool exists and how to call it.
"""
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Sandbox directory for notes. All file ops are scoped to this folder.
NOTES_DIR = Path("notes")


# =============================================================================
# Tool implementations
# =============================================================================

def fetch_url(url: str) -> str:
    """Fetch a URL and return the cleaned text content of the page."""
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "claude-cli/0.1 (learning project)"},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching URL: {e}"

    # Strip HTML down to readable text. Not perfect, but good enough for a CLI.
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)

    # Truncate to keep token usage sane. 8000 chars ≈ 2000 tokens.
    if len(text) > 8000:
        text = text[:8000] + "\n\n[...truncated]"

    return text


def read_local_file(filename: str) -> str:
    """Read a file from the notes/ sandbox. Filename only — no paths."""
    # Reject anything that tries to escape the sandbox
    if "/" in filename or "\\" in filename or ".." in filename:
        return f"Error: filename must not contain path separators or '..'"

    path = NOTES_DIR / filename
    if not path.exists():
        return f"Error: file not found: {filename}"

    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        return f"Error reading file: {e}"


def save_note(filename: str, content: str) -> str:
    """Save content as a markdown file in the notes/ sandbox."""
    if "/" in filename or "\\" in filename or ".." in filename:
        return f"Error: filename must not contain path separators or '..'"

    NOTES_DIR.mkdir(exist_ok=True)
    path = NOTES_DIR / filename

    try:
        path.write_text(content, encoding="utf-8")
        return f"Saved {len(content)} characters to notes/{filename}"
    except OSError as e:
        return f"Error writing file: {e}"


# =============================================================================
# Tool schemas — what we tell Claude about these tools
# =============================================================================

TOOL_SCHEMAS = [
    {
        "name": "fetch_url",
        "description": (
            "Fetch a webpage and return its cleaned text content. "
            "Use this when the user asks you to read, summarize, or analyze a URL."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to fetch, including https://",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "read_local_file",
        "description": (
            "Read a file the user has previously saved in the notes folder. "
            "Use this to recall earlier notes or saved content."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Filename only, no path. Example: 'my-summary.md'",
                }
            },
            "required": ["filename"],
        },
    },
    {
        "name": "save_note",
        "description": (
            "Save text content as a markdown note in the notes folder. "
            "Use this when the user asks you to save, store, or write down information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Filename for the note. Example: 'summary.md'. No path.",
                },
                "content": {
                    "type": "string",
                    "description": "The full content to save in the file.",
                },
            },
            "required": ["filename", "content"],
        },
    },
]


# Map tool names to their Python implementations. The agent uses this to
# dispatch tool calls from Claude to the right function.
TOOL_REGISTRY = {
    "fetch_url": fetch_url,
    "read_local_file": read_local_file,
    "save_note": save_note,
}