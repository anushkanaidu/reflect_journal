"""
Seeds fake-but-realistic historical entries so pattern analysis has
something to find on demo day, without waiting weeks for real data.

Run: python3 seed_demo_data.py
"""
import datetime
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "journal.db"

# (days_ago, raw_text, mood, tags)
DEMO_ENTRIES = [
    (6, "Long day debugging a pipeline, felt pretty behind on everything.", "stressed", "work,coding"),
    (5, "Good study session, actually got through the material I needed.", "good", "study"),
    (4, "Another late night on coursework, feeling drained but made progress.", "tired", "work,study"),
    (3, "Back-to-back meetings and no real breaks, exhausted by evening.", "stressed", "work"),
    (2, "Took a short walk in the afternoon, felt noticeably better after.", "good", "self-care"),
    (1, "Crunched on an assignment late into the night again, drained.", "tired", "work,study"),
    (0, "Finished a big task I'd been putting off, felt proud of that.", "proud", "work"),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    today = datetime.date.today()
    for days_ago, text, mood, tags in DEMO_ENTRIES:
        entry_date = (today - datetime.timedelta(days=days_ago)).isoformat()
        conn.execute(
            """INSERT INTO entries (entry_date, raw_text, mood, tags, flagged, created_at)
               VALUES (?, ?, ?, ?, 0, ?)""",
            (entry_date, text, mood, tags, datetime.datetime.now().isoformat()),
        )
    conn.commit()
    conn.close()
    print(f"Seeded {len(DEMO_ENTRIES)} demo entries.")


if __name__ == "__main__":
    seed()
