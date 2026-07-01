"""
Reflect Journal — Streamlit UI.

A daily reflection journal agent: onboarding, daily check-ins, and pattern
analysis, backed by an ADK agent talking to journal storage via MCP.

Design: warm cream-paper journal aesthetic. Deep ink-brown text, muted
terracotta + sage + brass accents, Fraunces/Lora/IBM Plex Mono type system.

Run with:  streamlit run app.py
Requires:  GROQ_API_KEY set in the environment (agent uses Groq via LiteLLM).
"""
import asyncio
import datetime
import sqlite3
import uuid
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent

DB_PATH = Path(__file__).parent / "data" / "journal.db"
APP_NAME = "reflect_journal"
USER_ID = "local_user"  # single-user MVP

st.set_page_config(page_title="Reflect", page_icon="📔", layout="wide")

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
PAPER = "#F6EEDF"
PAPER_SHADE = "#ECE0C8"
INK = "#3B2B22"
INK_SOFT = "#7A6552"
RUST = "#A85D3B"
SAGE = "#5C6E4E"
GOLD = "#B9924F"
BORDER = "#D9C7A3"

MOOD_COLORS = {
    "good": SAGE,
    "proud": GOLD,
    "stressed": RUST,
    "tired": "#8C6E58",
    "anxious": "#8A5A63",
    "neutral": INK_SOFT,
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,500&family=Lora:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {{
    --paper: {PAPER};
    --paper-shade: {PAPER_SHADE};
    --ink: {INK};
    --ink-soft: {INK_SOFT};
    --rust: {RUST};
    --sage: {SAGE};
    --gold: {GOLD};
    --border: {BORDER};
}}

html, body, [data-testid="stAppViewContainer"], .main {{
    background-color: var(--paper) !important;
    color: var(--ink) !important;
    font-family: 'Lora', serif;
}}

[data-testid="stHeader"] {{
    background-color: transparent !important;
}}

[data-testid="stAppViewContainer"] > .main .block-container {{
    padding-top: 2rem;
    max-width: 900px;
}}

/* Ribbon bookmark, top-right, showing today's date */
.reflect-ribbon {{
    position: fixed;
    top: 0;
    right: 48px;
    background: var(--rust);
    color: var(--paper);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 10px 14px 22px 14px;
    border-radius: 0 0 4px 4px;
    z-index: 999;
    box-shadow: 0 2px 6px rgba(59,43,34,0.25);
}}
.reflect-ribbon::after {{
    content: "";
    position: absolute;
    bottom: -10px;
    right: 0;
    border-style: solid;
    border-width: 10px 14px 0 0;
    border-color: #7A3F27 transparent transparent transparent;
}}

/* Header wordmark */
.reflect-header {{
    display: flex;
    align-items: baseline;
    gap: 14px;
    margin-bottom: 4px;
}}
.reflect-title {{
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-weight: 500;
    font-size: 2.6rem;
    color: var(--ink);
    letter-spacing: -0.01em;
}}
.reflect-caption {{
    font-family: 'Lora', serif;
    font-style: italic;
    color: var(--ink-soft);
    font-size: 1.02rem;
    margin-bottom: 1.6rem;
}}

/* Section headers */
.reflect-section {{
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.3rem;
    color: var(--ink);
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
    margin-top: 1.8rem;
    margin-bottom: 0.9rem;
}}

/* Tabs styled as notebook tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    border-bottom: 2px solid var(--border);
}}
.stTabs [data-baseweb="tab"] {{
    background-color: var(--paper-shade);
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    padding: 10px 20px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: var(--ink-soft);
}}
.stTabs [aria-selected="true"] {{
    background-color: var(--paper) !important;
    color: var(--rust) !important;
    border-color: var(--rust) !important;
    font-weight: 600;
}}

/* Chat messages */
[data-testid="stChatMessage"] {{
    background-color: var(--paper-shade);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 4px 6px;
    margin-bottom: 10px;
    font-family: 'Lora', serif;
    font-size: 0.98rem;
    line-height: 1.55;
    color: var(--ink);
}}

/* Chat input */
[data-testid="stChatInput"] textarea {{
    background-color: var(--paper) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: 'Lora', serif !important;
    color: var(--ink) !important;
}}
[data-testid="stChatInput"] {{
    border-top: 1px dashed var(--border);
    padding-top: 12px;
}}

/* Goal list */
.reflect-goal {{
    font-family: 'Lora', serif;
    font-size: 0.98rem;
    color: var(--ink);
    padding: 8px 0 8px 4px;
    border-bottom: 1px dotted var(--border);
    display: flex;
    align-items: baseline;
    gap: 10px;
}}
.reflect-goal-badge {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--paper);
    background: var(--sage);
    padding: 2px 8px;
    border-radius: 10px;
    flex-shrink: 0;
}}
.reflect-goal-badge.year {{ background: var(--gold); }}

