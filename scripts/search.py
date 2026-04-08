#!/usr/bin/env python3
"""
search.py — Search Robin's commonplace book

Usage:
  python3 search.py <query>          # Search entry bodies and sources
  python3 search.py --topic <name>  # List all entries in a topic
  python3 search.py --tags tag1,tag2 # Find entries with these tags
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


def _parse_frontmatter_and_body(text: str) -> tuple[dict, str]:
    """Frontmatter: key:value lines until first blank line. Body: rest."""
    lines = text.split("\n")
    fm = {}
    body_start = 0
    for i, line in enumerate(lines):
        if not line.strip():
            body_start = i + 1
            break
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip()
            if key == "date_added":
                fm["date_added"] = val
            elif key == "source":
                fm["source"] = val
            elif key == "tags":
                fm["tags"] = [t.strip().rstrip("]") for t in val.split(",")]
    body = "\n".join(lines[body_start:]).strip()
    return fm, body


def load_all_entries(config: dict) -> list[dict]:
    """Load all entries from all topic files in file order."""
    vault = Path(config["vault_path"])
    topics_dir = vault / config.get("topics_dir", "topics")

    if not topics_dir.exists():
        return []

    all_entries = []

    for filepath in sorted(topics_dir.glob("*.md")):
        topic = filepath.stem

        with open(filepath) as f:
            content = f.read().strip()

        raw_parts = content.split(SEPARATOR)

        for part in raw_parts:
            part = part.strip()
            if not part:
                continue
            fm, body = _parse_frontmatter_and_body(part)
            entry = {
                "topic": topic,
                "filename": filepath.name,
                "date_added": fm.get("date_added"),
                "source": fm.get("source"),
                "tags": fm.get("tags", []),
                "body": body
            }
            all_entries.append(entry)

    return all_entries


def search_entries(entries: list[dict], query: str) -> list[dict]:
    q = query.lower()
    return [e for e in entries
            if q in e["body"].lower() or (e["source"] and q in e["source"].lower())]


def filter_by_topic(entries: list[dict], topic: str) -> list[dict]:
    return [e for e in entries if e["topic"] == topic]


def filter_by_tags(entries: list[dict], tags: list[str]) -> list[dict]:
    results = []
    for e in entries:
        entry_tags = {t.lower() for t in e["tags"]}
        if all(t.lower() in entry_tags for t in tags):
            results.append(e)
    return results


def _find_index_key(topic: str, date_added: str, seq: str, index: dict) -> str | None:
    """Look up a rating from the index by topic+date+seq."""
    key_candidate = f"{topic}:{date_added}:{seq}"
    return key_candidate if key_candidate in index.get("items", {}) else None


def print_entry(e: dict, index: dict, entry_seq: int | None = None):
    topic_slug = e["topic"]
    date_added = e["date_added"] or ""
    seq = f"{entry_seq:03d}" if entry_seq is not None else None

    # Try to find the right index key
    rating = "—"
    if seq:
        key = _find_index_key(topic_slug, date_added, seq, index)
        if key:
            rating = index["items"][key].get("rating") or "—"

    print(f"[{e['filename']}] {topic_slug} / {date_added}  ★{rating}")
    if e["source"]:
        print(f"  Source: {e['source']}")
    if e["tags"]:
        print(f"  Tags: {', '.join(e['tags'])}")

    body = e["body"].replace("\n", " ").strip()
    print(f"  {body[:200]}{'...' if len(body) > 200 else ''}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Search Robin's commonplace book")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--topic", help="Filter by topic name")
    parser.add_argument("--tags", help="Comma-separated tag filter")

    args = parser.parse_args()

    config = load_config()
    index = load_index()
    entries = load_all_entries(config)

    if args.topic:
        entries = filter_by_topic(entries, args.topic)
        print(f"Topic '{args.topic}': {len(entries)} entries")
    elif args.tags:
        tags = [t.strip() for t in args.tags.split(",")]
        entries = filter_by_tags(entries, tags)
        print(f"Tags [{', '.join(tags)}]: {len(entries)} results")
    elif args.query:
        entries = search_entries(entries, args.query)
        print(f"Query '{args.query}': {len(entries)} results")
    else:
        print(f"Total: {len(entries)} entries\n")

    # Assign seq numbers for display/rating lookup
    seq_counters: dict[tuple, int] = {}
    for e in entries:
        group_key = (e["topic"], e["date_added"] or "")
        if group_key not in seq_counters:
            seq_counters[group_key] = 0
        seq_counters[group_key] += 1
        print_entry(e, index, seq_counters[group_key])


if __name__ == "__main__":
    main()
