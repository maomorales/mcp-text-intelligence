#!/usr/bin/env python3
"""
MCP Text Intelligence Server

A minimal MCP server that provides two text analysis tools:
1. extract_outcomes - Extract decisions, action items, and open questions
2. trim_context - Reduce text to minimal context for a goal
"""

import json
import logging
import re
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-text-intelligence")

# Create server instance
app = Server("mcp-text-intelligence")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="extract_outcomes",
            description="Extract explicit decisions, action items, and open questions from text. Returns only items explicitly stated in the input.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze for outcomes"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="trim_context",
            description="Reduce long text to the minimum context required to accomplish a goal. Removes filler and preserves essential facts, constraints, and decisions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to reduce"
                    },
                    "goal": {
                        "type": "string",
                        "description": "The goal that the context should support"
                    },
                    "max_chunks": {
                        "type": "number",
                        "description": "Maximum number of chunks to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["text", "goal"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "extract_outcomes":
            return await extract_outcomes(arguments)
        elif name == "trim_context":
            return await trim_context(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}")
        raise


def extract_decisions(text: str) -> list[str]:
    """Extract explicit decisions from text using pattern matching."""
    decisions = []

    # Patterns that indicate decisions
    decision_patterns = [
        r'(?:we|they|the team|I)?\s*(?:decided|chose|selected|agreed|concluded)\s+(?:to\s+)?([^.!?\n]+[.!?])',
        r'(?:decision|choice):\s*([^.!?\n]+[.!?])',
        r'(?:will|shall)\s+(?:go with|use|implement|adopt)\s+([^.!?\n]+[.!?])',
    ]

    for pattern in decision_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            decision = match.group(0).strip()
            if decision and decision not in decisions:
                decisions.append(decision)

    return decisions


def extract_action_items(text: str) -> list[str]:
    """Extract explicit action items from text using pattern matching."""
    action_items = []

    # Patterns that indicate action items
    action_patterns = [
        r'(?:TODO|Action|Task|Action item):\s*([^.\n]+\.?)',
        r'(?:will|shall|should|must|need to)\s+([^.!?\n]+[.!?])',
        r'\[(?:TODO|ACTION)\]\s*([^.\n]+\.?)',
        r'(?:^|\n)\s*[-*]\s*([^.\n]+(?:will|should|needs? to|must)[^.\n]+\.?)',
    ]

    for pattern in action_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            action = match.group(0).strip()
            if action and action not in action_items:
                action_items.append(action)

    return action_items


def extract_questions(text: str) -> list[str]:
    """Extract explicit open questions from text."""
    questions = []

    # Find all sentences ending with ?
    question_pattern = r'[^.!?\n]*\?'
    matches = re.finditer(question_pattern, text, re.MULTILINE)

    for match in matches:
        question = match.group(0).strip()
        if question and len(question) > 5:  # Avoid very short matches
            # Clean up the question
            question = re.sub(r'^\s*[-*•]\s*', '', question)
            if question not in questions:
                questions.append(question)

    return questions


async def extract_outcomes(arguments: dict[str, Any]) -> list[TextContent]:
    """Extract explicit outcomes from text."""
    text = arguments.get("text", "")

    if not text:
        return [TextContent(
            type="text",
            text=json.dumps({
                "decisions": [],
                "action_items": [],
                "open_questions": []
            })
        )]

    # Extract each category
    decisions = extract_decisions(text)
    action_items = extract_action_items(text)
    open_questions = extract_questions(text)

    result = {
        "decisions": decisions,
        "action_items": action_items,
        "open_questions": open_questions
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def calculate_relevance_score(chunk: str, goal: str) -> float:
    """Calculate how relevant a chunk is to the goal."""
    goal_words = set(goal.lower().split())
    chunk_words = set(chunk.lower().split())

    # Simple word overlap score
    overlap = len(goal_words & chunk_words)
    return overlap / len(goal_words) if goal_words else 0.0


def is_filler_sentence(sentence: str) -> bool:
    """Check if a sentence is likely filler content."""
    sentence_lower = sentence.lower().strip()

    # Common filler patterns
    filler_patterns = [
        r'^(?:hi|hello|hey|dear|greetings)',
        r'^(?:thanks|thank you|cheers)',
        r'^(?:best|regards|sincerely)',
        r'^(?:hope this helps|let me know)',
        r'^(?:i think|i feel|i believe|in my opinion)',
    ]

    for pattern in filler_patterns:
        if re.match(pattern, sentence_lower):
            return True

    return False


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Simple sentence splitter
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


async def trim_context(arguments: dict[str, Any]) -> list[TextContent]:
    """Reduce text to minimum context for a goal."""
    text = arguments.get("text", "")
    goal = arguments.get("goal", "")
    max_chunks = int(arguments.get("max_chunks", 5))

    if not text or not goal:
        return [TextContent(
            type="text",
            text=json.dumps({"selected_chunks": []})
        )]

    # Split text into sentences
    sentences = split_into_sentences(text)

    # Filter out filler sentences and score remaining ones
    chunks_with_scores = []
    for sentence in sentences:
        if not is_filler_sentence(sentence):
            score = calculate_relevance_score(sentence, goal)
            if score > 0:  # Only include if relevant
                chunks_with_scores.append((sentence, score))

    # Sort by relevance and take top chunks
    chunks_with_scores.sort(key=lambda x: x[1], reverse=True)
    top_chunks = chunks_with_scores[:max_chunks]

    # Format the result
    selected_chunks = []
    for chunk, score in top_chunks:
        selected_chunks.append({
            "text": chunk,
            "reason": f"High relevance to goal (score: {score:.2f})"
        })

    result = {
        "selected_chunks": selected_chunks
    }

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
