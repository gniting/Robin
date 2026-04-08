#!/usr/bin/env python3
"""
add_entry.py — Robin add entry script

Usage:
  python3 add_entry.py --topic "AI Reasoning" --content "..." [--source URL] [--note "..."] [--tags tag1,tag2]
"""

import argparse
import json
from datetime import date
from pathlib import Path

CONFIG_PATH = Path.home() / ".hermes" / "data" / "cb-config.json"
INDEX_PATH = Path.home() / ".hermes" / "data" / "cb-review-index.json"
SEPARATOR = "\n***\n"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_index():
    if INDEX_PATH.exists():
        with open(INDEX_PATH) as f:
            return json.load(f)
    return {"items": {}, "config": {"min_items_before_review": 30, "review_cooldown_days": 60}}


def save_index(index):
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)


def topic_to_filename(topic: str) -> str:
    return topic.lower().replace(" ", "-") + ".md"


def build_entry(content: str, source: str | None, note: str | None, tags: list[str], date_added: str) -> str:
    """Build an entry: frontmatter + blank line + body."""
    fm = f"""\
date_added: {date_added}
source: {source or ""}
tags: [{", ".join(tags)}]"""

    body_parts = []
    if source:
        body_parts.append(f"**Source:** {source}")
        body_parts.append("")
    body_parts.append(content)
    if note:
        body_parts.append("")
        body_parts.append(f"**Robin note:** {note}")

    return fm + "\n\n" + "\n".join(body_parts)


def add_to_topic(config: dict, topic: str, entry: str):
    vault = Path(config["vault_path"])
    topics_dir = vault / config.get("topics_dir", "topics")
    topics_dir.mkdir(parents=True, exist_ok=True)
    filepath = topics_dir / topic_to_filename(topic)

    if filepath.exists():
        with open(filepath) as f:
            content = f.read().rstrip()
        out = content + SEPARATOR + entry
    else:
        out = entry

    with open(filepath, "w") as f:
        f.write(out + "\n")


def _make_key(topic: str, date_added: str, seq: int) -> str:
    return f"{topic.lower().replace(' ', '-')}:{date_added}:{seq:03d}"


def _parse_seq_from_key(key: str) -> int:
    """Extract seq number from a key like 'ai-reasoning:2026-04-08:001'."""
    return int(key.split(":")[-1])


def register_in_index(topic: str, date_added: str, index: dict):
    """Register a new entry in the index with a unique topic:date:seq key."""
    topic_slug = topic.lower().replace(" ", "-")
    date_key = f"{topic_slug}:{date_added}"

    # Find the highest existing seq for this topic+date
    existing_seqs = [
        _parse_seq_from_key(k)
        for k in index["items"]
        if k.startswith(date_key + ":")
    ]
    next_seq = (max(existing_seqs) + 1) if existing_seqs else 1

    key = _make_key(topic, date_added, next_seq)
    index["items"][key] = {
        "topic": topic_slug,
        "date": date_added,
        "seq": f"{next_seq:03d}",
        "rating": None,
        "last_surfaced": None,
        "times_surfaced": 0
    }
    save_index(index)
    return key


def main():
    parser = argparse.ArgumentParser(description="Add an entry to Robin's commonplace book")
    parser.add_argument("--topic", required=True, help="Topic name")
    parser.add_argument("--content", required=True, help="Content to file")
    parser.add_argument("--source", help="Source URL")
    parser.add_argument("--note", help="Robin note")
    parser.add_argument("--tags", default="", help="Comma-separated tags")

    args = parser.parse_args()

    config = load_config()
    index = load_index()

    topic = args.topic.strip()
    date_added = str(date.today())
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    entry = build_entry(
        content=args.content.strip(),
        source=args.source.strip() if args.source else None,
        note=args.note.strip() if args.note else None,
        tags=tags,
        date_added=date_added
    )

    add_to_topic(config, topic, entry)
    key = register_in_index(topic, date_added, index)

    filename = topic_to_filename(topic)
    print(f"✓ Filed under [{topic}]({filename})")


if __name__ == "__main__":
    main()
