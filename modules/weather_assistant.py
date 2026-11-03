"""
Module for Tab 4: Daily Site Assistant & Weather-Aware Advisory (Epic 5)
Provides weather-contingent site engineering protocols (crane suspension, electrical hazard mitigation,
concrete curing adjustments under IS 456 / OSHA), paired with an interactive multi-turn AI engineering assistant chatbot.
"""

import streamlit as st
from modules.sample_data import WEATHER_PROTOCOLS
from modules.gemini_service import generate_chat_response

QUICK_PROMPTS = [
    "IS 456 Minimum Curing Period & Formwork Stripping Times",
    "Tower Crane High Wind Wind Speed Limits & Slewing Protocol",
    "Epoxy Grouting Procedure for 2.5mm Shear Crack",
    "Monsoon Electrical Safety & De-watering Checklist"
]

def render_weather_assistant_tab(api_key: str, selected_model: str):
    """Renders the Daily Site Assistant & Weather-Aware Advisory."""
    st.markdown("""
        <div class="section-banner">
            <div>
                <h2 style="margin:0; font-size: 1.55rem; color: #F8FAFC;">
                    🌤️ Daily Site Assistant & Weather-Aware Advisory (Epic 5)
                </h2>
                <p style="margin:4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">
                    Dynamic Meteorological Safety Protocols & Multi-Turn Resident Construction Engineering AI
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-accent">IS 13367 Crane Safety</span>
                <span class="badge badge-warning">OSHA Subpart M</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_weather, col_chat = st.columns([5, 7], gap="large")

    with col_weather:
        st.markdown("#### 🌦️ 1. Active Weather Condition & Site Protocol")
        weather_choice = st.selectbox(
            "Select Current / Forecast Site Weather Condition:",
            list(WEATHER_PROTOCOLS.keys()),
            index=0,
            help="Simulates micro-climatic impacts on crane operations, scaffolding stability, and concrete hydration"
        )
        protocol = WEATHER_PROTOCOLS[weather_choice]

        # Dynamic Alert Badge
        alert_bg = protocol["color"]
        st.markdown(f"""
            <div style="background:{alert_bg}22; border-left: 5px solid {alert_bg}; padding: 12px 16px; border-radius: 8px; margin: 12px 0 18px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:{alert_bg}; font-size:1.05rem;">{protocol['alert_level']}</span>
                    <span class="badge" style="background:{alert_bg}; color:#0F172A; font-weight:700;">ACTIVE WEATHER TRIGGER</span>
                </div>
                <div style="font-size:0.88rem; color:#CBD5E1; margin-top:4px;">
                    Protocol strictly enforced across all tower cranes, elevated scaffolds, and concreting decks.
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 4 Core Protocol Blocks
        st.markdown("##### 🚨 Operational Stoppage & Mitigation Rules")

        # 1. Cranes
        st.markdown(f"""
            <div class="weather-rule-card">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                    <span style="font-size:1.2rem;">🏗️</span>
                    <strong style="color:#F8FAFC; font-size:0.95rem;">Tower Cranes & Lifting Operations</strong>
                </div>
                <div style="color:#CBD5E1; font-size:0.88rem; line-height:1.45;">
                    {protocol['crane_operations']}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 2. Scaffolding
        st.markdown(f"""
            <div class="weather-rule-card">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                    <span style="font-size:1.2rem;">🪜</span>
                    <strong style="color:#F8FAFC; font-size:0.95rem;">Scaffolding & Work at Elevation</strong>
                </div>
                <div style="color:#CBD5E1; font-size:0.88rem; line-height:1.45;">
                    {protocol['scaffolding_work']}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 3. Electrical
        st.markdown(f"""
            <div class="weather-rule-card">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                    <span style="font-size:1.2rem;">⚡</span>
                    <strong style="color:#F8FAFC; font-size:0.95rem;">Electrical Hazard & Water Ingress</strong>
                </div>
                <div style="color:#CBD5E1; font-size:0.88rem; line-height:1.45;">
                    {protocol['electrical_safety']}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 4. Concrete Curing
        st.markdown(f"""
            <div class="weather-rule-card">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                    <span style="font-size:1.2rem;">🧱</span>
                    <strong style="color:#F8FAFC; font-size:0.95rem;">Concrete Curing & Hydration (IS 456)</strong>
                </div>
                <div style="color:#CBD5E1; font-size:0.88rem; line-height:1.45;">
                    {protocol['concrete_curing']}
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_chat:
        st.markdown("#### 💬 2. Resident Construction AI Engineering Assistant")
        
        # Chat reset & status
        chat_head_col1, chat_head_col2 = st.columns([8, 4])
        with chat_head_col1:
            st.caption("Trained on IS 456, IS 800, IS 3696, OSHA 1926 & ACI Structural Standards.")
        with chat_head_col2:
            if st.button("🧹 Clear Chat History", use_container_width=True):
                st.session_state["chat_messages"] = []
                st.rerun()

        # Quick prompt buttons
        st.markdown("<div style='font-size:0.82rem; color:#94A3B8; margin-bottom:6px;'>⚡ Quick-Trigger Engineering Questions:</div>", unsafe_allow_html=True)
        q_cols = st.columns(2)
        for i, q in enumerate(QUICK_PROMPTS):
            target_col = q_cols[i % 2]
            with target_col:
                if st.button(f"📌 {q[:32]}...", key=f"quick_{i}", use_container_width=True):
                    _append_and_respond(q, weather_choice, api_key, selected_model)
                    st.rerun()

        # Initialize chat history if not present
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [
                {
                    "role": "model",
                    "content": (
                        "Greetings Engineer! I am your Multimodal Construction & Safety AI Co-Pilot. "
                        f"I am actively monitoring site conditions under **{weather_choice}**. "
                        "Ask me about IS 456 curing specs, formwork stripping intervals, crane wind cut-offs, "
                        "or structural rehabilitation methodologies."
                    )
                }
            ]

        # Chat container
        chat_container = st.container(height=420)
        with chat_container:
            for msg in st.session_state["chat_messages"]:
                if msg["role"] == "user":
                    st.chat_message("user", avatar="👷").markdown(msg["content"])
                else:
                    st.chat_message("assistant", avatar="🤖").markdown(msg["content"])

        # Chat user input
        user_query = st.chat_input("Ask civil engineering question or site safety query...")
        if user_query:
            _append_and_respond(user_query, weather_choice, api_key, selected_model)
            st.rerun()


def _append_and_respond(user_text: str, weather_condition: str, api_key: str, model_name: str):
    """Helper to append user query and fetch response from Gemini / Knowledge Engine."""
    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    st.session_state["chat_messages"].append({"role": "user", "content": user_text})
    
    with st.spinner("Resident Engineer analyzing codes & engineering calculations..."):
        reply = generate_chat_response(
            messages=st.session_state["chat_messages"],
            current_weather=weather_condition,
            api_key=api_key,
            model_name=model_name
        )
    st.session_state["chat_messages"].append({"role": "model", "content": reply})
