# Vocab
> The stages of the conversation pipeline.

## Concepts
| **Term** | what it is | why it must exist |
|---|---|---|
| **Dump** | one saved item: idea, concept, blog, video, podcast or text, as the user gave it | the unit of capture |
| **Ingest** | processing one dump into talkable form: text or transcript, core claim, tags | a session needs content the agent has read |
| **Backlog** | ingested dumps waiting for a session, listed in the app without counts | where items wait without becoming a pile |
| **Triage** | picking the cluster of related backlog items worth a session now | the user's attention goes to one conversation |
| **Cluster** | related backlog items taken into one session | comparison produces conclusions |
| **Infer** | reading the cluster against current insights to frame the conversation | the step that makes insights compound |
| **Convo** | the user-led conversation on the cluster, kept in convo/ as raw turns, key turns and a summary | where conclusions are made, and the trail back to them |
| **Insight** | one `learning:` (what the user concluded or came to understand) or `aha:` (a connection that clicked), naming its own subject, merged with past ones under a topic | what the next infer starts from |
| **Topic** | a subject the insights are bucketed under, one file each | conclusions build up by subject |
| **Index** | `insights/index.md`: one line per topic with the user's current stance | triage and infer find the right topics without reading them all |
| **Convo index** | `convo-index.md`: one entry per convo, brain's and golden, with title, why, labels and path | a session sees every past conversation without opening one |

## Decisions
- "Backlog" names the stage and the app's tab; the tab never shows counts or unread badges.
  why: the user wants to see what's waiting; pile metrics, not the list, are what make it a chore
  not: a user-facing inbox with counts; an internal term the user never sees (why: naming the stage must not turn into showing the pile)
