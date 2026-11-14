# How we work

## Who owns what

| Role | Folders | First tasks |
|---|---|---|
| Data and AI | `pipeline/` | Connect the LLM in `extract_rules.py`; test it on 10 real adverts |
| Back end | `backend/` | Add a database; add endpoints for profiles and saved matches |
| Front end | `frontend/` | Set up the React app; build the profile and matches screens |
| Design and UX | `docs/`, `frontend/` | Screens for profile, matches, Unlock and Founder Path |
| Research and pitch | `docs/` | Collect real adverts and founder interviews; keep the deck updated |

## Branches

1. Never push straight to `main`.
2. Make a branch per task: `feature/unlock-screen`, `fix/date-check`.
3. Open a pull request. One teammate reviews it before it's merged.
4. Tests must pass (GitHub runs them automatically on every pull request).

## Commits

Short and clear, e.g. `Add readiness check for certified copies`.

## Never commit

- API keys or passwords (use `.env`, which is ignored by git)
- Real people's personal information (use the fictional demo data)
