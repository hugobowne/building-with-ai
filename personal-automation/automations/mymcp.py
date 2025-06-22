from fastmcp import FastMCP, Client
import asyncio
from dotenv import load_dotenv
import lilypad
import json
from automations.utils import ToolClient
from automations.browsermcp import mcp as browser_mcp
from automations.browser_tasks import run_browser_task, get_linkedin_analytics, LinkedInAnalytics
from automations.config import SERVER_URL
import argparse
from automations.gmailmcp import mcp as gmail_mcp

load_dotenv()
lilypad.configure(auto_llm=True)

mcp = FastMCP('MyMCP')
# hl = HumanLayer(verbose=True)

sse_app = mcp.sse_app()

mcp.mount('browser', browser_mcp)
mcp.mount('gmail', gmail_mcp)


@mcp.tool()
async def summarize_linkedin_analytics() -> LinkedInAnalytics:
    """Get the LinkedIn analytics."""
    res = await run_browser_task(get_linkedin_analytics)
    return res


@mcp.tool()
async def weekly_review():
    async with Client(SERVER_URL) as client:
        tool_client = ToolClient(client)
        # Note: we have max_emails=5 for purposes of a live demo!
        await tool_client.gmail_process_inbox(max_emails=5)
        res = await tool_client.summarize_linkedin_analytics()
        return res


async def list_tools():
    async with Client(SERVER_URL) as client:
        result = await client.list_tools()
        return result

async def call_tool(name: str, args: dict):
    async with Client(SERVER_URL) as client:
        tool_client = ToolClient(client)
        result = await getattr(tool_client, name)(**args)
        return result


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('tool_name', nargs='?', help='Tool name to call')
    parser.add_argument('tool_args', nargs='?', help='Tool arguments as JSON')
    
    args = parser.parse_args()
    
    if args.tool_name:
        tool_args = json.loads(args.tool_args) if args.tool_args else {}
        res = await call_tool(args.tool_name, tool_args)
        print(res)
    else:
        res = await list_tools()
        for tool in res:
            print(tool)

if __name__ == '__main__':
    asyncio.run(main())