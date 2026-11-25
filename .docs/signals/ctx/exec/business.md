# Business
> A conversation pipeline: dump what you find, and the brain prepares the next good conversation about it.

## Problem
Ideas, concepts, blogs, videos and podcasts turn up mid-work. Bookmarks and second brains store
them and wait; most become a pile nobody revisits. Memory layers (Mem0, Meko) store facts for
agents to retrieve; the LLM Wiki compiles sources into pages. None of them prepares a person to
think.

## For whom
One person: a senior software engineer with ADHD who works in Claude Code across many repos,
saves more than they can consume, and wants their own conclusions to sharpen over time.

## Why this wins
Bookmarks store links. Memory layers store facts. The brain prepares conversations. Each session
starts from what the user already concluded, so every conversation leaves the next one further
along.

## Decisions
- The brain is a conversation pipeline: its output is the next good conversation; insights are what that conversation produces.
  why: agent experience over bookmarks; the agent does the revisit work a bookmark leaves to the user
  not: a bookmark store; a retrieval layer that feeds facts to agents
- Build on plain files, not on an existing memory layer.
  why: Mem0 reduces sources to facts and drops the argument; Meko is multi-agent infrastructure; the hard parts are ingesting media and preparing the conversation, which neither does
  not: Mem0, Meko or a vector store as the base
