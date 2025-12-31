#!/usr/bin/env python3
"""Basic functionality tests for the MCP text intelligence server."""

import sys
sys.path.insert(0, '.')

from server import extract_decisions, extract_action_items, extract_questions
from server import calculate_relevance_score, is_filler_sentence, split_into_sentences

def test_extract_decisions():
    text = "We decided to use PostgreSQL. The team agreed to move forward."
    decisions = extract_decisions(text)
    print(f"✓ extract_decisions: Found {len(decisions)} decisions")
    for d in decisions:
        print(f"  - {d}")

def test_extract_action_items():
    text = "John will set up the environment. TODO: Review the documentation. We must complete this by Friday."
    actions = extract_action_items(text)
    print(f"✓ extract_action_items: Found {len(actions)} action items")
    for a in actions:
        print(f"  - {a}")

def test_extract_questions():
    text = "Should we use Docker? How do we handle authentication? This works fine."
    questions = extract_questions(text)
    print(f"✓ extract_questions: Found {len(questions)} questions")
    for q in questions:
        print(f"  - {q}")

def test_relevance_score():
    chunk = "The API requires authentication and rate limiting"
    goal = "API requirements"
    score = calculate_relevance_score(chunk, goal)
    print(f"✓ calculate_relevance_score: score={score:.2f}")

def test_filler_detection():
    filler = "Hi there, hope you're well"
    non_filler = "The deadline is March 15th"
    print(f"✓ is_filler_sentence:")
    print(f"  - '{filler}' is filler: {is_filler_sentence(filler)}")
    print(f"  - '{non_filler}' is filler: {is_filler_sentence(non_filler)}")

def test_sentence_splitting():
    text = "First sentence. Second sentence! Third sentence?"
    sentences = split_into_sentences(text)
    print(f"✓ split_into_sentences: Found {len(sentences)} sentences")

if __name__ == "__main__":
    print("Testing MCP Text Intelligence Functions\n")
    test_extract_decisions()
    print()
    test_extract_action_items()
    print()
    test_extract_questions()
    print()
    test_relevance_score()
    print()
    test_filler_detection()
    print()
    test_sentence_splitting()
    print("\n✅ All basic tests passed!")
