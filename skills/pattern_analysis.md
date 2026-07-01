# Skill: Pattern Analysis

## When to use this skill
Use when the user asks to see patterns/trends, or proactively once there are
enough entries (roughly 5+) to say something meaningful. Call
`get_recent_entries` (a reasonable window, e.g. last 14) to pull history.

## Goal
Surface ONE real, specific, evidence-backed observation — not a vague
summary. This is the "why not track your mental health like you track sleep
or steps" piece: the value is in noticing something the person themselves
might not have consciously connected.

## Steps
1. Pull recent entries with `get_recent_entries`.
2. EXCLUDE any entries with `flagged=1` (crisis-flagged) from pattern
   analysis — do not use those as data points for trend-spotting.
3. Look for real patterns across mood, tags, and recurring language:
   - A tag or topic that correlates with a recurring mood
     ("work" appears alongside "stressed" 4 of the last 5 times)
   - A goal that's mentioned as stuck/blocked repeatedly
   - A positive pattern worth reinforcing (what's working)
4. Only surface a pattern if it's genuinely supported by at least 3 data
   points. If there isn't enough signal yet, say so honestly rather than
   inventing a trend.
5. Present the insight in plain language, cite what it's based on loosely
   ("this is the third time this week you've mentioned feeling behind after
   long coding sessions"), and pair it with one practical, concrete
   suggestion — not therapy, not a lecture.
6. Call `save_insight` with the summary and the entry ids it's based on.

## Guardrail
- Never present a pattern as a diagnosis or clinical label ("this sounds like
  burnout/anxiety/depression"). Describe the observed pattern in behavioral
  terms instead ("you've described feeling drained after back-to-back days
  with no breaks").
- If the recent entries (even unflagged ones) suggest a persistent, serious
  decline, gently suggest talking to a real person — a friend, mentor, or
  professional — alongside whatever practical insight you offer.

## Tone rules
- Confident but not clinical. Like a friend who's paying attention, not a
  dashboard generating a report.
