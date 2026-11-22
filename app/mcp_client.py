"""An MCP client: starts mcp_server.py, asks which tools it offers, and calls one (chapter 16).

    uv run python app/mcp_client.py

Written for version 2 of the `mcp` Python package (version 1 used different class names).
"""

import asyncio
import sys
from pathlib import Path

from mcp import Client  # pyright: ignore[reportMissingImports]
from mcp.client.stdio import StdioServerParameters  # pyright: ignore[reportMissingImports]

SERVER = Path(__file__).parent / "mcp_server.py"


async def main() -> None:
    # The client starts the server as a subprocess and talks to it over stdin and stdout.
    async with Client(StdioServerParameters(command=sys.executable, args=[str(SERVER)])) as client:
        for tool in (await client.list_tools()).tools:
            print("tool:", tool.name, "-", tool.description)
        result = await client.call_tool("holiday_days_left", {"employee": "Maria Lind"})
        first = result.content[0]  # a tool can return text, images or files; ours returns text
        print("result:", first.text if first.type == "text" else first)


if __name__ == "__main__":
    asyncio.run(main())
