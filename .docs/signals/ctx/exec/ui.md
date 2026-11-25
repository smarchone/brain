# UI
> One slash command; the conversation is the interface.

## Surfaces
- `/brain <idea | link | text>`: dump; one line back, then back to work.
- `/brain`: start a session in the current conversation.
- The brain folder: plain markdown the user can read, grep and edit.
- The app (`python3 app/serve.py`): Insights, Convos and Backlog tabs in a browser.

## Feel
- Never behind: no counts or badges in view.
- Dumping takes seconds.
- A session feels like a conversation with someone who read your saves and remembers what you concluded.
- Every session leaves a sharper conclusion.

## Decisions
- One command, two verbs: `/brain <thing>` dumps; bare `/brain` starts a session.
  why: one name to remember from any repo; the argument tells them apart
  not: separate commands per stage
- The app's tabs are ordered Insights, Convos, Backlog; the app opens on Convos (`#`).
  why: insights are what the brain produces, the convos behind them come next, the backlog waiting last; the request was the order, and moving the landing page would change every `#` link back to the convo list
  not: Convos, Insights, Backlog (the earlier order); making Insights the landing page
- The app has a Backlog tab: each dump as its title, kind, added date and tags, newest first; its ingest claim shows as a tooltip on hover; clicking opens the claim, gist, key quotes, found-while and a source link. No counts or unread badges.
  why: the user wants to see what is waiting; kept clean with no pile metrics
  not: the claim shown under every title (cluttered); an inbox with counts or badges; no backlog shown at all (why: a visible pile makes people avoid the tool; the pile metrics, not the list, are what's dropped)
- The Insights tab has two levels. Home: a search box over every insight, then a grid of topic cards in index order, each with the topic title, its stance from index.md, its insight count and last update; search filters insights across topics, grouped by topic, matches highlighted. Topic page: title, stance as the lead line, the insights, previous/next topic links and a link back to all topics.
  why: one long scroll of every insight left the user lost; the map shows the whole brain at a glance and a topic page is read alone
  not: one page listing every topic with its stance and insights (no overview; every entry weighs the same)
- On a topic page, insights are plain points, one sentence each: no cards, borders, numbers or meta rows. Each ends in one faint source link (→ a convo in the app, ↗ a golden session) that brightens on hover; its date and source name are in the link's tooltip. The `learning:`/`aha:` prefix is not shown.
  why: the user makes sense of the topic, not each entry; links must not distract
  not: each insight as a large entry with its date and full source slug under it
- Aha insights are shown in the accent blue, bullet included; learnings in the normal text color.
  why: an aha is the connection that clicked, worth spotting at a glance
  not: marking aha with a label or the bullet alone
- A session opens with one prepared cluster and its tension; the user can take it or name another topic.
  why: the agent prepares, the user drives
  not: a menu of saves to choose from
