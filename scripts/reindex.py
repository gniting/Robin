#!/usr/bin/env python3
"""
reindex.py — Rebuild Robin's review index from topic files

Usage:
  python3 reindex.py

Scans all topic files, extracts entries, and rebuilds the review index from scratch.
Preserves existing ratings and last_surfaced data where the item still exists.
"""

import json
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


def _parse_frontmatter_and_body(text: str) -> tuple[dict, str]:
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


def scan_topics(config: dict) -> list[dict]:
    """Scan all topic files and return a list of entry dicts in file order."""
    vault = Path(config["vault_path"])
    topics_dir = vault / config.get("topics_dir", "topics")

    if not topics_dir.exists():
        return []

    found = []

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
            found.append({
                "topic": topic,
                "filename": filepath.name,
                "date_added": fm.get("date_added"),
                "source": fm.get("source"),
                "tags": fm.get("tags", []),
                "body": body
            })

    return found


def main():
    config = load_config()
    old_index = load_index()

    print("Scanning topic files...")
    entries = scan_topics(config)
    print(f"Found {len(entries)} entries")

    # Preserve old ratings/surfaced data by old-style key (topic:date)
    preserved_ratings = {k: v["rating"] for k, v in old_index["items"].items()}
    preserved_surfaced = {k: (v["last_surfaced"], v["times_surfaced"])
                          for k, v in old_index["items"].items()}

    # Assign seq numbers per topic:date group in file order
    new_items = {}
    seq_counters: dict[tuple, int] = {}

    for entry in entries:
        topic_slug = entry["topic"]
        date_added = entry["date_added"] or ""
        group_key = (topic_slug, date_added)

        if group_key not in seq_counters:
            seq_counters[group_key] = 0

        seq_counters[group_key] += 1
        seq = seq_counters[group_key]
        key = f"{topic_slug}:{date_added}:{seq:03d}"

        # Try to preserve old data by old key format
        old_key = f"{topic_slug}:{date_added}"
        old_rating = preserved_ratings.get(old_key)
        old_surfaced = preserved_surfaced.get(old_key)

        new_items[key] = {
            "topic": topic_slug,
            "date": date_added,
            "seq": f"{seq:03d}",
            "rating": old_rating if old_rating is not None else None,
            "last_surfaced": old_surfaced[0] if old_surfaced else None,
            "times_surfaced": old_surfaced[1] if old_surfaced else 0
        }

    new_index = {
        "items": new_items,
        "config": old_index["config"]
    }

    save_index(new_index)

    rated = sum(1 for v in new_items.values() if v["rating"] is not None)
    print(f"✓ Index rebuilt: {len(new_items)} items, {rated} rated, {len(new_items) - rated} unrated")


if __name__ == "__main__":
    main()
