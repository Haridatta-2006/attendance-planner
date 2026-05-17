import streamlit as st
from datetime import date, timedelta
import plotly.graph_objects as go
import requests
from streamlit_lottie import st_lottie

# ==========================================
# CUSTOM ARCHITECTURE: ATTENDANCE MODEL
# ==========================================
class AttendanceDataModel:
    def __init__(self):
        self._init_state()

    def _init_state(self):
        """Initialize all session state variables safely."""
        defaults = {
            'attended': 0,
            'total': 1,
            'target_percent': 75.0,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30),
            'today_status': "Present",
            'timetable': [1, 1, 1, 1, 1, 0], # Mon-Sat
            'holidays': [],
            'simulated_bunks': 0
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    @property
    def data(self):
        return st.session_state

    def add_holiday(self, new_date):
        if new_date not in self.data.holidays and new_date.weekday() != 6:
            self.data.holidays.append(new_date)
            return True
        return False

    def remove_holiday(self, index):
        if 0 <= index < len(self.data.holidays):
            self.data.holidays.pop(index)

    def calculate_metrics(self):
        """Core computation engine."""
        d = self.data
        today_classes = d.timetable[d.start_date.weekday()] if d.start_date.weekday() != 6 else 0
        
        # Adjust for today's status
        attended_updated = d.attended
        total_updated = d.total
        if d.today_status == "Present":
            attended_updated += today_classes
            total_updated += today_classes
        elif d.today_status == "Absent":
            total_updated += today_classes
            
        # Future classes calculation
        future_classes = 0
        current_date = d.start_date + timedelta(days=1)
        while current_date <= d.end_date:
            if current_date.weekday() != 6 and current_date not in d.holidays:
                future_classes += d.timetable[current_date.weekday()]
            current_date += timedelta(days=1)
            
        # What-If Simulation Adjustment
        simulated_attended = attended_updated
        simulated_future = max(0, future_classes - d.simulated_bunks)
        
        current_ratio = simulated_attended / total_updated if total_updated > 0 else 0
        target_ratio = d.target_percent / 100.0
        
        total_possible_classes = total_updated + future_classes
        max_possible_ratio = (simulated_attended + simulated_future) / total_possible_classes if total_possible_classes > 0 else 0
        
        needed_attend = (target_ratio * total_possible_classes) - simulated_attended
        needed_attend = max(0, int(needed_attend + 0.999))
        
        immediate_required = 0
        if target_ratio < 1 and current_ratio < target_ratio:
            x = ((target_ratio * total_updated) - simulated_attended) / (1 - target_ratio)
            immediate_required = max(0, int(x) + 1)
            
        return {
            "current_percent": current_ratio * 100,
            "max_possible_percent": max_possible_ratio * 100,
            "future_classes": future_classes,
            "simulated_future": simulated_future,
            "needed_attend": needed_attend,
            "immediate_required": immediate_required,
            "total_possible": total_possible_classes
        }

