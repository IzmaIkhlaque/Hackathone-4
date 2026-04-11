# Phase 3 — Full Next.js Web App

This folder will contain the Next.js application replacing the Phase 1 HTML pages.

## Planned structure
```
web/nextjs/
├── app/
│   ├── layout.tsx
│   ├── page.tsx           ← Landing page
│   ├── dashboard/page.tsx
│   ├── learn/[chapter]/page.tsx
│   └── quiz/[id]/page.tsx
├── components/
│   ├── ChapterList.tsx
│   ├── ProgressBar.tsx
│   └── QuizCard.tsx
└── package.json
```

## New features in Phase 3
- JWT authentication
- Admin dashboard
- Team management
- Full observability (Langfuse)

## What stays the same
All backend API routes — same FastAPI, same DB, same R2.
