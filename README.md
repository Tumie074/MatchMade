# Match Made

**Stop knocking on closed doors.**

Match Made is an AI opportunity matcher for young South Africans. It shows each person only the
opportunities they qualify for, explains every yes or no, and points to the one step that opens
the most new doors.

Built for the **NEMISA Hackathon 2026 · Challenge Area 02: Youth Employment and Digital Entrepreneurship**.

## The problem

Youth unemployment (ages 15–34) is 47.3%, and 3.7 million South Africans have stopped looking
for work (Stats SA, QLFS Q3 2026). The opportunities that do exist are hard to reach:

- Eligibility rules are hidden at the bottom of adverts.
- Closing dates differ between listing sites and official portals.
- Every advert needs a tailored CV.
- Listings are scattered, cost data, and some are scams that ask for fees.

## What Match Made does

| Feature | What it answers |
|---|---|
| **Qualify** | "Do I qualify?" A clear yes or no for every rule, with the reason. |
| **Unlock** | "What's my next step?" The certificate that opens the most opportunities, ranked. |
| **Verify** | "Is this real?" Dates checked on official portals; listings that ask for money are blocked. |
| **Readiness** | Which documents are missing or out of date (e.g. certified copies older than 3 months). |
| **Founder Path** | Funding young founders qualify for, plus short business playbooks. |

The innovation: **everyone else lists opportunities, we read them.** AI turns each advert into
structured rules (`pipeline/`). Matching is then plain rule checks (`backend/app/matching.py`),
so every answer is exact and explainable.

## Repository layout

```
matchmade/
├── backend/        FastAPI app and matching engine (Python)
│   ├── app/        models.py, matching.py, main.py
│   ├── data/       demo opportunities (fictional organisations)
│   └── tests/      pytest tests
├── pipeline/       AI rule extraction from adverts
├── whatsapp/       WhatsApp bot (planned)
├── frontend/       React web app (planned)
└── docs/           architecture and pitch material
```

## Run it locally

You need Python 3.11 or newer.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                            # 7 tests should pass
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs and try `POST /match` with this profile:

```json
{
  "name": "Thandi",
  "age": 22,
  "province": "Gauteng",
  "qualification": "degree",
  "field_of_study": "IT",
  "average": 68,
  "employment_status": "unemployed",
  "documents": [
    {"type": "cv"},
    {"type": "academic_record"},
    {"type": "certified_id", "issued": "2026-06-01"}
  ]
}
```

You'll get her eligible matches, near misses with reasons, the top **Unlock** step
(Azure Fundamentals opens 2 more internships) and the blocked scam listing.

## Tech stack

| Layer | Technology |
|---|---|
| App | React progressive web app |
| Messaging | WhatsApp Business Cloud API; USSD later |
| Back end | Python (FastAPI) on Microsoft Azure |
| Data | PostgreSQL; encrypted blob storage |
| Pipeline | Python collectors and Databricks jobs |
| AI | LLM for rule extraction, CV tailoring and interview practice |
| Insights | Power BI |

## Privacy (POPIA)

Consent first, minimal data, no ID numbers stored, and users can delete everything.
Never commit real personal information or API keys to this repository. Use `.env` (see `.env.example`).

## Team

| Name | Role |
|---|---|
| [Name] | Data and AI |
| [Name] | Back end |
| [Name] | Front end |
| [Name] | Design and UX |
| [Name] | Research and pitch |

See [CONTRIBUTING.md](CONTRIBUTING.md) for how we work together.
