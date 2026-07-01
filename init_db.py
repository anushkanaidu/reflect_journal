"""
Initializes the SQLite database used by the journal MCP server.
Run once: python3 init_db.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "journal.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- single-user MVP, one row
    name TEXT,
    onboarded_at TEXT,
    likes TEXT,          -- freeform text: what makes them happy
    dislikes TEXT,        -- freeform text: what drains/upsets them
    checkin_tone TEXT     -- preferred tone: e.g. "gentle", "direct", "hype"
);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    horizon TEXT NOT NULL,        -- 'month' or 'year'
    created_at TEXT NOT NULL,
    status TEXT DEFAULT 'active'  -- 'active', 'done', 'dropped'
);

CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT NOT NULL,     -- YYYY-MM-DD
    raw_text TEXT NOT NULL,       -- what the user wrote/said
    mood TEXT,                    -- short label, e.g. 'good', 'stressed', 'tired'
    tags TEXT,                    -- comma-separated topic tags, e.g. 'work,sleep'
    flagged INTEGER DEFAULT 0,    -- 1 if guardrail triggered on this entry
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    generated_at TEXT NOT NULL,
    summary TEXT NOT NULL,        -- the pattern/insight text
    based_on_entry_ids TEXT       -- comma-separated entry ids used
);
"""

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
