# CommitConfessions — Development Notes

## Overview
A single-page React app (Vite + TypeScript + Tailwind) that analyzes a GitHub user's commit history via Gemini AI and generates a shareable retro-styled personality card.

## How to run
```bash
npm install
npm run dev
```

## How to deploy
```bash
npm run deploy
```
This builds to `dist/` and pushes to `gh-pages` branch. Enable Pages in repo settings to serve from `gh-pages`.

## Architecture
- **GitHub API** (free, no key) — fetches public commit history
- **Gemini 2.0 Flash API** (bring your own key) — analyzes commit personality
- **html2canvas** — renders the card as a downloadable PNG
- No backend, no database, no user data stored

## Key design decisions
- Retro/vaporwave aesthetic with CRT scanlines — stands out, hooks engagement
- Bring your own API key — no backend costs, security concerns eliminated
- GitHub Pages deployable — zero infrastructure
- Open graph tags planned for social sharing of cards
