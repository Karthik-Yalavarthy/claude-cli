'''
THe agent loop: send a question to Claude, handle any tool calls. loop until Claude gives final text answer.

THis is the core pattern that power every agentic LLM application. Understand this loop and you understand 80% of how LLM agent work.
'''

import os
from anthropic import Anthropic
from dotenv import load_dotenv

from tools import TOOL_SCHEMAS, TOOL_REGISTRY

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# MODEL = "claude-sonnet-4-5"
MODEL = "claude-haiku-4-5"
MAX_TOKENS = 2048
MAX_ITERATIONS = 5

def run_agent(user_question: str) -> str:
    """
    Run the agent loop for a single user question.
    Returns the final text answer from Claude.
    """

    # The full conversion history. Start with just the user's questions
    # We append to this list as the conversation progress.

    messages = [
        {"role": "user", "content": user_question}
    ]

    for iteration in range(MAX_ITERATIONS):
        print(f'\n[iteration {iteration + 1}]')
        print(messages)

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            tools=TOOL_SCHEMAS,
            messages=messages
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return extract_text(response.content)
        
        if response.stop_reason == "tool_use":
            tool_results = execute_tool_calls(response.content)
            messages.append({"role": "user", "content": tool_results})
            continue

        return f"[Stopped unexpectedly: stop_reason={response.stop_reason}]\n" + extract_text(response.content)
    
    return "[Reached Max iterations without a final answer]"



def execute_tool_calls(content_block: list) -> list:

    results = []
    for block in content_block:
        if block.type != "tool_use":
            continue

        tool_name = block.name
        tool_input = block.input
        tool_use_id = block.id

        print(f' -> calling {tool_name}({tool_input})')

        if tool_name not in TOOL_REGISTRY:
            result = f'Error: Unknown tool " {tool_name}"'
        else:
            try:
                result = TOOL_REGISTRY[tool_name](**tool_input)
                
            except Exception as e:
                result = f"Error executing {tool_name}: {e}"
        
        preview = result[:120].replace("\n", " ")
        print(f" <- result: {preview}{'...' if len(result)> 120 else ''}")

        results.append({
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result,
        })
    print(f"\n{'%'*60}")
    print(results)
    print(f"\n{'%'*60}")
    return results
        

def extract_text(content_block: list) -> str:
    text_parts = []
    for block in content_block:
        if block.type == "text":
            text_parts.append(block.text)
    return "\n".join(text_parts)