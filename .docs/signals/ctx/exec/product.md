# Product
> dump → ingest → backlog → session: triage → infer from insights → convo → insights, compounding.

## Core loop
1. Dump: the user hands over an idea, concept, blog, video or podcast and goes back to work.
2. Ingest: the agent processes that one item into something quick to talk about.
3. Backlog: ingested items wait; the app lists them, with no counts.
4. Session start: the user starts a session; triage picks one or more related backlog items.
5. Infer: the agent reads the picked items against the current insights and frames the conversation.
6. Convo: the user thinks it through and reaches a conclusion.
7. Close: the conversation is kept in convo/ with its key turns and summary, and its conclusion merges into its topic in insights/, which the next infer reads.

## The moment
The conversation opens on the user's own past thinking: "you concluded X; these two saves
push against it." The user ends with a sharper conclusion than they started with.

## Non-goals
- Counts or unread badges for the backlog.
- Making the user consume a source in full.
- Summaries for the user to read in place of a conversation.

## Decisions
- Dump only dumps: it stores what the user gave and returns at once; all processing is ingest.
  why: the user is mid-work; dumping must cost no attention
  not: processing, fetching or asking questions at dump
- Ingest processes one item at a time into talkable form, doing whatever fits the media: text for a blog, transcript for a video or podcast, core claim and tags for all.
  why: a session can only start from content the agent has read; ideas, blogs, videos and podcasts each need different processing
  not: one fixed summarizer for every kind; ingest reading insights
- Ingest runs in the background right after a dump; any item still not ingested is ingested at the start of the next session.
  why: the dump returns at once and the session starts from ready items; the fallback covers a dump whose background ingest never ran
  not: ingesting only at session start (slow start); blocking the dump on ingest
- Triage picks one related cluster of backlog items, usually 2-4, for a session.
  why: a comparison across items produces more conclusions than one item alone
  not: one item per session; a walk through a list
- Triage ranks clusters by tension: items that disagree with each other or with an insight rank first.
  why: tension is what makes a conversation worth having
  not: first-in-first-out; newest first
- Infer runs at session start and reads the picked items against the current insights: confirms, contradicts or extends.
  why: insights are freshest at session start; this is the loop that compounds
  not: inferring at ingest against stale insights
- A session opens with a three-line briefing, then the opening question: what it's about (the cluster and what it pushes on from past insights), why it matters (what changes in the user's work or thinking if it lands), and what they could walk away with (a decision, a revised insight, a sharper question). The briefing frames the session; it never summarizes the sources.
  why: the user knows what they're walking into before thinking starts, which lowers the cost of starting; a tension, not a reading digest, still drives the conversation
  not: opening cold on the tension in two or three lines (no frame for why it matters or what the payoff is); "here's what these items say" (a summary is a reading digest; a tension is a conversation)
- Convo to insights is progressive summarization: the session's raw conversation is kept with its key turns and a summary, and the insight distills it further and links back.
  why: each layer is smaller than the last and nothing is lost; the user can always drill from a conclusion to how they reached it
  not: keeping only the conclusion; summarizing sources instead of the user's thinking
- Every session merges its conclusion into its topic's insights: add, update or replace.
  why: insights must say what is true now so the next infer starts further along; the convo files keep the history
  not: appending only; keeping contradicted conclusions
- One insight is one claim: a related but different conclusion is added as its own entry; update only revises the same claim, at about the same length.
  why: a fused entry can't be confirmed or contradicted in part, grows every session, and costs attention to read
  not: merging related conclusions into one entry
- Insights are plain text, not bold.
  why: when everything is emphasized, nothing is
  not: bolding every insight
- A new topic is added only when no existing topic fits; topics that keep drawing the same dumps are merged.
  why: few topics keep the index readable and conclusions connected
  not: one topic per session or per insight
- Items the conversation settled leave the backlog; items it did not reach stay unchanged.
  why: every session clears what it used and nothing else
  not: forcing a verdict on every picked item
- The user starts every session; nothing runs on a schedule.
  why: interruptions bring back the context-switching cost the brain exists to remove
  not: reminders, nudges or scheduled sessions
- An insight is memory with a purpose: it makes later conversations better and lets them compound. It holds only two kinds, prefixed on each entry: `learning:` (what the user concluded or came to understand) and `aha:` (a connection that clicked). Facts are not stored in insights; they stay in the convo and are read through the backlink when a conversation needs them.
  why: the user wants beliefs, learnings and aha moments remembered without the noise of stored facts; a fact a learning rests on is one hop away
  not: conclusions only (dropped what the user learned from a session); also storing facts, taste and interests (too much becomes noise, for now); a size-triggered merge once a topic passes about 15 entries (not wanted yet)
- Each insight carries its own context: the claim names what it's about (the product, idea, system or situation), never a bare "it", "the report" or "this".
  why: an insight is quoted alone into a later conversation; without its subject it can't be understood or pushed on
  not: relying on the topic file or the source for context
- At golden sync, saving a session as golden counts as the user endorsing its `why`, so a `why_source: suggested` why can stand as a learning when nothing else in the session states it.
  why: sessions where the user mostly asked kept nothing, though the user chose to save them
  not: treating a suggested why as never the user's
