"""
Hello-world script: confirm we can call Claude via the Anthropic SDK.
This is the smoke test before we add streaming and tools.
"""
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load ANTHROPIC_API_KEY from .env into the environment
load_dotenv()

# The SDK auto-reads ANTHROPIC_API_KEY from the env, but being explicit is clearer
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Say hello in exactly one short sentence."}
    ],
)

# response.content is a list of content blocks. For a simple text response,
# there's one block of type "text" with the text in .text
print(response.content[0].text)