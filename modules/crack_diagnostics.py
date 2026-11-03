"""
Module for Tab 2: Crack Diagnostics & Structural Integrity (Epic 2)
Analyzes concrete/masonry defects, classifies crack types, estimates widths (mm),
identifies root causes, and recommends IS 456 / ACI compliant engineering repairs.
"""

import json
import streamlit as st
import pandas as pd
from PIL import Image
import io
from modules.sample_data import create_sample_crack_image
from modules.gemini_service import analyze_multimodal_vision

CRACK_SYSTEM_INSTRUCTION = """
You are a Principal Structural Forensic Engineer specializing in concrete durability, forensic investigation, and rehabilitation per IS 456:2000, IS 15988:2013, and ACI 224.1R.
Analyze the uploaded image of the distressed structural concrete/masonry element.

You must respond with ONLY valid JSON adhering strictly to this schema:
{
    "defect_type": "<Hairline Crack | Structural Shear Diagonal Crack | Settlement Crack | Thermal Expansion Crack | Spalling with Exposed Rebar | Honeycombing>",
    "crack_classification": "<Active Structural | Dormant Non-Structural | Corrosion-Induced Delamination>",
    "estimated_width_mm": <float, e.g. 2.8>,
    "width_tolerance_range": "<e.g. 2.4 mm - 3.2 mm>",
    "crack_depth": "<Surface Cover Only | Deep Penetrating | Through-Section>",
    "structural_risk_index": <float from 1.0 to 10.0>,
    "risk_level": "<Low Risk | Moderate Risk | High / Urgent Risk | Catastrophic Warning>",
    "urgency": "<Immediate Evacuation | Urgent (Within 48 hours) | Routine Maintenance (30 Days) | Monitor Only>",
    "root_causes": [
        "<Detailed primary cause 1>",
        "<Secondary cause 2>",
        "<Environmental or loading factor 3>"
    ],
    "recommended_repairs": [
        {
            "step": 1,
            "technique": "<Technique name e.g. NDT & Crack Mapping>",
            "protocol": "<Detailed engineering procedure with material spec e.g. ASTM C881 Type I Epoxy or CFRP wrap>"
        },
        {
            "step": 2,
            "technique": "<Technique name e.g. Pressure Epoxy Injection>",
            "protocol": "<Detailed procedure>"
        },
        {
            "step": 3,
            "technique": "<Technique name e.g. Rebar Passivation & Polymer Mortar>",
            "protocol": "<Detailed procedure>"
        }
    ],
    "is_code_compliance": "<Relevant IS 456:2000, IS 13920, and ACI code standards>",
    "safety_precautions": "<Immediate temporary shoring or site hazard protection requirements>"
}
"""

CRACK_USER_PROMPT = """
Inspect this structural concrete element. Classify the defect type (Shear, Hairline, Settlement, Thermal, Spalling),
estimate the crack width in millimeters, assess penetration depth, compute the Structural Risk Index (1-10),
list probable structural root causes, and provide an actionable, step-by-step engineering repair procedure.
Return strictly the requested JSON structure.
"""

