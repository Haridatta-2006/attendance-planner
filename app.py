import streamlit as st
from datetime import date, timedelta

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Attendance Planner", layout="centered")

# -------------------------------
# STYLE
# -------------------------------
st.markdown("""
<style>
.card {
    background-color:#111827;
    padding:18px;
    border-radius:14px;
    margin-bottom:15px;
    box-shadow:0px 4px 12px rgba(0,0,0,0.4);
}
.title {
    text-align:center;
    color:#4CAF50;
    font-size:36px;
    font-weight:bold;
}
.subtitle {
    text-align:center;
    color:#9CA3AF;
    margin-bottom:20px;
}
.highlight {
    padding:15px;
    border-radius:12px;
    text-align:center;
    font-size:16px;
    font-weight:bold;
    height:120px;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-direction:column;
}
.target { background:#1e3a8a; color:white; }
.max { background:#14532d; color:white; }
.plan { background:#7c2d12; color:white; }
.bunk { background:#064e3b; color:white; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# HEADER
# -------------------------------
st.markdown('<div class="title">📊 Smart Attendance Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Plan Smart • Stay Consistent • Achieve Your Goal 🎯</div>', unsafe_allow_html=True)

# -------------------------------
# CURRENT ATTENDANCE
# -------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📌 Current Attendance Overview")

col1, col2 = st.columns(2)

with col1:
    attended = st.number_input("Classes Attended", min_value=0)

with col2:
    total = st.number_input("Total Classes Conducted", min_value=1)

if attended > total:
    st.error("❌ Attended classes cannot exceed total classes")
    st.stop()

current_percent = (attended / total) * 100
st.success(f"📈 Current Attendance: {current_percent:.2f}%")

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# TARGET
# -------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🎯 Set Your Attendance Goal")

target_percent = st.number_input("Enter Target (%)", 50.0, 100.0, 75.0)

st.markdown(f"""
<div class="highlight target">
🎯 Target<br>{target_percent:.2f}%
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# ATTENDANCE PERIOD
# -------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📅 Attendance Period")
st.caption("From Today to Selected End Date")

start_date = date.today()
st.text_input("Start Date", value=str(start_date), disabled=True)

end_date = st.date_input("End Date")

if end_date < start_date:
    st.error("❌ End date must be after today")
    st.stop()

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# TIMETABLE
# -------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📚 Weekly Timetable (Enter Number of Classes per Day)")

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

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# HOLIDAY SELECTION (FINAL FIX)
# -------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🎉 Holiday Selection")

if "holiday_list" not in st.session_state:
    st.session_state.holiday_list = []

if "last_selected" not in st.session_state:
    st.session_state.last_selected = None

selected_date = st.date_input(
    "Pick a date",
    value=None,
    min_value=start_date,
    max_value=end_date
)

# FIXED ADD LOGIC
if selected_date and selected_date != st.session_state.last_selected:
    if selected_date.weekday() == 6:
        st.warning("Sunday already excluded ❌")
    elif selected_date not in st.session_state.holiday_list:
        st.session_state.holiday_list.append(selected_date)

    st.session_state.last_selected = selected_date

holidays = st.session_state.holiday_list

# SHOW + DELETE
if holidays:
    st.success(f"Selected {len(holidays)} holiday(s)")

    for i, d in enumerate(holidays):
        col1, col2 = st.columns([4,1])
        col1.write(d)

        if col2.button("❌", key=f"remove_{i}"):
            st.session_state.holiday_list.pop(i)
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# FUTURE CLASSES
# -------------------------------
total_future_classes = 0
current_date = start_date

while current_date <= end_date:
    if current_date.weekday() != 6 and current_date not in holidays:
        total_future_classes += timetable[current_date.weekday()]
    current_date += timedelta(days=1)

st.info(f"📅 Total Future Classes Available: {total_future_classes}")

# -------------------------------
# RESULT (FINAL PERFECT LOGIC)
# -------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📊 Attendance Summary")

current = attended / total
target = target_percent / 100

max_att = (attended + total_future_classes) / (total + total_future_classes)

# Immediate requirement
x = ((target * total) - attended) / (1 - target)
required_now = max(0, int(x) + 1)

# Final requirement
needed_attend = (target * (total + total_future_classes)) - attended
needed_attend = max(0, int(needed_attend + 0.999))

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"<div class='highlight target'>🎯 Target<br>{target_percent:.2f}%</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='highlight max'>🔥 Max<br>{max_att*100:.2f}%</div>", unsafe_allow_html=True)

with col3:
    msg = "Reached 🎉" if current >= target else f"Attend {required_now}"
    st.markdown(f"<div class='highlight plan'>⚡ Now<br>{msg}</div>", unsafe_allow_html=True)

with col4:
    msg = "Not possible ❌" if needed_attend > total_future_classes else f"Attend {needed_attend}"
    st.markdown(f"<div class='highlight plan'>📌 Final<br>{msg}</div>", unsafe_allow_html=True)

with col5:
    if needed_attend > total_future_classes:
        msg = "No bunk ❌"
    else:
        msg = f"Skip {total_future_classes - needed_attend}"
    st.markdown(f"<div class='highlight bunk'>😎 Bunk<br>{msg}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<hr>
<div style='text-align:center; color:gray;'>
    <p>Developed by: <b>ME</b></p>
</div>
""", unsafe_allow_html=True)
