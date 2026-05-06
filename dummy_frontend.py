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
    /* Main container styling */
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Title styling */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 800 !important;
    }
    
    /* Sidebar styling - Explicit Dark Mode */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }
    
    /* Fix for invisible text in sidebar inputs */
    [data-testid="stSidebar"] input {
        color: #0f172a !important;
        background-color: #f8fafc !important;
    }

    /* Card-like containers */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #2563eb;
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital.png", width=80)
    st.title("Admin Portal")
    
    # Internal communication on HF uses localhost
    base_url = st.text_input("Backend URL", "http://127.0.0.1:4444").rstrip("/")
    
    st.divider()
    st.markdown("### 🤖 Agent Connectivity")
    st.success("VAPI Sync Active")
    
    st.markdown("### 🛠 Tools")
    if st.button("🔄 Force Refresh System"):
        st.rerun()
    
    st.info("Management Portal for Dubai Hospital AI Agent.")

# Header Section
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏥 Dubai Hospital")
    st.markdown("<p style='color: #94a3b8; font-size: 1.2rem;'>Advanced AI Appointment Management</p>", unsafe_allow_html=True)
with col2:
    try:
        st.markdown(f"<div style='text-align: right; padding-top: 10px;'><b>Status:</b> 🔵 Live<br><small>Hugging Face Space</small></div>", unsafe_allow_html=True)
    except:
        st.markdown(f"<div style='text-align: right; padding-top: 10px;'><b>Status:</b> 🔴 Offline</div>", unsafe_allow_html=True)

st.divider()

# Dashboard Overview (Metrics)
st.subheader("📊 Real-time Stats")
try:
    stats_resp = requests.get(f"{base_url}/stats/", timeout=5)
    if stats_resp.status_code == 200:
        stats = stats_resp.json()
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Records", stats.get("total", 0))
        with m2:
            st.metric("Active Appointments", stats.get("active", 0))
        with m3:
            st.metric("Canceled", stats.get("canceled", 0))
    else:
        st.error("Stats endpoint returned an error.")
except Exception as e:
    st.warning(f"Connecting to backend... {e}")

st.markdown("<br>", unsafe_allow_html=True)

# Main Interaction Area
tab1, tab2, tab3 = st.tabs(["📅 Schedule", "❌ Cancel", "📋 Appointment List"])

with tab1:
    st.markdown("### Book a New Appointment")
    c1, c2 = st.columns(2)
    with c1:
        patient_name = st.text_input("Patient Name", placeholder="e.g. John Doe")
        reason = st.text_input("Reason for Visit", placeholder="e.g. General Checkup")
    with c2:
        # Default to tomorrow to avoid timezone confusion
        start_date = st.date_input("Date", value=dt.date.today() + dt.timedelta(days=1))
        start_time = st.time_input("Time", value=dt.time(10, 0))
    
    if st.button("Confirm Booking", key="btn_schedule"):
        if not patient_name:
            st.warning("Patient name is required.")
        else:
            start_dt = dt.datetime.combine(start_date, start_time)
            payload = {
                "patient_name": patient_name.strip(),
                "reason": reason.strip() or "Consultation",
                "start_time": start_dt.isoformat(),
            }
            with st.spinner("Processing..."):
                try:
                    resp = requests.post(f"{base_url}/schedule_appointment/", json=payload, timeout=10)
                    if resp.status_code == 200:
                        st.success(f"✅ Scheduled: {patient_name}")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Server Error: {resp.text}")
                except Exception as e:
                    st.error(f"Network Error: {e}")

with tab2:
    st.markdown("### Cancel Appointments")
    st.warning("Cancels all active appointments for a patient on a specific date.")
    cc1, cc2 = st.columns(2)
    with cc1:
        cancel_name = st.text_input("Patient Name")
    with cc2:
        cancel_date = st.date_input("Date", value=dt.date.today())
    
    if st.button("Cancel Appointment", key="btn_cancel"):
        if not cancel_name:
            st.warning("Name is required.")
        else:
            payload = {"patient_name": cancel_name.strip(), "date": cancel_date.isoformat()}
            try:
                resp = requests.post(f"{base_url}/cancel_appointment/", json=payload, timeout=10)
                data = resp.json()
                if data.get("canceled_count", 0) > 0:
                    st.success(f"Canceled {data['canceled_count']} appointment(s).")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("No matching appointments found.")
            except Exception as e:
                st.error(f"Error: {e}")

with tab3:
    st.markdown("### Appointment Directory")
    st.info("Displaying active (non-canceled) appointments.")
    
    view_date = st.date_input("View for Date", value=dt.date.today())
    
    if st.button("🔍 Fetch Records", key="btn_fetch"):
        payload = {"date": view_date.isoformat()}
        try:
            resp = requests.post(f"{base_url}/list_appointments/", json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    df = pd.DataFrame(data)
                    df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%H:%M')
                    display_df = df[['id', 'patient_name', 'reason', 'start_time']].copy()
                    display_df.columns = ['ID', 'Patient Name', 'Reason', 'Time']
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"No active appointments for {view_date}.")
            else:
                st.error(f"Server Error: {resp.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>"
    "VAPI Voice Agent Backend Dashboard • Dubai Hospital AI"
    "</div>", 
    unsafe_allow_html=True
)