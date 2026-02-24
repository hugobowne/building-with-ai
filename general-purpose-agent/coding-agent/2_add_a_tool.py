import sys
import anthropic
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


class ReadArgs(BaseModel):
    """Read a file from the filesystem."""
    path: str


def execute_read(args: ReadArgs) -> str:
    try:
        return Path(args.path).read_text()
    except Exception as e:
        return f"Error: {e}"


read_tool = {
    "name": "read",
    "description": "Read a file and return its contents.",
    "input_schema": ReadArgs.model_json_schema(),
}

query = sys.argv[1]
messages = [{"role": "user", "content": query}]

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=[read_tool],
    messages=messages,
)

# Claude requested a tool - execute it
tool_use = next(block for block in response.content if block.type == "tool_use")
print(f"[Tool: {tool_use.name}]")
args = ReadArgs.model_validate(tool_use.input)
result = execute_read(args)

# Send the result back to Claude
messages.append({"role": "assistant", "content": response.content})
messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": result,
    }]
})

# Get Claude's final response
final_response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=[read_tool],
    messages=messages,
)
print(final_response.content[0].text)
