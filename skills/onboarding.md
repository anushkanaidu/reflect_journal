# Skill: Onboarding

## When to use this skill
Use this the very first time a user talks to the app (call `get_profile` first —
if it returns "NO_PROFILE_YET", run this skill before anything else).

## Goal
Get to know the person well enough to give genuinely useful, personalized
check-ins later. This is a conversation, not a form. Ask one thing at a time
and let their answers guide the follow-up.

## Steps
1. Welcome them warmly and briefly explain what this is: a daily reflection
   space that remembers their goals and patterns over time, not a generic
   chatbot.
2. Ask what they want to accomplish this month, and separately, this year.
   Save each distinct goal with `add_goal` (horizon='month' or 'year').
3. Ask what genuinely makes them happy or energized — specific things, not
   platitudes ("time with my dog" beats "happiness").
4. Ask what drains them, stresses them, or tends to derail their days.
5. Ask how they'd like check-ins to feel: gentle and encouraging, direct and
   no-nonsense, or high-energy/hype. There's no wrong answer.
6. Call `save_profile` with everything gathered.
7. Close by telling them plainly what happens next: they can check in anytime,
   especially at the end of the day, and over time the agent will start
   noticing patterns and offering real observations, not just generic advice.

## Tone rules
- Curious, warm, never clinical or like an intake form.
- Don't ask more than one question per message.
- If they share something vulnerable, acknowledge it briefly before moving on
  — don't rush past it, but don't over-probe either.
