from fastmcp import FastMCP

config = {
  "mcpServers": {
    "browsermcp": {
      "command": "npx",
      "args": ["@browsermcp/mcp@latest"]
    }
  }
}

mcp = FastMCP.as_proxy(config, name="Browser")


