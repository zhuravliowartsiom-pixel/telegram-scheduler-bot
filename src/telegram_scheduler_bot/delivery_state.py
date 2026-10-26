import sqlite3
from datetime import date
from pathlib import Path


class DeliveryState:
    def __init__(self, path: str = "data/delivery.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS deliveries (
                    day TEXT NOT NULL,
                    chat_id INTEGER NOT NULL,
                    PRIMARY KEY (day, chat_id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    day TEXT NOT NULL,
                    slot TEXT NOT NULL,
                    chat_id INTEGER NOT NULL,
                    thread_id INTEGER NOT NULL,
                    PRIMARY KEY (day, slot, chat_id, thread_id)
                )
                """
            )

    def was_sent(self, day: date, chat_id: int) -> bool:
        with sqlite3.connect(self.path) as connection:
            row = connection.execute(
                "SELECT 1 FROM deliveries WHERE day = ? AND chat_id = ?",
                (day.isoformat(), chat_id),
            ).fetchone()

        return row is not None

    def mark_sent(self, day: date, chat_id: int) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO deliveries (day, chat_id)
                VALUES (?, ?)
                """,
                (day.isoformat(), chat_id),
            )

    def reminder_was_sent(
        self,
        day: date,
        slot: str,
        chat_id: int,
        thread_id: int | None,
    ) -> bool:
        with sqlite3.connect(self.path) as connection:
            row = connection.execute(
                """
                SELECT 1 FROM reminders
                WHERE day = ? AND slot = ? AND chat_id = ? AND thread_id = ?
                """,
                (day.isoformat(), slot, chat_id, thread_id or 0),
            ).fetchone()

        return row is not None

    def mark_reminder_sent(
        self,
        day: date,
        slot: str,
        chat_id: int,
        thread_id: int | None,
    ) -> None:
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO reminders
                (day, slot, chat_id, thread_id)
                VALUES (?, ?, ?, ?)
                """,
                (day.isoformat(), slot, chat_id, thread_id or 0),
            )
