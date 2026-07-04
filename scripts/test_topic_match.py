#!/usr/bin/env python3
"""CLI to test layperson topic pattern matching."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.src.services.layperson_topic_service import LaypersonTopicService


def main() -> None:
    parser = argparse.ArgumentParser(description="Test layperson topic matching")
    parser.add_argument("--topic", help="Expected topic id")
    parser.add_argument("--should-match", action="append", default=[], dest="should_match")
    parser.add_argument("--should-not-match", action="append", default=[], dest="should_not_match")
    args = parser.parse_args()
    service = LaypersonTopicService()
    failed = False
    for question in args.should_match:
        match = service.match(question)
        got = match.topic_id if match else None
        if args.topic and got != args.topic:
            print(f"FAIL match: {question!r} -> {got} (expected {args.topic})")
            failed = True
        elif not match:
            print(f"FAIL no match: {question!r}")
            failed = True
        else:
            print(f"OK match: {question!r} -> {got}")
    for question in args.should_not_match:
        match = service.match(question)
        if match and (not args.topic or match.topic_id == args.topic):
            print(f"FAIL unexpected: {question!r} -> {match.topic_id}")
            failed = True
        else:
            print(f"OK no match: {question!r}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
