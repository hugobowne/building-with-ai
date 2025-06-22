from mirascope import llm, Messages, BaseTool
from mirascope.mcp import sse_client
from pydantic import BaseModel
import lilypad
from dotenv import load_dotenv
import sys
import asyncio
from typing import Callable

load_dotenv()
lilypad.configure(auto_llm=True)


# This represents a single call to an LLM, where the response should be a Result object.
# However, it can return Tools for us to call if we provide tools
# @lilypad.trace(versioning='automatic')
@llm.call(provider='openai', model='gpt-4o-mini')
async def math_problem(query: str, *, history: list[Messages.Type] | None = None) -> list[Messages.Type]:
    history = history or []
    return [
        Messages.System("You are a math problem solver. You will be given a math problem and you will need to solve it using available tools."),
        Messages.User(query),
        # history will keep track of all the tool calls and results as the agent does stuff
        *history,
    ]


async def run_agent_one_step_(task, *args, history: list[Messages.Type], **kwargs):
    result = await task(*args, history=history, **kwargs)
    # Each step either calls tools or returns a result
    if tools := getattr(result, 'tools', None):
        tools_and_outputs = []
        for tool in tools:
            print(f"Calling tool {tool._name()}")
            tool_result = await tool.call()
            tools_and_outputs.append((tool, tool_result))
        if tools_and_outputs:
            history.append(result.message_param)
            history += result.tool_message_params(tools_and_outputs)
        # If we called a tool, we are not done yet
        return result, history, False
    return result, history, True


# Function which takes a list of tools and returns a (smaller) list of tools
ToolFilterFn = Callable[[list[type[BaseTool]]], list[type[BaseTool]]]

# @lilypad.trace(versioning='automatic')
async def run_agent(*args, max_steps: int = 5, tool_filter: ToolFilterFn | None = None, **kwargs):
    async with sse_client("http://127.0.0.1:8082/sse") as client:
        tools = await client.list_tools()
        # Our MCP server will have a LOT of tools over time... remember the function calling leaderboard!
        if tool_filter:
            tools = tool_filter(tools)
        # we patch in the tools because we were _discovering_ them via MCP server
        agent_fn = llm.override(math_problem, tools=tools)
        history = []
        done = False
        step = 0
        while not done:
            step += 1
            if step > max_steps:
                raise Exception('Agent took too long to complete')
            result, history, done = await run_agent_one_step_(agent_fn, *args, history=history, **kwargs)
        return result
    

if __name__ == "__main__":
    print(asyncio.run(run_agent(sys.argv[1])))