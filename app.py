"""
Multimodal Construction Intelligence Platform
Skill Wallet Capstone Project 1
Turnkey Production-Ready Streamlit Application

Modules:
- Tab 1: Site Safety & PPE Audit (Epic 2)
- Tab 2: Crack Diagnostics & Structural Integrity (Epic 2)
- Tab 3: Planning & Real Estate Valuation (Epic 3)
- Tab 4: Daily Site Assistant & Weather-Aware Advisory (Epic 5)
"""

import os
import streamlit as st
from modules.gemini_service import validate_api_key
from modules.site_safety import render_site_safety_tab
from modules.crack_diagnostics import render_crack_diagnostics_tab
from modules.real_estate_valuation import render_real_estate_valuation_tab
from modules.weather_assistant import render_weather_assistant_tab

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Multimodal Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Global Premium Modern CSS Stylesheet
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Import Inter / Space Grotesk modern web fonts */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Background & main wrapper */
.stApp {
    background-color: #0B1120;
    color: #F8FAFC;
}

/* Header Banner */
.main-header {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(245, 158, 11, 0.25);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 22px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35);
    display: flex;
    justify-content: space-between;
    align-items: center;
    backdrop-filter: blur(8px);
}

.main-title {
    font-size: 1.85rem;
    font-weight: 800;
    background: linear-gradient(90deg, #F8FAFC 0%, #F59E0B 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}

.main-subtitle {
    font-size: 0.92rem;
    color: #94A3B8;
    margin-top: 4px;
    font-weight: 500;
}

/* Section Header Banners */
.section-banner {
    background: #111827;
    border: 1px solid #1F2937;
    border-left: 4px solid #F59E0B;
    border-radius: 8px;
    padding: 14px 20px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Metric Cards */
.metric-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
}

.metric-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 14px 16px;
    transition: transform 0.2s ease, border-color 0.2s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: #F59E0B;
}

.metric-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
}

.metric-value {
    font-size: 1.7rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 4px;
}

.metric-subtitle {
    font-size: 0.8rem;
    color: #CBD5E1;
}

/* Badges / Status Pills */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}

.badge-success {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

.badge-danger {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

.badge-accent {
    background: rgba(56, 189, 248, 0.15);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.4);
}

/* Hazard & Recipe Cards */
.hazard-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-left: 4px solid #EF4444;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.recipe-card {
    background: #0F172A;
    border: 1px solid #334155;
    border-left: 4px solid #38BDF8;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.weather-rule-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 10px;
}

/* Mode Banner */
.demo-banner {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.35);
    color: #FCD34D;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 14px;
    font-size: 0.88rem;
}

.live-banner {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #6EE7B7;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 14px;
    font-size: 0.88rem;
}

/* Empty State Card */
.empty-state-card {
    background: #111827;
    border: 2px dashed #334155;
    border-radius: 12px;
    padding: 50px 24px;
    text-align: center;
    margin-top: 10px;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    border-right: 1px solid #1E293B;
}

