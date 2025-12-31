# Quick Start Guide

## Testing the MCP Server

You now have **two ways** to test the MCP server:

### Option 1: Automated Quick Test (Recommended First)

Run a quick automated test to verify everything works:

```bash
./venv/bin/python test_client_quick.py
```

This will:
- Connect to the MCP server
- List available tools
- Test `extract_outcomes` with example text
- Test `trim_context` with example text
- Show you the results

**Expected output:**
```
Testing MCP Client-Server Connection...

✓ Connected to MCP server

1. Listing tools...
✓ Found 2 tools:
  - extract_outcomes
  - trim_context

2. Testing extract_outcomes...
✓ Result:
{
  "decisions": [...],
  "action_items": [...],
  "open_questions": [...]
}

3. Testing trim_context...
✓ Result:
{
  "selected_chunks": [...]
}

✅ All tests passed!
```

### Option 2: Interactive Test Client

For hands-on testing with your own text:

```bash
./test.sh
```

Or manually:
```bash
./venv/bin/python test_client.py
```

**Interactive Menu:**
```
MCP Text Intelligence Test Client

1. List available tools
2. Extract outcomes (interactive)
3. Trim context (interactive)
4. Run extract_outcomes example
5. Run trim_context example
6. Exit

Choose an option (1-6):
```

**Using the interactive options:**

- **Option 2 (Extract outcomes)**: Paste your text, press Ctrl+D (Mac/Linux) or Ctrl+Z (Windows) when done
- **Option 3 (Trim context)**: Paste your text, press Ctrl+D/Z, then enter your goal and max chunks
- **Options 4-5**: Run pre-built examples to see how the tools work

## Example Session

```bash
$ ./venv/bin/python test_client.py

MCP Text Intelligence Test Client

1. List available tools
2. Extract outcomes (interactive)
3. Trim context (interactive)
4. Run extract_outcomes example
5. Run trim_context example
6. Exit

Choose an option (1-6): 4

Extracting outcomes from: "We decided to use PostgreSQL. John will set up..."

✓ Results:
{
  "decisions": [
    "We decided to use PostgreSQL."
  ],
  "action_items": [
    "John will set up the environment."
  ],
  "open_questions": [
    "Should we use Docker?"
  ]
}
```

## What's Happening Behind the Scenes

When you run the test client:

1. **Client starts** - The test client (`test_client.py`) launches
2. **Server spawns** - The client spawns `server.py` as a subprocess
3. **MCP handshake** - They establish an MCP connection via stdio
4. **Tools available** - The server advertises its two tools
5. **You interact** - You call tools through the menu
6. **Server processes** - The server processes text using pattern matching
7. **Results returned** - Results come back as JSON

## Troubleshooting

**Issue**: "Connection closed" or "No module named 'mcp'"
- **Solution**: Make sure you're using the venv Python: `./venv/bin/python test_client.py`

**Issue**: "No such file or directory: 'server.py'"
- **Solution**: Run the test client from the project directory: `cd /Users/mauricio/www/vibecoding/mcp`

**Issue**: Ctrl+D not working on Windows
- **Solution**: Use Ctrl+Z followed by Enter

## Next Steps

Once you've tested the MCP server locally:

1. **Integrate with Claude Desktop**: Add to your MCP configuration
2. **Use in production**: Deploy the server for your applications
3. **Extend functionality**: Add more text intelligence tools
4. **Share**: The server is production-ready and self-contained

See `README.md` for full documentation.
