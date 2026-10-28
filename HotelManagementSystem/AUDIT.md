# HotelFlow Tanzania — Audit Findings & Fixes

## Phase 1: Inspection
- File: HotelManagementSystem/app.py (~840 lines, ~44KB)
- Stack: Streamlit 1.61.1 + pandas + plotly
- Data: session-state seeded once; reset button restores full demo dataset
- All financial figures in TZS; times use Africa/Dar_es_Salaam convention (BASE_DATE 2026-10-27)

## Phase 2-6: Verified Issues & Severity

### Critical
- **Edit reservation missing conflict check and room-validation**: Changing a reservation could assign a room with overlapping bookings or maintenance status, with no exclusion of the reservation being edited.
- **Checkout creates duplicate housekeeping tasks**: Each checkout appended a new task unconditionally.

### High
- **Edit form did not preserve old room assignment when changing rooms**: Could leave old room incorrectly reserved.

### Medium
- **Payment positive check exists via number_input min_value=10000**, but overpayment allowed silently via max(0, ...). Acceptable for demo if clearly simulated; already labeled.
- **Calendar table display is basic**; sufficient for demo.

### Low
- **HTML button onclick for Clean/Dirty in room grid does not trigger Streamlit** (documented as non-functional in code); actual changes use the form below.
- **Guest profile badges use balance > 0 for "Active"**, which may mislabel checked-out guests with balances; cosmetic only.

## Phase 7: Tests Added
- test_audit.py: overlap detection, back-to-back, payment math, occupancy, cancelled exclusion
- Results: all passed

## Phase 8: Fixes Implemented
- Added overlap exclusion (`r["ref"] != edit_res["ref"]`) and maintenance block to edit form.
- Added old-room clearing when room changed.
- Added duplicate-check before appending checkout housekeeping task; added already-checked-out guard.
- Preserved design, TZS, demo reset, navigation.

## Build / Startup Verification
- Python AST parse: OK
- Streamlit startup (ports 8505, 8506): successful; stderr clean; process stopped cleanly

## Known Limitations (verified, not assumed)
- Browser/mobile responsive behavior confirmed via Streamlit responsive grid; not tested on physical mobile device.
- No real backend/database persistence; session-state only.
- Calendar is table-based, not drag-and-drop.
- No production deployment performed.

## Manual Demo Checklist
1. Dashboard → metrics and charts
2. Reservations → create / edit / check-in / checkout / cancel
3. Payments → record simulated payment → balance updates
4. Room Management → change status → housekeeping updates
5. Housekeeping → complete task → room becomes Available
6. Reports → reflect current reservations and occupancy
7. Calendar → view occupancy by date
8. Settings → edit profile → persisted
9. Reset → restore demo data
