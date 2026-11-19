# Tracker + PRD workflow

A reusable pattern for running a build across many sessions. Portable —
copy this file into `~/.claude/CLAUDE.md` (or a project's `CLAUDE.md`) to
make it the default way work gets tracked.

## The pattern

Two artifacts, different jobs:

| | Holds | Changes |
|---|---|---|
| **PRD** (a doc) | why, what, constraints, decisions | rarely, deliberately |
| **Tracker** (an artifact + database) | the enumerated items and their state | constantly |

The tracker is **generated from the PRD** so the two cannot drift. If an
item is not in the PRD it should not be in the tracker, and vice versa.

## Why it is an artifact and not a checklist in chat

- **The page holds the spec, the database holds the state.** They are
  separate, so the page can be redesigned without losing ticked items.
- **Progress survives the session.** A chat checklist dies with the
  conversation; this does not.
- **Claude can read the state back.** "Where am I?" is answered from the
  database, not from scrolling.
- **It is the record.** Each item carries its real constraints (exact
  dimensions, file limits, gotchas) so the spec is not re-derived later.

## How to set one up

1. Write or read the PRD first. Items come from it.
2. Create the tracker as a published artifact declaring the `db` and
   `user` capabilities.
3. Give each item a stable id. Ids are database keys — never renumber
   them, or history is orphaned.
4. Store only state in the database (`{status, updatedAt}`). Keep the
   item's description in the page.
5. Seed nothing. An empty database means "nothing started", which is the
   correct initial state.

## Rules that keep it honest

- **Tick items only when the work is actually done**, not when it is
  started or believed done.
- **Re-read the tracker before reporting progress.** Do not report counts
  from memory; they drift.
- Group items in **phases that gate each other**, so "what's next" has an
  answer rather than a list.
- Record *why* an item is hard in the item itself (e.g. "fails below
  48px"), so the constraint is not rediscovered.
- When an item's scope changes, edit the page — not the id.

## Status vocabulary

`todo` -> `wip` -> `done`. Three states. More than three invites
debate about which one applies.
