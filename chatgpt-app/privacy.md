# Course Companion FTE — Privacy Policy

**Last updated:** 2026-04-11

## Overview

Course Companion FTE is a ChatGPT App powered by a Zero-Backend-LLM FastAPI service. This policy explains what data is collected, stored, and used when you interact with the Course Companion.

---

## What Data Is Stored

The following data is stored in our database (Neon PostgreSQL) when you use the app:

| Data | Purpose | Retention |
|---|---|---|
| `user_id` | Unique identifier for your session (provided by ChatGPT) | Until account deletion |
| Chapter progress | Track which chapters you have read and completed | Until account deletion |
| Quiz scores | Record your quiz attempts and scores | Until account deletion |
| Study streak | Track your daily study activity streak | Until account deletion |
| `email` (optional) | Only if you voluntarily provide it | Until account deletion |

---

## What Data Is NOT Stored

We do **not** store:

- Your name, address, phone number, or any government-issued ID
- Payment information of any kind
- Conversation messages or chat history
- IP addresses or device fingerprints
- Any data beyond what is listed in the "What Data Is Stored" section above

---

## How Your Data Is Used

Your stored data is used exclusively to:
1. Track your learning progress across sessions
2. Display your streak and completion percentage
3. Record quiz attempts so you can review past scores
4. Enforce freemium access control (free vs. premium chapters)

Your data is **never sold, shared with third parties, or used for advertising**.

---

## Data Storage Location

All data is stored in a Neon PostgreSQL database hosted on the Neon serverless platform (AWS us-east-1 region). Course content (chapters and quizzes) is stored in Cloudflare R2 object storage.

---

## Your Rights

You may request:
- **Access**: A copy of all data stored under your user_id
- **Deletion**: Removal of all your data from our database
- **Correction**: Update of any incorrect data

---

## Contact

For privacy-related requests or questions, contact:

**Project:** Course Companion FTE  
**Hackathon:** Panaversity Agent Factory Hackathon IV  
**Contact:** [your-email@example.com] ← replace with real contact before submission  
**GitHub:** [your-github-repo] ← replace with real repo URL before submission

---

*This privacy policy applies to the Course Companion FTE ChatGPT App and its associated backend API.*
