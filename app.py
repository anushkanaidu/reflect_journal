"""
Reflect Journal — Streamlit UI.

A daily reflection journal agent: onboarding, daily check-ins, and pattern
analysis, backed by an ADK agent talking to journal storage via MCP.

Run with:  streamlit run app.py
Requires:  GOOGLE_API_KEY (or GEMINI_API_KEY) set in the environment,
           since the agent calls a Gemini model.
"""
import asyncio
import sqlite3
import uuid
from pathlib import Path

import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent

DB_PATH = Path(__file__).parent / "data" / "journal.db"
APP_NAME = "reflect_journal"
USER_ID = "local_user"  # single-user MVP

st.set_page_config(page_title="Reflect", page_icon="📔", layout="wide")


# --- Session / Runner setup (once per browser session) ---
@st.cache_resource
def get_runner():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    return runner, session_service


runner, session_service = get_runner()

if "adk_session_id" not in st.session_state:
    st.session_state.adk_session_id = str(uuid.uuid4())
    asyncio.run(
        session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=st.session_state.adk_session_id,
        )
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def send_to_agent(user_text: str) -> str:
    """Send a message to the agent and return its final text response."""
    content = types.Content(role="user", parts=[types.Part(text=user_text)])
    final_text = ""
    for event in runner.run(
        user_id=USER_ID,
        session_id=st.session_state.adk_session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(p.text or "" for p in event.content.parts)
    return final_text or "(no response)"


# --- Layout: chat on the left, dashboard on the right ---
tab_chat, tab_dashboard = st.tabs(["💬 Journal", "📊 Patterns & Goals"])

with tab_chat:
    st.title("📔 Reflect")
    st.caption("Your daily reflection space. Talk to it like you'd write a journal entry.")

    for role, text in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(text)

    user_input = st.chat_input("What's on your mind today?")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Reflecting..."):
                response = send_to_agent(user_input)
            st.write(response)
        st.session_state.chat_history.append(("assistant", response))

with tab_dashboard:
    st.title("📊 Patterns & Goals")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    goals = conn.execute(
        "SELECT description, horizon FROM goals WHERE status='active'"
    ).fetchall()
    st.subheader("Active goals")
    if goals:
        for g in goals:
            st.markdown(f"- **({g['horizon']})** {g['description']}")
    else:
        st.caption("No goals saved yet — start a conversation in the Journal tab.")

    st.subheader("Mood over time")
    entries = conn.execute(
        "SELECT entry_date, mood FROM entries WHERE flagged=0 ORDER BY entry_date"
    ).fetchall()
    if entries:
        import pandas as pd

        df = pd.DataFrame(entries, columns=["entry_date", "mood"])
        mood_counts = df.groupby(["entry_date", "mood"]).size().unstack(fill_value=0)
        st.bar_chart(mood_counts)
    else:
        st.caption("No entries yet.")

    st.subheader("Recent insights")
    insights = conn.execute(
        "SELECT generated_at, summary FROM insights ORDER BY generated_at DESC LIMIT 10"
    ).fetchall()
    if insights:
        for i in insights:
            st.markdown(f"- {i['summary']}")
    else:
        st.caption("No insights generated yet — ask the agent to look for patterns once you have a few entries.")

    conn.close()
