# HotelFlow Tanzania — Demo

A premium Streamlit demo for Tanzanian hotel operations: reservations, rooms, guests, payments, housekeeping, reports, calendar, settings, and demo reset.

## Setup (local)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```

## Entry point

`app.py`

## Demo environment

- All data is simulated fiction (names, bookings, payments).
- Currency: TZS. Base date: 2026-10-27.
- Session-state persistence only — changes survive refreshes within a session, not across browsers/devices.
- Reset button in sidebar restores full demo dataset.
- No real payment processing or external APIs.

## Deployment — Streamlit Community Cloud (recommended)

1. Push this directory to a public GitHub repository.
2. Go to https://streamlit.io/cloud and sign in with GitHub.
3. Select the repo and branch; set main file path to `HotelManagementSystem/app.py` (or move `app.py` to repo root).
4. Deploy; copy the public URL.
5. Set repository visibility to public for easiest sharing.

Requirements checked:
- `requirements.txt` includes streamlit, pandas, plotly.
- No embedded API keys, tokens, or real customer data.
- `.gitignore` excludes temp files and secrets.

## Security / persistence limitations

- Not a production multi-user SaaS.
- No database backend; session-state temporary.
- No authentication implemented (demonstration only).
- Do not expose to production traffic without adding auth, database, and security review.

## Test

```bash
python test_audit.py
```

## Demo checklist for a hotel owner

1. Dashboard — occupancy, revenue chart, arrivals/departures
2. Reservations — create/edit/check-in/checkout/cancel
3. Payments — simulated recording; balances update
4. Rooms — status/housekeeping changes
5. Housekeeping — complete task → room available
6. Reports — live metrics from records
7. Calendar — booking view
8. Settings — editable profile
9. Reset — restore demo data
