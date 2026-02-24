# Coding Agent

A minimal coding agent built with Claude in 131 lines of Python. This agent can read, write, edit files, and execute shell commands.

See the full blog post: [How To Build a General Purpose AI Agent in 250 lines of Python](../post-v2.md)

## Setup

```bash
uv init
uv add anthropic pydantic python-dotenv
```

Set your `ANTHROPIC_API_KEY` in a `.env` file.

## The Progression

Each file builds on the previous one:

| File | What it adds |
|------|--------------|
| `1_hook_up_claude.py` | Basic LLM call - text in, text out |
| `2_add_a_tool.py` | Single tool (`read`) - one tool call, one response |
| `2a_add_more_tools.py` | Multiple tools (`read`, `write`, `edit`, `bash`) |
| `3_agentic_loop.py` | Agentic loop - Claude keeps calling tools until done |
| `4_conversational_loop.py` | Conversational loop - back-and-forth interaction |

## Running

```bash
# Step 1: Basic query
uv run python 1_hook_up_claude.py "What's the capital of France?"

# Step 2: Read a file
uv run python 2_add_a_tool.py "Read this file and summarize it: README.md"

# Step 2a: Multiple tools
uv run python 2a_add_more_tools.py "Create a file called hello.py that prints hello world"

# Step 3: Multi-step tasks
uv run python 3_agentic_loop.py "Write a Python script that prints hello world, save it to hello.py, and run it"

# Step 4: Interactive conversation
uv run python 4_conversational_loop.py
```
