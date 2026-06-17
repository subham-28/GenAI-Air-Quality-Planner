from dotenv import load_dotenv
load_dotenv()

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from services.advisor_service import get_air_quality_plan
from services.rag_service import ask_guidelines

from services.geocoding_service import search_locations

import plotly.express as px
import plotly.graph_objects as go


# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="AirAware | GenAI Air Quality Action Planner",
    page_icon="logo.jpeg",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================
st.markdown(
    """
<style>
/* ------------------ Global ------------------ */
.stApp {
    background: radial-gradient(circle at top left, #182848 0%, #0f172a 35%, #020617 100%);
    color: #e5e7eb;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15,23,42,0.98), rgba(2,6,23,0.98));
    border-right: 1px solid rgba(148,163,184,0.2);
}

/* ------------------ Animated background blobs ------------------ */
.bg-blob {
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.35;
    z-index: 0;
    animation: floatBlob 10s ease-in-out infinite alternate;
}

.blob1 {
    width: 300px;
    height: 300px;
    background: #38bdf8;
    top: 10%;
    left: 5%;
}

.blob2 {
    width: 280px;
    height: 280px;
    background: #22c55e;
    bottom: 10%;
    right: 8%;
    animation-delay: 2s;
}

.blob3 {
    width: 220px;
    height: 220px;
    background: #a855f7;
    top: 55%;
    left: 45%;
    animation-delay: 4s;
}

@keyframes floatBlob {
    from {
        transform: translate3d(0, 0, 0) scale(1);
    }
    to {
        transform: translate3d(40px, -30px, 0) scale(1.12);
    }
}

/* ------------------ Hero ------------------ */
.hero-card {
    position: relative;
    z-index: 1;
    padding: 2.2rem;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(15,23,42,0.92), rgba(30,41,59,0.78));
    border: 1px solid rgba(148,163,184,0.22);
    box-shadow: 0 25px 80px rgba(0,0,0,0.45);
    overflow: hidden;
}

.hero-card::before {
    content: "";
    position: absolute;
    top: -80px;
    right: -80px;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(56,189,248,0.35), transparent 65%);
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 900;
    line-height: 1.05;
    margin-bottom: 0.6rem;
    background: linear-gradient(90deg, #e0f2fe, #7dd3fc, #86efac);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #cbd5e1;
    max-width: 850px;
}

.hero-chip {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    margin-right: 0.5rem;
    margin-top: 0.9rem;
    border-radius: 999px;
    background: rgba(14,165,233,0.14);
    border: 1px solid rgba(125,211,252,0.35);
    color: #bae6fd;
    font-size: 0.82rem;
}

/* ------------------ Glass cards ------------------ */
.glass-card {
    position: relative;
    z-index: 1;
    padding: 1.2rem;
    border-radius: 22px;
    background: rgba(15,23,42,0.72);
    border: 1px solid rgba(148,163,184,0.2);
    box-shadow: 0 18px 50px rgba(0,0,0,0.32);
    backdrop-filter: blur(14px);
    margin-bottom: 1rem;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #f8fafc;
    margin-bottom: 0.7rem;
}

.small-muted {
    color: #94a3b8;
    font-size: 0.88rem;
}

/* ------------------ 3D AQI orb ------------------ */
.orb-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 260px;
    perspective: 900px;
}

.aqi-orb {
    width: 210px;
    height: 210px;
    border-radius: 50%;
    position: relative;
    background:
        radial-gradient(circle at 35% 30%, rgba(255,255,255,0.95), transparent 10%),
        radial-gradient(circle at 40% 35%, rgba(186,230,253,0.7), transparent 18%),
        radial-gradient(circle at 70% 75%, rgba(34,197,94,0.55), transparent 35%),
        linear-gradient(135deg, #0ea5e9, #22c55e);
    box-shadow:
        inset -28px -28px 55px rgba(2,6,23,0.52),
        inset 18px 18px 45px rgba(255,255,255,0.18),
        0 0 55px rgba(56,189,248,0.42),
        0 35px 70px rgba(0,0,0,0.45);
    animation: rotateOrb 7s ease-in-out infinite alternate;
    transform-style: preserve-3d;
}

.aqi-orb::before {
    content: "";
    position: absolute;
    inset: 15px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.25);
    transform: rotateX(65deg);
}

.aqi-orb::after {
    content: "";
    position: absolute;
    width: 78%;
    height: 18px;
    bottom: -34px;
    left: 11%;
    border-radius: 50%;
    background: rgba(0,0,0,0.45);
    filter: blur(12px);
}

@keyframes rotateOrb {
    from {
        transform: rotateY(-18deg) rotateX(8deg) translateY(0);
    }
    to {
        transform: rotateY(22deg) rotateX(-8deg) translateY(-12px);
    }
}

.orb-text {
    position: absolute;
    text-align: center;
    width: 210px;
    margin-top: 82px;
    pointer-events: none;
}

.orb-category {
    font-size: 1.05rem;
    font-weight: 900;
    color: #020617;
}

.orb-pollutant {
    font-size: 0.75rem;
    color: #0f172a;
}

/* ------------------ Status badges ------------------ */
.status-badge {
    display: inline-block;
    padding: 0.45rem 0.85rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 800;
    letter-spacing: 0.02em;
}

.badge-good {
    background: rgba(34,197,94,0.18);
    color: #86efac;
    border: 1px solid rgba(34,197,94,0.45);
}

.badge-satisfactory {
    background: rgba(132,204,22,0.18);
    color: #bef264;
    border: 1px solid rgba(132,204,22,0.45);
}

.badge-moderate {
    background: rgba(234,179,8,0.18);
    color: #fde68a;
    border: 1px solid rgba(234,179,8,0.45);
}

.badge-poor {
    background: rgba(249,115,22,0.18);
    color: #fdba74;
    border: 1px solid rgba(249,115,22,0.45);
}

.badge-very-poor {
    background: rgba(239,68,68,0.18);
    color: #fca5a5;
    border: 1px solid rgba(239,68,68,0.45);
}

.badge-severe {
    background: rgba(168,85,247,0.18);
    color: #d8b4fe;
    border: 1px solid rgba(168,85,247,0.45);
}

/* ------------------ Native widget polish ------------------ */
div[data-testid="stMetric"] {
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(148,163,184,0.18);
    padding: 1rem;
    border-radius: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.25);
}

div[data-testid="stMetricLabel"] {
    color: #cbd5e1;
}

div[data-testid="stMetricValue"] {
    color: #f8fafc;
}

.stButton > button {
    width: 100%;
    border-radius: 16px;
    padding: 0.75rem 1rem;
    font-weight: 800;
    border: 1px solid rgba(125,211,252,0.4);
    background: linear-gradient(135deg, #0ea5e9, #22c55e);
    color: #020617;
    box-shadow: 0 15px 35px rgba(14,165,233,0.22);
    transition: all 0.25s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 45px rgba(34,197,94,0.26);
}

[data-testid="stExpander"] {
    background: rgba(15,23,42,0.58);
    border-radius: 16px;
    border: 1px solid rgba(148,163,184,0.16);
}

/* ------------------ Recommendation box ------------------ */
.reco-box {
    padding: 1.25rem;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(14,165,233,0.12), rgba(34,197,94,0.10));
    border: 1px solid rgba(125,211,252,0.24);
    color: #e0f2fe;
    font-size: 1rem;
}

/* ------------------ Footer ------------------ */
.footer-note {
    color: #94a3b8;
    text-align: center;
    font-size: 0.85rem;
    padding: 1rem;
}
</style>

<div class="bg-blob blob1"></div>
<div class="bg-blob blob2"></div>
<div class="bg-blob blob3"></div>
""",
    unsafe_allow_html=True
)


