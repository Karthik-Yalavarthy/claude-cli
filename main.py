"""
Streaming CLI: ask Claude a question, stream the answer to stdout.
Usage: uv run python main.py "your question here"
"""
import os
import sys
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def stream_answer(question: str) -> None:
    """Stream Claude's answer to the given question to stdout."""
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": question}
        ],
    ) as stream:
        for text_chunk in stream.text_stream:
            print(text_chunk, end="", flush=True)
    print()  # final newline after stream ends


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your question\"", file=sys.stderr)
        sys.exit(1)
    
    question = sys.argv[1]
    stream_answer(question)


if __name__ == "__main__":
    main()