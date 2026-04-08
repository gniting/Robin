# Robin  ·  [skills.sh](https://github.com/vercel-labs/skills)

A digital commonplace book for AI agents — collect, curate, and periodically review items from your personal digital Commonplace Book

## What is a Commonplace Book?

A commonplace book is a personal collection of ideas, phrases, and passages worth keeping. Traditionally, it is a notebook where someone gathers quotations, observations, arguments, anecdotes, and striking turns of phrase from what they read or hear, then organizes them so those pieces can be revisited and used later. One of its most practical benefits is that it sharpens vocabulary: by repeatedly noticing, recording, and returning to precise language, a reader begins to absorb better words, clearer sentence patterns, and more nuanced ways of expressing ideas. That expanded command of language tends to improve communication, because stronger vocabulary makes it easier to speak and write with accuracy, persuasion, and confidence. Over time, a commonplace book becomes more than a record of reading. It turns into a tool for better thinking, better communication, and, by extension, better work, relationships, and decision-making.


> Named for Robin Williams' portrayal of Sean Maguire in *Good Will Hunting* — a therapist who helped a brilliant but lost young man find his voice.

## Features

You feed Robin things you want to remember — quotes, articles, links, thoughts — and it files them into topic-organized markdown files. Robin also runs a spaced-repetition review engine that surfaces items on a schedule so you reinforce learning over time.

- Filing — Send Robin any content and it determines the right topic, files it away, and confirms
- Topic management — Creates new topics on demand, suggests topic names, resolves conflicts
- Spaced repetition review — Surfaces items on a configurable schedule so you reinforce learning
- Rating — Rate surfaced items 1–5; Robin tracks what you care about most over time
- Searchable vault — All entries live in plain markdown topic files; open in Obsidian, Logseq, or any editor
- Agent-agnostic — Works with any agent that implements a skills interface

## Prerequisites

- An AI agent that supports skills (Hermes, OpenClaw, Claude Code, Codex, etc.)
- Python 3.11+ (for the supporting scripts)
- A vault directory on the skill host (local filesystem)

## Quick Start

### 1. Install the skill

Hermes:
```
hermes skills install ~/.hermes/skills/personal/robin
```

OpenClaw / Claude Code / Codex: refer to your agent's docs for loading a skill from a local path.

### 2. First-run setup

Run the install script:
```
bash ~/.hermes/skills/personal/robin/install.sh
```

This creates `~/.hermes/data/cb-config.json` from the example template. Alternatively, create it manually:
```json
{
  "vault_path": "/path/to/your/vault",
  "topics_dir": "topics",
  "min_items_before_review": 30,
  "review_cooldown_days": 60,
  "preferred_rating_scale": "1-5",
  "file_naming": "kebab"
}
```

### 3. Create your vault directory

```bash
mkdir -p /path/to/your/vault/topics
```

### 4. Start filing

Just send Robin things you want to collect:

```
Robin, this quote from Paul Graham:
"The most important thing is to decide what you are optimizing for."
```

Robin will file it under an appropriate topic and confirm.

### 5. Set up review cron

Create a cron job for daily review (example: noon on weekdays):

```bash
hermes cron create \
  --name "robin:review" \
  --prompt "Run Robin's review mode..." \
  --schedule "0 12 * * 1-5" \
  --skills robin \
  --deliver origin
```

## Vault Structure

```
vault_path/
  topics/
    reasoning.md
    lyrics.md
    poerty.md
    idioms.md
    quotes.md
    ...
```

Topic filename format: lowercase, spaces become dashes (e.g. "Song Lyrics" -> `song-lyrics.md`).

## Topic File Format

Entries are separated by `***`. Each entry has a frontmatter block (key:value lines) followed by a blank line, then the body text.

```
date_added: 2026-04-08
source: https://example.com/article
tags: [ai, reasoning]

**Source:** [article title](https://example.com/article)

Notable excerpt or the thing you sent.

**Robin note:** Brief curation note
***
date_added: 2026-04-08
source: https://example.com/other
tags: [books]

Another entry body here.
```

Frontmatter keys are matched case-insensitively. A blank line must separate frontmatter from body.

## Commands

- `robin review` — Manually trigger a review cycle
- `robin reindex` — Rebuild review index from topic files
- `robin search <query>` — Search all topics for matching entries
- `robin topics` — List all existing topics
- `robin add` — File something new (or just send content directly)
- `robin setup` — First-run config wizard

## Review System

Robin maintains a review index (`~/.hermes/data/cb-review-index.json`) that tracks:

- rating — your 1–5 rating (overwritten on each new rating)
- last_surfaced — when Robin last showed you this item
- times_surfaced — how many times Robin has surfaced it

When review fires:

1. Robin picks the best candidate (unrated first, then lowest rating, then least recently surfaced)
2. Skips items surfaced within the last `review_cooldown_days`
3. Surfaces the item with context
4. You rate it 1–5
5. Robin updates the index

Robin only triggers a review when you have at least `min_items_before_review` items in your vault.

## Configuration Reference

| Key | Default | Description |
|---|---|---|
| `vault_path` | required | Path to your vault root |
| `topics_dir` | `"topics"` | Subdirectory for topic files |
| `min_items_before_review` | `30` | Min items before review triggers |
| `review_cooldown_days` | `60` | Days before an item can be surfaced again |
| `preferred_rating_scale` | `"1-5"` | Rating scale (currently fixed to 1-5) |
| `file_naming` | `"kebab"` | Filename convention (kebab-case) |

## Syncing to Other Devices

Robin writes to a local vault path. To access it from other devices:

- Rsync over SSH — periodically sync the vault to your other devices
- SMB share — mount the vault directory on your MacBook
- Git — commit and push the vault to a private Git repo, pull on other devices

Syncing is not built into Robin; choose the method that fits your setup.

## License

MIT — see [LICENSE](LICENSE)
