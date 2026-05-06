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

# Custom CSS for enhanced aesthetics
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f8fafc;
    }
    
    /* Title styling */
    .stTitle {
        color: #1e293b;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.5rem;
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
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2563eb;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/hospital.png", width=80)
    st.title("Settings")
    base_url = st.text_input("Backend URL", "http://127.0.0.1:4444").rstrip("/")
    
    st.divider()
    st.markdown("### 🤖 Voice Agent Status")
    st.success("Connected to VAPI")
    
    st.info("This dashboard manages appointments synchronized with the VAPI Voice Agent.")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Header Section
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏥 Dubai Hospital")
    st.markdown("<p style='color: #64748b; font-size: 1.2rem;'>AI Appointment Management Portal</p>", unsafe_allow_html=True)
with col2:
    try:
        st.markdown(f"<div style='text-align: right; padding-top: 10px;'><b>Server:</b> <code>{base_url}</code><br><b>Status:</b> 🟢 Online</div>", unsafe_allow_html=True)
    except:
        st.markdown(f"<div style='text-align: right; padding-top: 10px;'><b>Status:</b> 🔴 Offline</div>", unsafe_allow_html=True)

st.divider()

# Dashboard Overview (Metrics)
st.subheader("📊 System Overview")
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
            st.metric("Canceled", stats.get("canceled", 0), delta_color="inverse")
except:
    st.warning("Could not load real-time statistics.")

st.markdown("<br>", unsafe_allow_html=True)

# Main Interaction Area
tab1, tab2, tab3 = st.tabs(["📅 Schedule", "❌ Cancel", "📋 Appointment List"])

with tab1:
    st.markdown("### Book a New Appointment")
    c1, c2 = st.columns(2)
    with c1:
        patient_name = st.text_input("Patient Name", placeholder="Enter full name")
        reason = st.text_input("Reason for Visit", placeholder="e.g., General Checkup, Fever, etc.")
    with c2:
        start_date = st.date_input("Preferred Date", value=dt.date.today() + dt.timedelta(days=1))
        start_time = st.time_input("Preferred Time", value=dt.time(9, 0))
    
    if st.button("Confirm Booking", key="btn_schedule"):
        if not patient_name:
            st.warning("Please enter a patient name.")
        else:
            start_dt = dt.datetime.combine(start_date, start_time)
            payload = {
                "patient_name": patient_name.strip(),
                "reason": reason.strip() or "General Consultation",
                "start_time": start_dt.isoformat(),
            }
            with st.spinner("Scheduling..."):
                try:
                    resp = requests.post(f"{base_url}/schedule_appointment/", json=payload, timeout=10)
                    resp.raise_for_status()
                    st.success(f"✅ Appointment scheduled successfully for {patient_name}!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to schedule: {e}")

with tab2:
    st.markdown("### Cancel Existing Appointments")
    st.warning("This will cancel all active appointments for the patient on the selected date.")
    cc1, cc2 = st.columns(2)
    with cc1:
        cancel_name = st.text_input("Patient Name", key="cancel_name_input")
    with cc2:
        cancel_date = st.date_input("Date to Cancel", value=dt.date.today(), key="cancel_date_input")
    
    if st.button("Process Cancellation", key="btn_cancel"):
        if not cancel_name:
            st.warning("Please enter the patient name.")
        else:
            payload = {
                "patient_name": cancel_name.strip(),
                "date": cancel_date.isoformat()
            }
            with st.spinner("Processing..."):
                try:
                    resp = requests.post(f"{base_url}/cancel_appointment/", json=payload, timeout=10)
                    resp.raise_for_status()
                    data = resp.json()
                    count = data.get("canceled_count", 0)
                    if count > 0:
                        st.success(f"✅ Successfully canceled {count} appointment(s).")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.info("No active appointments found for this patient on the selected date.")
                except Exception as e:
                    st.error(f"Cancellation failed: {e}")

with tab3:
    st.markdown("### View Scheduled Appointments")
    st.info("Select a date to view all non-canceled appointments scheduled for that day.")
    
    view_date = st.date_input("Select Date to View", value=dt.date.today(), key="view_date_input")
    
    if st.button("🔍 Fetch Appointments", key="btn_fetch"):
        payload = {"date": view_date.isoformat()}
        with st.spinner(f"Fetching appointments for {view_date}..."):
            try:
                resp = requests.post(f"{base_url}/list_appointments/", json=payload, timeout=15)
                
                if resp.status_code == 200:
                    data = resp.json()
                    if data and len(data) > 0:
                        df = pd.DataFrame(data)
                        df['start_time'] = pd.to_datetime(df['start_time']).dt.strftime('%Y-%m-%d %H:%M')
                        display_df = df[['id', 'patient_name', 'reason', 'start_time']].copy()
                        display_df.columns = ['ID', 'Patient Name', 'Reason', 'Appointment Time']
                        
                        st.success(f"Found {len(data)} appointment(s)")
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.warning(f"No active appointments found for {view_date}.")
                else:
                    st.error(f"Server error: {resp.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>"
    "VAPI Voice Agent Backend Dashboard • Dubai Hospital AI"
    "</div>", 
    unsafe_allow_html=True
)