# ==========================================================
# HELPERS
# ==========================================================
def get_badge_class(category: str) -> str:
    if not category:
        return "badge-good"

    c = category.lower()

    if c == "good":
        return "badge-good"
    if c == "satisfactory":
        return "badge-satisfactory"
    if "moderately" in c or "moderate" in c:
        return "badge-moderate"
    if c == "poor":
        return "badge-poor"
    if c == "very poor":
        return "badge-very-poor"
    if c == "severe":
        return "badge-severe"

    return "badge-good"


def get_risk_score(category: str) -> int:
    mapping = {
        "Good": 15,
        "Satisfactory": 30,
        "Moderately Polluted": 50,
        "Moderate": 50,
        "Poor": 70,
        "Very Poor": 88,
        "Severe": 100,
    }
    return mapping.get(category, 0)


def init_state():
    if "history" not in st.session_state:
        st.session_state.history = []

    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    if "active_page" not in st.session_state:
        st.session_state.active_page = "🧠 Action Plan"


init_state()


# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    st.markdown("## 🌫️ AirAware")
    st.caption("GenAI Air Quality Action Planner")

    st.divider()

    st.markdown("### System modules")
    st.markdown(
        """
        - Live pollution API  
        - Live weather API  
        - CPCB AQI rule engine  
        - FAISS retriever  
        - CPCB/WHO RAG  
        - GenAI explanation  
        """
    )

    st.divider()
    st.caption("Use the Action Plan tab to generate a personalized recommendation.")


