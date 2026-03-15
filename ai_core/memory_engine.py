"""SQLite-backed memory engine for command/result history."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class MemoryEngine:
    """Stores command history persistently and exposes recent context."""

    def __init__(self, db_path: str | Path = "data/projectm_memory.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                command_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                was_success INTEGER NOT NULL
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory_state (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def add_entry(self, command: dict[str, Any], result: dict[str, Any]) -> None:
        self._conn.execute(
            """
            INSERT INTO memory_entries (command_json, result_json, was_success)
            VALUES (?, ?, ?)
            """,
            (
                json.dumps(command, ensure_ascii=True),
                json.dumps(result, ensure_ascii=True),
                1 if result.get("status") == "success" else 0,
            ),
        )
        self._conn.commit()

    def get_last_entry(self) -> dict[str, Any] | None:
        row = self._conn.execute(
            """
            SELECT command_json, result_json
            FROM memory_entries
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None
        return {
            "command": json.loads(row[0]),
            "result": json.loads(row[1]),
        }

    def get_history(self, limit: int = 10) -> list[dict[str, Any]]:
        if limit <= 0:
            return []
        rows = self._conn.execute(
            """
            SELECT command_json, result_json
            FROM memory_entries
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        history = [{"command": json.loads(row[0]), "result": json.loads(row[1])} for row in rows]
        history.reverse()
        return history

    def close(self) -> None:
        self._conn.close()

    def get_last_entry_id(self) -> int:
        row = self._conn.execute(
            """
            SELECT id
            FROM memory_entries
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return 0
        return int(row[0])

    def get_entries_since(self, entry_id: int, limit: int = 500) -> list[dict[str, Any]]:
        if limit <= 0:
            return []
        rows = self._conn.execute(
            """
            SELECT command_json, result_json
            FROM memory_entries
            WHERE id > ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (max(0, int(entry_id)), limit),
        ).fetchall()
        return [{"command": json.loads(row[0]), "result": json.loads(row[1])} for row in rows]

    def set_state(self, key: str, value: Any) -> None:
        self._conn.execute(
            """
            INSERT INTO memory_state (key, value_json)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json
            """,
            (str(key), json.dumps(value, ensure_ascii=True)),
        )
        self._conn.commit()

    def get_state(self, key: str) -> Any | None:
        row = self._conn.execute(
            """
            SELECT value_json
            FROM memory_state
            WHERE key = ?
            LIMIT 1
            """,
            (str(key),),
        ).fetchone()
        if row is None:
            return None
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return None

    def delete_state(self, key: str) -> None:
        self._conn.execute(
            """
            DELETE FROM memory_state
            WHERE key = ?
            """,
            (str(key),),
        )
        self._conn.commit()