# ==========================================
# VISUAL ENGINE (CSS & PLOTLY)
# ==========================================
class VisualEngine:
    @staticmethod
    def load_lottieurl(url: str):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return None
            return r.json()
        except:
            return None

    @staticmethod
    def inject_custom_css():
        st.markdown("""
        <style>
        /* Modern Neumorphic / Glassmorphic UI */
        .stApp { background-color: #0b0f19; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .glass-card {
            background: linear-gradient(145deg, rgba(30,41,59,0.6), rgba(15,23,42,0.8));
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .glass-card:hover { transform: translateY(-4px); box-shadow: 0 15px 35px -10px rgba(0,0,0,0.7); }
        .hero-title {
            text-align: center; font-size: 3rem; font-weight: 900;
            background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        .hero-subtitle { text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 30px; letter-spacing: 1px; }
        .stat-box {
            padding: 18px; border-radius: 16px; text-align: center; display: flex; flex-direction: column;
            justify-content: center; height: 130px; border: 1px solid rgba(255,255,255,0.1);
            position: relative; overflow: hidden;
        }
        .stat-box::before {
            content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
            opacity: 0; transition: opacity 0.3s;
        }
        .stat-box:hover::before { opacity: 1; }
        .stat-target { background: linear-gradient(135deg, #1e3a8a, #3b82f6); }
        .stat-max { background: linear-gradient(135deg, #064e3b, #10b981); }
        .stat-now { background: linear-gradient(135deg, #7c2d12, #f97316); }
        .stat-end { background: linear-gradient(135deg, #4c1d95, #8b5cf6); }
        .stat-bunk { background: linear-gradient(135deg, #831843, #f43f5e); }
        .stat-title { font-size: 0.95rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; z-index: 1;}
        .stat-value { font-size: 1.8rem; font-weight: 800; z-index: 1;}
        .stat-sub { font-size: 0.8rem; opacity: 0.8; z-index: 1;}
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def create_gauge_chart(current, target):
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current,
            number={'suffix': "%", 'font': {'size': 48, 'color': '#ffffff'}},
            delta={'reference': target, 'increasing': {'color': "#10b981"}, 'decreasing': {'color': "#f43f5e"}},
            title={'text': "Current vs Goal", 'font': {'size': 20, 'color': '#94a3b8'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#334155"},
                'bar': {'color': "#4facfe"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, target], 'color': "rgba(244, 63, 94, 0.2)"},
                    {'range': [target, 100], 'color': "rgba(16, 185, 129, 0.2)"}
                ],
                'threshold': {
                    'line': {'color': "#ffffff", 'width': 4}, 'thickness': 0.75, 'value': target
                }
            }
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=50, b=20), height=320
        )
        return fig

# ==========================================
# MAIN APP CONTROLLER
# ==========================================
class PlannerApp:
    def __init__(self):
        st.set_page_config(page_title="Smart Attendance", page_icon="🎓", layout="wide")
        self.model = AttendanceDataModel()
        self.visuals = VisualEngine()
        
    def render_header(self):
        self.visuals.inject_custom_css()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # High-quality Lottie animation URL
            lottie_url = "https://assets3.lottiefiles.com/packages/lf20_q5pk6p1k.json"
            lottie_json = self.visuals.load_lottieurl(lottie_url)
            if lottie_json:
                st_lottie(lottie_json, height=200, key="header_anim")
        
        st.markdown('<div class="hero-title">Smart Attendance Planner</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-subtitle">Optimize your presence. Master your schedule. 🚀</div>', unsafe_allow_html=True)

    def render_sidebar(self):
        with st.sidebar:
            st.markdown("### 🎛️ App Controls")
            st.session_state.focus_mode = st.toggle("🔍 Focus Mode (Hide Setup)", value=False)
            st.markdown("---")
            st.markdown("### 🎮 What-If Simulator")
            st.info("💡 Simulate missing future classes to see how it affects your goal!")
            
            # Recalculate future classes to set max slider value
            metrics = self.model.calculate_metrics()
            max_bunks = metrics['future_classes']
            
            self.model.data.simulated_bunks = st.slider(
                "Simulate Bunks (Future Classes)",
                min_value=0, max_value=max_bunks if max_bunks > 0 else 0, value=0, step=1,
                help="Move this slider to pretend you missed upcoming classes."
            )
            
            if self.model.data.simulated_bunks > 0:
                st.warning(f"⚠️ Simulating {self.model.data.simulated_bunks} bunks. Gauge chart reflects this simulated drop.")

    def render_setup(self):
        if st.session_state.focus_mode:
            return
            
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⚙️ 1. Core Parameters")
        c1, c2, c3, c4 = st.columns(4)
        with c1: self.model.data.attended = st.number_input("Attended", min_value=0, value=self.model.data.attended)
        with c2: self.model.data.total = st.number_input("Total Conducted", min_value=1, value=self.model.data.total)
        with c3: self.model.data.target_percent = st.number_input("Target %", 0.0, 100.0, self.model.data.target_percent)
        with c4: 
            st.markdown("<br>", unsafe_allow_html=True)
            self.model.data.today_status = st.segmented_control("Today's Status", ["Present", "Absent", "None"], default="Present")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.expander("📅 2. Timeline & Timetable", expanded=False):
            sc1, sc2 = st.columns(2)
            with sc1: self.model.data.end_date = st.date_input("End of Term Date", value=self.model.data.end_date)
            with sc2: st.write("Weekly Schedule")
            
            tc1, tc2, tc3, tc4, tc5, tc6 = st.columns(6)
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            for i, (col, day) in enumerate(zip([tc1, tc2, tc3, tc4, tc5, tc6], days)):
                with col: self.model.data.timetable[i] = st.number_input(day, min_value=0, value=self.model.data.timetable[i])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.expander("🌴 3. Holiday Management", expanded=False):
            col_picker, col_list = st.columns([1, 2])
            with col_picker:
                new_hol = st.date_input("Add a Holiday", value=None, min_value=self.model.data.start_date)
                if new_hol and st.button("Add ➕", use_container_width=True):
                    if self.model.add_holiday(new_hol):
                        st.toast(f"Added {new_hol.strftime('%b %d')}", icon="🏖️")
                    else:
                        st.warning("Invalid or duplicate date.")
            with col_list:
                if not self.model.data.holidays:
                    st.info("No holidays added yet.")
                else:
                    for i, h in enumerate(self.model.data.holidays):
                        hc1, hc2 = st.columns([4, 1])
                        hc1.write(f"🎈 {h.strftime('%A, %B %d, %Y')}")
                        if hc2.button("❌", key=f"del_{i}"):
                            self.model.remove_holiday(i)
                            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    def render_dashboard(self):
        metrics = self.model.calculate_metrics()
        
        # Feedback logic
        if metrics['current_percent'] >= self.model.data.target_percent and metrics['current_percent'] > 0:
            if "celebrated" not in st.session_state:
                st.balloons()
                st.session_state.celebrated = True
        else:
            if "celebrated" in st.session_state:
                del st.session_state.celebrated

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col_text, col_chart = st.columns([1, 1.2])
        
        with col_text:
            st.subheader("📊 Performance Analytics")
            st.markdown(f"### Current Standing: `{metrics['current_percent']:.2f}%`")
            st.progress(min(metrics['current_percent']/100.0, 1.0))
            st.markdown(f"### Target Goal: `{self.model.data.target_percent:.2f}%`")
            st.progress(self.model.data.target_percent/100.0)
            st.info(f"📆 Future Classes Remaining: **{metrics['future_classes']}**")
            
            if self.model.data.simulated_bunks > 0:
                st.error(f"📉 After simulated bunks, future classes drop to: **{metrics['simulated_future']}**")

        with col_chart:
            fig = self.visuals.create_gauge_chart(metrics['current_percent'], self.model.data.target_percent)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🎯 Strategic Action Plan")
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1:
            st.markdown(f"""
            <div class='stat-box stat-target'>
                <div class='stat-title'>Target</div>
                <div class='stat-value'>{self.model.data.target_percent:.1f}%</div>
            </div>""", unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"""
            <div class='stat-box stat-max'>
                <div class='stat-title'>Max Possible</div>
                <div class='stat-value'>{metrics['max_possible_percent']:.1f}%</div>
                <div class='stat-sub'>if you attend all</div>
            </div>""", unsafe_allow_html=True)
            
        with c3:
            msg = "Reached ✨" if metrics['current_percent'] >= self.model.data.target_percent else f"{metrics['immediate_required']} classes"
            st.markdown(f"""
            <div class='stat-box stat-now'>
                <div class='stat-title'>Immediate</div>
                <div class='stat-value' style='font-size:1.4rem;'>{msg}</div>
                <div class='stat-sub'>to hit goal now</div>
            </div>""", unsafe_allow_html=True)
            
        with c4:
            msg = "Impossible ❌" if metrics['needed_attend'] > metrics['simulated_future'] else f"{metrics['needed_attend']} classes"
            st.markdown(f"""
            <div class='stat-box stat-end'>
                <div class='stat-title'>End of Term</div>
                <div class='stat-value' style='font-size:1.4rem;'>{msg}</div>
                <div class='stat-sub'>required out of {metrics['simulated_future']}</div>
            </div>""", unsafe_allow_html=True)
            
        with c5:
            safe = max(0, metrics['simulated_future'] - metrics['needed_attend']) if metrics['needed_attend'] <= metrics['simulated_future'] else 0
            icon = "😎" if safe > 0 else "😰"
            st.markdown(f"""
            <div class='stat-box stat-bunk'>
                <div class='stat-title'>Safe Bunks</div>
                <div class='stat-value'>{safe} {icon}</div>
                <div class='stat-sub'>you can skip</div>
            </div>""", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    def run(self):
        self.render_header()
        self.render_sidebar()
        self.render_setup()
        self.render_dashboard()
        
        st.markdown("""
        <div style='text-align:center; color:#475569; padding:20px; font-weight:bold;'>
            Architected & Crafted with ❤️ & Streamlit
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    app = PlannerApp()
    app.run()
