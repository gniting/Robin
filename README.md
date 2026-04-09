# Robin

Use your fav AI agent to curate a digital commonplace book. You feed Robin things you want to remember — quotes, articles, links, thoughts, images, and video links — and it files them into topic-organized markdown files. Robin also runs a spaced-repetition review engine that surfaces items on a schedule so you reinforce learning over time.

> Dedicated to and named for [Robin Williams'](https://en.wikipedia.org/wiki/Robin_Williams) portrayal of Sean Maguire in *[Good Will Hunting](https://en.wikipedia.org/wiki/Good_Will_Hunting)* — a therapist who helped a brilliant but lost young man find his voice.

## What is a Commonplace Book?

A commonplace book[[1](https://ryanholiday.net/how-and-why-to-keep-a-commonplace-book/)][[2](https://en.wikipedia.org/wiki/Commonplace_book)] is a personal collection of ideas, phrases, and passages worth keeping. Traditionally, it is a notebook where one gathers quotations, observations, arguments, anecdotes, and striking turns of phrase from what they read or hear, then organizes them so those pieces can be revisited and used later. 
One of its most practical benefits is that it sharpens vocabulary: by repeatedly noticing, recording, and returning to precise language, a reader begins to absorb better words, clearer sentence patterns, and more nuanced ways of expressing ideas. That expanded command of language tends to improve communication, because stronger vocabulary makes it easier to speak and write with accuracy, persuasion, and confidence. 
Over time, a commonplace book becomes more than a record of reading. It turns into a tool for better thinking, better communication, and, by extension, better work, relationships, and decision-making.

## Features

- Filing — Send Robin any content and it determines the right topic, files it away, and confirms
- Media-aware filing — Local images are copied into the vault, video URLs are stored by reference, and uploaded/local video files are rejected
- Topic management — Creates new topics on demand, suggests topic names, resolves conflicts
- Spaced repetition review — Surfaces items on a configurable schedule so you reinforce learning
- Rating — Rate surfaced items 1–5; Robin tracks what you care about most over time
- Searchable vault — All entries live in plain markdown topic files; open in Obsidian, Logseq, or any editor
- Agent-agnostic — Works with any agent that implements a skills interface

## Prerequisites

- An agent host that supports local, filesystem-backed skills
- Python 3.11+
- A local vault directory

## Quick Start

### 1. Install the skill

Make the Robin directory available to your agent host using that host's normal local-skill mechanism.

### 2. Run setup

```bash
bash /path/to/robin/install.sh
```

Optional:

```bash
bash /path/to/robin/install.sh --robin-home /path/to/robin-runtime
```

By default, Robin stores:

- config in `${XDG_CONFIG_HOME:-~/.config}/robin/robin-config.json`
- review state in `${XDG_DATA_HOME:-~/.local/share}/robin/robin-review-index.json`

If `ROBIN_HOME` is set, Robin instead uses:

- `$ROBIN_HOME/config/robin-config.json`
- `$ROBIN_HOME/data/robin-review-index.json`

### 3. Create your vault

```bash
mkdir -p /path/to/your/vault/topics /path/to/your/vault/media
```

### 4. Start filing

Example:

```text
Robin, save this quote:
"The most important thing is to decide what you are optimizing for."
```

For media items, the host agent must also provide:

- `description` for every entry
- `creator`, `published_at`, and `summary` for image and video entries

### 5. Review saved items

```bash
robin-review
robin-review --rate 20260408-a1f3 5
```

## What Robin Stores

- Topic files in your vault under `topics/`
- Copied images in your vault under `media/<topic>/`
- Review metadata in Robin's runtime data directory

Robin stores content and review state. The host agent is responsible for topic selection, contextual summaries, and media metadata extraction.

If your host agent supports file indexing, it should include Robin's topic files in its normal searchable corpus. Use host/global search for broad semantic recall, and use `robin-search` when you need Robin-specific structured lookup by topic, tags, ids, or Robin metadata.

## Commands

Installed CLI entry points:

- `robin-add`
- `robin-review`
- `robin-reindex`
- `robin-search` for Robin-specific structured lookup
- `robin-topics`

Repo-local script entry points:

- `python3 scripts/add_entry.py`
- `python3 scripts/review.py`
- `python3 scripts/reindex.py`
- `python3 scripts/search.py`
- `python3 scripts/topics.py`

Examples:

```bash
robin-search "clear thinking"
robin-topics --json
robin-add --topic "reasoning" --content "The most important thing is to decide what you are optimizing for." --description "A short Paul Graham line about choosing the objective before optimizing. Useful when reviewing tradeoff-heavy decisions."
```

## More Detail

See [docs/guide.md](docs/guide.md) for:

- topic file format and media rules
- runtime paths and configuration
- review/index behavior
- when to use host search vs `robin-search`
- host-specific examples
- compatibility notes and error behavior

## License

MIT — see [LICENSE](LICENSE)
