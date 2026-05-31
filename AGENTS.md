# Commit Roast — Dev Notes

## Architecture
- Vite + React + TypeScript + Tailwind
- Multi-provider AI (OpenAI / Gemini / Anthropic)
- GitHub API (free, no key)
- html2canvas for PNG export
- Deployed to GitHub Pages

## Key decisions
- **No backend** — API calls go directly from browser to provider
- **Bring your own key** — users paste their own API key
- **Local storage** — keys stored only in memory (React state), cleared on refresh

## Providers
| Provider | Model | Endpoint |
|----------|-------|----------|
| OpenAI | gpt-4o-mini | api.openai.com |
| Gemini | gemini-1.5-flash | generativelanguage.googleapis.com |
| Anthropic | claude-3-haiku | api.anthropic.com |
