import streamlit as st
from datetime import date, timedelta

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Attendance Planner", layout="centered")

# -------------------------------
# HEADER
# -------------------------------
st.title("📊 Smart Attendance Planner")

# -------------------------------
# WEEKLY TIMETABLE (FIRST)
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
# ATTENDANCE TILL NOW
# -------------------------------
st.subheader("📅 Attendance Till Yesterday")

attended = st.number_input("Classes Attended", min_value=0)
total = st.number_input("Total Classes Conducted", min_value=1)

if attended > total:
    st.error("❌ Attended cannot exceed total")
    st.stop()

# -------------------------------
# TODAY SECTION
# -------------------------------
today = date.today()
today_classes = timetable[today.weekday()] if today.weekday() != 6 else 0

st.subheader(f"📍 Today ({today})")
st.info(f"📚 Total classes today: {today_classes}")

# -------- PRESENT OR ABSENT --------
today_status = st.radio(
    "Did you attend today?",
    ["Present", "Absent"]
)

# -------- IF PRESENT ASK HOW MANY --------
if today_status == "Present":
    attended_today = st.number_input(
        "How many classes did you attend today?",
        min_value=0,
        max_value=today_classes
    )
else:
    attended_today = 0

# -------- REMAINING --------
remaining_today = today_classes - attended_today
st.write(f"📌 Remaining classes today: {remaining_today}")

# -------- FUTURE PLAN --------
attend_more = st.number_input(
    "Out of remaining classes, how many will you attend?",
    min_value=0,
    max_value=remaining_today
)

# -------------------------------
# CALCULATIONS
# -------------------------------
final_today_attended = attended_today + attend_more

attended_updated = attended + final_today_attended
total_updated = total + today_classes

# Percentages
today_percent = (final_today_attended / today_classes * 100) if today_classes > 0 else 0
final_percent = (attended_updated / total_updated) * 100
max_percent = ((attended + today_classes) / (total + today_classes)) * 100
now_percent = ((attended + attended_today) / (total + today_classes)) * 100

# Bunk
bunk = remaining_today - attend_more

# -------------------------------
# RESULT
# -------------------------------
st.subheader("📊 Today's Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📍 Today %", f"{today_percent:.2f}%")
col2.metric("🔥 Max %", f"{max_percent:.2f}%")
col3.metric("⚡ Now %", f"{now_percent:.2f}%")
col4.metric("📌 Final %", f"{final_percent:.2f}%")
col5.metric("😎 Bunk", f"{bunk}")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<hr>
<div style='text-align:center; color:gray;'>
    <p>Developed by: <b>YOU</b></p>
</div>
""", unsafe_allow_html=True)
