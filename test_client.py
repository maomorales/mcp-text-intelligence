#!/usr/bin/env python3
"""
Interactive MCP Test Client

A simple CLI client to test the MCP text intelligence server interactively.
"""

import asyncio
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a colored header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")


def print_success(text):
    """Print a success message."""
    print(f"{Colors.OKGREEN}{text}{Colors.ENDC}")


def print_info(text):
    """Print an info message."""
    print(f"{Colors.OKCYAN}{text}{Colors.ENDC}")


def print_error(text):
    """Print an error message."""
    print(f"{Colors.FAIL}{text}{Colors.ENDC}")


def print_json(data):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2))


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


async def list_tools_command(session: ClientSession):
    """List available tools."""
    print_header("Available Tools")
    tools = await session.list_tools()

    for tool in tools.tools:
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}{tool.name}{Colors.ENDC}")
        print(f"  {tool.description}")
        print(f"\n  Input Schema:")
        print_json(tool.inputSchema)


async def extract_outcomes_command(session: ClientSession):
    """Interactive extract_outcomes tool."""
    print_header("Extract Outcomes Tool")
    print("Enter the text to analyze (press Ctrl+D or Ctrl+Z when done):")
    print(f"{Colors.WARNING}> {Colors.ENDC}", end="")

    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    text = "\n".join(lines)

    if not text.strip():
        print_error("No text provided.")
        return

    print_info("\nCalling extract_outcomes...")

    result = await session.call_tool("extract_outcomes", arguments={"text": text})

    print_success("\n✓ Results:")
    for content in result.content:
        if hasattr(content, 'text'):
            data = json.loads(content.text)
            print_json(data)


async def trim_context_command(session: ClientSession):
    """Interactive trim_context tool."""
    print_header("Trim Context Tool")

    print("Enter the text to reduce (press Ctrl+D or Ctrl+Z when done):")
    print(f"{Colors.WARNING}> {Colors.ENDC}", end="")

    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    text = "\n".join(lines)

    if not text.strip():
        print_error("No text provided.")
        return

    print(f"\nEnter the goal: ", end="")
    goal = input()

    if not goal.strip():
        print_error("No goal provided.")
        return

    print(f"Max chunks (default 5): ", end="")
    max_chunks_input = input().strip()
    max_chunks = int(max_chunks_input) if max_chunks_input else 5

    print_info(f"\nCalling trim_context with goal='{goal}', max_chunks={max_chunks}...")

    result = await session.call_tool(
        "trim_context",
        arguments={
            "text": text,
            "goal": goal,
            "max_chunks": max_chunks
        }
    )

    print_success("\n✓ Results:")
    for content in result.content:
        if hasattr(content, 'text'):
            data = json.loads(content.text)
            print_json(data)


async def quick_extract_outcomes(session: ClientSession, text: str):
    """Quick extract_outcomes call with provided text."""
    print_info(f"Extracting outcomes from: \"{text[:50]}...\"")

    result = await session.call_tool("extract_outcomes", arguments={"text": text})

    print_success("\n✓ Results:")
    for content in result.content:
        if hasattr(content, 'text'):
            data = json.loads(content.text)
            print_json(data)


async def quick_trim_context(session: ClientSession, text: str, goal: str, max_chunks: int = 5):
    """Quick trim_context call with provided text."""
    print_info(f"Trimming context for goal: \"{goal}\"")

    result = await session.call_tool(
        "trim_context",
        arguments={
            "text": text,
            "goal": goal,
            "max_chunks": max_chunks
        }
    )

    print_success("\n✓ Results:")
    for content in result.content:
        if hasattr(content, 'text'):
            data = json.loads(content.text)
            print_json(data)


async def interactive_mode(session: ClientSession):
    """Run interactive menu."""
    while True:
        print_header("MCP Text Intelligence Test Client")
        print("1. List available tools")
        print("2. Extract outcomes (interactive)")
        print("3. Trim context (interactive)")
        print("4. Run extract_outcomes example")
        print("5. Run trim_context example")
        print("6. Exit")
        print(f"\n{Colors.WARNING}Choose an option (1-6): {Colors.ENDC}", end="")

        try:
            choice = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break

        if choice == "1":
            await list_tools_command(session)
        elif choice == "2":
            await extract_outcomes_command(session)
        elif choice == "3":
            await trim_context_command(session)
        elif choice == "4":
            example_text = """
            In today's meeting, we decided to use PostgreSQL for the database.
            John will set up the development environment by Friday.
            Should we use Docker for local development?
            The team agreed to move forward with the API-first approach.
            TODO: Review the security requirements.
            """
            await quick_extract_outcomes(session, example_text)
        elif choice == "5":
            example_text = """
            Hi there! Hope you're doing well. I wanted to reach out about the API integration project.
            The deadline is March 15th. We need to support JSON and XML formats.
            The API must handle at least 1000 requests per second.
            Thanks for your help on this. Let me know if you have questions!
            """
            await quick_trim_context(session, example_text, "API requirements", 3)
        elif choice == "6":
            print_success("\nGoodbye!")
            break
        else:
            print_error("Invalid choice. Please select 1-6.")

        print("\n" + "="*60)


async def main():
    """Main entry point."""
    print(f"{Colors.BOLD}Starting MCP Text Intelligence Test Client...{Colors.ENDC}")

    try:
        async with create_mcp_client() as session:
            print_success("✓ Connected to MCP server")
            await interactive_mode(session)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        sys.exit(0)
