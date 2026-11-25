#!/usr/bin/env python3
"""Plumbing for the /brain skill. The agent does the thinking; this only finds, lists and fetches.

  brain.py root              print the brain folder (creating backlog/, archive/, convo/, insights/index.md if missing;
                             renaming a leftover catalog.md or golden.md to its new name)
  brain.py backlog           list open dumps (status dumped or ingested), one line each, oldest first
  brain.py transcript <url>  print a video's or podcast's transcript as plain text (needs yt-dlp)
  brain.py convo <name> --list [--session ID] [--from N]
                             print this session's turns, numbered from the last bare `/brain` prompt
  brain.py convo <name> --keep 2-5,8 [--session ID] [--from N]
                             write convo/<YYYY-MM-DD>-<name>.md with only those turns, verbatim from the
                             session log and renumbered from 1; print its path
  brain.py golden [--force]  list golden sessions ($GOLDEN_REPO) not yet synced, newest first;
                             --force lists every one, marking those already synced
  brain.py golden --read ID  print the golden file's path and the cite line insights use for it
  brain.py catalog           rebuild convo-index.md: every convo (brain's convo/ and golden) as title, why, labels, tags
                             and path, newest first; generated from frontmatter, never edited by hand

The brain folder is brain/ inside the repo: $BRAIN_REPO, or else the repo this skill lives in (skill/ is inside it).
Stdlib only, plus yt-dlp on PATH for `transcript`.
"""
import argparse, datetime, glob, json, os, re, shutil, subprocess, sys, tempfile

OPEN = ("dumped", "ingested")
HOME = os.path.expanduser("~")
HIDDEN = re.compile(r"<(system-reminder|local-command-stdout|local-command-caveat)>.*?</\1>\s*", re.S)
ASK = ("AskUserQuestion", "ask_question")  # the only tool calls kept: a question the user answered
RENAMED = (("catalog.md", "convo-index.md"), ("golden.md", "golden-sync.md"))  # old name -> new
INDEX_HEAD = "# Insights index\n\n<!-- one line per topic: - [topic](topic.md) — current stance · updated YYYY-MM-DD -->\n"


def root():
    repo = os.environ.get("BRAIN_REPO") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    r = os.path.join(repo, "brain")
    for d in ("backlog", "archive", "convo", "insights"):
        os.makedirs(os.path.join(r, d), exist_ok=True)
    p = os.path.join(r, "insights", "index.md")
    if not os.path.exists(p):
        open(p, "w", encoding="utf-8").write(INDEX_HEAD)
    for old, new in RENAMED:  # a brain from before the rename; never overwrite a file already at the new name
        o, n = os.path.join(r, old), os.path.join(r, new)
        if os.path.exists(o) and not os.path.exists(n):
            os.rename(o, n)
    return r


def frontmatter(path):
    """Flat `key: value` frontmatter; `[a, b]` becomes a list. Enough for brain's own files."""
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    fm = {}
    for line in (m.group(1).splitlines() if m else []):
        k, sep, v = line.partition(":")
        if not sep or line.startswith(" "):
            continue
        v = v.strip().strip('"')
        fm[k.strip()] = [x.strip() for x in v[1:-1].split(",") if x.strip()] if v.startswith("[") else v
    claim = re.search(r"^claim:\s*(.+)$", text, re.M)
    body = text[m.end():] if m else text
    first = claim.group(1).strip() if claim else next((l.strip() for l in body.splitlines() if l.strip()), "")
    return fm, first


def backlog():
    r = root()
    for p in sorted(glob.glob(os.path.join(r, "backlog", "*.md"))):
        fm, first = frontmatter(p)
        if fm.get("status", "dumped") not in OPEN:
            continue
        bits = [os.path.relpath(p, r)] + [
            f"{c}={','.join(fm[c]) if isinstance(fm.get(c), list) else fm.get(c)}"
            for c in ("added", "status", "kind", "tags", "found_while") if fm.get(c)]
        print(" | ".join(bits + [first[:140]]))


