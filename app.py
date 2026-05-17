import streamlit as st
from datetime import date, timedelta
import plotly.graph_objects as go
import pandas as pd
import io

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Attendance Planner", page_icon="📊", layout="wide")

# -------------------------------
# STYLE
# -------------------------------
st.markdown("""
<style>
/* Modern Glassmorphism Design */
.stApp {
    background-color: #0f172a;
    color: #f8fafc;
}
.card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
}
.title {
    text-align: center;
    background: linear-gradient(to right, #4ade80, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 10px;
}
.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 30px;
    font-size: 18px;
}
.highlight {
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 16px;
    font-weight: bold;
    height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.1);
}
.highlight:hover {
    transform: scale(1.05);
}
.target { background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; }
.max { background: linear-gradient(135deg, #14532d, #22c55e); color: white; }
.plan { background: linear-gradient(135deg, #7c2d12, #f97316); color: white; }
.bunk { background: linear-gradient(135deg, #064e3b, #10b981); color: white; }
.metric-value { font-size: 24px; font-weight: 900; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown('<div class="title">📊 Smart Attendance Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Plan Smart • Stay Consistent • Achieve Your Goal 🎯</div>', unsafe_allow_html=True)

# -------------------------------
# NAVIGATION STATE
# -------------------------------
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# -------------------------------
# SETUP SECTION
# -------------------------------
with st.expander("⚙️ Setup & Configuration", expanded=not st.session_state.submitted):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📌 Current Attendance & Goal")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        attended = st.number_input("Classes Attended", min_value=0, value=0)
    with col2:
        total = st.number_input("Total Classes Conducted", min_value=1, value=1)
    with col3:
        target_percent = st.number_input("Target Attendance (%)", min_value=0.0, max_value=100.0, value=75.0, step=1.0)
    
    if attended > total:
        st.error("❌ Attended classes cannot exceed total classes")
        st.stop()
        
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Timeline & Today's Status")
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = date.today()
        st.text_input("Start Date (Auto)", value=str(start_date), disabled=True)
    with col2:
        end_date = st.date_input("End Date", value=start_date + timedelta(days=30))
    with col3:
        today_status = st.radio("Did you attend today's classes?", ["Present", "Absent", "No Classes Today"], index=0)

    if end_date < start_date:
        st.error("❌ End date must be after today")
        st.stop()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.expander("📚 Weekly Timetable Setup", expanded=True):
        st.write("Enter the number of classes you have each day:")
        col1, col2, col3 = st.columns(3)
        with col1:
            mon = st.number_input("Monday", min_value=0, value=1)
            thu = st.number_input("Thursday", min_value=0, value=1)
        with col2:
            tue = st.number_input("Tuesday", min_value=0, value=1)
            fri = st.number_input("Friday", min_value=0, value=1)
        with col3:
            wed = st.number_input("Wednesday", min_value=0, value=1)
            sat = st.number_input("Saturday", min_value=0, value=0)
        
        timetable = [mon, tue, wed, thu, fri, sat]
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.expander("🎉 Holiday Selection", expanded=False):
        if "holiday_list" not in st.session_state:
            st.session_state.holiday_list = []
        if "last_selected" not in st.session_state:
            st.session_state.last_selected = None

        selected_date = st.date_input("Pick a holiday", value=None, min_value=start_date, max_value=end_date)

        if selected_date and selected_date != st.session_state.last_selected:
            if selected_date.weekday() == 6:
                st.warning("Sunday is already excluded! ❌")
            elif selected_date not in st.session_state.holiday_list:
                st.session_state.holiday_list.append(selected_date)
                st.toast(f"Holiday added: {selected_date}", icon="🏖️")
            st.session_state.last_selected = selected_date

        holidays = st.session_state.holiday_list
        if holidays:
            st.write("**Selected Holidays:**")
            for i, d in enumerate(holidays):
                col_date, col_btn = st.columns([4,1])
                col_date.write(f"🌴 {d.strftime('%b %d, %Y (%A)')}")
                if col_btn.button("❌ Remove", key=f"remove_{i}"):
                    st.session_state.holiday_list.pop(i)
                    st.rerun()
        else:
            st.info("No holidays selected yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.submitted:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Submit & View Dashboard", use_container_width=True, type="primary"):
            st.session_state.submitted = True
            st.rerun()

# -------------------------------
# DASHBOARD SECTION
# -------------------------------
if st.session_state.submitted:
    
    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🔙 Edit Setup"):
        st.session_state.submitted = False
        st.rerun()
    
    # -------------------------------
    # CALCULATIONS
    # -------------------------------
    today_classes = timetable[start_date.weekday()] if start_date.weekday() != 6 else 0
    if today_status == "Present":
        attended_updated = attended + today_classes
        total_updated = total + today_classes
    elif today_status == "Absent":
        attended_updated = attended
        total_updated = total + today_classes
    else: # No Classes Today
        attended_updated = attended
        total_updated = total

    current_percent = (attended_updated / total_updated * 100) if total_updated > 0 else 0

    total_future_classes = 0
    current_date = start_date + timedelta(days=1)
    while current_date <= end_date:
        if current_date.weekday() != 6 and current_date not in st.session_state.holiday_list:
            total_future_classes += timetable[current_date.weekday()]
        current_date += timedelta(days=1)

    current_ratio = attended_updated / total_updated if total_updated > 0 else 0
    target_ratio = target_percent / 100
    max_att = (attended_updated + total_future_classes) / (total_updated + total_future_classes) if (total_updated + total_future_classes) > 0 else 0

    if target_ratio < 1:
        x = ((target_ratio * total_updated) - attended_updated) / (1 - target_ratio)
        required_now = max(0, int(x) + 1)
    else:
        required_now = float('inf')

    needed_attend = (target_ratio * (total_updated + total_future_classes)) - attended_updated
    needed_attend = max(0, int(needed_attend + 0.999))

    # Check if balloons should be shown (if target reached just now)
    if "prev_percent" not in st.session_state:
        st.session_state.prev_percent = current_percent

    if current_percent >= target_percent and st.session_state.prev_percent < target_percent:
        st.balloons()
    st.session_state.prev_percent = current_percent

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Attendance Overview")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"**Updated Attendance (Including Today):** {current_percent:.2f}%")
        st.progress(current_percent / 100 if current_percent <= 100 else 1.0)
        st.markdown(f"**Target Attendance:** {target_percent:.2f}%")
        st.progress(target_percent / 100 if target_percent <= 100 else 1.0)
        st.info(f"📅 Future Classes (from tomorrow): **{total_future_classes}**")
        
    with col2:
        # Plotly Gauge Chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = current_percent,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Current vs Target", 'font': {'size': 20, 'color': '#f8fafc'}},
            delta = {'reference': target_percent, 'increasing': {'color': "#4ade80"}, 'decreasing': {'color': "#ef4444"}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#3b82f6"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, target_percent], 'color': "rgba(239, 68, 68, 0.3)"},
                    {'range': [target_percent, 100], 'color': "rgba(74, 222, 128, 0.3)"}],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': target_percent}
            }
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "#f8fafc"}, height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎯 Action Plan")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"<div class='highlight target'>🎯 Target<div class='metric-value'>{target_percent:.1f}%</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='highlight max'>🔥 Max Possible<div class='metric-value'>{max_att*100:.1f}%</div></div>", unsafe_allow_html=True)
    with col3:
        if current_percent >= target_percent:
            msg = "Reached 🎉"
        elif required_now > total_future_classes:
            msg = "Impossible ❌"
        else:
            msg = f"Attend {required_now}"
        st.markdown(f"<div class='highlight plan'>⚡ Immediate<br><span style='font-size:14px;font-weight:normal;'>to hit target now</span><div class='metric-value' style='font-size:18px;'>{msg}</div></div>", unsafe_allow_html=True)
    with col4:
        msg = "Not possible ❌" if needed_attend > total_future_classes else f"Attend {needed_attend}"
        st.markdown(f"<div class='highlight plan'>📌 End of Term<br><span style='font-size:14px;font-weight:normal;'>out of {total_future_classes} classes</span><div class='metric-value' style='font-size:18px;'>{msg}</div></div>", unsafe_allow_html=True)
    with col5:
        if needed_attend > total_future_classes:
            msg = "No bunk ❌"
        else:
            msg = f"Skip {total_future_classes - needed_attend}"
        st.markdown(f"<div class='highlight bunk'>😎 Bunk Allowance<br><span style='font-size:14px;font-weight:normal;'>safe to miss</span><div class='metric-value' style='font-size:18px;'>{msg}</div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Download Report Feature
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📥 Export Plan")
    report_text = f'''Smart Attendance Planner Report
Date: {date.today()}
=========================================
Current Status:
- Classes Attended: {attended_updated}
- Total Classes: {total_updated}
- Current Percentage: {current_percent:.2f}%
- Target Percentage: {target_percent:.2f}%

Future Outlook:
- End Date: {end_date}
- Future Classes Remaining: {total_future_classes}
- Max Possible Attendance: {max_att*100:.2f}%

Action Plan:
- To hit target immediately: {'Target Reached' if current_percent >= target_percent else f'Attend {required_now}'}
- Needed by end of term: {'Not possible' if needed_attend > total_future_classes else f'Attend {needed_attend}'}
- Safe to skip: {'None' if needed_attend > total_future_classes else f'{total_future_classes - needed_attend}'}
=========================================
Plan Smart • Stay Consistent • Achieve Your Goal!
'''
    st.download_button(
        label="📄 Download Attendance Report",
        data=report_text,
        file_name="attendance_report.txt",
        mime="text/plain",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<div style='text-align:center; color:gray; padding-top:20px; border-top: 1px solid rgba(255,255,255,0.1);'>
    <p>Developed with ❤️ & Streamlit</p>
</div>
""", unsafe_allow_html=True)
