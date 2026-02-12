# Agentic Loop Plan

## Overview

Building an agentic loop from scratch, following John Berryman's "Builder's Playbook" homework from the podcast with Doug Turnbull.

## Steps

### 1. Ping an LLM
Make a basic call against a model: text in, text out. It's just an HTTP request.

### 2. Add a Tool
Add a tool call to the model call. Introduce the model to function/tool calling.

### 3. Build the Agentic Loop
Wrap a loop around the model so one input can trigger as many tool calls as needed (search is a good common tool) until the model is satisfied it has the answer. This is a RAG agent.

### 4. Add a Conversational Loop
Wrap another loop around the agent that incorporates the user across turns (multi-turn interaction). Now it's not just an agent - it's an assistant.

### 5. (Optional) Context Engineering
Go further by empathizing with the agent and thinking about what it sees in its context.

### 6. Frameworks Last
Only after building from scratch, look at frameworks. If one takes longer than ~2 hours to learn, it may be too thick or opaque. Lighter, newer ones are preferable.

---

## Use Case

A simple research assistant. Ask about a topic/person/company and the agent searches the web to find answers.

**Why agentic loop helps**: First search might give partial info, model searches again to fill gaps (e.g., "Who is Doug Turnbull?" → search him → search his company → synthesize)

**Why conversational loop helps**: User can drill down on things mentioned (e.g., "Tell me more about his take on search" → "Any recent talks?")

**Design decision**: Use a system prompt to force grounding via search rather than letting the model answer from weights. This reduces hallucination and provides verifiable sources.

---

## Tech Stack

- **Language**: Python
- **Package Manager**: uv
- **LLM**: Gemini (using `google-genai` library)
- **Tool**: Exa (web search API)
- **Reference**: `src/helpers.py` has existing Gemini code we can borrow from

## Code Style

- Follow PEP8
- Keep code as concise as possible
- Prioritize readability over cleverness
- Focus on the features, not boilerplate
- No abstractions until step 5 - keep scripts 1-4 as flat procedural code

---

## Setup

Create a `.env.example` with required API keys:
- `GEMINI_API_KEY`
- `EXA_API_KEY`

---

## Test Queries

Use these to test at each step:
1. "Who is Doug Turnbull?"
2. "What is OpenSource Connections?"
3. "What's Doug Turnbull's take on search and AI?"

---

## Exa API Reference

**Endpoint**: `https://api.exa.ai/search`

**Auth**: `x-api-key` header

**Basic search**:
```python
import requests

response = requests.post(
    "https://api.exa.ai/search",
    headers={"x-api-key": EXA_API_KEY},
    json={
        "query": "your search query",
        "numResults": 5,
        "contents": {"text": True}
    }
)
results = response.json()
```

**Response structure**:
```python
for result in results.get("results", []):
    print(result["title"])
    print(result["url"])
    print(result.get("text", "")[:500])
```

---

## Implementation Plan

Each step will be a separate script, building on the previous one:

- [ ] `01_ping_llm.py` - Basic Gemini call (text in, text out)
- [ ] `02_add_tool.py` - Add Exa search tool definition and handling
- [ ] `03_agentic_loop.py` - Agentic loop with tool execution
- [ ] `04_conversation_loop.py` - Multi-turn conversation loop
- [ ] `05_context_engineering.py` - Context engineering refinements (optional)
