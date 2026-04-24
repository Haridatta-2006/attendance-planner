import streamlit as st
from datetime import date

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Smart Attendance Planner", layout="centered")

# -------------------------------
# HEADER
# -------------------------------
st.title("📊 Smart Attendance Planner")

# -------------------------------
# WEEKLY TIMETABLE (TOP)
# -------------------------------
st.subheader("📚 Weekly Timetable")

col1, col2, col3 = st.columns(3)

with col1:
    mon = st.number_input("Monday", min_value=0)
    tue = st.number_input("Tuesday", min_value=0)

with col2:
    wed = st.number_input("Wednesday", min_value=0)
    thu = st.number_input("Thursday", min_value=0)

with col3:
    fri = st.number_input("Friday", min_value=0)
    sat = st.number_input("Saturday", min_value=0)

timetable = [mon, tue, wed, thu, fri, sat]

# -------------------------------
# ATTENDANCE TILL YESTERDAY
# -------------------------------
st.subheader("📅 Attendance Till Yesterday")

attended = st.number_input("Total Classes Attended", min_value=0)
total = st.number_input("Total Classes Conducted", min_value=1)

if attended > total:
    st.error("❌ Attended cannot exceed total")
    st.stop()

# -------------------------------
# TODAY DETAILS
# -------------------------------
today = date.today()
today_classes = timetable[today.weekday()] if today.weekday() != 6 else 0

st.subheader(f"📍 Today ({today})")

st.info(f"📚 Total classes today (from timetable): {today_classes}")

attended_today = st.number_input(
    "How many classes attended till now today?",
    min_value=0,
    max_value=today_classes
)

remaining_today = today_classes - attended_today

st.write(f"📌 Remaining classes today: {remaining_today}")

# -------------------------------
# FUTURE DECISION
# -------------------------------
attend_more = st.number_input(
    "Out of remaining classes, how many will you attend?",
    min_value=0,
    max_value=remaining_today
)

# -------------------------------
# CALCULATIONS
# -------------------------------

# Final attended today
final_today_attended = attended_today + attend_more

# Updated totals
attended_updated = attended + final_today_attended
total_updated = total + today_classes

# Current final percentage (end of today)
final_percent = (attended_updated / total_updated) * 100

# Max possible (if attend all today)
max_percent = ((attended + today_classes) / (total + today_classes)) * 100

# Now percentage (current situation)
now_percent = ((attended + attended_today) / (total + today_classes)) * 100

# Bunk count
bunk = remaining_today - attend_more

# -------------------------------
# RESULT DISPLAY
# -------------------------------
st.subheader("📊 Today's Attendance Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📍 Today %", f"{final_percent:.2f}%")

with col2:
    st.metric("🔥 Max %", f"{max_percent:.2f}%")

with col3:
    st.metric("⚡ Now %", f"{now_percent:.2f}%")

with col4:
    st.metric("📌 Final %", f"{final_percent:.2f}%")

with col5:
    st.metric("😎 Bunk", f"{bunk}")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<hr>
<div style='text-align:center; color:gray;'>
    <p>Developed by: <b>YOU</b></p>
</div>
""", unsafe_allow_html=True)