/* Insight cards */
.reflect-insight {{
    background: var(--paper-shade);
    border-left: 3px solid var(--gold);
    border-radius: 4px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-family: 'Lora', serif;
    font-style: italic;
    color: var(--ink);
    font-size: 0.95rem;
}}
.reflect-insight-date {{
    font-family: 'IBM Plex Mono', monospace;
    font-style: normal;
    font-size: 0.68rem;
    text-transform: uppercase;
    color: var(--ink-soft);
    display: block;
    margin-bottom: 4px;
}}

.reflect-empty {{
    font-family: 'Lora', serif;
    font-style: italic;
    color: var(--ink-soft);
    font-size: 0.92rem;
}}

/* Scrollbar + misc */
::-webkit-scrollbar {{ width: 10px; }}
::-webkit-scrollbar-track {{ background: var(--paper); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 6px; }}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

today_str = datetime.date.today().strftime("%b %d")
st.markdown(f'<div class="reflect-ribbon">{today_str}</div>', unsafe_allow_html=True)


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


# --- Layout ---
st.markdown(
    '<div class="reflect-header">'
    '<span style="font-size:2rem;">📔</span>'
    '<span class="reflect-title">Reflect</span>'
    "</div>",
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="reflect-caption">Your daily reflection space. '
    "Talk to it like you'd write a journal entry.</div>",
    unsafe_allow_html=True,
)

tab_chat, tab_dashboard = st.tabs(["Journal", "Patterns & Goals"])

with tab_chat:
    for role, text in st.session_state.chat_history:
        avatar = "🖋️" if role == "user" else "🪶"
        with st.chat_message(role, avatar=avatar):
            st.write(text)

    user_input = st.chat_input("What's on your mind today?")
    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        with st.chat_message("user", avatar="🖋️"):
            st.write(user_input)

        with st.chat_message("assistant", avatar="🪶"):
            with st.spinner("Reflecting..."):
                response = send_to_agent(user_input)
            st.write(response)
        st.session_state.chat_history.append(("assistant", response))

with tab_dashboard:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    st.markdown('<div class="reflect-section">Active goals</div>', unsafe_allow_html=True)
    goals = conn.execute(
        "SELECT description, horizon FROM goals WHERE status='active'"
    ).fetchall()
    if goals:
        for g in goals:
            badge_class = "year" if g["horizon"] == "year" else ""
            st.markdown(
                f'<div class="reflect-goal">'
                f'<span class="reflect-goal-badge {badge_class}">{g["horizon"]}</span>'
                f"{g['description']}</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="reflect-empty">No goals saved yet — start a conversation in the Journal tab.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="reflect-section">Mood over time</div>', unsafe_allow_html=True)
    entries = conn.execute(
        "SELECT entry_date, mood FROM entries WHERE flagged=0 ORDER BY entry_date"
    ).fetchall()
    if entries:
        df = pd.DataFrame(entries, columns=["entry_date", "mood"])
        mood_domain = list(MOOD_COLORS.keys())
        mood_range = list(MOOD_COLORS.values())

        chart = (
            alt.Chart(df)
            .mark_bar(size=28, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("entry_date:N", title=None, axis=alt.Axis(labelAngle=-40)),
                y=alt.Y("count():Q", title=None),
                color=alt.Color(
                    "mood:N",
                    scale=alt.Scale(domain=mood_domain, range=mood_range),
                    legend=alt.Legend(title=None, orient="bottom"),
                ),
                tooltip=["entry_date", "mood"],
            )
            .properties(height=260, background=PAPER)
            .configure_axis(
                labelFont="IBM Plex Mono",
                labelColor=INK_SOFT,
                labelFontSize=10,
                grid=False,
                domainColor=BORDER,
            )
            .configure_legend(labelFont="IBM Plex Mono", labelFontSize=10, labelColor=INK_SOFT)
            .configure_view(strokeWidth=0)
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.markdown(
            '<div class="reflect-empty">No entries yet.</div>', unsafe_allow_html=True
        )

    st.markdown('<div class="reflect-section">Recent insights</div>', unsafe_allow_html=True)
    insights = conn.execute(
        "SELECT generated_at, summary FROM insights ORDER BY generated_at DESC LIMIT 10"
    ).fetchall()
    if insights:
        for i in insights:
            date_label = i["generated_at"][:10]
            st.markdown(
                f'<div class="reflect-insight">'
                f'<span class="reflect-insight-date">{date_label}</span>'
                f"{i['summary']}</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="reflect-empty">No insights generated yet — ask the agent to '
            "look for patterns once you have a few entries.</div>",
            unsafe_allow_html=True,
        )

    conn.close()
