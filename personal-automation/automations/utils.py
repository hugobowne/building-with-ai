from fastmcp import Client
from mcp.types import TextContent
import json

JSON = dict[str, 'JSON'] | list['JSON'] | str | int | float | bool | None

def res2json(x: list[TextContent], expect_single_item: bool = True) -> JSON:
    """Converts an assumed list[TextContent] to a JSON string."""
    try:
        res = [json.loads(item.text) for item in x]
    except json.JSONDecodeError:
        res = [item.text for item in x]
    if expect_single_item:
        assert len(res) == 1, "Expected a single item"
        return res[0]
    else:
        return res


class ToolClient(Client):
    """A simple wrapper to make it a bit easier to call tools and get the results back as a JSON object."""
    def __init__(self, client: Client):
        self.client = client

    def __getattr__(self, name: str):
        async def mcp_call(_format='json', **kwargs):
            res = await self.client.call_tool(name, kwargs)

            if _format == 'json':
                return res2json(res)
            else:
                return res
        return mcp_call
    
    def __call__(self, name: str, _format='json', **kwargs):
        return self.__getattr__(name)(_format, **kwargs)