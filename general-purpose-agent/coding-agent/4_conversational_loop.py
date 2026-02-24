import subprocess
import anthropic
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


class ReadArgs(BaseModel):
    """Read a file from the filesystem."""
    path: str


class WriteArgs(BaseModel):
    """Create or overwrite a file."""
    file_path: str
    content: str


class EditArgs(BaseModel):
    """Find and replace text in a file."""
    file_path: str
    old_str: str
    new_str: str


class BashArgs(BaseModel):
    """Execute a shell command."""
    command: str


def execute_read(args: ReadArgs) -> str:
    try:
        return Path(args.path).read_text()
    except Exception as e:
        return f"Error: {e}"


def execute_write(args: WriteArgs) -> str:
    try:
        path = Path(args.file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(args.content)
        return f"Wrote {len(args.content)} bytes to {args.file_path}"
    except Exception as e:
        return f"Error: {e}"


def execute_edit(args: EditArgs) -> str:
    try:
        path = Path(args.file_path)
        content = path.read_text()
        new_content = content.replace(args.old_str, args.new_str)
        path.write_text(new_content)
        return "Edit successful"
    except Exception as e:
        return f"Error: {e}"


def execute_bash(args: BashArgs) -> str:
    try:
        result = subprocess.run(
            args.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout + result.stderr
        return output if output.strip() else "(no output)"
    except Exception as e:
        return f"Error: {e}"


tools = [
    {"name": "read", "description": "Read a file.", "input_schema": ReadArgs.model_json_schema()},
    {"name": "write", "description": "Write a file.", "input_schema": WriteArgs.model_json_schema()},
    {"name": "edit", "description": "Edit a file.", "input_schema": EditArgs.model_json_schema()},
    {"name": "bash", "description": "Run a shell command.", "input_schema": BashArgs.model_json_schema()},
]

executors = {
    "read": (ReadArgs, execute_read),
    "write": (WriteArgs, execute_write),
    "edit": (EditArgs, execute_edit),
    "bash": (BashArgs, execute_bash),
}

messages = []

while True:
    user_input = input("> ")
    if not user_input.strip():
        continue

    messages.append({"role": "user", "content": user_input})

    # Agentic loop
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"[{block.name}]")
                args_cls, executor = executors[block.name]
                args = args_cls.model_validate(block.input)
                result = executor(args)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})
