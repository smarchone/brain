#!/usr/bin/env python3
"""Read the brain in a browser: convos, insights and backlog, rendered by view.html. Not part of the /brain skill.

  python3 app/serve.py                 serve on http://127.0.0.1:8765, rebuilt on every reload
  python3 app/serve.py --port 9000
  python3 app/serve.py --out page.html write the page to a file instead

Reads <repo>/brain/{convo,insights,backlog}/*.md ($BRAIN_REPO overrides the repo).
Listens on localhost only: the brain is private. Stdlib only.
"""
import argparse, glob, json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.realpath(__file__))
VIEW = os.path.join(HERE, "view.html")
BRAIN = os.path.join(os.environ.get("BRAIN_REPO") or os.path.dirname(HERE), "brain")


def embed(html, slot, folder):
    files = sorted(glob.glob(os.path.join(BRAIN, folder, "*.md")))
    data = [{"path": os.path.relpath(f, BRAIN), "content": open(f, encoding="utf-8").read()} for f in files]
    tag = f'<script type="application/json" id="{slot}"></script>'
    if tag not in html:
        sys.exit(f"{VIEW} has no {slot} slot")
    blob = json.dumps(data).replace("</", "<\\/")  # a "</script>" inside a convo must not end the tag
    return html.replace(tag, f'<script type="application/json" id="{slot}">{blob}</script>')


def page():
    html = open(VIEW, encoding="utf-8").read()
    return embed(embed(embed(html, "sessions", "convo"), "insights", "insights"), "backlog", "backlog")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--out", help="write the page to this file and exit")
    a = ap.parse_args()
    if not os.path.isdir(BRAIN):
        sys.exit(f"no brain folder at {BRAIN}")
    if a.out:
        open(a.out, "w", encoding="utf-8").write(page())
        print(a.out)
        return
    httpd = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"serving brain on http://127.0.0.1:{a.port}  (ctrl-c to stop)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
