# How To Build a General Purpose AI Agent in 131 lines of Python 

*Implementing a coding agent in 131 lines of Python code and a Search Agent in 61 lines*

In this post, we’ll build two AI from scratch in Python. One will be a coding agent, the other a Search agent.

Why have I then called this post “How To Build a General Purpose AI Agent in 250 lines of Python” then? Well, as it turns out now, coding agents are actually general purpose agents in some quite surprising ways.

What I mean by this is once you have an agent that can write code, it can 1\) do a huge number of things you don’t often think of as involving code and 2\) it can extend itself to do even more things.

It’s more appropriate to think of coding agents as “computer-using agents” that happen to be great at writing code. That doesn’t mean you should always build a general-purpose agent—but it’s worth understanding what you’re actually building when you give an LLM shell access. That’s also why we’ll build a search agent in this post: to show the pattern works regardless of what you’re building.

For example, the coding agent we’ll build below has four tools: `read`, `write`, `edit`, and `bash`.   
[Watch this 90 second video to see how it can clean your desktop](https://www.loom.com/share/7b5ffe88b7df4367a961aaa965db72bf). It can do 

* **File/life organization:** clean your desktop, sort Downloads by type, rename vacation photos with dates, find and delete duplicates, organize receipts into folders;  
* **Personal productivity:** search all your notes for something you half-remember, compile a packing list from past trips, find all PDFs containing "tax" from last year;  
* **Media management:** rename a season of TV episodes properly, convert images to different formats, extract audio from videos, resize photos for social media;  
* **Writing & content:** combine multiple docs into one, convert between formats, find-and-replace across many files;  
* **Data wrangling:** turn a messy CSV into a clean address book, extract emails from a pile of files, merge spreadsheets from different sources.

This is a small subset of what’s possible. It’s also the reason Claude Cowork seemed promising and why OpenClaw has taken off in the way it did\!

*So how can you build this?* In this post, I’ll show you how to build a minimal version. To build a more sophisticated and powerful version, join Ivan Leo (ex-Manus) and myself for our free workshop [*Building Your Own OpenClaw Agent from Scratch*](https://luma.com/9gp9xy2f).

Agents are just LLMs with tools in a conversation loop and once you know the pattern, you’ll be able to build all types of agents with it:


To show you the pattern, I'll build two agents from scratch: our **“general-purpose” coding agent** and a **search agent**.

As [Ivan Leo wrote](https://ivanleo.com/blog/building-an-agent),

*The barrier to entry is remarkably low: 30 minutes and you have an AI that can understand your codebase and make edits just by talking to it.*

The goal here is to show that the pattern is the same regardless of what you're building an agent for. Coding agent, search agent, browser agent, email agent, database agent: they all follow the same structure. The only difference is the tools you give them.

## Part 1: The Coding Agent

We’ll start with a coding agent that can read, write, and execute code. As stated, the ability to write and execute code with `bash` also turns a "coding agent" into a “general-purpose agent”. With shell access, it can do anything you can do from a terminal:

- Sort and organize your local file system  
- Clean up your desktop  
- Batch rename photos  
- Convert file formats  
- Manage git repos across multiple projects  
- Install and configure software

Check out [Ivan Leo’s post](https://ivanleo.com/blog/building-an-agent) for how to do this in Javascript and [Thorsten Ball’s post](https://ampcode.com/notes/how-to-build-an-agent) for how to do it in Go.

You can find all the code here. <!-- TODO: add code link -->

### Setup

Start by creating our project:

```bash
mkdir coding-agent
cd coding-agent
uv init
uv add anthropic pydantic python-dotenv
```


Make sure you've got an Anthropic API Key set as `ANTHROPIC_API_KEY` environment variable.

We'll code our agent in a file called `agent.py` and build it in 4 steps:

1. Hook up Claude
2. Add a tool (read)
   2a. Add more tools: write, edit, and bash
3. Build the agentic loop
4. Build the conversational loop

### 1. Hook Up Claude


```python
import sys
import anthropic

client = anthropic.Anthropic()

query = sys.argv[1]

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": query}],
)

print(response.content[0].text)
```


```
$ python agent.py "What's the capital of Australia"

Canberra
```

Text in, text out. Good! Now let's give it a tool.

### 2. Add a Tool (read)

We'll start by implementing a tool called `read` which will allow the agent to read files from the filesystem. In Python, we can use Pydantic for schema validation, which also generates JSON schemas we can provide to the API:

```python
from pathlib import Path
from pydantic import BaseModel

class ReadArgs(BaseModel):
    """Read a file from the filesystem."""
    path: str

def execute_read(args: ReadArgs) -> str:
    try:
        return Path(args.path).read_text()
    except Exception as e:
        return f"Error: {e}"
```

The Pydantic model gives us two things: validation and a JSON schema. We can see what the schema looks like:

```python
print(ReadArgs.model_json_schema())
```

```json
{
  "description": "Read a file from the filesystem.",
  "properties": {
    "path": {"title": "Path", "type": "string"}
  },
  "required": ["path"],
  "title": "ReadArgs",
  "type": "object"
}
```

We wrap this into a tool definition that Claude understands:

```python
read_tool = {
    "name": "read",
    "description": "Read a file and return its contents.",
    "input_schema": ReadArgs.model_json_schema(),
}
```

Then we add tools to the API call, handle the tool request, execute it, and send the result back:

```python
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
```

Let's see what happens when we run it:

```
$ python agent.py "read agent.py and tell me what it does"

[Tool: read]

This script calls the Claude API with a user query passed via command line.
It sends the query, gets a response, and prints it.
```



### 2a. Add More Tools (write, edit, bash)

We have a `read` tool, but a coding agent needs to do more than read. It needs to 

- write new files, 
- edit existing ones, and 
- execute code to test it. 

That's three more tools: `write`, `edit`, and `bash`.

Same pattern as `read`. First the schemas:

```python
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
```

Then the executors:

```python
import subprocess

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
```

And the tool definitions, along with the code that runs whichever one Claude picks:

```python
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

args_cls, executor = executors[tool_use.name]
args = args_cls.model_validate(tool_use.input)
result = executor(args)
```

The `bash` tool is what makes this actually useful: Claude can now write code, run it, see errors, and fix them. But it's also dangerous. This tool could delete your entire file system! Proceed with caution: run it in a sandbox, a container, or a VM.

Interestingly, `bash` is what turns a "coding agent" into a general-purpose agent. With shell access, it can do anything you can do from a terminal:

- Sort and organize your local file system
- Clean up your desktop
- Batch rename photos
- Convert file formats
- Manage git repos across multiple projects
- Install and configure software

It was actually [Pi: The Minimal Agent Within OpenClaw](https://lucumr.pocoo.org/2026/1/31/pi/), that inspired this example!

Try asking Claude to edit a file: it often wants to read it first to see what's there. But our current code only handles one tool call. That's where the agentic loop comes in.

### 3. Build the Agentic Loop

Right now Claude can only call one tool per request. But real tasks need multiple steps: read a file, edit it, run it, see the error, fix it. We need a loop that lets Claude keep calling tools until it's done.

We wrap the tool handling in a `while True` loop:

```python
executors = {
    "read": (ReadArgs, execute_read),
    "write": (WriteArgs, execute_write),
    "edit": (EditArgs, execute_edit),
    "bash": (BashArgs, execute_bash),
}

messages = [{"role": "user", "content": query}]

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
```

Let's try a multi-step task:

```
$ python agent.py "write a python script that prints hello world, save it to hello.py, and run it"

[write]
[bash]

Done! I created hello.py with a simple print statement and ran it.
The output was: Hello, World!
```

### 4. Build the Conversational Loop

Right now the agent handles one query and exits. But we want a back-and-forth conversation: ask a question, get an answer, ask a follow-up. We need an outer loop that keeps asking for input.

We wrap everything in a `while True`:

```python
messages = []

while True:
    user_input = input("> ")
    if not user_input.strip():
        continue

    messages.append({"role": "user", "content": user_input})

    # Agentic loop (from Step 3)
    while True:
        response = client.messages.create(...)
        # ... handle tools until done
        if response.stop_reason != "tool_use":
            break

    # Ready for next user input
```

The `messages` list persists across turns, so Claude remembers context. That's the complete coding agent.

You may have noticed that we’re merely appending all previous messages which means the context will grow quite quickly! Solving this is part of the wonderful world of context engineering and we’ll be covering some of this in our [*Building Your Own OpenClaw Agent from Scratch with Ivan Leo (Manus)*](https://luma.com/9gp9xy2f) workshop (register to join live or get the recording afterwards.)

## A Note On Agent Harnesses

An agent harness is the scaffolding and infrastructure that wraps around an LLM to turn it into an agent. It handles:

- **The loop:** prompting the model, parsing its output, executing tools, feeding results back  
- **Tool execution:** actually running the code/commands the model asks for  
- **Context management:** what goes in the prompt, token limits, history  
- **Safety/guardrails:** confirmation prompts, sandboxing, disallowed actions  
- **State:** keeping track of the conversation, files touched, etc.

And more.

Think of it like this:  the LLM is the brain, the harness is everything else that lets it actually do things.

What we’ve built above is the hello world of agent harnesses: it covers the loop, tool execution, and basic context management. What it doesn't have: safety guardrails, token limits, persistence, or even a system prompt!

When building out from the basis, I encourage you to follow the paths of:

- [**The Pi Coding Agent, which adds**:](https://github.com/badlogic/pi-mono) context loading (`AGENTS.md` from multiple directories), persistent sessions you can resume and branch, and an extensibility system (skills, extensions, prompts) and  
- [**OpenClaw, which goes further**:](https://openclaw.ai/) a persistent daemon (always-on, not invoked), chat as the interface (Telegram, WhatsApp, etc.), file-based continuity (`SOUL.md`), `MEMORY.md`, daily logs), proactive behavior (heartbeats, cron), pre-integrated tools (browser, sub-agents, device control), and the ability to message you without being prompted.



## Part 2: The Search Agent

In order to really show you that agentic loop is what powers any agent, we'll now build a Search Agent (inspired by a [podcast I did with Search legends John Berryman & Doug Turnbull](https://hugobowne.substack.com/p/episode-68-a-builders-guide-to-agentic)). We'll use Gemini for the LLM and Exa for web search.

You can find all the code here.

But first, the astute reader may have an interesting question: if a coding agent really is a general purpose agent, why would anyone want to build a Search agent, when we could just get a coding agent to extend itself and turn itself into a Search agent? Well, because if you want to build a Search agent for a business, you're not going to do it by building a coding agent first… So let’s build it!

### What You'll Need

Let's build this step by step. Start by creating our project:

```bash
mkdir search-agent
cd search-agent
uv init
uv add google-genai requests python-dotenv
```

Set `GEMINI_API_KEY` (from Google AI Studio) and `EXA_API_KEY` (from exa.ai) as environment variables.

We'll code our agent in a file called `search_agent.py` and build it in 4 steps:

1. Hook up Gemini
2. Add a tool (`web_search`)
3. Build the agentic loop
4. Build the conversational loop

### 1. Hook Up Gemini

```python
import os
import sys
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

query = sys.argv[1]

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=query
)

print(response.text)
```

```
$ python agent.py "Who is Doug Turnbull?"

Doug Turnbull is a search relevancy expert and consultant.
```

### 2. Add a Tool (`web_search`)

Gemini can answer from its training data, but we don't want that, man! For current information, it needs to search the web. We'll give it a `web_search` tool that calls Exa.

```python
import requests
from google.genai import types

search_tool = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="web_search",
        description="Search the web for current information",
        parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
    )
])

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[types.Content(role="user", parts=[types.Part(text=query)])],
    config=types.GenerateContentConfig(
        tools=[search_tool],
        system_instruction="Always use web_search to answer. Do not rely on training data."
    )
)
```

The system instruction grounds the model, forcing it to search instead of guessing.

```python
part = response.candidates[0].content.parts[0]
if part.function_call:
    search_query = part.function_call.args["query"]

    results = requests.post(
        "https://api.exa.ai/search",
        headers={"x-api-key": os.getenv("EXA_API_KEY")},
        json={"query": search_query, "numResults": 3, "contents": {"text": True}}
    ).json()

    results_text = "\n\n".join(
        f"Title: {r['title']}\nURL: {r['url']}\nContent: {r.get('text', '')[:500]}"
        for r in results.get("results", [])
    )

    # Send results back to Gemini
    final_response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[
            types.Content(role="user", parts=[types.Part(text=query)]),
            types.Content(role="model", parts=[part]),
            types.Content(role="user", parts=[types.Part(text=f"Search results:\n{results_text}")])
        ]
    )
    print(final_response.text)
```

### 3. Build the Agentic Loop

Some questions need multiple searches. "Compare X and Y" requires searching for X, then searching for Y. We need a loop that lets Gemini keep searching until it has enough information.

```python
messages = [types.Content(role="user", parts=[types.Part(text=query)])]

while True:
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[search_tool],
            system_instruction="Always use web_search to answer. Do not rely on training data."
        )
    )

    part = response.candidates[0].content.parts[0]

    if part.function_call:
        search_query = part.function_call.args["query"]
        print(f"Searching: {search_query}")

        results = requests.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": os.getenv("EXA_API_KEY")},
            json={"query": search_query, "numResults": 3, "contents": {"text": True}}
        ).json()

        results_text = "\n\n".join(
            f"Title: {r['title']}\nURL: {r['url']}\nContent: {r.get('text', '')[:500]}"
            for r in results.get("results", [])
        )

        messages.append(types.Content(role="model", parts=[part]))
        messages.append(types.Content(role="user", parts=[types.Part(text=f"Search results:\n{results_text}")]))
    else:
        print(response.text)
        break
```

```
$ python agent.py "Compare Doug Turnbull and John Berryman's work on search"

Searching: Doug Turnbull search relevancy
Searching: John Berryman search relevancy

Both are search relevancy experts who co-authored "Relevant Search"...
```

### 4. Build the Conversational Loop

Same as before: we want back-and-forth conversation, not one query and exit. Wrap everything in an outer loop.

```python
messages = []

while True:
    user_input = input("> ")
    if user_input.lower() == "quit":
        break

    messages.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    # Agentic loop
    while True:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[search_tool],
                system_instruction="Always use web_search to answer. Do not rely on training data."
            )
        )

        part = response.candidates[0].content.parts[0]

        if part.function_call:
            # ... execute search, append results to messages
        else:
            print(response.text)
            messages.append(types.Content(role="model", parts=[types.Part(text=response.text)]))
            break
```

Messages persist across turns, so follow-up questions have context.


## Extend It

The pattern is the same for both agents. Add any tool:

- `web_search` to the coding agent: look things up while coding  
- `bash` to the search agent: act on what it finds  
- `browser`: navigate websites  
- `send_email`: communicate  
- `database_query`: run SQL

We’ll be building some of these examples in the free online workshop [*Building Your Own OpenClaw Agent from Scratch with Ivan Leo (Manus).*](https://luma.com/9gp9xy2f) Register to join live or get the recording afterwards.

*One thing we’ll be doing is showing how general purpose a coding agent really can be*. [As Armin Ronacher wrote about Pi: The Minimal Agent Within OpenClaw](https://lucumr.pocoo.org/2026/1/31/pi/)

> Pi’s entire idea is that **if you want the agent to do something that it doesn’t do yet**, you **don’t go and download an extension or a skill** or something like this. **You ask the agent to extend itself**. It celebrates the idea of code writing and running code.

## Conclusion

Building agents is straightforward. The magic isn't complex algorithms, it's the conversation loop and well-designed tools.

Both agents follow the same pattern:

1. Hook up the LLM
2. Add tools
3. Build the agentic loop
4. Build the conversational loop

The only difference is the tools.  