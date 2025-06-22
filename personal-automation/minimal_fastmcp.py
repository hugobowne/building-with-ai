"""
Usage (run server):
    uv run uvicorn minimal_fastmcp:sse_app --port 8082 --reload

Usage (run client):
    (call tool) uv run minimal_fastmcp.py --tool add --args '{"a": 1, "b": 2}'
    (list tools) uv run minimal_fastmcp.py
"""

from fastmcp import FastMCP, Client
from mcp.types import TextContent
import asyncio
import argparse
import json
import lilypad
from dotenv import load_dotenv

load_dotenv()

lilypad.configure(auto_llm=True)

mcp = FastMCP("My MCP Server")
sse_app = mcp.sse_app()

JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

def parse_as_json(x: list[TextContent], expect_one_result: bool = True) -> JSON:
    parsed = [json.loads(t.text) for t in x]
    if expect_one_result:
        assert len(parsed) == 1, f"Expected one result, got {len(parsed)}"
        return parsed[0]
    return parsed

@mcp.tool()
@lilypad.trace(versioning="automatic")
async def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
@lilypad.trace(versioning="automatic")
async def square(a: int) -> int:
    return a * a

@mcp.tool()
@lilypad.trace(versioning="automatic")
async def sum_of_squares(a: int, b: int) -> int:
    async with Client("http://127.0.0.1:8082/sse") as client:
        a2 = parse_as_json(await client.call_tool("square", {"a": a}))
        b2 = parse_as_json(await client.call_tool("square", {"a": b}))
        res = parse_as_json(await client.call_tool("add", {"a": a2, "b": b2}))
        return res

async def main(tool: str | None = None, **kwargs):
    async with Client("http://127.0.0.1:8082/sse") as client:
        if tool:
            result = await client.call_tool(tool, kwargs)
            print(result)
        else:
            result = await client.list_tools()
            print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", type=str)
    parser.add_argument("--args", type=json.loads, default={})
    args = parser.parse_args()
    asyncio.run(main(args.tool, **args.args))