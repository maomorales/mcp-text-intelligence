#!/usr/bin/env python3
"""Quick automated test of the MCP client-server connection."""

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@asynccontextmanager
async def create_mcp_client():
    """Create and connect to the MCP server."""
    # Get the current directory and venv python path
    current_dir = Path(__file__).parent
    venv_python = current_dir / "venv" / "bin" / "python"

    server_params = StdioServerParameters(
        command=str(venv_python),
        args=["server.py"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def test_connection():
    """Test MCP connection and tools."""
    print("Testing MCP Client-Server Connection...\n")

    async with create_mcp_client() as session:
        print("✓ Connected to MCP server")

        # List tools
        print("\n1. Listing tools...")
        tools = await session.list_tools()
        print(f"✓ Found {len(tools.tools)} tools:")
        for tool in tools.tools:
            print(f"  - {tool.name}")

        # Test extract_outcomes
        print("\n2. Testing extract_outcomes...")
        test_text = "We decided to use PostgreSQL. John will set up the environment. Should we use Docker?"
        result = await session.call_tool("extract_outcomes", arguments={"text": test_text})

        print("✓ Result:")
        for content in result.content:
            if hasattr(content, 'text'):
                data = json.loads(content.text)
                print(json.dumps(data, indent=2))

        # Test trim_context
        print("\n3. Testing trim_context...")
        test_text = "Hi! The deadline is March 15th. We need JSON and XML support. Thanks!"
        result = await session.call_tool(
            "trim_context",
            arguments={"text": test_text, "goal": "deadline", "max_chunks": 2}
        )

        print("✓ Result:")
        for content in result.content:
            if hasattr(content, 'text'):
                data = json.loads(content.text)
                print(json.dumps(data, indent=2))

        print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_connection())