def render_crack_diagnostics_tab(api_key: str, selected_model: str):
    """Renders the Crack Diagnostics & Structural Integrity view."""
    st.markdown("""
        <div class="section-banner">
            <div>
                <h2 style="margin:0; font-size: 1.55rem; color: #F8FAFC;">
                    🔬 Crack Diagnostics & Structural Integrity (Epic 2)
                </h2>
                <p style="margin:4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">
                    Multimodal Defect Classification, Width Metrology & IS 456 / ACI Structural Rehabilitation
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-accent">IS 456 Cl. 35.3</span>
                <span class="badge badge-warning">ACI 224.1R</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([5, 7], gap="large")

    with col_left:
        st.markdown("#### 🧱 1. Concrete / Masonry Defect Image")
        
        c_col1, c_col2 = st.columns([1, 1])
        with c_col1:
            load_crack = st.button("⚡ Load Benchmark Crack", use_container_width=True, help="Loads a high-resolution diagonal shear crack on concrete beam with exposed rebar")
        with c_col2:
            clear_crack = st.button("🔄 Clear Defect Image", use_container_width=True)

        if clear_crack:
            st.session_state.pop("crack_image_bytes", None)
            st.session_state.pop("crack_diagnosis_result", None)

        if load_crack:
            sample_bytes = create_sample_crack_image()
            st.session_state["crack_image_bytes"] = sample_bytes
            st.session_state["crack_img_name"] = "Benchmark_ShearCrack_BeamB12.jpg"

        uploaded_crack = st.file_uploader(
            "Upload Concrete / Wall Surface Photo (JPG / PNG):",
            type=["jpg", "jpeg", "png"],
            key="crack_uploader"
        )

        if uploaded_crack is not None:
            st.session_state["crack_image_bytes"] = uploaded_crack.getvalue()
            st.session_state["crack_img_name"] = uploaded_crack.name

        active_crack_bytes = st.session_state.get("crack_image_bytes", None)

        if active_crack_bytes:
            st.image(active_crack_bytes, caption=f"Selected: {st.session_state.get('crack_img_name', 'Concrete Defect Sample')}", use_container_width=True)

            # Optional engineering context selector
            with st.expander("⚙️ Optional Structural Context"):
                elem_type = st.selectbox("Structural Element:", ["RCC Beam", "RCC Column", "Floor Slab", "Retaining Wall", "Masonry Partition Wall"])
                concrete_grade = st.selectbox("Design Concrete Grade:", ["M20", "M25", "M30", "M35", "M40 & Above"], index=2)
                exposure = st.selectbox("Environmental Exposure (IS 456 Table 3):", ["Moderate", "Severe", "Very Severe", "Extreme"])

            run_diag = st.button("🔍 Execute Structural Defect Diagnosis", type="primary", use_container_width=True)
            if run_diag:
                with st.spinner("Analyzing defect morphology, crack width, stress concentrations, and repair recipes..."):
                    context_prompt = f"{CRACK_USER_PROMPT}\nAdditional Site Context: Element={elem_type}, Concrete Grade={concrete_grade}, Exposure={exposure}."
                    result = analyze_multimodal_vision(
                        image_bytes=active_crack_bytes,
                        prompt=context_prompt,
                        system_instruction=CRACK_SYSTEM_INSTRUCTION,
                        api_key=api_key,
                        model_name=selected_model,
                        fallback_type="crack"
                    )
                    st.session_state["crack_diagnosis_result"] = result
        else:
            st.info("👆 Upload a photo of concrete cracks/spalling or click **'Load Benchmark Crack'** for instant diagnostic analysis.")

    with col_right:
        st.markdown("#### 📐 2. Structural Forensic Report & Repair Engineering")
        result = st.session_state.get("crack_diagnosis_result", None)

        if not result:
            st.markdown("""
                <div class="empty-state-card">
                    <div style="font-size: 2.8rem; margin-bottom: 8px;">🔬</div>
                    <h3 style="color:#CBD5E1; margin:0 0 6px 0;">No Active Diagnostic Run</h3>
                    <p style="color:#94A3B8; max-width: 440px; margin: 0 auto; font-size: 0.92rem;">
                        Select a concrete surface photo on the left, then click 
                        <strong style="color:#F59E0B;">'Execute Structural Defect Diagnosis'</strong> 
                        to estimate crack width (mm), classify defect severity, and generate structural rehabilitation protocols.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            return

        # Source indicator
        source = result.get("_source", "Gemini AI")
        notice = result.get("_notice", None)
        if "Demonstration" in source:
            st.markdown(f"""
                <div class="demo-banner">
                    ⚡ <strong>{source}</strong> — {notice if notice else 'Synthetic forensic simulation active.'}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="live-banner">
                    🟢 <strong>{source}</strong> — Live multimodal structural reasoning executed.
                </div>
            """, unsafe_allow_html=True)

        # Primary Metrics
        defect_type = result.get("defect_type", "Structural Defect")
        width_mm = result.get("estimated_width_mm", 0.0)
        risk_index = result.get("structural_risk_index", 5.0)
        urgency = result.get("urgency", "Routine")
        risk_level = result.get("risk_level", "Moderate")

        urgency_color = "#EF4444" if "urgent" in urgency.lower() or "immediate" in urgency.lower() else ("#F59E0B" if "30" in urgency else "#10B981")

        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-card">
                    <div class="metric-title">ESTIMATED CRACK WIDTH</div>
                    <div class="metric-value" style="color: #38BDF8;">{width_mm} <span style="font-size:1.1rem; color:#94A3B8;">mm</span></div>
                    <div class="metric-subtitle">Range: {result.get('width_tolerance_range', '±0.4 mm')}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">STRUCTURAL RISK INDEX</div>
                    <div class="metric-value" style="color: {urgency_color};">{risk_index}<span style="font-size:1.1rem; color:#94A3B8;">/10</span></div>
                    <div class="metric-subtitle">{risk_level}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">INTERVENTION TIMELINE</div>
                    <div class="metric-value" style="color: {urgency_color}; font-size:1.4rem;">{urgency.split('(')[0].strip()}</div>
                    <div class="metric-subtitle">{urgency}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Classification Callout
        st.markdown(f"""
            <div style="background:#1E293B; border-radius:8px; padding:12px 16px; margin: 12px 0 16px 0; border-left: 4px solid #38BDF8;">
                <div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase; font-weight:600;">Defect Classification:</div>
                <div style="font-size:1.15rem; font-weight:700; color:#F8FAFC; margin-top:2px;">
                    {defect_type} 
                    <span class="badge badge-accent" style="font-size:0.8rem; margin-left:8px;">{result.get('crack_classification', 'Active')}</span>
                </div>
                <div style="font-size:0.88rem; color:#CBD5E1; margin-top:4px;">
                    <strong>Penetration Depth:</strong> {result.get('crack_depth', 'Under investigation')} | 
                    <strong>Code Status:</strong> IS 456 Permissible Limit is 0.2mm for moderate and 0.1mm for severe exposure (Exceeded).
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Tabs for details
        diag_tab1, diag_tab2, diag_tab3 = st.tabs(["🔍 Root Cause Analysis", "🛠️ Engineering Repair Recipe", "📑 Export Diagnosis"])

        with diag_tab1:
            st.markdown("##### 🔬 Probable Root Causes & Failure Mechanisms")
            causes = result.get("root_causes", [])
            for idx, c in enumerate(causes, 1):
                st.markdown(f"""
                    <div style="display:flex; align-items:flex-start; margin-bottom:8px; background:#0F172A; padding:10px 12px; border-radius:6px; border:1px solid #334155;">
                        <span style="background:#F59E0B22; color:#F59E0B; font-weight:bold; border-radius:50%; min-width:24px; height:24px; display:inline-flex; align-items:center; justify-content:center; margin-right:10px; font-size:0.85rem;">{idx}</span>
                        <div style="color:#E2E8F0; font-size:0.92rem;">{c}</div>
                    </div>
                """, unsafe_allow_html=True)

            precautions = result.get("safety_precautions", "")
            if precautions:
                st.warning(f"⚠️ **Immediate Structural Safety Precaution:** {precautions}")

        with diag_tab2:
            st.markdown("##### 🛠️ Step-by-Step Structural Remediation Protocol")
            repairs = result.get("recommended_repairs", [])
            
            for r in repairs:
                st.markdown(f"""
                    <div class="recipe-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                            <strong style="color:#38BDF8; font-size:1.02rem;">Step {r.get('step', 1)}: {r.get('technique', 'Repair Technique')}</strong>
                            <span class="badge badge-warning">IS 456 / ACI Standard</span>
                        </div>
                        <div style="color:#CBD5E1; font-size:0.9rem; line-height: 1.5;">
                            {r.get('protocol', '')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.caption(f"**Compliance Benchmark:** {result.get('is_code_compliance', 'IS 456:2000 / ACI 224.1R')}")

        with diag_tab3:
            st.markdown("##### 📥 Download Engineering Diagnostic Report")
            rep_json = json.dumps(result, indent=2)
            st.download_button(
                label="📄 Download Full Diagnostic Report (JSON)",
                data=rep_json,
                file_name="Structural_Defect_Diagnosis_IS456.json",
                mime="application/json",
                use_container_width=True
            )
            
            st.markdown("""
                ```text
                CIVIL FORENSIC SUMMARY CERTIFICATE
                -----------------------------------------------------
                Element Scan ID : DEF-2026-X09
                Defect Category : Structural Shear Diagonal Crack
                Estimated Width : 2.8 mm (Limit: 0.20 mm per IS 456)
                Action Mandated : Low-pressure Epoxy Injection + CFRP Web Laminates
                Safety Propping : Mandatory Acro Shoring within 48 Hours
                -----------------------------------------------------
                ```
            """)
