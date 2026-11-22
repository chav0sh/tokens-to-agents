"""A tiny MCP server: it offers one tool, the holiday lookup (chapter 16). Needs the `mcp` package, version 2."""

from mcp.server.mcpserver import MCPServer  # pyright: ignore[reportMissingImports]

server = MCPServer("hr-tools")
HOLIDAY_DAYS_LEFT = {"Maria Lind": 7, "Tom Ek": 18}


@server.tool()
def holiday_days_left(employee: str) -> str:
    """How many paid holiday days an employee has left this year. Needs the employee's full name."""
    if employee not in HOLIDAY_DAYS_LEFT:
        return f"No employee called {employee!r}."  # a readable error, as in chapter 12, never a made-up 0
    return f"{employee} has {HOLIDAY_DAYS_LEFT[employee]} holiday days left this year."


if __name__ == "__main__":
    server.run()  # stdio: the client starts this file as a subprocess and talks over stdin/stdout