/* Custom Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #1E293B;
    padding-bottom: 4px;
}

.stTabs [data-baseweb="tab"] {
    padding: 10px 18px;
    font-weight: 600;
    font-size: 0.95rem;
    color: #94A3B8;
    border-radius: 6px 6px 0 0;
    background: transparent;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    color: #F59E0B !important;
    border-bottom: 2px solid #F59E0B !important;
    background: rgba(245, 158, 11, 0.08) !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0B1120;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar Configuration & Architecture Overview
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display:flex; align-items:center; gap: 10px; margin-bottom: 12px;">
            <span style="font-size: 2rem;">🏗️</span>
            <div>
                <h3 style="margin:0; font-size:1.15rem; font-weight:800; color:#F8FAFC;">Skill Wallet Capstone</h3>
                <span class="badge badge-warning" style="font-size:0.7rem;">Project 1 • Multimodal AI</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🔑 Google Gemini API Configuration")

    # API Key Input
    existing_env_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Gemini API Key:",
        value=st.session_state.get("gemini_api_key", existing_env_key),
        type="password",
        help="Input your Google Gemini API key. If omitted, the platform gracefully defaults to full Demonstration Simulation Mode."
    )
    if user_api_key:
        st.session_state["gemini_api_key"] = user_api_key

    # Model selector
    model_choice = st.selectbox(
        "Multimodal AI Model:",
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
        index=0,
        help="Select Google Gemini foundation model variant"
    )

    # API Status check
    has_key = bool(user_api_key.strip())
    if has_key:
        if st.button("🧪 Verify API Key Connection", use_container_width=True):
            with st.spinner("Pinging Google Generative Language API..."):
                valid, msg = validate_api_key(user_api_key)
                if valid:
                    st.success(f"✅ {msg}")
                else:
                    st.warning(f"⚠️ {msg}")
        st.markdown("""
            <div style="margin: 8px 0;">
                <span class="badge badge-success">🟢 Live Gemini Mode Active</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="margin: 8px 0;">
                <span class="badge badge-warning">⚡ Demonstration Mode Active</span>
            </div>
            <p style="font-size: 0.78rem; color: #94A3B8; margin-top: 4px;">
                No API key supplied. High-fidelity synthetic audits & offline expert responses are ready for instant 1-click evaluation.
            </p>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Architecture Overview Expander
    with st.expander("🏛️ System Architecture Overview", expanded=False):
        st.markdown("""
            **Multimodal AI Pipeline:**
            - **Input Layer:** High-res drone/CCTV/site imagery + civil engineering parameters.
            - **Multimodal Engine:** Google Gemini (Base64 JPEG inline data + structured JSON schema parsing).
            - **Code Standards Layer:** OSHA 1926, IS 456:2000, IS 13367 (Cranes), IS 3696 (Scaffolding).
            - **3D Neural Synthesis:** Pollinations AI REST integration.
            - **Zero-DB Cloud State:** Session State architecture optimized for 1-click Streamlit Community Cloud deployment.
        """)

    # Quick Navigation / Epics
    with st.expander("📚 Epics & Regulatory Matrix", expanded=False):
        st.markdown("""
            - **Epic 2 (Safety):** OSHA 1926.501 (Fall Protection), IS 2925 (Helmets), IS 3521 (Harnesses).
            - **Epic 2 (Defects):** IS 456 Cl. 35.3 (Crack Width Limits), ACI 224.1R (Epoxy Repair).
            - **Epic 3 (Valuation):** Indian RERA norms, Tier 1/2/3 construction indices, Steel/Cement BOQ.
            - **Epic 5 (Advisory):** Dynamic weather triggers (wind thresholds, curing hydration).
        """)

    st.markdown("""
        <div style="margin-top: 24px; padding: 12px; background:#111827; border-radius:8px; border:1px solid #1E293B; font-size:0.75rem; color:#64748B; text-align:center;">
            Skill Wallet Capstone Platform<br>
            Production-Ready Release v1.0<br>
            IS 456 & OSHA Compliant
        </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Main Application Header
# -----------------------------------------------------------------------------
effective_key = user_api_key.strip() if user_api_key else ""

st.markdown("""
    <div class="main-header">
        <div>
            <h1 class="main-title">🏗️ Multimodal Construction Intelligence Platform</h1>
            <div class="main-subtitle">
                Skill Wallet Capstone Project 1 • Autonomous Site Safety, Structural Forensics, Real Estate Valuation & Weather Advisory
            </div>
        </div>
        <div style="display:flex; gap:8px; align-items:center;">
            <span class="badge badge-accent">Production Ready</span>
            <span class="badge badge-warning">Zero DB Dependency</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Module Tabs Navigation
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🦺 Site Safety & PPE Audit (Epic 2)",
    "🔬 Crack Diagnostics & Structural Integrity (Epic 2)",
    "🏛️ Planning & Real Estate Valuation (Epic 3)",
    "🌤️ Daily Site Assistant & Weather Advisory (Epic 5)"
])

with tab1:
    render_site_safety_tab(api_key=effective_key, selected_model=model_choice)

with tab2:
    render_crack_diagnostics_tab(api_key=effective_key, selected_model=model_choice)

with tab3:
    render_real_estate_valuation_tab()

with tab4:
    render_weather_assistant_tab(api_key=effective_key, selected_model=model_choice)

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("""
    <div style="margin-top: 40px; padding: 16px 0; border-top: 1px solid #1E293B; display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; color:#64748B;">
        <div>
            Multimodal Construction Intelligence Platform • Developed for <strong>Skill Wallet Capstone</strong>
        </div>
        <div>
            Standards: IS 456:2000 | IS 13367 | OSHA 1926 | ACI 224.1R
        </div>
    </div>
""", unsafe_allow_html=True)
