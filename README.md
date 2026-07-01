# Reflect — Personal Reflection Journal Agent

A daily journaling agent that gets to know your goals and what makes you
happy/unhappy, takes end-of-day check-ins, and surfaces real patterns over
time — the way a WHOOP or Oura ring tracks physical health, but for your
goals and reflections.

Built for the Kaggle × Google **AI Agents: Intensive Vibe Coding Capstone**
(Concierge Agents track).

## Concepts demonstrated (3 of 6)

1. **Agent Skills** — behavior is split across `skills/onboarding.md`,
   `skills/daily_checkin.md`, and `skills/pattern_analysis.md` and loaded
   progressively rather than crammed into one system prompt.
2. **MCP server** — all journal storage (profile, goals, entries, insights)
   is exposed as tools via a local MCP server (`mcp_journal_server.py`),
   not called directly by the agent.
3. **Security / guardrails (human-in-the-loop)** — the daily check-in and
   pattern-analysis skills include an explicit guardrail: crisis/self-harm
   language is flagged, excluded from automated pattern analysis, and
   redirected to real support resources instead of AI-generated advice.
   The agent is also instructed to never issue mental-health diagnoses.

## Project structure

```
reflect_journal/
├── agent.py                # ADK agent: loads skills, connects to MCP tools
├── mcp_journal_server.py   # MCP server exposing SQLite journal storage
├── app.py                  # Streamlit UI (chat + patterns/goals dashboard)
├── init_db.py               # One-time DB schema setup
├── seed_demo_data.py       # Seeds fake history so pattern analysis has data to demo
├── skills/
│   ├── onboarding.md
│   ├── daily_checkin.md
│   └── pattern_analysis.md
├── data/
│   └── journal.db          # SQLite storage (created by init_db.py)
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
python3 init_db.py
python3 seed_demo_data.py   # optional: seeds 7 days of fake history for the demo
```

Set your model API key. The agent uses **Groq** (via ADK's LiteLLM
integration) rather than Gemini directly — ADK is model-agnostic, and Groq
has a generous, reliable free tier:

```bash
export GROQ_API_KEY=your_key_here
```

Get a free key at https://console.groq.com/keys (sign in, click "Create API
Key"). The agent uses `groq/llama-3.3-70b-versatile` by default — you can
change this in `agent.py` (`MODEL = LiteLlm(model="groq/...")`) to any model
listed at https://console.groq.com/docs/models.

## Run

```bash
streamlit run app.py
```

This opens a two-tab UI:
- **Journal** — chat with the agent (onboarding on first run, daily
  check-ins after that)
- **Patterns & Goals** — dashboard showing active goals, mood over time, and
  generated insights

## Testing the MCP server standalone

```bash
python3 mcp_journal_server.py
```

This runs the server over stdio, which is how `agent.py` connects to it
(spawned as a subprocess — see `agent.py`'s `StdioConnectionParams`).

## Notes on the guardrail design

Rather than have the agent silently "handle" sensitive entries the same way
as everyday ones, flagged entries are:
- Excluded from `get_recent_entries`-based pattern analysis (so a single bad
  week doesn't get pathologized into a "trend"), and
- Answered with direct care and real resources instead of AI-generated
  advice or a next-step suggestion.

This was a deliberate design choice, not an afterthought — a journaling
agent that gives out "next steps" for a crisis-level entry would be actively
harmful, so that path is short-circuited explicitly in the skill file rather
than left to the model's judgment alone.
