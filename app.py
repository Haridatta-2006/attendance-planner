import streamlit as st
from datetime import date

# AI imports
from langchain_google_genai import ChatGoogleGenerativeAI

# -------------------------------
# API KEY (PUT YOUR KEY HERE)
# -------------------------------
GOOGLE_API_KEY = "AIzaSyBc_7HxEEg65k8xeP9WmJiqzA8ZsW8w08g"

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.7
)

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Smart Attendance Planner + AI", layout="centered")

# -------------------------------
# HEADER
# -------------------------------
st.title("📊 Smart Attendance Planner + 🤖 AI Assistant")

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
# TODAY SECTION
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
# RESULT DISPLAY
# -------------------------------
st.subheader("📊 Today's Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("📍 Today %", f"{today_percent:.2f}%")
col2.metric("🔥 Max %", f"{max_percent:.2f}%")
col3.metric("⚡ Now %", f"{now_percent:.2f}%")
col4.metric("📌 Final %", f"{final_percent:.2f}%")
col5.metric("😎 Bunk", f"{bunk}")

# -------------------------------
# AI CHATBOT SECTION
# -------------------------------
st.markdown("---")
st.subheader("🤖 AI Attendance Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask anything about your attendance:")

if user_input:
    context = f"""
    Student Attendance Data:
    - Attended: {attended}
    - Total: {total}
    - Today Classes: {today_classes}
    - Attended Today: {attended_today}
    - Remaining Today: {remaining_today}
    - Planning to Attend: {attend_more}
    - Final Today Attendance %: {today_percent:.2f}
    - Overall Final %: {final_percent:.2f}

    Give smart advice like a helpful assistant.
    """

    prompt = context + "\nUser Question: " + user_input

    response = llm.invoke(prompt)

    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("AI", response.content))

# -------------------------------
# CHAT DISPLAY
# -------------------------------
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 AI:** {msg}")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("""
<hr>
<div style='text-align:center; color:gray;'>
    <p>Developed by: <b>YOU</b></p>
</div>
""", unsafe_allow_html=True)