# ==========================================================
# HERO SECTION
# ==========================================================
st.markdown(
    """
<div class="hero-card">
    <div class="hero-title">AirAware</div>
    <div class="hero-subtitle">
        A futuristic GenAI decision assistant that converts live air pollution,
        weather conditions, CPCB AQI logic, and WHO/CPCB guideline retrieval into
        personalized outdoor activity recommendations.
    </div>
    <span class="hero-chip">Live AQI</span>
    <span class="hero-chip">Weather-aware</span>
    <span class="hero-chip">RAG-grounded</span>
    <span class="hero-chip">Explainable</span>
</div>
""",
    unsafe_allow_html=True
)

st.write("")


# ==========================================================
# MAIN NAVIGATION
# ==========================================================
PAGES = [
    "🧠 Action Plan",
    "🛰️ Air Intelligence",
    "📘 Ask Guidelines",
    "📊 Session History"
]

st.radio(
    "Navigation",
    PAGES,
    horizontal=True,
    key="active_page",
    label_visibility="collapsed"
)

page = st.session_state.active_page
result = st.session_state.last_result



# ==========================================================
# ACTION PLAN TAB
# ==========================================================
if page == "🧠 Action Plan":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Smart Action Planner</div>', unsafe_allow_html=True)
    st.caption(
        "Search your city or area, choose the matched location, then generate a "
        "rule-based recommendation and guideline-grounded GenAI explanation."
    )

    col1, col2 = st.columns(2)

    with col1:
        city_query = st.text_input(
            "📍 Search city or area",
            placeholder="e.g., Bhubaneswar, Delhi, New Delhi, Patia"
        )

        selected_location = None

        if city_query:
            location_matches = search_locations(
                city=city_query,
                country_code="IN",
                count=10
            )

            if not location_matches:
                st.warning("No matching location found. Try another city or area name.")

            else:
                location_options = {}

                for loc in location_matches:
                    label = (
                        f"{loc.get('display_name')} "
                        f"({loc.get('latitude'):.4f}, {loc.get('longitude'):.4f})"
                    )
                    location_options[label] = loc

                selected_display_name = st.selectbox(
                    "Choose matched location",
                    list(location_options.keys())
                )

                selected_location = location_options[selected_display_name]

                st.success(f"Using location: {selected_location.get('display_name')}")

        profile = st.selectbox(
            "👤 Profile",
            [
                "Student",
                "Jogger",
                "Commuter",
                "Outdoor worker",
                "General user",
                "Elderly person"
            ],
            index=None,
            placeholder="Choose a profile"
        )

    with col2:
        activity = st.text_input(
            "🏃 Activity",
            placeholder="e.g., Outdoor jogging"
        )

        duration_minutes = st.slider(
            "⏱️ Duration in minutes",
            min_value=5,
            max_value=180,
            value=30,
            step=5
        )

    st.markdown("</div>", unsafe_allow_html=True)

    generate_btn = st.button("🚀 Explain My Air", type="primary")

    if generate_btn:
        if not city_query or selected_location is None or not profile or not activity:
            st.warning("Please search and select a location, choose profile, and enter activity.")

        else:
            with st.status("Building your air-quality action plan...", expanded=True) as status:
                try:
                    st.write("📍 Resolving selected location...")
                    st.write("🌫️ Fetching live air-quality data...")
                    st.write("🌦️ Fetching weather conditions...")
                    st.write("🧮 Applying CPCB AQI logic...")
                    st.write("📚 Retrieving CPCB/WHO guideline context...")
                    st.write("🧠 Generating grounded recommendation...")

                    result = get_air_quality_plan(
                        city=city_query,
                        profile=profile,
                        activity=activity,
                        duration_minutes=duration_minutes,
                        location=selected_location
                    )

                    if "error" in result:
                        st.session_state.last_result = result
                        status.update(label="Could not generate action plan.", state="error")
                        st.error(result["error"])

                    else:
                        st.session_state.last_result = result

                        st.session_state.history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "city": result.get("city"),
                            "location": result.get("matched_location"),
                            "profile": result.get("profile"),
                            "activity": result.get("activity"),
                            "pm2_5": result.get("pm2_5"),
                            "pm10": result.get("pm10"),
                            "category": result.get("overall_category"),
                            "dominant_pollutant": result.get("dominant_pollutant"),
                            "recommendation": result.get("recommendation")
                        })

                        status.update(label="Action plan generated successfully.", state="complete")

                except Exception as e:
                    st.session_state.last_result = {"error": str(e)}
                    status.update(label="Something went wrong.", state="error")
                    st.exception(e)

    result = st.session_state.last_result

    if result and "error" not in result:
        st.success(f"Using location: {result.get('matched_location')}")

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Live Situation Snapshot</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PM2.5", f"{result.get('pm2_5')} µg/m³")
        c2.metric("PM10", f"{result.get('pm10')} µg/m³")
        c3.metric("Category", result.get("overall_category"))
        c4.metric("Dominant Pollutant", result.get("dominant_pollutant"))

        st.caption(f"Last updated: {result.get('time')}")
        st.markdown("</div>", unsafe_allow_html=True)

        # -----------------------------
        # Best Time to Go Outside
        # -----------------------------
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Best Time to Go Outside</div>', unsafe_allow_html=True)

        t1, t2 = st.columns(2)

        with t1:
            st.success(f"Best outdoor window today: {result.get('best_outdoor_window')}")
            st.caption(
                f"Avg PM2.5: {result.get('best_window_avg_pm25')} µg/m³ | "
                f"Avg PM10: {result.get('best_window_avg_pm10')} µg/m³"
            )

        with t2:
            st.error(f"Worst window today: {result.get('worst_outdoor_window')}")
            st.caption(
                f"Avg PM2.5: {result.get('worst_window_avg_pm25')} µg/m³ | "
                f"Avg PM10: {result.get('worst_window_avg_pm10')} µg/m³"
            )

        st.markdown("</div>", unsafe_allow_html=True)


        # -----------------------------
        # Confidence Score Panel
        # -----------------------------
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Confidence Score</div>', unsafe_allow_html=True)

        conf1, conf2, conf3 = st.columns(3)

        with conf1:
            st.metric(
                "Confidence",
                result.get("confidence_label")
            )

        with conf2:
            st.metric(
                "Score",
                f"{result.get('confidence_score')}/100"
            )

        with conf3:
            st.metric(
                "Guideline Chunks",
                result.get("retrieved_guideline_chunks")
            )

        confidence_score = result.get("confidence_score") or 0
        st.progress(confidence_score / 100)

        st.write("**Why this confidence level?**")

        confidence_reasons = result.get("confidence_reasons", [])

        if confidence_reasons:
            for reason in confidence_reasons:
                st.write(f"- {reason}")
        else:
            st.write("- Confidence reasons unavailable.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Rule-Based Recommendation</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="reco-box">
    {result.get("recommendation")}
</div>
""",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Guideline-Grounded GenAI Explanation</div>', unsafe_allow_html=True)
        st.write(result.get("rag_explanation"))
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("🔍 Explainability trace"):
            st.write(f"**Using location:** {result.get('matched_location')}")
            st.write(f"**City:** {result.get('city')}, {result.get('country')}")
            st.write(f"**Latitude:** {result.get('latitude')}")
            st.write(f"**Longitude:** {result.get('longitude')}")
            st.write(f"**Overall category:** {result.get('overall_category')}")
            st.write(f"**Dominant pollutant:** {result.get('dominant_pollutant')}")
            st.write(f"**PM2.5 category:** {result.get('pm25_category')}")
            st.write(f"**PM10 category:** {result.get('pm10_category')}")
            st.write(f"**Profile:** {result.get('profile')}")
            st.write(f"**Activity:** {result.get('activity')}")
            st.write(f"**Duration:** {result.get('duration_minutes')} minutes")
            st.write("**RAG basis:** CPCB/WHO guideline context retrieved from FAISS vector store.")
            st.write(f"**Best outdoor window:** {result.get('best_outdoor_window')}")
            st.write(f"**Worst outdoor window:** {result.get('worst_outdoor_window')}")
            st.write(f"**Best window avg PM2.5:** {result.get('best_window_avg_pm25')} µg/m³")
            st.write(f"**Best window avg PM10:** {result.get('best_window_avg_pm10')} µg/m³")
            st.write(f"**Confidence:** {result.get('confidence_label')}")
            st.write(f"**Confidence score:** {result.get('confidence_score')}/100")
            st.write(f"**Retrieved guideline chunks:** {result.get('retrieved_guideline_chunks')}")

        report = json.dumps(result, indent=2, ensure_ascii=False)

        st.download_button(
            label="⬇️ Download action plan JSON",
            data=report,
            file_name=f"air_quality_action_plan_{result.get('city')}.json",
            mime="application/json"
        )

    elif result and "error" in result:
        st.error(result["error"])


# ==========================================================
# AIR INTELLIGENCE TAB
# ==========================================================
if page == "🛰️ Air Intelligence":
    result = st.session_state.last_result

    if not result:
        st.info("Generate an action plan first from the Action Plan tab.")

    elif "error" in result:
        st.error(result["error"])

    else:
        category = result.get("overall_category")
        badge_class = get_badge_class(category)
        risk_score = get_risk_score(category)

        left, right = st.columns([1.1, 1.4], gap="large")

        with left:
            st.markdown(
                f"""
<div class="glass-card">
    <div class="section-title">3D AQI Status Orb</div>
    <div class="orb-wrap">
        <div class="aqi-orb"></div>
        <div class="orb-text">
            <div class="orb-category">{category}</div>
            <div class="orb-pollutant">{result.get("dominant_pollutant")}</div>
        </div>
    </div>
    <div style="text-align:center;">
        <span class="status-badge {badge_class}">{category}</span>
    </div>
</div>
""",
                unsafe_allow_html=True
            )

        with right:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Live Air Quality Metrics</div>', unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("PM2.5", f"{result.get('pm2_5')} µg/m³")
            c2.metric("PM10", f"{result.get('pm10')} µg/m³")
            c3.metric("US AQI", result.get("us_aqi"))
            c4.metric("EU AQI", result.get("european_aqi"))

            st.write("")
            st.markdown("#### Risk intensity")
            st.progress(risk_score / 100)
            st.caption(f"Estimated risk intensity based on category: {risk_score}/100")

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Weather Context</div>', unsafe_allow_html=True)

        w1, w2, w3, w4 = st.columns(4)
        w1.metric("Temperature", f"{result.get('temperature')} °C")
        w2.metric("Humidity", f"{result.get('humidity')} %")
        w3.metric("Wind speed", f"{result.get('wind_speed')} km/h")
        w4.metric("Precipitation", f"{result.get('precipitation')} mm")

        st.caption(f"Last updated: {result.get('time')}")
        st.markdown("</div>", unsafe_allow_html=True)


        # -----------------------------
        # Pollutant Trend Chart
        # -----------------------------
        hourly_forecast = result.get("hourly_forecast", [])

        if hourly_forecast:
            trend_df = pd.DataFrame(hourly_forecast)

            trend_df["time"] = pd.to_datetime(trend_df["time"])
            trend_df = trend_df.sort_values("time").head(24)

            trend_df["hour_label"] = trend_df["time"].dt.strftime("%I %p").str.lstrip("0")

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Pollutant Trend: Next 24 Hours</div>', unsafe_allow_html=True)

            chart_tab1, chart_tab2, chart_tab3 = st.tabs(
                [
                    "PM2.5 Trend",
                    "PM10 Trend",
                    "AQI Trend"
                ]
            )

            with chart_tab1:
                fig_pm25 = go.Figure()

                fig_pm25.add_trace(
                    go.Scatter(
                        x=trend_df["hour_label"],
                        y=trend_df["pm2_5"],
                        mode="lines+markers",
                        name="PM2.5",
                        line=dict(width=3),
                        marker=dict(size=7),
                        fill="tozeroy"
                    )
                )

                fig_pm25.update_layout(
                    title="PM2.5 Forecast for Next 24 Hours",
                    xaxis_title="Time",
                    yaxis_title="PM2.5 concentration (µg/m³)",
                    template="plotly_dark",
                    height=420,
                    margin=dict(l=20, r=20, t=60, b=40),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15,23,42,0.4)"
                )

                st.plotly_chart(fig_pm25, width='stretch')

            with chart_tab2:
                fig_pm10 = go.Figure()

                fig_pm10.add_trace(
                    go.Scatter(
                        x=trend_df["hour_label"],
                        y=trend_df["pm10"],
                        mode="lines+markers",
                        name="PM10",
                        line=dict(width=3),
                        marker=dict(size=7),
                        fill="tozeroy"
                    )
                )

                fig_pm10.update_layout(
                    title="PM10 Forecast for Next 24 Hours",
                    xaxis_title="Time",
                    yaxis_title="PM10 concentration (µg/m³)",
                    template="plotly_dark",
                    height=420,
                    margin=dict(l=20, r=20, t=60, b=40),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15,23,42,0.4)"
                )

                st.plotly_chart(fig_pm10, width='stretch')

            with chart_tab3:
                fig_aqi = go.Figure()

                if "us_aqi" in trend_df.columns:
                    fig_aqi.add_trace(
                        go.Scatter(
                            x=trend_df["hour_label"],
                            y=trend_df["us_aqi"],
                            mode="lines+markers",
                            name="US AQI",
                            line=dict(width=3),
                            marker=dict(size=7)
                        )
                    )

                if "european_aqi" in trend_df.columns:
                    fig_aqi.add_trace(
                        go.Scatter(
                            x=trend_df["hour_label"],
                            y=trend_df["european_aqi"],
                            mode="lines+markers",
                            name="European AQI",
                            line=dict(width=3),
                            marker=dict(size=7)
                        )
                    )

                fig_aqi.update_layout(
                    title="AQI Forecast Trend for Next 24 Hours",
                    xaxis_title="Time",
                    yaxis_title="AQI",
                    template="plotly_dark",
                    height=420,
                    margin=dict(l=20, r=20, t=60, b=40),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15,23,42,0.4)"
                )

                st.plotly_chart(fig_aqi, width='stretch')

            st.caption(
                f"Best outdoor window: {result.get('best_outdoor_window')} | "
                f"Worst window: {result.get('worst_outdoor_window')}"
            )

            st.markdown("</div>", unsafe_allow_html=True)


        with st.expander("🧪 Detailed pollutant panel"):
            p1, p2, p3 = st.columns(3)

            with p1:
                st.write("### Particulate matter")
                st.write(f"**PM2.5:** {result.get('pm2_5')} µg/m³")
                st.write(f"**PM10:** {result.get('pm10')} µg/m³")
                st.write(f"**PM2.5 category:** {result.get('pm25_category')}")
                st.write(f"**PM10 category:** {result.get('pm10_category')}")

            with p2:
                st.write("### Gaseous pollutants")
                st.write(f"**Carbon monoxide:** {result.get('carbon_monoxide')}")
                st.write(f"**Nitrogen dioxide:** {result.get('nitrogen_dioxide')}")
                st.write(f"**Sulphur dioxide:** {result.get('sulphur_dioxide')}")
                st.write(f"**Ozone:** {result.get('ozone')}")

            with p3:
                st.write("### Decision context")
                st.write(f"**City:** {result.get('city')}, {result.get('country')}")
                st.write(f"**Profile:** {result.get('profile')}")
                st.write(f"**Activity:** {result.get('activity')}")
                st.write(f"**Duration:** {result.get('duration_minutes')} minutes")
                st.write(f"**Dominant pollutant:** {result.get('dominant_pollutant')}")

# ==========================================================
# GUIDELINE CHATBOT TAB
# ==========================================================
if page == "📘 Ask Guidelines":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Ask CPCB/WHO Guidelines</div>', unsafe_allow_html=True)
    st.caption("Ask guideline-based questions. The answer is generated using your RAG pipeline.")

    guideline_question = st.text_area(
        "Question",
        value="What should people do during very poor or severe AQI?",
        height=120
    )

    ask_col1, ask_col2 = st.columns([1, 3])

    with ask_col1:
        ask_btn = st.button("Ask Guidelines")

    with ask_col2:
        st.caption("Examples: What is PM2.5? How is AQI calculated? What are CPCB AQI categories?")

    if ask_btn:
        try:
            with st.spinner("Retrieving context and generating answer..."):
                guideline_answer = ask_guidelines(guideline_question)

            st.markdown("### Answer")
            st.write(guideline_answer)

        except Exception as e:
            st.error("Could not answer guideline question.")
            st.exception(e)

    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# HISTORY TAB
# ==========================================================
if page == "📊 Session History":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Session History</div>', unsafe_allow_html=True)

    if len(st.session_state.history) == 0:
        st.info("No history yet. Generate at least one action plan.")

    else:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, width='stretch')

        numeric_cols = ["pm2_5", "pm10"]
        chart_df = history_df[numeric_cols].apply(pd.to_numeric, errors="coerce")

        if len(chart_df) >= 2:
            st.markdown("### PM trend during this session")
            st.line_chart(chart_df)

        csv_data = history_df.to_csv(index=False)

        st.download_button(
            label="⬇️ Download session history CSV",
            data=csv_data,
            file_name="air_quality_session_history.csv",
            mime="text/csv"
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# FOOTER
# ==========================================================
st.markdown(
    """
<div class="footer-note">
    Disclaimer: AirAware provides general air-quality guidance only.
    It does not provide medical diagnosis, treatment, or medicine advice.
</div>
""",
    unsafe_allow_html=True
)