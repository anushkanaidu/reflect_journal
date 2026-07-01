"""
MCP server exposing the reflection journal's SQLite storage as tools.

Tools exposed:
  - save_profile(name, likes, dislikes, checkin_tone)
  - add_goal(description, horizon)
  - list_goals(status)
  - add_entry(entry_date, raw_text, mood, tags, flagged)
  - get_recent_entries(limit)
  - save_insight(summary, based_on_entry_ids)
  - get_recent_insights(limit)

Run standalone for local testing:
  python3 mcp_journal_server.py
"""
import sqlite3
import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

DB_PATH = Path(__file__).parent / "data" / "journal.db"

mcp = FastMCP("reflect-journal")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def save_profile(name: str, likes: str, dislikes: str, checkin_tone: str) -> str:
    """Save or update the user's onboarding profile: name, what makes them
    happy (likes), what drains/upsets them (dislikes), and their preferred
    check-in tone (e.g. 'gentle', 'direct', 'hype')."""
    conn = _conn()
    now = datetime.datetime.now().isoformat()
    conn.execute(
        """INSERT INTO user_profile (id, name, onboarded_at, likes, dislikes, checkin_tone)
           VALUES (1, ?, ?, ?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET
             name=excluded.name, likes=excluded.likes,
             dislikes=excluded.dislikes, checkin_tone=excluded.checkin_tone""",
        (name, now, likes, dislikes, checkin_tone),
    )
    conn.commit()
    conn.close()
    return f"Profile saved for {name}."


@mcp.tool()
def get_profile() -> str:
    """Retrieve the user's onboarding profile, if it exists."""
    conn = _conn()
    row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
    conn.close()
    if not row:
        return "NO_PROFILE_YET"
    return (
        f"name={row['name']}; likes={row['likes']}; "
        f"dislikes={row['dislikes']}; checkin_tone={row['checkin_tone']}"
    )


@mcp.tool()
def add_goal(description: str, horizon: str) -> str:
    """Add a new goal. horizon must be 'month' or 'year'."""
    conn = _conn()
    now = datetime.datetime.now().isoformat()
    conn.execute(
        "INSERT INTO goals (description, horizon, created_at) VALUES (?, ?, ?)",
        (description, horizon, now),
    )
    conn.commit()
    conn.close()
    return f"Goal added: '{description}' ({horizon})"


@mcp.tool()
def list_goals(status: str = "active") -> str:
    """List goals filtered by status ('active', 'done', 'dropped')."""
    conn = _conn()
    rows = conn.execute(
        "SELECT id, description, horizon FROM goals WHERE status = ?", (status,)
    ).fetchall()
    conn.close()
    if not rows:
        return "No goals found."
    return "\n".join(f"[{r['id']}] ({r['horizon']}) {r['description']}" for r in rows)


@mcp.tool()
def add_entry(
    entry_date: str,
    raw_text: str,
    mood: str,
    tags: str = "",
    flagged: bool = False,
) -> str:
    """Save a daily journal entry. entry_date is YYYY-MM-DD. mood is a short
    label like 'good', 'stressed', 'tired', 'proud'. tags is a comma-separated
    list of topics (e.g. 'work,sleep'). Set flagged=True if this entry
    triggered a safety guardrail (e.g. mentions of crisis/self-harm)."""
    conn = _conn()
    now = datetime.datetime.now().isoformat()
    conn.execute(
        """INSERT INTO entries (entry_date, raw_text, mood, tags, flagged, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (entry_date, raw_text, mood, tags, int(flagged), now),
    )
    conn.commit()
    conn.close()
    return f"Entry saved for {entry_date}."


@mcp.tool()
def get_recent_entries(limit: int = 14) -> str:
    """Retrieve the most recent journal entries (default last 14), most
    recent first. Used for pattern analysis and giving contextual advice."""
    conn = _conn()
    rows = conn.execute(
        """SELECT id, entry_date, raw_text, mood, tags FROM entries
           ORDER BY entry_date DESC LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    if not rows:
        return "No entries yet."
    lines = []
    for r in rows:
        lines.append(
            f"[{r['id']}] {r['entry_date']} (mood={r['mood']}, tags={r['tags']}): {r['raw_text']}"
        )
    return "\n".join(lines)


@mcp.tool()
def save_insight(summary: str, based_on_entry_ids: str) -> str:
    """Save a generated pattern/insight. based_on_entry_ids is a
    comma-separated list of entry ids that support the insight."""
    conn = _conn()
    now = datetime.datetime.now().isoformat()
    conn.execute(
        "INSERT INTO insights (generated_at, summary, based_on_entry_ids) VALUES (?, ?, ?)",
        (now, summary, based_on_entry_ids),
    )
    conn.commit()
    conn.close()
    return "Insight saved."


@mcp.tool()
def get_recent_insights(limit: int = 5) -> str:
    """Retrieve the most recently generated insights."""
    conn = _conn()
    rows = conn.execute(
        "SELECT generated_at, summary FROM insights ORDER BY generated_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    if not rows:
        return "No insights yet."
    return "\n".join(f"{r['generated_at']}: {r['summary']}" for r in rows)


if __name__ == "__main__":
    mcp.run()
