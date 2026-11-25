---
name: brain
description: Conversation pipeline for things found mid-work. `/brain <idea | link | text>` dumps an idea, concept, blog, video or podcast and returns at once, while a background agent ingests it; bare `/brain` starts a session where triage picks related saves, the agent infers from past insights, and the user talks it through to a sharper conclusion; `/brain sync-golden` distills past golden sessions into insights. Use when the user runs /brain, asks to save something "for later" or "to my brain", wants a brain session, or wants golden sessions synced into insights.
---

# Brain

Bookmarks store links. Memory layers store facts. The brain prepares conversations.

```
dump ──► ingest                                 (per item, background, no user)
              │
              ▼
           backlog/  (never shown)
              │
/brain ──► triage ──► infer from insights ──► convo ──► insights
                            ▲               convo/      insights/<topic>.md
                            │               by session  by topic, via index.md
                            └──────── compounding ───────────┘
```

Convo → insights is progressive summarization: the convo file keeps the raw conversation, its
key turns and a summary; the insight distills it further and links back, so nothing is lost.

Find the brain folder with `python3 <skill-dir>/scripts/brain.py root`. All paths below are
relative to it. Everything is plain markdown; never keep state anywhere else.

- **Keep what the user took away, not sources.** Source text lives only inside its dump file.
  convo/ holds the user's own thinking; insights/ holds their learnings and aha moments,
  never a source's text.
- **Never show the pile.** No counts, no lists of saves, no "you have N items". The user sees one
  prepared conversation.

A dump's `status:` is its stage: `dumped` → `ingested` → `distilled` or `released`.

## Dump: `/brain <thing>`

The user is mid-work. Store it and get out of the way.

1. Write `backlog/<YYYY-MM-DD>-<slug>.md` (add `-2`, `-3` on a clash):

   ```
   ---
   added: <ISO local time>
   kind: <idea | concept | blog | video | podcast | text>
   source: <url, if any>
   found_while: <what the user was doing, one line, from this session; never ask>
   status: dumped
   ---
   <exactly what the user gave: the url, the pasted text verbatim, or the idea in their words>
   ```

2. Start ingest for that file as a background agent (see Ingest), without waiting for it.
3. Reply with one line: `dumped: <a few words naming it>`. Nothing else.

Don't fetch, summarize or ask anything at dump. If the user pasted full content, keep it
verbatim; it might not be online later.

## Ingest (one item, background)

Turn one dump into something quick to talk about. Ingest never reads insights/.

Do what fits the kind:
- **blog / link**: fetch the page and keep its main text.
- **video**: `python3 <skill-dir>/scripts/brain.py transcript <url>` prints the transcript; keep it.
- **podcast**: try `transcript` too; if there's none, keep the episode page's show notes.
- **idea / concept / text**: nothing to fetch; the user's words are the content.

If a fetch fails, keep what the dump already holds and note `fetch failed` in the Ingest section.

Append to the dump file, and set `status: ingested` with `tags: [<2-4 short tags>]` in its
frontmatter:

```
## Ingest <YYYY-MM-DD>
claim: <the item's core claim or question, one line>
gist: <at most 3 lines: the argument, in plain words>
key: <the 2-4 best lines from the source, verbatim>

### Source
<the fetched text or transcript, as is>
```

## Session: `/brain`

A short conversation with someone who read the user's saves and remembers what they concluded.

**Read `../SOUL.md` first** (it sits at the repo root, beside `brain/`). It defines who the user is and how every turn of the conversation
goes: how to open, ask, push back, handle tangents and close. Where it and this file differ on
conversation style, SOUL.md wins.

### 1. Triage (silent)

