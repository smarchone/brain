# app
> app/: serve.py and view.html, for reading convos, insights and the backlog in a browser
## Decisions
- app/view.html loads only the convos, insights and backlog embedded by app/serve.py, each in its own slot; the golden page's posts.json, index.json and GitHub fallbacks are removed.
  why: the brain has no site or index to fetch from, and a private page should make no data requests
  not: keeping the golden page's loaders; fetching backlog files
- The page reserves the scrollbar's width (`scrollbar-gutter: stable` on html) except in reading mode, which scrolls inside `.screen`.
  why: tabs of different lengths otherwise shift the centered layout sideways when a scrollbar appears
  not: `overflow-y: scroll` on html (a dead scrollbar on short pages); reserving the gutter in reading mode (an empty strip)
