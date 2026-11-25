# brain

> Bookmarks are a dump yard. The brain pulls conversations out of it and compounds them into insights.

## Use

```
/brain <idea | link | text>  dump it and keep working; ingested in the background
/brain                       ~10 min conversation session on related topics from the backlog
```

```
dump ──► ingest ──► backlog/
                       │
/brain ──► triage ──► infer from insights ──► convo ──► insights
                            ▲                                │
                            └──────────── compounding ───────┘
```

## Layout

| Path | Holds |
|---|---|
| `SOUL.md` | who you are and how conversations go |
| `brain/backlog/` | open dumps and their ingest output |
| `brain/convo/` | one file per session |
| `brain/insights/` | conclusions, one per topic; `index.md` lists them |
| `brain/archive/` | settled dumps |
| `skill/` | the `/brain` skill |
| `app/` | browser reader: `python3 app/serve.py` |

Plain markdown throughout.

## Install

```sh
git clone https://github.com/smarchone/brain.git ~/brain
npx skills add smarchone/brain -g
echo 'export BRAIN_REPO="$HOME/brain"' >> ~/.zshrc   # or ~/.bashrc
```

The clone holds your brain (`brain/`, `SOUL.md`); the skill is installed as a copy, so `BRAIN_REPO` tells it where the clone is. Open a new shell after setup. Needs `yt-dlp` for video transcripts.
