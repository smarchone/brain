# skill
> the /brain skill: SKILL.md holds the behavior, scripts/brain.py the plumbing
## Decisions
- brain.py only finds, lists and fetches transcripts; triage, infer and insight merging stay in SKILL.md for the agent.
  why: judgment belongs to the model and improves with it; a script would freeze it
  not: a script that clusters, scores or summarizes dumps
- Transcripts come from published captions via yt-dlp (manual subs, then auto subs); no audio is downloaded.
  why: no local speech-to-text is installed; captions cover most videos at no cost
  not: downloading audio and transcribing it
- `brain.py convo` reads the session log with its own copy of golden.py's `find_session` and `load_claude` (and their helpers), marked as copied and kept in step with golden.py; /brain needs no other skill.
  why: a new user without the golden skill couldn't save a session, which breaks the core loop
  not: importing golden.py's loader from ~/.claude/skills/golden at run time (why: one shared extractor, so log-format fixes reach both skills; a hidden dependency isn't worth a broken close)
- A convo starts at the last bare `/brain` prompt in the session and runs to the end; `--from N` overrides.
  why: `/brain <thing>` is a dump, not a session start; one session may hold dumps before the session
  not: saving the whole session
- `brain.py backlog` prints each dump's ingest `claim:` in place of its first line.
  why: triage compares items by claim without opening every file
  not: printing the raw first line for ingested dumps
- `brain.py convo` refuses to write without `--keep`; `--list` shows the numbered turns to choose from.
  why: the script makes curation a required step, so a whole session can't land by default
  not: keeping every turn unless told otherwise
- `brain.py catalog` builds convo-index.md from the frontmatter of convo/ and $GOLDEN_REPO, decoding `\uXXXX` escapes left by quoted YAML; it's generated, never edited, and rebuilt at session start, after Close and after sync.
  why: a deterministic rebuild can't drift from the files, unlike golden-convo's own posts.json (39 of 41)
  not: a hand-maintained index; reading golden-convo's posts.json
- `brain.py root` renames a leftover `catalog.md` or `golden.md` to `convo-index.md` or `golden-sync.md`, unless a file already exists at the new name; the `brain.py catalog` command keeps its name.
  why: a brain from before the rename, or another session writing the old name, keeps working with one copy, and nothing is overwritten; SKILL.md and habits call the command, and the verb still fits
  not: a one-off manual rename (an old-named file written later would sit beside the new one); overwriting the new file; renaming the command
- `brain.py golden --read <id>` prints the golden file's path and the cite line; it writes nothing. `GOLDEN_URL` overrides the public base URL.
  why: sync no longer creates files; the cite line keeps both backlinks consistent
  not: `--pull` writing a convo/ stub
