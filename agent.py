"""
Reflect Journal agent — an ADK agent that:
  1. Loads its behavior from skill files (skills/*.md) — progressive
     disclosure instead of one giant system prompt.
  2. Talks to journal storage exclusively through the MCP server
     (mcp_journal_server.py) via stdio.

This is the Concierge-track capstone agent: a personal reflection journal
that remembers goals, takes daily check-ins, and surfaces real patterns.
"""
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# --- Model backend ---
# Using Groq (via LiteLLM) instead of calling Gemini directly. ADK is
# model-agnostic; LiteLLM lets it talk to Groq, OpenAI, Anthropic, etc.
# Requires GROQ_API_KEY to be set in the environment.
# Groq's currently-available models: https://console.groq.com/docs/models
MODEL = LiteLlm(model="groq/llama-3.3-70b-versatile")

ROOT = Path(__file__).parent
SKILLS_DIR = ROOT / "skills"


def load_skill(name: str) -> str:
    return (SKILLS_DIR / f"{name}.md").read_text()


# --- MCP connection: spawns mcp_journal_server.py as a subprocess over stdio ---
journal_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[str(ROOT / "mcp_journal_server.py")],
        ),
        timeout=10.0,
    )
)

# --- Root instruction: the agent's "always-on" context is intentionally thin.
# Skill content is loaded on demand rather than crammed into one system
# prompt, per the Unit 3 "Agent Skills" progressive-disclosure pattern. The
# root instruction just tells the agent HOW to decide which skill applies. ---
ROOT_INSTRUCTION = f"""
You are Reflect — a personal reflection journal agent. You help the user set
goals, check in daily, and notice real patterns over time, the way a fitness
tracker tracks physical health but for their goals and mental wellbeing.

You have three skills available. Decide which one applies to the current
message and follow it closely:

1. ONBOARDING — use when `get_profile` returns "NO_PROFILE_YET", or the user
   is clearly new.
{load_skill("onboarding")}

2. DAILY CHECK-IN — use for a returning user's regular reflection.
{load_skill("daily_checkin")}

3. PATTERN ANALYSIS — use when the user asks about trends/patterns, or
   proactively once there's enough history.
{load_skill("pattern_analysis")}

General rules that apply across all skills:
- Never diagnose or use clinical/mental-health labels for what the user is
  experiencing.
- Never fabricate goals, entries, or patterns — only reference what's
  actually in storage via your tools.
- Always use your tools (save_profile, add_goal, list_goals, add_entry,
  get_recent_entries, save_insight, get_recent_insights, get_profile) to
  read and write real state. Do not just say you saved something — call the
  tool.
"""

root_agent = Agent(
    name="reflect_journal_agent",
    model=MODEL,
    description="A personal daily reflection and goal-tracking journal agent.",
    instruction=ROOT_INSTRUCTION,
    tools=[journal_tools],
)
