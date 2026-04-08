#!/usr/bin/env python3
"""
topics.py — List all Robin topics

Usage:
  python3 topics.py         # List all topics with stats
  python3 topics.py --json  # Output as JSON
"""

import argparse
import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".hermes" / "data" / "cb-config.json"
INDEX_PATH = Path.home() / ".hermes" / "data" / "cb-review-index.json"
SEPARATOR = "\n***\n"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_index():
    with open(INDEX_PATH) as f:
        return json.load(f)


def count_entries_in_file(filepath: Path) -> int:
    with open(filepath) as f:
        content = f.read().strip()
    if not content:
        return 0
    return content.count(SEPARATOR) + 1


def main():
    parser = argparse.ArgumentParser(description="List all Robin topics")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    config = load_config()
    index = load_index()

    vault = Path(config["vault_path"])
    topics_dir = vault / config.get("topics_dir", "topics")

    if not topics_dir.exists():
        print("No topics directory found." if not args.json else "{}")
        return

    topics = []
    for filepath in sorted(topics_dir.glob("*.md")):
        topic = filepath.stem
        entry_count = count_entries_in_file(filepath)

        rated = 0
        unrated = 0
        for key, item in index.get("items", {}).items():
            # Keys are topic:date:seq — match by topic prefix
            key_topic = key.split(":")[0]
            if key_topic == topic:
                if item.get("rating") is not None:
                    rated += 1
                else:
                    unrated += 1

        topics.append({
            "topic": topic,
            "filename": filepath.name,
            "entries": entry_count,
            "rated": rated,
            "unrated": unrated
        })

    if args.json:
        print(json.dumps(topics, indent=2))
        return

    if not topics:
        print("No topics yet. Start filing things with Robin!")
        return

    total_entries = sum(t["entries"] for t in topics)
    print(f"{len(topics)} topics, {total_entries} total entries\n")

    for t in topics:
        stars = "★" * t["rated"] + "☆" * t["unrated"] if t["rated"] or t["unrated"] else ""
        print(f"  {t['topic']}")
        print(f"    {t['entries']} entries  {stars}")
        print()


if __name__ == "__main__":
    main()
