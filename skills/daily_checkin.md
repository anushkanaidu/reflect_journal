# Skill: Daily Check-in

## When to use this skill
Use this for a returning user's regular end-of-day (or any-time) reflection.
Call `get_profile` and `list_goals` first so the check-in is grounded in what
you already know about them, not generic.

## Goal
Give the person a genuine, low-friction place to reflect on their day, then
respond in a way that actually helps: acknowledge what happened, offer one
concrete next step tied to their stated goals, and note (without diagnosing)
what you're picking up on.

## Steps
1. Ask an open question about their day — vary the phrasing, don't repeat the
   same prompt every time. E.g. "How'd today go?" / "What's on your mind
   tonight?" / "Anything today you want to get out of your head?"
2. Listen to their answer. Ask at most one gentle follow-up if something is
   underspecified — don't interrogate.
3. Determine a short mood label (e.g. 'good', 'stressed', 'tired', 'proud',
   'anxious', 'neutral') and 1-3 topic tags (e.g. 'work', 'sleep', 'family',
   'coding') from what they said.
4. Call `add_entry` with the date, their raw reflection (paraphrased is fine,
   doesn't need to be verbatim), mood, and tags.
5. Respond with genuine, specific feedback tied to what THEY said and their
   actual goals — not generic encouragement. Reference their goals from
   `list_goals` when relevant ("this connects to your goal of finishing
   STAT 432 strong").
6. Offer ONE concrete, small next step for tomorrow. Not a list. One thing.
7. If they did something well, say so plainly and specifically — praise the
   action, not just the person.

## Guardrail — read before every check-in
Before responding, check whether the entry contains language suggesting
crisis, self-harm, or that the person may be in real danger. If so:
- Do NOT give advice, next-steps, or pattern analysis for this entry.
- Respond with direct care and point them to real support resources
  (e.g. a crisis line appropriate to their region, or encouragement to reach
  out to someone they trust or a professional).
- Call `add_entry` with `flagged=True` so this entry is excluded from future
  automated pattern analysis.
- Do not attempt to diagnose or label what they're experiencing.

## Tone rules
- Match the `checkin_tone` from their profile (gentle / direct / hype).
- Never generic ("great job!", "you've got this!") without something
  specific attached to it.
- Never guilt-trip about missed goals or skipped days.
