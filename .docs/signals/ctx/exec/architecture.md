# Architecture
> A global skill reading and writing one private folder of plain markdown.

## Shape
```
  any Claude Code session, any repo
            │  /brain
            ▼
  ~/.claude/skills/brain ──symlink──► brain repo
                                        README.md
                                        SOUL.md       who the user is; how conversations go
                                        skill/        SKILL.md + scripts/brain.py
                                        app/          serve.py + view.html: read the brain in a browser
                                        brain/        the data, gitignored: never committed
                                          backlog/    one file per dump; ingest writes into it
                                          convo/      one file per session: raw convo, key turns, summary
                                          insights/   index.md + one file per topic: the user's learnings and ahas
                                          convo-index.md  generated registry of every convo, brain's and golden
                                          golden-sync.md  golden sync ledger
                                          archive/    dumps a session settled
```

## Hard lines
- The brain folder is the only state; the skill holds none.
- Everything is plain markdown a human can read and edit.
- The brain is private.

## Decisions
- One global skill whose source lives in the brain repo's skill/, symlinked to ~/.claude/skills/brain; `$BRAIN_REPO` overrides the repo.
  why: things are found in every repo; the skill and the brain evolve together
  not: per-project stores; a required environment variable
- The data folders (backlog/, convo/, insights/, archive/) live under brain/ in the repo; README.md, SOUL.md and skill/ stay at the root.
  why: the repo root stays uncluttered; the data is one folder
  not: data folders at the repo root
- A dump and its ingest output live in one file in backlog/; nothing about a source is stored outside it.
  why: one record per item; the brain keeps conclusions, not sources
  not: a separate store for transcripts or summaries
- convo/ is bucketed by session: `convo/<YYYY-MM-DD>-<name>.md` holds the session's relevant turns, its key turns and a summary; the summary is the session log.
  why: the conversation is where the user's thinking happened; keeping it raw means an insight can always be traced back
  not: a separate log.md; keeping only the conclusion
- Convo files use golden-convo's format (frontmatter title, why, captured, golden_turns, labels, tags; turns as `### n · **role:**`); key turns are `golden_turns`, topics are `labels`, and `tags` are the tags of the convo's dumps, merged in order with duplicates dropped (none when it used no dumps).
  why: the brain's copy of golden-convo's page renders them, with key turns in full and the rest folded; inherited tags make convos findable by subject, as their sources are
  not: a brain-only format with a `## Key turns` section; a separate viewer; the agent choosing new tags at close; tags only on dumps (convos had topic labels alone)
- `app/view.html` is the brain's own copy of golden-convo's page, tailored: no analytics, no golden branding, "key" turns, the convo's summary, topics, dumps and session turns shown, plus Insights and Backlog views. `app/serve.py` serves it on 127.0.0.1, rebuilt per request, or writes it to a file; never published.
  why: the brain renders its convos without depending on the golden-convo repo, and private titles never reach analytics
  not: rendering through $GOLDEN_REPO's index.html; deploying the brain to a site; a page without the backlog
- A convo file keeps only the turns relevant to the cluster's thinking; procedural turns (the /brain prompt, other threads, dumps, clarifications, notifications, the close) are dropped. Kept turns are renumbered from 1, and `source_turns` records their numbers in the session.
  why: a convo is read for the thinking; the whole session is noise and costs attention
  not: dumping the entire session into convo/
- The raw conversation in a convo file comes from the session log via brain.py's extractor (copied from golden's), never written by the agent; curation chooses turns and never edits their text.
  why: an agent recalling a conversation paraphrases it
  not: the agent rewriting the conversation from memory
- insights/ is bucketed by topic: one `insights/<topic>.md` per topic; each insight's second line carries two backlinks to the convo behind it: the web link for the viewer, then the file path (`$GOLDEN_REPO/<YYYY-MM>/<id>.md` or `convo/<file>.md`) for progressive disclosure. Insights from golden sessions cite the public golden page (`https://smarchone.github.io/golden-convo/#<id>`) directly; no convo/ file is made for a golden session.
  why: conclusions build up by subject across sessions, not by date; golden sessions are public and hosted already; the web link renders in the app and the path lets an agent open the source with a plain file read
  not: one insights.md; one note per thread; a convo/ stub per golden session holding its Summary and labels (duplicated title and why, and filled convo/ with files that aren't brain conversations); the web link alone (the agent needs a script or a fetch to drill down)
- `insights/index.md` holds one line per topic (its file, the user's current stance, last update). `brain/convo-index.md` is a cached registry of every convo, brain's and golden: title, why, labels and path, newest first, like a skill's name and description. A session's entrypoint is the convo index plus the insights index; topic files and convos open only on demand.
  why: session start stays fast as the brain grows; the pattern of how coding agents register skills: descriptions always loaded, bodies loaded when needed; the name says what it holds and pairs with insights/index.md
  not: reading every topic file at every session; the index alone as the entrypoint (past convos were invisible to triage); reading convos at session start; naming it catalog.md (the name didn't say what's inside)
- Settled dumps move to archive/ unchanged.
  why: backlog/ stays small enough to read whole at triage
  not: deleting them; keeping them in backlog/
- `SOUL.md` at the repo root defines how conversations take place and who the user is; every session reads it first, and it wins over SKILL.md on conversation style.
  why: the conversation is the product, and its style belongs to the user, editable without touching the skill
  not: conversation style buried in SKILL.md
- The brain stays private.
  why: dumps hold half-formed thoughts and work material
  not: publishing by default; a session worth sharing goes through /golden
- The repo is pushed to a private GitHub repo; brain/ is gitignored and absent from every commit, so the data exists only in the local folder.
  why: the repo carries the code (skill, app, SOUL, README); the brain's data is personal and never leaves the machine
  not: committing brain/ to a private remote (the data would sit on GitHub, in history for good)
- The app lives in app/, outside the skill; the skill never serves or renders pages.
  why: reading the brain in a browser is a tool for the user, not a step in the pipeline; the skill stays small
  not: view and serve commands in brain.py
- `brain/golden-sync.md` is the golden sync ledger, one line per synced session: `- <id> · <topics, or "nothing kept"> · synced <YYYY-MM-DD>`; a golden session counts as synced when it's listed there or a brain convo carries its session_id.
  why: with no convo/ stub, sync state needs a home, including sessions that kept nothing so they aren't listed again; the name says what it records
  not: deriving sync state from insight citations alone (a session with nothing kept would be offered forever); state outside the brain folder; naming it golden.md (didn't say it's the sync ledger); golden-sync.log (breaks the plain-markdown hard line, and `*.log` is skipped or ignored by common tools)
