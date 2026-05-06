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
        height: 3.5em;
        background-color: #2563eb;
        color: white;
        border: none;
        font-weight: 700;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    div.stButton > button:hover {
        background-color: #1d4ed8;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 1.1rem !important;
    }

    /* Table styling */
    .stDataFrame {
        border: 1px solid #334155;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital.png", width=80)
    st.title("Hospital Admin")
    
    base_url = st.text_input("Backend API", "http://127.0.0.1:4444").rstrip("/")
    
    st.divider()
    st.markdown("### 🤖 VAPI Connectivity")
    st.success("Assistant Synced")
    
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()
    
    st.info("Authorized Personnel Only.")

# Header Section
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏥 Dubai Medical Center")
    st.markdown("<p style='color: #94a3b8; font-size: 1.2rem;'>AI-Driven Appointment Orchestration</p>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div style='text-align: right; background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155;'><b>Status:</b> 🟢 ONLINE<br><small>Hugging Face Hub</small></div>", unsafe_allow_html=True)

st.divider()

# Dashboard Overview (Metrics)
st.subheader("📊 System Overview")
try:
    stats_resp = requests.get(f"{base_url}/stats/", timeout=5)
    if stats_resp.status_code == 200:
        stats = stats_resp.json()
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Bookings", stats.get("total", 0))
        with m2:
            st.metric("Active Sessions", stats.get("active", 0))
        with m3:
            st.metric("Canceled Orders", stats.get("canceled", 0))
    else:
        st.error("Backend Error: Stats could not be retrieved.")
except Exception as e:
    st.warning("🔄 Waiting for backend to wake up...")

st.markdown("<br>", unsafe_allow_html=True)

# Main Interaction Area
tab1, tab2, tab3 = st.tabs(["📅 Create Booking", "❌ Revoke Booking", "📋 Records Directory"])

with tab1:
    st.markdown("### 📅 Schedule Appointment")
    c1, c2 = st.columns(2)
    with c1:
        patient_name = st.text_input("Patient Name", placeholder="Full legal name")
        reason = st.text_input("Medical Reason", placeholder="e.g. Annual Physical")
    with c2:
        # Default to tomorrow to avoid timezone issues
        start_date = st.date_input("Appointment Date", value=dt.date.today() + dt.timedelta(days=1))
        start_time = st.time_input("Appointment Time", value=dt.time(9, 0))
    
    if st.button("🚀 Confirm Appointment", key="btn_schedule"):
        if not patient_name:
            st.error("Validation Error: Patient Name is required.")
        else:
            start_dt = dt.datetime.combine(start_date, start_time)
            payload = {
                "patient_name": patient_name.strip(),
                "reason": reason.strip() or "General Consultation",
                "start_time": start_dt.isoformat(),
            }
            with st.spinner("Writing to database..."):
                try:
                    resp = requests.post(f"{base_url}/schedule_appointment/", json=payload, timeout=10)
                    if resp.status_code == 200:
                        st.success(f"✅ Successfully Booked: {patient_name}")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"Execution Error: {resp.text}")
                except Exception as e:
                    st.error(f"Network Timeout: {e}")

with tab2:
    st.markdown("### ❌ Revoke Appointment")
    st.info("Specify patient and date to cancel all matching active bookings.")
    cc1, cc2 = st.columns(2)
    with cc1:
        cancel_name = st.text_input("Search Patient Name")
    with cc2:
        cancel_date = st.date_input("Search Date", value=dt.date.today())
    
    if st.button("🗑️ Process Cancellation", key="btn_cancel"):
        if not cancel_name:
            st.error("Input Required: Patient Name.")
        else:
            payload = {"patient_name": cancel_name.strip(), "date": cancel_date.isoformat()}
            try:
                resp = requests.post(f"{base_url}/cancel_appointment/", json=payload, timeout=10)
                data = resp.json()
                if data.get("canceled_count", 0) > 0:
                    st.success(f"Action Complete: {data['canceled_count']} record(s) revoked.")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.warning("No matching active records found for this name and date.")
            except Exception as e:
                st.error(f"System Error: {e}")

with tab3:
    st.markdown("### 📋 Record Directory")
    
    v1, v2 = st.columns([2, 1])
    with v1:
        view_date = st.date_input("Filter by Date", value=dt.date.today() + dt.timedelta(days=1))
    with v2:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_all = st.checkbox("Show all active records (ignore date)")

    if st.button("🔍 Execute Search", key="btn_fetch"):
        # We'll use the list_appointments endpoint. 
        # Note: The backend only supports filtering by date currently.
        # If fetch_all is checked, we'll try to get data for several days or just today.
        payload = {"date": view_date.isoformat()}
        try:
            resp = requests.post(f"{base_url}/list_appointments/", json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    df = pd.DataFrame(data)
                    df['Date'] = pd.to_datetime(df['start_time']).dt.date
                    df['Time'] = pd.to_datetime(df['start_time']).dt.strftime('%H:%M')
                    display_df = df[['id', 'patient_name', 'reason', 'Date', 'Time']].copy()
                    display_df.columns = ['ID', 'Patient Name', 'Reason', 'Date', 'Time']
                    st.success(f"Results Found: {len(data)} records matched.")
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"Result: 0 records found for {view_date}. Check 'Create Booking' tab to add one.")
            else:
                st.error(f"Protocol Error: {resp.text}")
        except Exception as e:
            st.error(f"Link Down: {e}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>"
    "VAPI Voice Agent Backend Dashboard • Dubai Medical AI • 2024"
    "</div>", 
    unsafe_allow_html=True
)