import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import plotly.express as px
import plotly.graph_objects as go
import random
import hashlib

# -----------------------------------------------------------
# Setup
# -----------------------------------------------------------
st.set_page_config(
    page_title="HotelFlow Tanzania — Demo",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------
# Custom CSS: premium dark navy / warm white / teal accents
# -----------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
* { font-family: 'Instrument Sans', ui-sans-serif, system-ui, sans-serif; }
html, body, [class*="css"] { background-color: #0b1220; color: #ede9e0; }
.stApp { background: linear-gradient(180deg, #0b1220 0%, #0f1a2e 100%); }

/* Sidebar */
[data-testid="stSidebar"] { background: #09101a; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebar"] .stMarkdown { color: #ede9e0; }

/* Cards */
.card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 22px; margin-bottom: 16px; }
.card h3, .card h4 { color: #f0ebe2; margin: 0 0 6px 0; }
.card p { color: #b0a99e; font-size: 0.9rem; margin: 0; }

/* Metrics */
[data-testid="metric-container"] { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 18px; }
[data-testid="metric-container"] > div { color: #ede9e0 !important; }

/* Inputs */
.stTextInput>div>div>input, .stSelectbox>div>div>div>input, .stDateInput>div>div>input, .stNumberInput>div>div>input { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12); border-radius: 10px; color: #ede9e0 !important; }
.stTextInput>label, .stSelectbox>label, .stDateInput>label { color: #cfc9bc !important; font-weight: 500; font-size: 0.85rem; }

/* Tables */
[data-testid="stDataFrame"] { background: rgba(255,255,255,0.03); border-radius: 14px; border: 1px solid rgba(255,255,255,0.08); }

/* Divider */
.stDivider { border-color: rgba(255,255,255,0.08); }

/* Badges */
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.03em; border: 1px solid transparent; }
.badge-green { background: rgba(60,185,130,0.12); color: #3cb982; border-color: rgba(60,185,130,0.25); }
.badge-amber { background: rgba(220,170,80,0.12); color: #dca850; border-color: rgba(220,170,80,0.25); }
.badge-red { background: rgba(220,90,90,0.12); color: #dc5a5a; border-color: rgba(220,90,90,0.25); }
.badge-blue { background: rgba(70,160,220,0.12); color: #46a0dc; border-color: rgba(70,160,220,0.25); }
.badge-teal { background: rgba(30,170,160,0.12); color: #1eaaa0; border-color: rgba(30,170,160,0.25); }
.badge-gold { background: rgba(210,170,90,0.12); color: #d2aa5a; border-color: rgba(210,170,90,0.25); }

/* Buttons */
.stButton>button { background: linear-gradient(135deg, #1eaaa0 0%, #17766c 100%); color: #fff; border: none; border-radius: 10px; font-weight: 600; padding: 8px 18px; transition: all 0.2s; box-shadow: 0 2px 10px rgba(30,170,160,0.25); }
.stButton>button:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(30,170,160,0.35); }

/* Headers */
.section-title { font-family: 'Instrument Serif', serif; font-size: 1.9rem; color: #f0ebe2; letter-spacing: -0.02em; margin-bottom: 4px; }
.subtitle { color: #8e8778; font-size: 0.95rem; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# Data helpers / seed
# -----------------------------------------------------------

NAMES_TZ = ["Fatma Ali", "Juma Nyerere", "Neema Manda", "Khalid Said", "Zambia Hamza", "Aisha Bwana", "David Kessy", "Grace Mwanga", "Loran Mallya", "Omar Hussein", "Patricia Mroz", "Samuel Kamala"]
ROOM_TYPES = ["Standard", "Double", "Deluxe", "Suite"]
STATES = ["Available", "Occupied", "Reserved", "Dirty", "Maintenance"]

BASE_DATE = date(2026, 10, 27)

def make_ref():
    return "HTZ-" + str(random.randint(100, 999))

def seed_data(reset=False):
    # Rooms ~20
    rooms = []
    for i in range(1, 21):
        rt = ROOM_TYPES[i % 4] if i % 4 else ROOM_TYPES[0]
        rate = {"Standard": 120000, "Double": 180000, "Deluxe": 320000, "Suite": 650000}[rt]
        status = random.choices(STATES, weights=[30, 35, 10, 15, 10])[0]
        rooms.append({
            "id": f"R{i:03d}", "number": f"{i}" if i < 100 else str(i),
            "type": rt, "capacity": 2 if rt in ["Standard","Double"] else (3 if rt=="Deluxe" else 4),
            "rate": rate, "status": status,
            "housekeeping": "Clean" if status == "Available" else ("Dirty" if status == "Dirty" else "In Progress" if status == "Occupied" else "Clean"),
            "guest": "-" if status != "Occupied" else random.choice(NAMES_TZ),
        })
    # Reservations ~13
    reservations = []
    statuses = ["Confirmed", "Checked-in", "Checked-out", "Cancelled"]
    for i in range(13):
        ref = make_ref()
        room = random.choice([r["number"] for r in rooms])
        guest = random.choice(NAMES_TZ)
        check_in = BASE_DATE + timedelta(days=random.randint(-2, 5))
        nights = random.randint(2, 6)
        check_out = check_in + timedelta(days=nights)
        total = rooms[[r["number"] for r in rooms].index(room)]["rate"] * nights
        paid = round(total * random.choice([0.0, 0.3, 0.5, 1.0]), 0)
        res = {
            "ref": ref, "guest": guest, "room": room,
            "type": rooms[[r["number"] for r in rooms].index(room)]["type"],
            "check_in": check_in, "check_out": check_out,
            "nights": nights, "guests": random.randint(1, 3),
            "rate": rooms[[r["number"] for r in rooms].index(room)]["rate"],
            "total": int(total), "paid": int(paid), "balance": int(total - paid),
            "status": random.choices(statuses, weights=[30, 25, 25, 20])[0],
            "source": random.choice(["Direct", "Booking.com", "Walk-in", "Phone"]),
            "created": BASE_DATE - timedelta(days=random.randint(1, 30)),
        }
        reservations.append(res)

    # Guests ~12
    guests = []
    for g in NAMES_TZ:
        spent = random.randint(250000, 3200000)
        balance = random.randint(0, 1200000)
        guests.append({
            "name": g, "phone": f"+255 7{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}",
            "email": f"{g.lower().replace(' ','').replace('.','')}@example.co.tz",
            "total_spent": spent, "balance": balance,
            "notes": random.choice(["Requests early check-in", "Dietary restrictions", "Champagne welcome", "Prefers high floor", ""]),
            "history_count": random.randint(1, 4),
        })

    # Payments ~8
    payments = []
    for r in reservations:
        if r["paid"] > 0:
            payments.append({
                "ref": r["ref"], "guest": r["guest"],
                "amount": r["paid"], "method": random.choice(["Cash", "Bank Transfer", "Mobile Money (M-Pesa)", "Card"]),
                "date": r["check_in"] + timedelta(days=random.randint(0, 2)),
                "status": "Completed",
            })
    # Add a couple extra payments
    for _ in range(2):
        payments.append({
            "ref": random.choice([r["ref"] for r in reservations]),
            "guest": random.choice(NAMES_TZ),
            "amount": random.randint(300000, 1200000),
            "method": random.choice(["Cash", "Bank Transfer", "Mobile Money (M-Pesa)"]),
            "date": BASE_DATE - timedelta(days=random.randint(1, 10)),
            "status": "Completed",
        })

    # Housekeeping ~10
    housekeeping = []
    for i in range(10):
        room = random.choice([r["number"] for r in rooms])
        housekeeping.append({
            "room": room,
            "task": random.choice(["Clean room", "Change linens", "Inspect bathroom", "Restock amenities", "Deep clean"]),
            "status": random.choice(["Pending", "In Progress", "Completed"]),
            "staff": random.choice(["Amina Hussein", "Joseph Kessy", "Grace Manda", "Michael Nyambala"]),
            "priority": random.choice(["Low", "Medium", "High"]),
            "updated": BASE_DATE - timedelta(hours=random.randint(0, 12)),
        })

    # Revenue by day (7 days)
    revenue_days = []
    for d in range(7):
        rev = random.randint(350000, 1200000)
        revenue_days.append({"date": BASE_DATE - timedelta(days=6-d), "revenue": rev})

    # Save to session
    st.session_state.rooms = rooms
    st.session_state.reservations = reservations
    st.session_state.guests = guests
    st.session_state.payments = payments
    st.session_state.housekeeping = housekeeping
    st.session_state.revenue_days = revenue_days
    st.session_state.hotel = {
        "name": "HotelFlow Tanzania — Demo",
        "address": "Tanzania Hotel Centre, Ali Hassan Mwinyi Road, Dar es Salaam",
        "phone": "+255 22 123 4567",
        "email": "demo@hotelflow.co.tz",
        "currency": "TZS",
        "check_in": "14:00",
        "check_out": "11:00",
    }
    st.session_state.data_initialized = True
    st.session_state.seed_version = 2

# Initialize
if "data_initialized" not in st.session_state or st.session_state.get("seed_version") != 2:
    seed_data()

# -----------------------------------------------------------
# Helper functions
# -----------------------------------------------------------
def fmt_tzs(n):
    return f"{int(n):,}"

def calc_occupancy(rooms):
    total = len(rooms)
    occ = sum(1 for r in rooms if r["status"] == "Occupied")
    return round(occ / total * 100, 1) if total else 0

def get_today_arrivals(reservations):
    return [r for r in reservations if r["status"] == "Checked-in" and r["check_in"] == BASE_DATE]

def get_today_departures(reservations):
    return [r for r in reservations if r["status"] in ("Checked-out", "Checked-in") and r["check_out"] == BASE_DATE]

def get_active_reservations(reservations):
    return [r for r in reservations if r["status"] in ("Confirmed", "Checked-in")]

def find_room_by_number(number):
    for r in st.session_state.rooms:
        if r["number"] == number:
            return r
    return None

def find_reservation(ref):
    for r in st.session_state.reservations:
        if r["ref"] == ref:
            return r
    return None

# -----------------------------------------------------------
# Sidebar nav
# -----------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0;">
        <h1 style="font-family:'Instrument Serif',serif; color:#ede9e0; font-size:1.7rem; letter-spacing:-0.02em; margin:0;">HotelFlow</h1>
        <p style="color:#1eaaa0; font-size:0.7rem; letter-spacing:3px; font-weight:700; margin-top:4px;">TANZANIA DEMO</p>
    </div>
    <div style="border-top:1px solid rgba(255,255,255,0.08); margin:8px 0;"></div>
    """, unsafe_allow_html=True)

    nav = st.radio(
        "",
        ["Dashboard", "Reservations", "Rooms", "Guests", "Payments", "Housekeeping", "Reports", "Calendar", "Settings"],
        label_visibility="collapsed",
    )

    st.divider()

    # Reset button
    if st.button("🔄 Reset Demo Data", use_container_width=True):
        seed_data()
        st.experimental_rerun()

    st.markdown("""
    <div style="padding:8px 0; opacity:0.7; font-size:0.75rem; line-height:1.6;">
        <p><strong>Demo Environment</strong></p>
        <p>All data is simulated. No real payments or guests.</p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------
# Dashboard
# -----------------------------------------------------------
if nav == "Dashboard":
    st.markdown("<div class='section-title'>Executive Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>HotelFlow Tanzania — real-time operations overview (Demo)</div>", unsafe_allow_html=True)

    rooms = st.session_state.rooms
    reservations = st.session_state.reservations
    occupancy = calc_occupancy(rooms)
    total_rooms = len(rooms)
    occupied = sum(1 for r in rooms if r["status"] == "Occupied")
    available = sum(1 for r in rooms if r["status"] == "Available")
    reserved = sum(1 for r in rooms if r["status"] == "Reserved")

    arrivals = len(get_today_arrivals(reservations))
    departures = len(get_today_departures(reservations))

    today_rev = sum(r["total"] for r in reservations if r["check_in"] == BASE_DATE)
    total_rev_active = sum(r["total"] for r in get_active_reservations(reservations))
    outstanding = sum(r["balance"] for r in reservations if r["status"] in ("Confirmed", "Checked-in"))

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Rooms", total_rooms, delta=f"{reserved} reserved")
    with c2:
        st.metric("Occupied", occupied, delta=f"{occupancy}% occupancy")
    with c3:
        st.metric("Available", available)
    with c4:
        st.metric("Today's Revenue", f"{fmt_tzs(today_rev)} TZS", delta=f"{fmt_tzs(total_rev_active)} active")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric("Arrivals Today", arrivals)
    with c6:
        st.metric("Departures Today", departures)
    with c7:
        st.metric("Outstanding Balances", f"{fmt_tzs(outstanding)} TZS", delta="Pending payments")
    with c8:
        st.metric("Active Reservations", len(get_active_reservations(reservations)))

    # Main content split
    left, right = st.columns([3, 2])
    with left:
        st.markdown("### Occupancy Overview")
        status_counts = pd.DataFrame({"Status": ["Available","Occupied","Reserved","Dirty","Maintenance"], "Count": [
            sum(1 for r in rooms if r["status"]=="Available"),
            sum(1 for r in rooms if r["status"]=="Occupied"),
            sum(1 for r in rooms if r["status"]=="Reserved"),
            sum(1 for r in rooms if r["status"]=="Dirty"),
            sum(1 for r in rooms if r["status"]=="Maintenance"),
        ]})
        fig = px.bar(status_counts, x="Status", y="Count", color="Status",
                     color_discrete_map={"Available":"#3cb982","Occupied":"#dca850","Reserved":"#46a0dc","Dirty":"#dc5a5a","Maintenance":"#8e8778"},
                     template="plotly_dark", height=320)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ede9e0",
                          margin=dict(l=20,r=20,t=30,b=20), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # Revenue 7-day chart
        rev_df = pd.DataFrame(st.session_state.revenue_days)
        rev_df["date_str"] = rev_df["date"].apply(lambda d: d.strftime("%a %d"))
        fig_rev = px.line(rev_df, x="date_str", y="revenue", markers=True,
                          template="plotly_dark", height=300)
        fig_rev.update_traces(line_color="#1eaaa0", marker=dict(color="#1eaaa0", size=8))
        fig_rev.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ede9e0",
                              margin=dict(l=20,r=20,t=30,b=20), yaxis_tickformat=",.0f")
        fig_rev.update_yaxes(tickprefix="TZS ")
        st.markdown("### Revenue (Last 7 Days)")
        st.plotly_chart(fig_rev, use_container_width=True)

    with right:
        st.markdown("### Recent Reservations")
        recent = sorted(reservations, key=lambda r: r["created"], reverse=True)[:5]
        for r in recent:
            status_badge = f'<span class="badge badge-green">{r["status"]}</span>' if r["status"]=="Checked-in" else f'<span class="badge badge-amber">{r["status"]}</span>' if r["status"]=="Confirmed" else f'<span class="badge badge-red">{r["status"]}</span>' if r["status"]=="Cancelled" else f'<span class="badge badge-teal">{r["status"]}</span>'
            st.markdown(f"""
            <div class="card" style="padding:14px 16px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h4 style="margin:0; font-size:0.95rem; color:#ede9e0;">{r["guest"]}</h4>
                        <p style="margin:2px 0 0; font-size:0.8rem; color:#8e8778;">Ref: <strong style="color:#d2aa5a;">{r["ref"]}</strong> · Room {r["room"]} · {r["check_in"].strftime("%b %d")} → {r["check_out"].strftime("%b %d")}</p>
                    </div>
                    <div style="text-align:right;">{status_badge}<br><span style="font-size:0.8rem; color:#1eaaa0; font-weight:600;">{fmt_tzs(r["total"])} TZS</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Upcoming Check-ins")
        upcoming = [r for r in reservations if r["status"] in ("Confirmed","Checked-in") and r["check_in"] >= BASE_DATE and r["check_in"] <= BASE_DATE + timedelta(days=3)]
        for r in upcoming[:4]:
            st.markdown(f"""
            <div style="padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.06); font-size:0.85rem; color:#ede9e0;">
                <strong>{r["guest"]}</strong> — Room {r["room"]} <span style="color:#8e8778;">· {r["check_in"].strftime("%b %d")}</span>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------
# Reservations
# -----------------------------------------------------------
elif nav == "Reservations":
    st.markdown("<div class='section-title'>Reservations</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Manage bookings, check-ins, payments, and changes</div>", unsafe_allow_html=True)

    reservations = st.session_state.reservations
    rooms = st.session_state.rooms

    # Search + filter
    search = st.text_input("Search by name, reference, or phone", placeholder="Fatma Ali / HTZ-101")
    status_filter = st.selectbox("Status", ["All", "Confirmed", "Checked-in", "Checked-out", "Cancelled"])

    filtered = reservations
    if search:
        s = search.lower()
        filtered = [r for r in filtered if s in r["guest"].lower() or s in r["ref"].lower()]
    if status_filter != "All":
        filtered = [r for r in filtered if r["status"] == status_filter]

    # Table
    df_res = pd.DataFrame(filtered)
    if not df_res.empty:
        df_res = df_res[["ref","guest","room","type","check_in","check_out","nights","guests","rate","total","paid","balance","status","source"]]
        df_res["check_in"] = df_res["check_in"].apply(lambda d: d.strftime("%Y-%m-%d") if isinstance(d, date) else d)
        df_res["check_out"] = df_res["check_out"].apply(lambda d: d.strftime("%Y-%m-%d") if isinstance(d, date) else d)
        df_display = df_res.copy()
        df_display["total"] = df_display["total"].apply(lambda x: f"{int(x):,}")
        df_display["paid"] = df_display["paid"].apply(lambda x: f"{int(x):,}")
        df_display["balance"] = df_display["balance"].apply(lambda x: f"{int(x):,}")
        df_display["rate"] = df_display["rate"].apply(lambda x: f"{int(x):,}")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No reservations match the filters.")

    # Detail / actions
    with st.expander("Open Reservation Detail / Actions"):
        selected_ref = st.selectbox("Select Reservation", [r["ref"] for r in reservations])
        res = find_reservation(selected_ref)
        if res:
            st.write(f"**Guest:** {res['guest']}  |  **Room:** {res['room']} ({res['type']})")
            st.write(f"**Dates:** {res['check_in']} → {res['check_out']} ({res['nights']} nights)  |  **Rate:** {fmt_tzs(res['rate'])} TZS/night")
            st.write(f"**Total:** {fmt_tzs(res['total'])} TZS  |  **Paid:** {fmt_tzs(res['paid'])} TZS  |  **Balance:** {fmt_tzs(res['balance'])} TZS")
            st.write(f"**Status:** {res['status']}  |  **Source:** {res['source']}")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("✅ Check In", key=f"ci_{res['ref']}"):
                    res["status"] = "Checked-in"
                    # Update room
                    room = find_room_by_number(res["room"])
                    if room:
                        room["status"] = "Occupied"
                        room["guest"] = res["guest"]
                        room["housekeeping"] = "In Progress"
                    st.experimental_rerun()
            with c2:
                if st.button("🚪 Check Out", key=f"co_{res['ref']}"):
                    if res["status"] == "Checked-out":
                        st.warning("Already checked out.")
                    else:
                        res["status"] = "Checked-out"
                        room = find_room_by_number(res["room"])
                        if room:
                            room["status"] = "Dirty"
                            room["guest"] = "-"
                            room["housekeeping"] = "Dirty"
                        # Add housekeeping task only if not already present for this room/task combo
                        existing = [h for h in st.session_state.housekeeping if h["room"] == res["room"] and h["task"] == "Clean room after checkout"]
                        if not existing:
                            st.session_state.housekeeping.append({
                                "room": res["room"], "task": "Clean room after checkout", "status": "Pending",
                                "staff": random.choice(["Amina Hussein","Joseph Kessy","Grace Manda"]), "priority": "High",
                                "updated": BASE_DATE,
                            })
                        st.experimental_rerun()
            with c3:
                if st.button("✏️ Edit", key=f"ed_{res['ref']}"):
                    st.session_state.edit_ref = res["ref"]
                    st.experimental_rerun()
            with c4:
                if st.button("❌ Cancel", key=f"cn_{res['ref']}"):
                    res["status"] = "Cancelled"
                    room = find_room_by_number(res["room"])
                    if room and room["guest"] == res["guest"]:
                        room["status"] = "Available"
                        room["guest"] = "-"
                    st.experimental_rerun()

    # Create new reservation
    with st.expander("➕ Create New Reservation"):
        with st.form("new_res_form", clear_on_submit=True):
            col_n, col_g = st.columns(2)
            with col_n:
                new_guest = st.text_input("Guest Name", placeholder="e.g. Fatma Ali")
            with col_g:
                new_room = st.selectbox("Room", [r["number"] for r in rooms if r["status"] != "Maintenance"])
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                new_in = st.date_input("Check-in", BASE_DATE + timedelta(days=1))
            with col_d2:
                new_out = st.date_input("Check-out", BASE_DATE + timedelta(days=4))
            new_nights = max(1, (new_out - new_in).days)
            new_guests = st.number_input("Guests", min_value=1, max_value=5, value=2)
            submitted = st.form_submit_button("Confirm Booking")
            if submitted:
                if new_guest and new_in < new_out:
                    # Check overlap for same room
                    conflicts = [r for r in reservations if r["room"] == new_room and r["status"] not in ("Cancelled",) and not (r["check_out"] <= new_in or r["check_in"] >= new_out)]
                    if conflicts:
                        st.error("Room is unavailable for those dates (conflicting booking).")
                    else:
                        room_obj = find_room_by_number(new_room)
                        rate = room_obj["rate"] if room_obj else 120000
                        total = rate * new_nights
                        new_ref = make_ref()
                        reservations.append({
                            "ref": new_ref, "guest": new_guest, "room": new_room,
                            "type": room_obj["type"] if room_obj else "Standard",
                            "check_in": new_in, "check_out": new_out,
                            "nights": new_nights, "guests": int(new_guests),
                            "rate": rate, "total": int(total), "paid": 0, "balance": int(total),
                            "status": "Confirmed", "source": "Direct", "created": BASE_DATE,
                        })
                        room_obj["status"] = "Reserved"
                        room_obj["guest"] = new_guest
                        st.success(f"Booking confirmed: {new_ref} for {new_guest}")
                        st.experimental_rerun()
                else:
                    st.error("Please enter valid dates and names.")

    # Edit mode
    if "edit_ref" in st.session_state:
        edit_res = find_reservation(st.session_state.edit_ref)
        if edit_res:
            edit_res["_old_room"] = edit_res.get("_old_room") or edit_res["room"]
            with st.form("edit_res_form", clear_on_submit=True):
                new_guest_e = st.text_input("Guest Name", value=edit_res["guest"])
                new_room_e = st.selectbox("Room", [r["number"] for r in rooms], index=[r["number"] for r in rooms].index(edit_res["room"]))
                new_out_e = st.date_input("New Checkout", edit_res["check_out"])
                submitted_e = st.form_submit_button("Save Changes")
                if submitted_e:
                    # Validate new room not under maintenance
                    new_room_obj = find_room_by_number(new_room_e)
                    if not new_room_obj:
                        st.error("Selected room not found.")
                    elif new_room_obj["status"] == "Maintenance":
                        st.error("Room is under maintenance.")
                    else:
                        # Check overlap excluding this reservation
                        conflicts = [r for r in reservations if r["ref"] != edit_res["ref"] and r["room"] == new_room_e and r["status"] not in ("Cancelled",) and not (r["check_out"] <= edit_res["check_in"] or r["check_in"] >= new_out_e)]
                        if conflicts:
                            st.error("This room is unavailable for the new dates due to another booking.")
                        else:
                            edit_res["guest"] = new_guest_e
                            edit_res["room"] = new_room_e
                            edit_res["check_out"] = new_out_e
                            edit_res["nights"] = max(1, (new_out_e - edit_res["check_in"]).days)
                            if new_room_obj:
                                edit_res["type"] = new_room_obj["type"]
                                edit_res["rate"] = new_room_obj["rate"]
                                edit_res["total"] = int(edit_res["rate"] * edit_res["nights"])
                                edit_res["balance"] = int(edit_res["total"] - edit_res["paid"])
                                if edit_res["status"] == "Confirmed":
                                    new_room_obj["status"] = "Reserved"
                                new_room_obj["guest"] = new_guest_e
                            # Clear old room assignment if changed
                            if edit_res.get("_old_room") and edit_res["_old_room"] != new_room_e:
                                old_r = find_room_by_number(edit_res["_old_room"])
                                if old_r and old_r["status"] == "Reserved" and old_r["guest"] == new_guest_e:
                                    old_r["status"] = "Available"
                                    old_r["guest"] = "-"
                            edit_res["_old_room"] = new_room_e
                            st.success("Reservation updated.")
                            del st.session_state.edit_ref
                            st.experimental_rerun()
            if st.button("Cancel Edit"):
                del st.session_state.edit_ref
                st.experimental_rerun()

# -----------------------------------------------------------
# Rooms
# -----------------------------------------------------------
elif nav == "Rooms":
    st.markdown("<div class='section-title'>Room Management</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Status, housekeeping, and details for every room</div>", unsafe_allow_html=True)

    rooms = st.session_state.rooms
    view = st.radio("View", ["Grid", "Table"], horizontal=True)
    filter_stat = st.multiselect("Filter by status", ["Available","Occupied","Reserved","Dirty","Maintenance"], default=["Available","Occupied","Reserved","Dirty","Maintenance"])
    filtered_rooms = [r for r in rooms if r["status"] in filter_stat]

    if view == "Grid":
        cols = st.columns(4)
        for idx, r in enumerate(filtered_rooms):
            with cols[idx % 4]:
                badge = f'<span class="badge badge-green">{r["status"]}</span>' if r["status"]=="Available" else f'<span class="badge badge-amber">{r["status"]}</span>' if r["status"]=="Occupied" else f'<span class="badge badge-blue">{r["status"]}</span>' if r["status"]=="Reserved" else f'<span class="badge badge-red">{r["status"]}</span>' if r["status"]=="Dirty" else f'<span class="badge badge-teal">{r["status"]}</span>'
                st.markdown(f"""
                <div class="card" style="padding:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <h4 style="margin:0; font-size:1.1rem; color:#ede9e0;">Room {r["number"]}</h4>
                        <div>{badge}</div>
                    </div>
                    <p style="margin:4px 0; color:#b0a99e; font-size:0.85rem;"><strong>{r["type"]}</strong> · {r["capacity"]} guests · {fmt_tzs(r["rate"])} TZS</p>
                    <p style="margin:4px 0; color:#8e8778; font-size:0.8rem;">Guest: <strong style="color:#ede9e0;">{r["guest"]}</strong></p>
                    <p style="font-size:0.8rem; color:#8e8778;">Housekeeping: {r["housekeeping"]}</p>
                    <div style="margin-top:8px; display:flex; gap:6px;">
                        <button onclick="window.streamlitSetComponentValue('change_{r['number']}','clean')" style="font-size:0.75rem; padding:4px 8px; border-radius:6px; border:none; background:#1eaaa0; color:#fff;">Clean</button>
                        <button onclick="window.streamlitSetComponentValue('change_{r['number']}','dirty')" style="font-size:0.75rem; padding:4px 8px; border-radius:6px; border:none; background:#dc5a5a; color:#fff;">Dirty</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # Actual actions via session-state buttons because HTML buttons don't trigger streamlit easily; instead use form-like buttons per card using columns
    else:
        df_r = pd.DataFrame(filtered_rooms)
        df_r_display = df_r[["number","type","capacity","rate","status","guest","housekeeping"]].copy()
        df_r_display["rate"] = df_r_display["rate"].apply(lambda x: f"{int(x):,}")
        st.dataframe(df_r_display, use_container_width=True, hide_index=True)

    # Change status actions (simpler approach: selectbox + button)
    with st.expander("Update Room Status / Housekeeping"):
        col_r, col_a = st.columns([2, 2])
        with col_r:
            target = st.selectbox("Select Room", [r["number"] for r in rooms])
            new_status = st.selectbox("New Status", ["Available", "Occupied", "Reserved", "Dirty", "Maintenance"])
        with col_a:
            if st.button("Apply Status Change", use_container_width=True):
                r_obj = find_room_by_number(target)
                if r_obj:
                    old = r_obj["status"]
                    r_obj["status"] = new_status
                    if new_status == "Available":
                        r_obj["guest"] = "-"
                        r_obj["housekeeping"] = "Clean"
                    elif new_status == "Dirty":
                        r_obj["housekeeping"] = "Dirty"
                        r_obj["guest"] = "-"
                    elif new_status == "Occupied":
                        r_obj["housekeeping"] = "In Progress"
                    else:
                        r_obj["housekeeping"] = "Clean"
                    st.success(f"Room {target}: {old} → {new_status}")
                    st.experimental_rerun()

# -----------------------------------------------------------
# Guests
# -----------------------------------------------------------
elif nav == "Guests":
    st.markdown("<div class='section-title'>Guest Directory</div>", unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Profiles, history, and balances</div>', unsafe_allow_html=True)

    guests = st.session_state.guests
    search_g = st.text_input("Search guests", placeholder="Name or phone")
    filtered_g = guests
    if search_g:
        s = search_g.lower()
        filtered_g = [g for g in filtered_g if s in g["name"].lower() or s in g["phone"]]
    for g in filtered_g:
        status = "Checked In" if g["balance"] > 0 else "Checked Out"
        badge = '<span class="badge badge-green">Active</span>' if g["balance"] < 100000 else '<span class="badge badge-amber">Balance Due</span>'
        st.markdown(f"""
        <div class="card" style="padding:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h4 style="margin:0; color:#ede9e0;">{g["name"]}</h4>
                    <p style="margin:4px 0 0; font-size:0.85rem; color:#b0a99e;">{g["phone"]} · {g["email"]}</p>
                    <p style="margin:4px 0 0; font-size:0.8rem; color:#8e8778;">History: <strong style="color:#ede9e0;">{g["history_count"]}</strong> stays · Notes: {g["notes"] if g["notes"] else "None"}</p>
                </div>
                <div style="text-align:right;">
                    {badge}<br>
                    <span style="font-size:1rem; color:#1eaaa0; font-weight:700;">{fmt_tzs(g["total_spent"])} TZS</span>
                    <br><span style="font-size:0.8rem; color:#dc5a5a;">Balance: {fmt_tzs(g["balance"])} TZS</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------
# Payments
# -----------------------------------------------------------
elif nav == "Payments":
    st.markdown("<div class='section-title'>Payments</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Simulated payment tracking — clearly marked as demo data</div>", unsafe_allow_html=True)

    payments = st.session_state.payments
    reservations = st.session_state.reservations
    st.warning("⚠️ This is a demo environment. No real money is transferred. All transactions are simulated.")

    # Table
    df_pay = pd.DataFrame(payments)
    if not df_pay.empty:
        df_pay = df_pay[["ref","guest","amount","method","date","status"]].copy()
        df_pay["amount"] = df_pay["amount"].apply(lambda x: f"{int(x):,}")
        df_pay["date"] = df_pay["date"].apply(lambda d: d.strftime("%Y-%m-%d") if isinstance(d, date) else d)
        st.dataframe(df_pay, use_container_width=True, hide_index=True)
    else:
        st.info("No payment records.")

    with st.expander("➕ Record Simulated Payment"):
        with st.form("pay_form", clear_on_submit=True):
            res_ref = st.selectbox("Booking Reference", [r["ref"] for r in reservations])
            amount = st.number_input("Amount (TZS)", min_value=10000, step=50000, value=100000)
            method = st.selectbox("Method", ["Cash", "Bank Transfer", "Mobile Money (M-Pesa)", "Card"])
            submitted_p = st.form_submit_button("Record Payment")
            if submitted_p:
                res_obj = find_reservation(res_ref)
                if res_obj:
                    res_obj["paid"] += int(amount)
                    res_obj["balance"] = max(0, int(res_obj["total"] - res_obj["paid"]))
                    payments.append({
                        "ref": res_ref, "guest": res_obj["guest"],
                        "amount": int(amount), "method": method,
                        "date": BASE_DATE, "status": "Completed",
                    })
                    st.success(f"Recorded {fmt_tzs(amount)} TZS for {res_ref}")
                    st.experimental_rerun()

# -----------------------------------------------------------
# Housekeeping
# -----------------------------------------------------------
elif nav == "Housekeeping":
    st.markdown("<div class='section-title'>Housekeeping</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Task board with staff assignments and priorities</div>", unsafe_allow_html=True)

    hk = st.session_state.housekeeping
    df_hk = pd.DataFrame(hk)
    if not df_hk.empty:
        df_hk = df_hk[["room","task","status","staff","priority","updated"]].copy()
        df_hk["updated"] = df_hk["updated"].apply(lambda d: d.strftime("%Y-%m-%d %H:%M") if isinstance(d, (date, datetime)) else d)
        st.dataframe(df_hk, use_container_width=True, hide_index=True)
    else:
        st.info("No housekeeping tasks.")

    with st.expander("Update Task / Mark Room"):
        col_t, col_s = st.columns(2)
        with col_t:
            task_room = st.selectbox("Room", [r["number"] for r in st.session_state.rooms])
            new_task = st.selectbox("Task Status", ["Pending", "In Progress", "Completed"])
        with col_s:
            staff_sel = st.selectbox("Assign Staff", ["Amina Hussein","Joseph Kessy","Grace Manda","Michael Nyambala","Fatma Hussein"])
            if st.button("Update Task", use_container_width=True):
                # Find or create
                found = False
                for h in hk:
                    if h["room"] == task_room and h["task"] == "Clean room":
                        h["status"] = new_task
                        h["staff"] = staff_sel
                        h["updated"] = datetime.now()
                        found = True
                        break
                if not found:
                    hk.append({"room": task_room, "task": "Clean room", "status": new_task, "staff": staff_sel, "priority": "Medium", "updated": datetime.now()})
                # If completed, update room status to clean
                if new_task == "Completed":
                    r_obj = find_room_by_number(task_room)
                    if r_obj and r_obj["status"] == "Dirty":
                        r_obj["status"] = "Available"
                        r_obj["guest"] = "-"
                        r_obj["housekeeping"] = "Clean"
                st.success("Housekeeping updated.")
                st.experimental_rerun()

# -----------------------------------------------------------
# Reports
# -----------------------------------------------------------
elif nav == "Reports":
    st.markdown("<div class='section-title'>Reports & Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Calculated from demo records</div>", unsafe_allow_html=True)

    reservations = st.session_state.reservations
    rooms = st.session_state.rooms

    # Occupancy rate
    occ_rate = calc_occupancy(rooms)
    # Revenue by room type
    rev_by_type = {}
    for r in rooms:
        rev_by_type[r["type"]] = rev_by_type.get(r["type"], 0) + (r["rate"] if r["status"]=="Occupied" else 0)
    # Reservations by source
    src_counts = {}
    for r in reservations:
        src_counts[r["source"]] = src_counts.get(r["source"], 0) + 1

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("### Key Metrics")
        st.metric("Occupancy Rate", f"{occ_rate}%")
        total_active_rev = sum(r["total"] for r in get_active_reservations(reservations))
        st.metric("Active Revenue", f"{fmt_tzs(total_active_rev)} TZS")
        total_outstanding = sum(r["balance"] for r in reservations if r["status"] in ("Confirmed","Checked-in"))
        st.metric("Outstanding Balances", f"{fmt_tzs(total_outstanding)} TZS")
    with col_r2:
        st.markdown("### Revenue by Room Type (Occupied)")
        rev_df_type = pd.DataFrame({"Type": list(rev_by_type.keys()), "Revenue": list(rev_by_type.values())})
        fig_type = px.pie(rev_df_type, names="Type", values="Revenue", hole=0.55, template="plotly_dark", height=300)
        fig_type.update_traces(marker=dict(colors=["#1eaaa0","#dca850","#46a0dc","#dc5a5a"]))
        fig_type.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ede9e0", showlegend=True, legend=dict(font_size=11))
        st.plotly_chart(fig_type, use_container_width=True)

    # Reservations by source chart
    st.markdown("### Reservations by Source")
    df_src = pd.DataFrame({"Source": list(src_counts.keys()), "Count": list(src_counts.values())})
    fig_src = px.bar(df_src, x="Source", y="Count", color="Source", template="plotly_dark", height=300)
    fig_src.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#ede9e0", showlegend=False, margin=dict(l=20,r=20,t=30,b=20))
    st.plotly_chart(fig_src, use_container_width=True)

    # Check-in / checkout summary table
    st.markdown("### Today's Operations")
    today_in = get_today_arrivals(reservations)
    today_out = get_today_departures(reservations)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write(f"**Arrivals: {len(today_in)}**")
        for r in today_in[:3]:
            st.write(f"• {r['guest']} — Room {r['room']}")
    with col_t2:
        st.write(f"**Departures: {len(today_out)}**")
        for r in today_out[:3]:
            st.write(f"• {r['guest']} — Room {r['room']}")

# -----------------------------------------------------------
# Calendar
# -----------------------------------------------------------
elif nav == "Calendar":
    st.markdown("<div class='section-title'>Booking Calendar</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Room occupancy over time — click to open reservation</div>", unsafe_allow_html=True)

    reservations = st.session_state.reservations
    rooms = st.session_state.rooms
    # Simple 7-day calendar grid: rows = rooms, cols = dates from BASE_DATE to BASE_DATE+6
    days = [BASE_DATE + timedelta(days=d) for d in range(7)]
    # Build table data
    data = []
    for r in rooms:
        row = {"Room": r["number"], "Type": r["type"]}
        for d in days:
            # Find reservation for this room on this date (check-in <= d <= check-out) and not cancelled
            matches = [res for res in reservations if res["room"] == r["number"] and res["status"] not in ("Cancelled",) and res["check_in"] <= d < res["check_out"]]
            label = ""
            if matches:
                m = matches[0]
                label = f"{m['guest'][:12]} · {m['ref']}"
                if d == m["check_in"]:
                    label += " (IN)"
                if d == m["check_out"] - timedelta(days=1):
                    label += " (OUT)"
            row[d.strftime("%a %d")] = label
        data.append(row)

    df_cal = pd.DataFrame(data)
    # For display, just show as table; highlight occupied cells
    st.dataframe(df_cal, use_container_width=True, hide_index=True)

    # List reservations by date for interaction
    st.markdown("### Reservations by Date")
    for d in days:
        day_res = [res for res in reservations if res["status"] not in ("Cancelled",) and res["check_in"] <= d < res["check_out"]]
        if day_res:
            with st.container():
                st.markdown(f"**{d.strftime('%A %d %B %Y')}** — {len(day_res)} bookings")
                for res in day_res:
                    with st.expander(f"{res['guest']} — Room {res['room']} — {res['ref']}"):
                        st.write(f"Status: {res['status']} · Nights: {res['nights']} · Source: {res['source']} · Total: {fmt_tzs(res['total'])} TZS")

# -----------------------------------------------------------
# Settings
# -----------------------------------------------------------
elif nav == "Settings":
    st.markdown("<div class='section-title'>Hotel Settings</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Edit demo hotel profile (simulated)</div>", unsafe_allow_html=True)

    hotel = st.session_state.hotel
    with st.form("settings_form", clear_on_submit=True):
        new_name = st.text_input("Hotel Name", value=hotel["name"])
        new_addr = st.text_area("Address", value=hotel["address"], height=80)
        new_phone = st.text_input("Phone", value=hotel["phone"])
        new_email = st.text_input("Email", value=hotel["email"])
        new_currency = st.selectbox("Currency", ["TZS", "USD", "EUR"], index=["TZS","USD","EUR"].index(hotel["currency"]))
        new_ci = st.text_input("Check-in Time", value=hotel["check_in"])
        new_co = st.text_input("Check-out Time", value=hotel["check_out"])
        submitted_s = st.form_submit_button("Save Settings")
        if submitted_s:
            hotel["name"] = new_name
            hotel["address"] = new_addr
            hotel["phone"] = new_phone
            hotel["email"] = new_email
            hotel["currency"] = new_currency
            hotel["check_in"] = new_ci
            hotel["check_out"] = new_co
            st.success("Settings saved.")

    st.divider()
    st.markdown("### Current Profile")
    for k, v in hotel.items():
        st.write(f"**{k.replace('_',' ').title()}:** {v}")

# -----------------------------------------------------------
# Footer / Confirmation
# -----------------------------------------------------------
st.markdown("""<div style="margin-top:40px; padding-top:20px; border-top:1px solid rgba(255,255,255,0.08); color:#8e8778; font-size:0.8rem;">
<strong>HotelFlow Tanzania — Sales Demo</strong> · All data is fictional and simulated for demonstration purposes.<br>
No real payments, guests, or bookings are processed. Reset data anytime with the button in the sidebar.
</div>""", unsafe_allow_html=True)
