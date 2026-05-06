import streamlit as st
import datetime as dt
import requests
import pandas as pd
import time

# Set page configuration for a premium feel
st.set_page_config(
    page_title="VAPI Hospital Agent | Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced aesthetics and visibility
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1, h2, h3 { color: #f8fafc !important; font-weight: 800 !important; }
    [data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    [data-testid="stSidebar"] input { color: #0f172a !important; background-color: #f8fafc !important; }
    div.stButton > button {
        width: 100%; border-radius: 8px; height: 3.5em; background-color: #2563eb; color: white;
        border: none; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
    }
    div.stButton > button:hover { background-color: #1d4ed8; transform: translateY(-2px); }
    [data-testid="stMetricValue"] { font-size: 2.5rem !important; font-weight: 800 !important; color: #38bdf8 !important; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital.png", width=80)
    st.title("Hospital Admin")
    base_url = st.text_input("Backend API", "http://127.0.0.1:4444").rstrip("/")
    st.divider()
    if st.button("🔄 Refresh Dashboard"): st.rerun()

col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏥 Dubai Medical Center")
    st.markdown("<p style='color: #94a3b8; font-size: 1.2rem;'>AI-Driven Appointment Orchestration</p>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='text-align: right; background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155;'><b>Status:</b> 🟢 ONLINE<br><small>Hugging Face Hub</small></div>", unsafe_allow_html=True)

st.divider()

# Stats
try:
    stats_resp = requests.get(f"{base_url}/stats/", timeout=5)
    if stats_resp.status_code == 200:
        stats = stats_resp.json()
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Bookings", stats.get("total", 0))
        m2.metric("Active Sessions", stats.get("active", 0))
        m3.metric("Canceled Orders", stats.get("canceled", 0))
except:
    st.warning("🔄 Connecting to backend...")

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📅 Create Booking", "❌ Revoke Booking", "📋 Records Directory"])

with tab1:
    st.markdown("### 📅 Schedule Appointment")
    c1, c2 = st.columns(2)
    p_name = c1.text_input("Patient Name", placeholder="Full legal name")
    p_reason = c1.text_input("Medical Reason", placeholder="e.g. Annual Physical")
    p_date = c2.date_input("Date", value=dt.date.today())
    p_time = c2.time_input("Time", value=dt.time(10, 0))
    
    if st.button("🚀 Confirm Appointment"):
        if not p_name: st.error("Patient Name is required.")
        else:
            payload = {"patient_name": p_name.strip(), "reason": p_reason.strip() or "Consultation", "start_time": dt.datetime.combine(p_date, p_time).isoformat()}
            try:
                resp = requests.post(f"{base_url}/schedule_appointment/", json=payload, timeout=10)
                if resp.status_code == 200:
                    st.success(f"✅ Successfully Booked: {p_name}")
                    st.balloons(); time.sleep(1); st.rerun()
                else: st.error(f"Error: {resp.text}")
            except Exception as e: st.error(f"Error: {e}")

with tab2:
    st.markdown("### ❌ Revoke Appointment")
    st.info("Searching is now CASE-INSENSITIVE (e.g., 'Prince' and 'prince' both work).")
    cc1, cc2 = st.columns(2)
    can_name = cc1.text_input("Patient Name (Exact)")
    can_date = cc2.date_input("Scheduled Date", value=dt.date.today())
    
    if st.button("🗑️ Process Cancellation"):
        if not can_name: st.error("Patient Name is required.")
        else:
            payload = {"patient_name": can_name.strip(), "date": can_date.isoformat()}
            try:
                resp = requests.post(f"{base_url}/cancel_appointment/", json=payload, timeout=10)
                if resp.status_code == 200:
                    cnt = resp.json().get("canceled_count", 0)
                    if cnt > 0: st.success(f"Action Complete: {cnt} record(s) revoked."); time.sleep(1); st.rerun()
                    else: st.warning("No active records found for this name and date.")
                else: st.error(f"Server says: {resp.json().get('detail', 'Error')}")
            except Exception as e: st.error(f"Error: {e}")

with tab3:
    st.markdown("### 📋 Record Directory")
    v_date = st.date_input("Filter by Date", value=dt.date.today())
    
    if st.button("🔍 Execute Search"):
        try:
            resp = requests.post(f"{base_url}/list_appointments/", json={"date": v_date.isoformat()}, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    df = pd.DataFrame(data)
                    df['Time'] = pd.to_datetime(df['start_time']).dt.strftime('%H:%M')
                    st.dataframe(df[['id', 'patient_name', 'reason', 'Time']], use_container_width=True, hide_index=True)
                else: st.warning(f"No active records for {v_date}. Use 'Create Booking' to add one.")
        except Exception as e: st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>VAPI Voice Agent Backend Dashboard • Dubai Medical AI</div>", unsafe_allow_html=True)