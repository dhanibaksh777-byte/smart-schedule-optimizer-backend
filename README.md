# Natural Language Task Parser

**Live app:** https://frontend-gse2.vercel.app/
**API:** https://ai-task-manager-ow0y.onrender.com

![App screenshot](https://github.com/dhanibaksh777-byte/smart-schedule-optimizer-backend/blob/328598c708b364ab02e5d88a4c6be5184bfb024f/Screenshot%202026-08-04%20021831.png?raw=true)

## The problem

Task managers make you fill out a form for every single task — pick a priority from a dropdown, click through a calendar to set a due date, then finally type what the task actually is. For something you're jotting down in ten seconds between meetings, that's too much friction. Most people either skip the priority/date fields entirely or abandon the task manager altogether.

## The solution

Type the task the way you'd say it out loud, and the details get pulled out for you.

> "Submit the client report by next Friday, this is really urgent"

becomes:

- **Task:** Submit the client report
- **Priority:** High
- **Due date:** the actual date of next 

No dropdowns. No date picker. You write one sentence, and the system figures out what matters.

## What it does

- **Create a task** by describing it in plain language — priority and due date are extracted automatically
- **Edit a task** — if you change the description, the priority and due date are re-extracted to match the new details
- **View, and delete tasks** — see everything in one place, color-coded by priority
- **Your tasks stay yours** — every account is private; nobody else can see or touch your tasks
- Understands relative time the way people actually talk — "tomorrow," "next Friday," "in two weeks" all resolve to the correct real-world date

## Account security

- **Email verification** — new accounts are unverified until you confirm via a link sent to your inbox
- **Password reset** — forgot your password? A self-service, email-based reset flow gets you back in, no support ticket needed
- **Rate limiting** — login, registration, and password-reset endpoints are throttled per IP to block brute-force and spam attempts
- **Hashed passwords, JWT sessions** — passwords are never stored in plain text, and every session is backed by a signed, time-limited token

## How it's built

- **Backend:** FastAPI + PostgreSQL, with secure account login (JWT-based sessions, hashed passwords), schema migrations managed with Alembic
- **AI layer:** Groq (Llama 3.3) reads the task description and extracts structured priority and due-date data
- **Email:** Transactional emails (verification, password reset) sent via Resend
- **Frontend:** A lightweight, single-page interface — no bloated dependencies, fast to load
- **Hosting:** Backend on Render, database on Neon, frontend on Vercel

## Try it

1. Open the [live app](https://frontend-gse2.vercel.app/)
2. Create an account and verify your email
3. Add a task the way you'd naturally describe it to a person — include timing and urgency if they matter
4. Watch the priority and due date get filled in automatically

---

*Note: the backend runs on a free hosting tier, so the first request after a period of inactivity may take a few extra seconds to respond while the server spins back up.*