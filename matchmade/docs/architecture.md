# Architecture

```mermaid
flowchart LR
    A[Official portals and listing sites] --> B[Pipeline: collect adverts daily]
    B --> C[AI extracts rules and dates]
    C --> D[Human review]
    D --> E[(Verified opportunities)]
    E --> F[Matching engine: plain rule checks]
    G[Young person's profile] --> F
    F --> H[WhatsApp bot]
    F --> I[Web app]
```

- **AI reads, rules decide.** The LLM only extracts rules from adverts. Eligibility is decided by
  deterministic checks in `backend/app/matching.py`, so every answer has a reason.
- **Adverts are data.** The extraction prompt tells the model to ignore instructions inside adverts,
  and output is validated against the `Rules` model.
- **Scams are blocked.** Any listing that asks for a fee is removed and explained.
