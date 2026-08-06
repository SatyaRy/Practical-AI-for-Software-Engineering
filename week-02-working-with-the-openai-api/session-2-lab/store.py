"""
store.py — SQLite persistence for saved conversations (Stretch Goal S2).

The conversation is just data: a list of role/content message dicts. Once
you see that, persisting it is mostly about choosing where the list lives.
This module wraps a small SQLite database (standard library `sqlite3`, no
new dependency) so `/save <name>` and `/load <name>` can keep a chat
between runs.

Validation (S2 step 4): a loaded conversation must still be a list of
dicts that each have a `role` and a `content` before it replaces the live
history.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

import config


class ConversationNotFoundError(Exception):
    """Raised when `/load <name>` asks for a conversation never saved."""


class StoreError(Exception):
    """Raised when the database is missing, corrupted, or unwritable."""


class ConversationStore:
    """A tiny SQLite shelf of conversations, keyed by name."""

    def __init__(self, db_path: str = config.CONVERSATION_DB):
        try:
            self._conn = sqlite3.connect(db_path)
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    name       TEXT PRIMARY KEY,
                    messages   TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise StoreError(f"could not open the conversation database: {exc}") from exc

    # ---- public API ------------------------------------------------------
    def save(self, name: str, messages: list[dict]) -> None:
        """Write the conversation under `name`, overwriting any older copy."""
        if not name or not name.strip():
            raise StoreError("a conversation name is required")
        payload = json.dumps(messages, ensure_ascii=False)
        now = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        try:
            self._conn.execute(
                """
                INSERT INTO conversations (name, messages, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    messages = excluded.messages,
                    updated_at = excluded.updated_at
                """,
                (name.strip(), payload, now),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise StoreError(f"could not save the conversation: {exc}") from exc

    def load(self, name: str) -> list[dict]:
        """Return the saved conversation, or raise if unknown or corrupted."""
        try:
            row = self._conn.execute(
                "SELECT messages FROM conversations WHERE name = ?",
                (name.strip(),),
            ).fetchone()
        except sqlite3.Error as exc:
            raise StoreError(f"could not read the conversation database: {exc}") from exc
        if row is None:
            raise ConversationNotFoundError(name)
        return self._decode(row[0])

    def load_latest(self) -> tuple[str, list[dict]]:
        """Return (name, messages) for the most recently saved conversation,
        or raise ConversationNotFoundError if nothing was ever saved."""
        try:
            row = self._conn.execute(
                "SELECT name, messages FROM conversations "
                "ORDER BY updated_at DESC LIMIT 1"
            ).fetchone()
        except sqlite3.Error as exc:
            raise StoreError(f"could not read the conversation database: {exc}") from exc
        if row is None:
            raise ConversationNotFoundError("")
        return row[0], self._decode(row[1])

    def list_names(self) -> list[str]:
        """Return the names of every saved conversation, sorted."""
        try:
            rows = self._conn.execute(
                "SELECT name FROM conversations ORDER BY name"
            ).fetchall()
        except sqlite3.Error as exc:
            raise StoreError(f"could not read the conversation database: {exc}") from exc
        return [row[0] for row in rows]

    def close(self) -> None:
        """Close the underlying connection. Call when done with the store."""
        self._conn.close()

    # ---- helpers ---------------------------------------------------------
    @staticmethod
    def _decode(raw: str) -> list[dict]:
        try:
            messages = json.loads(raw)
        except (TypeError, ValueError) as exc:
            raise StoreError("the saved conversation is corrupted") from exc
        if not _is_valid_messages(messages):
            raise StoreError("the saved conversation is not a valid message list")
        return messages


def _is_valid_messages(messages) -> bool:
    """True if `messages` is a non-empty list of dicts with role/content."""
    if not isinstance(messages, list) or not messages:
        return False
    return all(
        isinstance(msg, dict) and "role" in msg and "content" in msg
        for msg in messages
    )