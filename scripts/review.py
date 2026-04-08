#!/usr/bin/env python3
"""
review.py — Robin review script

Usage:
  python3 review.py                    # Pick and print best candidate
  python3 review.py --rate KEY 5      # Rate an item (overwrites previous)
  python3 review.py --status           # Show review stats without surfacing
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
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


def save_index(index):
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)


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


def load_topics(config: dict) -> dict[str, list[dict]]:
    """Load all topic files. Returns {filename: [entries in file order]}."""
    vault = Path(config["vault_path"])
    topics_dir = vault / config.get("topics_dir", "topics")

    if not topics_dir.exists():
        return {}

    entries_by_file = {}
    for filepath in sorted(topics_dir.glob("*.md")):
        with open(filepath) as f:
            content = f.read().strip()

        raw_parts = content.split(SEPARATOR)
        entries = []

        for part in raw_parts:
            part = part.strip()
            if not part:
                continue
            fm, body = _parse_frontmatter_and_body(part)
            entries.append({
                "date_added": fm.get("date_added"),
                "source": fm.get("source"),
                "tags": fm.get("tags", []),
                "body": body
            })

        if entries:
            entries_by_file[filepath.name] = entries

    return entries_by_file


def pick_best_candidate(index: dict, config: dict, entries_by_file: dict) -> str | None:
    """Pick the best item to surface based on review logic.

    Since entries don't carry a seq field, we match by topic+date and take the
    first matching entry in file order. When multiple index entries share the
    same topic+date, we surface them in seq order.
    """
    cooldown_days = config.get("review_cooldown_days", 60)
    cutoff = datetime.now() - timedelta(days=cooldown_days)

    candidates = []

    for key, item in index["items"].items():
        topic_file = f"{item['topic']}.md"

        if topic_file not in entries_by_file:
            continue

        matched_entry = None
        for entry in entries_by_file[topic_file]:
            if entry["date_added"] == item["date"]:
                matched_entry = entry
                break

        if not matched_entry:
            continue

        if item["last_surfaced"]:
            last = datetime.fromisoformat(item["last_surfaced"])
            if last > cutoff:
                continue

        if item["rating"] is None:
            score = (0, 0)
        else:
            score = (1, item["rating"])

        candidates.append({
            "key": key,
            "item": item,
            "entry": matched_entry,
            "score": score,
            "topic_file": topic_file
        })

    if not candidates:
        return None

    candidates.sort(key=lambda c: (c["score"][0], c["score"][1], c["item"]["times_surfaced"]))
    return candidates[0]


def rate_item(key: str, rating: int, index: dict):
    if key not in index["items"]:
        print(f"ERROR: Item '{key}' not found in index")
        sys.exit(1)

    index["items"][key]["rating"] = rating
    index["items"][key]["last_surfaced"] = datetime.now().isoformat() + "Z"
    index["items"][key]["times_surfaced"] += 1
    save_index(index)
    print(f"✓ Rated {key}: {rating}/5")


def show_status(index: dict, entries_by_file: dict):
    total = len(index["items"])
    rated = sum(1 for i in index["items"].values() if i["rating"] is not None)
    unrated = total - rated
    config = load_config()
    min_items = config.get("min_items_before_review", 30)

    print(f"Review status:")
    print(f"  Total items:  {total}")
    print(f"  Rated:        {rated}")
    print(f"  Unrated:      {unrated}")
    print(f"  Min to review: {min_items}")
    print(f"  Ready:         {'YES' if total >= min_items else 'NO'}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Robin review system")
    parser.add_argument("--status", action="store_true", help="Show review status")
    parser.add_argument("--rate", nargs=2, metavar=("KEY", "RATING"),
                        help="Rate an item (KEY=topic:date:seq)")

    args = parser.parse_args()

    config = load_config()
    index = load_index()
    entries_by_file = load_topics(config)

    if args.rate:
        key, rating = args.rate
        rate_item(key, int(rating), index)
        return

    if args.status:
        show_status(index, entries_by_file)
        return

    total = len(index["items"])
    min_items = config.get("min_items_before_review", 30)

    if total < min_items:
        print(f"SKIP: {total} items (need {min_items})")
        return

    candidate = pick_best_candidate(index, config, entries_by_file)

    if not candidate:
        print("SKIP: No eligible items (all recently surfaced or not indexed)")
        return

    item = candidate["item"]
    entry = candidate["entry"]
    key = candidate["key"]
    topic_file = candidate["topic_file"]

    print(f"[{topic_file}] {key}")
    print(f"Date: {item['date']} | Seq: {item['seq']} | Rating: {item['rating'] or 'unrated'} | Surfaced: {item['times_surfaced']}x")
    if item["tags"]:
        print(f"Tags: {', '.join(item['tags'])}")
    print()
    print(entry["body"])
    print()
    print(f"→ To rate: python3 review.py --rate \"{key}\" <1-5>")


if __name__ == "__main__":
    main()
