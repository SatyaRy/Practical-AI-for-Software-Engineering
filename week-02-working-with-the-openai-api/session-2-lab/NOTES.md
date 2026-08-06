# Notes

Practical AI for Software Engineering · Week 2 · Lab 2

## Stretch goal S2 — Save and resume a conversation (SQLite)

I implemented `/save <name>` and `/load <name>` backed by SQLite instead of
JSON files. The persistence lives in `store.py` (standard library `sqlite3`
only, no new dependency), with the database path in `config.py`. On startup
the app also auto-loads the most recently saved conversation, so a new
session picks up where the last one left off without typing a command.

What I learned:

- A conversation is just data, a list of `{role, content}` dicts, so
  persisting it is mostly about choosing where the list lives.
- SQLite gives named conversations in a single local file, and an upsert
  (`ON CONFLICT ... DO UPDATE`) makes saving under the same name twice
  natural.
- Validation still matters for your own storage: a loaded conversation must
  be a list of dicts with `role` and `content` before it replaces the live
  history, and a bad load should keep the current conversation.
- Keeping persistence behind one small module (`store.py`) follows the lab's
  rule that each file has one job: `main.py` stays about user interaction,
  `llm.py` stays about the API, and `store.py` stays about storage.