- Ingest any dump still `status: dumped` first (`brain.py backlog` lists them with their status).
- `brain.py catalog` rebuilds `convo-index.md`, the registry of every past convo (brain's and golden):
  title, why, labels, tags and path, like a skill's name and description. Read it and
  `insights/index.md` (one line per topic). These two are the entrypoint; don't open topic files
  or convos yet.
- From the `claim`, `gist` and `tags` of every `ingested` dump, plus the convo index and the insights index,
  group items by the question they're really about, across every repo and date.
- Pick **one cluster**, usually 2-4 items (one is fine if it stands alone). Rank by tension:
  items that disagree with each other or with an insight first, then items that extend an
  insight, then the repo `/brain` was run from, then age.

### 2. Infer (silent)

Read the topic files in `insights/` that the cluster touches, per the index, and the picked
items' Ingest sections. Then disclose progressively: open a past convo (from the convo index, or the
file path on an insight's second line) only when it's central and you need how the user got
there, or a fact behind a learning. Facts live there, not in insights. Read a brain convo's
Summary and Key turns first, a golden file's `golden_turns` first, the rest only if needed.
For the cluster, work out:
- which insights it **confirms**, **contradicts** or **extends**, quoted with their dates;
- where the items disagree with each other;
- the one question or tension the conversation should open on;
- why it matters to the user now, and what they could walk away with (for the briefing).

Never frame it as a summary of what the items say.

### 3. Open

A three-line briefing, as SOUL.md lays out: what it's about (the cluster and what it pushes on
from the user's past thinking), why it matters, and what they could walk away with. Then the
opening question. The user can take it, reshape it, or name another topic (then triage for that
topic on the spot).

### 4. Convo

The user thinks out loud; you bring what you inferred. Ask, don't lecture. Quote past insights
when they bear on it ("in July you concluded X; does this change it?"). Go into a source's text
only when the user wants. Keep it short.

### 5. Close

When the thread has run its course, propose in one reply and let the user confirm or change it:
- **the conclusion**, in the user's words where possible, and how it merges (below);
- per item: **distilled** (it fed the conclusion) or **released** (let go); items the
  conversation didn't reach stay `ingested`, untouched.

Then, in order:

1. **Convo file (session-bucketed, relevant turns only).** From the session's working directory:

   1. `python3 <skill-dir>/scripts/brain.py convo <name> --list` prints the session's turns,
      numbered from the bare `/brain`.
   2. Pick the turns that carry the thinking on this cluster: the opening tension, the user's
      reasoning, the pushback that moved it. Drop the rest: the `/brain` prompt itself, other
      threads, dumps, clarifications that didn't move the thinking, task notifications, and the
      close (verdicts, confirmations).
   3. `brain.py convo <name> --keep 2-5,8` writes `convo/<YYYY-MM-DD>-<name>.md` with only those
      turns, verbatim from the session log and renumbered from 1, and prints its path.

   Never write or edit the conversation's text yourself; curation is choosing turns, not
   rewriting them. The file uses golden-convo's format, so the golden site's page renders it. Fill:

   - `title:` what the session found, a short phrase;
   - `why:` the conclusion in one line, in the user's words;
   - `golden_turns:` the 2-4 turns where the thinking turned (the key turns);
   - `labels:` the insight topics it touched; `dumps:` the dumps it used;
   - `tags:` the `tags:` of those dumps, merged in order with duplicates dropped (none if no dumps);
   - under `## Summary`: at most 5 lines in the user's words where possible: the question, where
     they landed, what moved them. The summary also serves as the session log.


2. **Dumps.** Set each settled dump's `status:` and move it to `archive/`.

3. **Insights (topic-bucketed).** Merge the conclusion into `insights/<topic>.md`. Pick the topic
   from the index; add a topic only when none fits, and when two topics keep drawing the same
   dumps, merge them. A topic file:

   ```
   # <Topic>

   - <kind>: <one claim, one or two sentences, plain text>
     <YYYY-MM-DD> · convo/<file>.md
   ```

   An insight is memory with a purpose: it makes later conversations better and lets them
   compound. Each entry has one kind:

   - **learning**: something the user concluded or came to understand (a position, a design
     call, how something works for them);
   - **aha**: a connection the user made between two ideas, or that clicked for them.

   Facts aren't stored: they stay in the convo, reached through the backlink when needed.

   The bar: it's the user's (said, agreed to, or clearly took up), and a future conversation
   would go differently because of it. Leftover research doesn't pass.

   **One insight is one claim.** A related but different claim is its own entry; sharing a topic
   file is the link. No bold: when everything is emphasized, nothing is.

   **Each entry carries its own context.** It's read alone, quoted into a later conversation,
   so it names what it's about (the product, idea, system or situation) in the claim itself,
   never "it", "the report" or "this". Not "Frame it as situation vs stakes", but "In connect
   the dots (simulated experience), frame a scenario as situation vs stakes, not world vs room".
   Still one or two sentences.

   - **add** when it's a new claim, even one related to an existing entry;
   - **update** only when it revises the same claim: rewrite that entry to what's true now, at
     about the same length, and add the date and convo to its second line;
   - **replace** when it contradicts the claim: rewrite it to the new conclusion; keep no stale
     version (the convo files keep the history).

   If the user didn't state it themselves, say so in one line when you end.

4. **Index.** Keep `insights/index.md` at one line per topic, rewritten whenever its file changes:

   ```
   - [<topic>](<topic>.md) — <the user's current stance on it, one line> · updated <YYYY-MM-DD>
   ```

5. **Convo index.** Run `brain.py catalog` so the new convo is listed for the next session.

End with one line: the conclusion and where it landed.

## Sync golden: `/brain sync-golden [id | all] [--force]`

Golden sessions (`$GOLDEN_REPO`, saved with /golden) are conversations that already happened.
Don't talk them through again; run only the Close step on them, so they reach insights.

Golden sessions are public at `https://smarchone.github.io/golden-convo/#<id>`, so insights cite
them there directly: no convo/ file is made for them. `golden-sync.md` (beside `convo/`) is the sync
ledger, one line per synced session, so a session isn't listed again:

```
- <id> · <topics it touched, or "nothing kept"> · synced <YYYY-MM-DD>
```

1. `python3 <skill-dir>/scripts/brain.py golden` lists sessions not yet synced, newest first;
   with `--force` it lists every session, marking the ones already `synced`. Take the given id,
   every listed session for `all`, or else the newest 5. Work in batches of 5: steps 2-6 for one
   batch, then the next, so each confirmation stays one short list.
2. `brain.py golden --read <id>` prints the golden file's path and the URL to cite. Read the file,
   starting with its `golden_turns`. Never copy its turns into the brain, and never edit it.
3. Extract **every** learning and aha that passes the bar (Close step 3): many per session
   is normal, one claim per insight. The agent's research isn't an insight unless the user took
   it up. Saving a session as golden is itself an endorsement, so `why` with `why_source:
   suggested` can stand as a learning when nothing else in the session states it.
4. Propose them in one reply, grouped by session, one line each:
   `<topic> · <kind> · add | update | replace · <the claim>`, plus `ok / edit / drop`. A claim that
   contradicts an insight gets flagged as worth a real `/brain` session. The user confirms.
5. **Idempotent merge.** A golden insight's second line is `<YYYY-MM-DD> · <the cite line>`
   (the web URL for the viewer, then the `$GOLDEN_REPO/...` file path for progressive
   disclosure). Before
   adding a claim, look for an entry that already cites this session's URL: the same claim stays
   as it is, a revised one is updated in place, and none is ever added twice. Re-syncing a session
   therefore changes nothing unless the user changed their mind.
6. Merge and index exactly as Close steps 3 and 4, then add or rewrite the session's line in
   `golden-sync.md` (a session with nothing kept gets one too). Finish with `brain.py catalog`.

End with one line: how many insights landed, in which topics.
