---
name: progress-motivator
version: 1.0
triggers: ["my progress", "streak", "how am I doing", "achievements", "stats"]
---

# Progress Motivator Skill

## Purpose
Celebrate achievements and maintain student motivation using real progress data.

## Workflow
1. Fetch progress: GET /progress/{user_id}
2. Analyze: completed chapters, streak, quiz scores
3. Generate personalized motivation message
4. Suggest next action

## Response Templates

### High Performer (>80% completion)
"🔥 You're on a [N]-day streak! That's incredible dedication.
You've completed [N] chapters — you're [X]% through the course.
Your best quiz score is [score]%. You're crushing it!
Next: [specific chapter recommendation]"

### Mid Progress (40-80%)
"📚 Great progress! [N] chapters down, [N] to go.
Your [N]-day streak shows real commitment.
Tip: [specific advice based on weak quiz areas]"

### Just Starting (0-40%)
"🚀 You've started your AI Agent journey!
[N] chapters completed so far.
Today's goal: Complete Chapter [N] and take the quiz.
You've got this!"

## Key Principles
- Always use REAL numbers from backend, never make up data
- Celebrate streaks loudly — they drive retention
- Always end with a specific, actionable next step
