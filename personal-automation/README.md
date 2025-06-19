# Personal Automation

This subdirectory contains code from the lightning talk [10x Your Productivity by Building Personal Agents with MCP](https://maven.com/p/05b8f8/10x-your-productivity-by-building-personal-agents-with-mcp).

## Quick Start

All the below comamnds assume you are running from the same directory this README is located in.
Explanations of several files can be found near the end of this README.

Install uv

- [ ] Write instructions for installing uv

```bash
TODO
```

Sync environment:

```bash
uv sync
```

Run the sample MCP server:

```bash
uv run uvicorn minimal_fastmcp:sse_app --port 8082
```

List available tools on the MCP server:

```bash
uv run minimal_fastmcp.py
```

Call a tool on the MCP server:

```bash
uv run minimal_fastmcp.py add '{"a": 1, "b": 2}'
```

Run a simple agent:

```bash
uv run simple_mirascope_agent.py 'what is 1 + 1?'
```

Great! You have the basic examples working. Follow the pre-requisite setup steps below to run the more feature-complete examples!

## Setup

- [ ] Write instructions for installing uv
- [ ] Write instructions for getting google creds
- [ ] Write instructions for installing browser mcp extension
- [ ] Write instructions for setting up HumanLayer
- [ ] Write instructions for setting up Lilypad

## Example Usage

```bash
# run the server
uv run uvicorn automations.mymcp:sse_app --port 8082 --reload

# Trigger the weekly review
uv run automations/mymcp.py weekly_review
```


## Important Files

- [ ] Write explanation of simple mcp server
- [ ] Write explanation of simple mirascope agent
- [ ] write explanation of the rest of the files
