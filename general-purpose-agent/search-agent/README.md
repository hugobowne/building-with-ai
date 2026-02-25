# Search Agent

A minimal search agent built with Gemini and Exa in 61 lines of Python. This agent searches the web to answer questions with current information.

Companion code for the blog post: [How To Build a General Purpose AI Agent in 131 Lines of Python](https://hugobowne.substack.com/p/how-to-build-a-general-purpose-ai)

## Setup

```bash
uv init
uv add google-genai requests python-dotenv
```

Set your `GEMINI_API_KEY` and `EXA_API_KEY` in a `.env` file.

## The Progression

Each file builds on the previous one:

| File | What it adds |
|------|--------------|
| `1_hook_up_gemini.py` | Basic LLM call - text in, text out |
| `2_add_a_tool.py` | Single tool (`web_search`) - search and respond |
| `3_agentic_loop.py` | Agentic loop - Gemini keeps searching until it has enough info |
| `4_conversational_loop.py` | Conversational loop - back-and-forth interaction |

## Running

```bash
# Step 1: Basic query
uv run python 1_hook_up_gemini.py "Who is Doug Turnbull?"

# Step 2: Search the web
uv run python 2_add_a_tool.py "What happened in tech news today?"

# Step 3: Multi-step search
uv run python 3_agentic_loop.py "Compare Doug Turnbull and John Berryman's work on search"

# Step 4: Interactive conversation
uv run python 4_conversational_loop.py
```
