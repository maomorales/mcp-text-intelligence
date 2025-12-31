# MCP Text Intelligence

A minimal Model Context Protocol (MCP) server that provides text analysis tools for extracting outcomes and trimming context.

## Overview

This MCP server exposes two stateless tools designed to help analyze and process text:

1. **extract_outcomes** - Extract explicit decisions, action items, and open questions from text
2. **trim_context** - Reduce long text to the minimum context required for a specific goal

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

## Testing

### Interactive Test Client

An interactive test client is included to test the MCP server without needing to configure an MCP client application.

**Quick start:**
```bash
./test.sh
```

Or manually:
```bash
source ./venv/bin/activate
python test_client.py
```

**Features:**
- Interactive menu-driven interface
- Test both tools with custom inputs
- Run pre-built examples
- View tool definitions and schemas
- Color-coded output for easy reading

**Menu options:**
1. **List available tools** - See all tools and their schemas
2. **Extract outcomes (interactive)** - Paste text and extract outcomes
3. **Trim context (interactive)** - Paste text, enter goal, and trim context
4. **Run extract_outcomes example** - See a quick demo
5. **Run trim_context example** - See a quick demo
6. **Exit** - Close the client

## Tools

### 1. extract_outcomes

**Purpose**: Extract explicit outcomes from raw text, including decisions made, action items to complete, and open questions that remain.

**When to use**:
- After meetings to identify actionable items
- Processing notes to find what was decided
- Identifying questions that need answers
- Extracting structured data from unstructured text

**Input Schema**:
```json
{
  "text": "string"
}
```

**Output Schema**:
```json
{
  "decisions": ["string"],
  "action_items": ["string"],
  "open_questions": ["string"]
}
```

**Example**:

Input:
```json
{
  "text": "In today's meeting, we decided to use PostgreSQL for the database. John will set up the development environment by Friday. We still need to figure out: should we use Docker for local development? The team agreed to move forward with the API-first approach."
}
```

Output:
```json
{
  "decisions": [
    "we decided to use PostgreSQL for the database.",
    "The team agreed to move forward with the API-first approach."
  ],
  "action_items": [
    "John will set up the development environment by Friday."
  ],
  "open_questions": [
    "should we use Docker for local development?"
  ]
}
```

---

### 2. trim_context

**Purpose**: Reduce lengthy text to only the essential information needed to accomplish a specific goal, removing greetings, filler, repetition, and tangential content.

**When to use**:
- Processing long documents for specific information
- Preparing context for token-limited operations
- Extracting relevant facts from verbose messages
- Focusing on what matters for a particular task

**Input Schema**:
```json
{
  "text": "string",
  "goal": "string",
  "max_chunks": "number (optional, default: 5)"
}
```

**Output Schema**:
```json
{
  "selected_chunks": [
    {
      "text": "string",
      "reason": "string"
    }
  ]
}
```

**Example**:

Input:
```json
{
  "text": "Hi there! Hope you're doing well. I wanted to reach out about the API integration project. The deadline is March 15th. We need to support JSON and XML formats. Thanks for your help on this. Let me know if you have questions!",
  "goal": "understand API requirements",
  "max_chunks": 3
}
```

Output:
```json
{
  "selected_chunks": [
    {
      "text": "We need to support JSON and XML formats.",
      "reason": "High relevance to goal (score: 0.33)"
    },
    {
      "text": "The deadline is March 15th.",
      "reason": "High relevance to goal (score: 0.00)"
    },
    {
      "text": "I wanted to reach out about the API integration project.",
      "reason": "High relevance to goal (score: 0.00)"
    }
  ]
}
```

## How It Works

### extract_outcomes

Uses pattern matching to identify:
- **Decisions**: Phrases containing "decided", "chose", "agreed", "concluded", etc.
- **Action Items**: Phrases with "will", "should", "must", "TODO", task markers, etc.
- **Open Questions**: Sentences ending with "?"

The tool preserves original wording and only extracts explicitly stated items.

### trim_context

Uses a simple relevance algorithm:
1. Splits text into sentences
2. Filters out common filler patterns (greetings, sign-offs, etc.)
3. Scores each sentence based on word overlap with the goal
4. Returns the top N most relevant chunks with justifications

## Limitations

- Stateless: No memory between requests
- Pattern-based: May miss items phrased unusually
- English-optimized: Best results with English text
- Simple scoring: Relevance based on word overlap, not semantic understanding

## Configuration

This MCP server runs via stdio and can be configured in your MCP client (e.g., Claude Desktop) by adding to the configuration file:

```json
{
  "mcpServers": {
    "text-intelligence": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

## License

MIT