def vtt_to_text(vtt):
    """Auto-captions repeat each line as it scrolls; keep each distinct line once, in order."""
    out, seen = [], set()
    for line in vtt.splitlines():
        line = re.sub(r"<[^>]+>", "", line).strip()
        if not line or line == "WEBVTT" or "-->" in line or re.match(r"^(Kind|Language|NOTE)\b", line):
            continue
        if line not in seen:
            seen.add(line)
            out.append(line)
    return "\n".join(out)


def transcript(url):
    if not shutil.which("yt-dlp"):
        sys.exit("yt-dlp not found; keep the page text instead")
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(
            ["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs", "--sub-langs", "en.*,en",
             "--sub-format", "vtt", "-o", os.path.join(d, "t.%(ext)s"), url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        subs = sorted(glob.glob(os.path.join(d, "*.vtt")))
        if not subs:
            sys.exit("no transcript available; keep the show notes or page text instead")
        print(vtt_to_text(open(subs[0], encoding="utf-8").read()))


def parse_keep(spec, n):
    """'2-5,8' -> [2, 3, 4, 5, 8], each within 1..n."""
    out = []
    for part in spec.split(","):
        a, _, b = part.strip().partition("-")
        lo, hi = int(a), int(b or a)
        if not 1 <= lo <= hi <= n:
            sys.exit(f"--keep {part}: turns run 1..{n}")
        out += [i for i in range(lo, hi + 1) if i not in out]
    return sorted(out)


# Session-log reader: copied from the golden skill's golden.py so /brain needs no other skill.
# Keep in step with it if Claude Code's log format changes.
def find_session(arg):
    if arg and os.path.exists(arg):
        return arg
    if arg:
        hits = glob.glob(os.path.join(HOME, ".claude", "projects", "*", arg + ".jsonl"))
    else:
        project = re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
        hits = sorted(glob.glob(os.path.join(HOME, ".claude", "projects", project, "*.jsonl")), key=os.path.getmtime)[-1:]
    if not hits:
        sys.exit(f"session not found: {arg or os.getcwd()}")
    return hits[0]


def prompt_text(content):
    """The prompt as the user typed it, or None for records that aren't a prompt."""
    if isinstance(content, list):
        if any(b.get("type") == "tool_result" for b in content):
            return None
        content = "\n".join(b.get("text", "") for b in content if b.get("type") == "text")
    m = re.search(r"<command-name>(.*?)</command-name>", content, re.S)
    if m:
        args = re.search(r"<command-args>(.*?)</command-args>", content, re.S)
        return (m.group(1).strip() + " " + (args.group(1).strip() if args else "")).strip()
    content = HIDDEN.sub("", content).strip()
    if not content or content.startswith("[Request interrupted"):
        return None
    return content


def asked(inp):
    """One line for a question put to the user."""
    return "[asked: " + " / ".join(q.get("question", "") for q in inp.get("questions", [])) + "]"


def answer(content):
    """The user's pick in an AskUserQuestion result, which they did see and choose."""
    text = content if isinstance(content, str) else "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict))
    m = re.search(r'"[^"]*"="([^"]*)"', text)
    return f"[answered: {m.group(1)}]" if m else None


def collector():
    turns = []

    def add(role, text):
        if turns and turns[-1][0] == role:
            turns[-1][1].append(text)
        else:
            turns.append((role, [text]))
    return turns, add


def joined(turns):
    """Consecutive same-role pieces merged; [asked/answered: …] lines stack, prose gets a blank line."""
    join = lambda parts: "".join(("\n" if p.startswith("[") and q.startswith("[") else "\n\n") + q
                                 for p, q in zip([""] + parts, parts)).lstrip()
    return [(r, join(parts)) for r, parts in turns]


def load_claude(path):
    """Turns as [(role, text)] from a Claude Code session log, plus session metadata."""
    records = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    meta, asks = {}, set()
    turns, add = collector()

    for o in records:
        if o.get("isSidechain") or o.get("isCompactSummary"):
            continue
        for k, mk in (("version", "version"), ("cwd", "cwd"), ("sessionId", "session_id"), ("timestamp", "started")):
            meta[mk] = meta.get(mk) or o.get(k)
        msg = o.get("message") or {}
        if o.get("type") == "user" and not o.get("isMeta"):
            content = msg.get("content", "")
            if isinstance(content, list):
                for b in content:
                    if b.get("type") == "tool_result" and b.get("tool_use_id") in asks and (a := answer(b.get("content"))):
                        add("user", a)
            p = prompt_text(content)
            if p is not None:
                add("user", p)
        elif o.get("type") == "assistant" and turns:
            meta["model"] = meta.get("model") or msg.get("model")
            for b in msg.get("content", []):
                if b.get("type") == "text" and b["text"].strip():
                    add("assistant", b["text"].strip())
                elif b.get("type") == "tool_use" and b["name"] in ASK:
                    asks.add(b["id"])
                    add("assistant", asked(b.get("input", {})))
    return joined(turns), meta


def convo(name, session=None, start=None, keep=None, listing=False):
    """Raw layer of a convo file, read from the session log (never recalled by the agent).
    Only the turns in `keep` are written, verbatim and renumbered from 1; `listing` prints the turns to choose from."""
    turns, meta = load_claude(find_session(session))
    if start:
        turns = turns[start - 1:]
    else:  # a recall session starts at the last bare /brain; /brain <thing> is a dump
        starts = [i for i, (r, t) in enumerate(turns) if r == "user" and re.fullmatch(r"/?(\S+:)?brain", t.strip())]
        if not starts:
            sys.exit("no bare /brain prompt in this session; pass --from N")
        turns = turns[starts[-1]:]
    if listing:
        for i, (r, t) in enumerate(turns, 1):
            print(f"{i:>3} {r:<9} {' '.join(t.split())[:150]}")
        return
    if not keep:
        sys.exit("pass --keep with the relevant turns (see --list); a convo never holds the whole session")
    picked = parse_keep(keep, len(turns))
    turns = [turns[i - 1] for i in picked]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:48].rstrip("-")
    base = os.path.join(root(), "convo", f"{datetime.date.today():%Y-%m-%d}-{slug}")
    out, n = base + ".md", 2
    while os.path.exists(out):
        out, n = f"{base}-{n}.md", n + 1
    body = "".join(f"### {i} · **{r}:**\n\n{t}\n\n" for i, (r, t) in enumerate(turns, 1))
    now = datetime.datetime.now(datetime.timezone.utc)
    head = (f"---\ntitle: {name}\nwhy: \"\"\ndate: {now.astimezone():%Y-%m-%d}\n"
            f"captured: {now:%Y-%m-%dT%H:%M:%SZ}\nmodel: {meta.get('model')}\nsession_id: {meta.get('session_id')}\n"
            f"turns: {len(turns)}\nsource_turns: \"{keep}\"\ngolden_turns: []\nlabels: []\ndumps: []\ntags: []\n---\n\n## Summary\n\n## Conversation\n\n")
    open(out, "w", encoding="utf-8").write(head + body.rstrip() + "\n")
    print(out)



def golden_repo():
    repo = os.environ.get("GOLDEN_REPO")
    if not repo or not os.path.isdir(repo):
        sys.exit("no golden repo: set GOLDEN_REPO to the golden-convo clone")
    return repo


GOLDEN_URL = os.environ.get("GOLDEN_URL", "https://smarchone.github.io/golden-convo/")


def synced(r):
    """Golden ids already synced: listed in golden-sync.md (the sync ledger), or a /brain session's own convo/ file."""
    ids = set()
    ledger = os.path.join(r, "golden-sync.md")
    if os.path.exists(ledger):
        ids.update(re.findall(r"^- (\S+)", open(ledger, encoding="utf-8").read(), re.M))
    for p in glob.glob(os.path.join(r, "convo", "*.md")):
        fm, _ = frontmatter(p)
        ids.update(v for v in (fm.get("golden"), fm.get("session_id")) if v)
    return ids


def golden(read=None, force=False):
    r, repo = root(), golden_repo()
    paths = sorted(glob.glob(os.path.join(repo, "[0-9][0-9][0-9][0-9]-[0-9][0-9]", "*.md")))
    if read:
        src = next((p for p in paths if os.path.basename(p)[:-3] == read), None)
        if not src:
            sys.exit(f"no golden session {read} in {repo}")
        print(f"read: {src}\ncite: {GOLDEN_URL}#{read} · $GOLDEN_REPO/{os.path.relpath(src, repo)}")
        return
    done = synced(r)
    for p in reversed(paths):
        gid = os.path.basename(p)[:-3]
        fm, _ = frontmatter(p)
        linked = gid in done or fm.get("session_id") in done
        if linked and not force:
            continue
        labels = fm.get("labels")
        bits = [gid] + (["synced"] if linked else []) + [f"why_source={fm.get('why_source', '?')}", f"turns={fm.get('turns', '?')}"]
        if labels:
            bits.append(f"labels={','.join(labels) if isinstance(labels, list) else labels}")
        print(" | ".join(bits + [fm.get("why", "")[:160]]))


def catalog():
    """Write convo-index.md, the registry of every convo: a session reads it first, then opens files on demand."""
    r = root()
    rows = []
    for p in glob.glob(os.path.join(r, "convo", "*.md")):
        fm, _ = frontmatter(p)
        rows.append((os.path.basename(p)[:-3], fm, os.path.relpath(p, r)))
    repo = os.environ.get("GOLDEN_REPO")
    if repo and os.path.isdir(repo):
        for p in glob.glob(os.path.join(repo, "[0-9][0-9][0-9][0-9]-[0-9][0-9]", "*.md")):
            fm, _ = frontmatter(p)
            rows.append((os.path.basename(p)[:-3], fm, "$GOLDEN_REPO/" + os.path.relpath(p, repo)))
    def one(s):  # one line, with any \uXXXX escapes left by quoted YAML decoded
        s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(s or ""))
        return re.sub(r"\s+", " ", s).strip()
    out = ["# Convo index", "", "<!-- generated by `brain.py catalog`; do not edit. One entry per convo, newest first. -->", ""]
    for cid, fm, path in sorted(rows, key=lambda x: x[0], reverse=True):
        def joined(k):
            v = fm.get(k) or []
            return ", ".join(v) if isinstance(v, list) else str(v)
        labels, tags = joined("labels"), joined("tags")
        out += [f"- {cid[:10]} · {one(fm.get('title')) or cid}", f"  why: {one(fm.get('why'))}",
                f"  {path}" + (f" · labels: {labels}" if labels else "") + (f" · tags: {tags}" if tags else "")]
    dst = os.path.join(r, "convo-index.md")
    open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"{dst} ({len(rows)} convos)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("root", "backlog", "transcript", "convo", "golden", "catalog"))
    ap.add_argument("arg", nargs="?", help="url for transcript, name for convo")
    ap.add_argument("--session", help="convo: session id or .jsonl path (default: newest for this cwd)")
    ap.add_argument("--from", dest="start", type=int, help="convo: turn where the session starts (default: last bare /brain)")
    ap.add_argument("--list", action="store_true", help="convo: print the numbered turns to choose from, write nothing")
    ap.add_argument("--keep", help="convo: the relevant turns to write, e.g. 2-5,8 (numbering from --list)")
    ap.add_argument("--force", action="store_true", help="golden: also list sessions already synced")
    ap.add_argument("--read", metavar="ID", help="golden: print that session's file path and citation URL")
    a = ap.parse_args()
    if a.cmd in ("transcript", "convo") and not a.arg:
        ap.error(f"{a.cmd} needs {'a url' if a.cmd == 'transcript' else 'a name'}")
    if a.cmd == "transcript":
        transcript(a.arg)
    elif a.cmd == "golden":
        golden(a.read, a.force)
    elif a.cmd == "catalog":
        catalog()
    elif a.cmd == "convo":
        convo(a.arg, a.session, a.start, a.keep, a.list)
    else:
        print(root()) if a.cmd == "root" else backlog()


if __name__ == "__main__":
    main()
