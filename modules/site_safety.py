"""
Module for Tab 1: Site Safety & PPE Audit (Epic 2)
Analyzes worker PPE compliance, identifies site hazards under OSHA and IS 456,
and outputs structured audit scorecards and reports.
"""

import json
import streamlit as st
import pandas as pd
from PIL import Image
import io
from modules.sample_data import create_sample_safety_image
from modules.gemini_service import analyze_multimodal_vision

SAFETY_SYSTEM_INSTRUCTION = """
You are an expert AI Construction Safety Inspector certified in OSHA 1926 Regulations and Indian Standards IS 456 / IS 3696.
Analyze the uploaded construction site photograph meticulously for PPE compliance and site safety hazards.

You must respond with ONLY valid JSON adhering strictly to this schema:
{
    "safety_score": <integer from 0 to 100>,
    "overall_status": "<Compliant | Minor Infractions | Critical Safety Risk>",
    "worker_count": <estimated integer number of workers in frame>,
    "compliance_grade": "<A | B | C | D | F>",
    "ppe_detection": {
        "helmets": {
            "status": "<Fully Compliant | Partial Compliance | Missing | Not Visible>",
            "detected_count": <int>,
            "missing_count": <int>,
            "confidence": <float 0.0 to 1.0>,
            "standard_ref": "IS 2925 / OSHA 1926.100"
        },
        "high_vis_vests": {
            "status": "<Fully Compliant | Partial Compliance | Missing | Not Visible>",
            "detected_count": <int>,
            "missing_count": <int>,
            "confidence": <float 0.0 to 1.0>,
            "standard_ref": "EN ISO 20471 / OSHA 1926.201"
        },
        "steel_toe_boots": {
            "status": "<Fully Compliant | Partial Compliance | Missing | Not Visible>",
            "detected_count": <int>,
            "missing_count": <int>,
            "confidence": <float 0.0 to 1.0>,
            "standard_ref": "IS 15298 / ASTM F2413"
        },
        "safety_harnesses": {
            "status": "<Fully Compliant | Partial Compliance | CRITICAL VIOLATION | Not Applicable>",
            "detected_count": <int>,
            "missing_count": <int>,
            "confidence": <float 0.0 to 1.0>,
            "standard_ref": "IS 3521 / OSHA 1926.502"
        },
        "eye_face_protection": {
            "status": "<Fully Compliant | Partial Compliance | Missing | Not Applicable>",
            "detected_count": <int>,
            "missing_count": <int>,
            "confidence": <float 0.0 to 1.0>,
            "standard_ref": "IS 5983 / OSHA 1926.102"
        }
    },
    "identified_hazards": [
        {
            "id": "HAZ-001",
            "hazard": "<Short hazard name>",
            "location_in_frame": "<Specific area in photo>",
            "severity": "<Low | Medium | High | Critical>",
            "osha_is_violation_reference": "<Code reference e.g. OSHA 1926.501 or IS 3696>",
            "description": "<Detailed explanation of unsafe condition>",
            "corrective_remedy": "<Mandatory engineering and administrative fix>"
        }
    ],
    "osha_summary": "<Executive summary of findings and site supervisor action item>"
}
"""

SAFETY_USER_PROMPT = """
Perform an exhaustive multimodal safety audit of this construction scene.
Audit each worker for helmets, high-visibility clothing, safety harnesses (especially if at elevation >2m), and protective footwear.
Inspect scaffolds, crane swing radius, exposed edges, and electrical drops under OSHA and IS 456 rules.
Return purely the requested JSON structure.
"""

def render_site_safety_tab(api_key: str, selected_model: str):
    """Renders the complete Site Safety & PPE Audit view."""
    st.markdown("""
        <div class="section-banner">
            <div>
                <h2 style="margin:0; font-size: 1.55rem; color: #F8FAFC;">
                    🦺 Site Safety & PPE Multimodal Audit (Epic 2)
                </h2>
                <p style="margin:4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">
                    AI Computer Vision Compliance Engine for OSHA 1926 & Indian Standards IS 456 / IS 3696
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-accent">OSHA 1926.501</span>
                <span class="badge badge-warning">IS 3696 Scaffolding</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([5, 7], gap="large")

    with col_left:
        st.markdown("#### 📸 1. Capture or Select Site Imagery")
        
        # Action bar with Sample loader
        sample_col1, sample_col2 = st.columns([1, 1])
        with sample_col1:
            load_sample = st.button("⚡ Load Benchmark Sample", use_container_width=True, help="Loads a high-resolution simulated elevated work zone with scaffolding and PPE infraction")
        with sample_col2:
            clear_img = st.button("🔄 Clear Active Image", use_container_width=True)

        if clear_img:
            st.session_state.pop("safety_image_bytes", None)
            st.session_state.pop("safety_audit_result", None)

        if load_sample:
            sample_bytes = create_sample_safety_image()
            st.session_state["safety_image_bytes"] = sample_bytes
            st.session_state["safety_img_name"] = "Benchmark_Scaffolding_FallHazard_Cam04.jpg"

        uploaded_file = st.file_uploader(
            "Upload Construction Site Image (JPG / PNG):",
            type=["jpg", "jpeg", "png"],
            key="safety_uploader"
        )

        if uploaded_file is not None:
            st.session_state["safety_image_bytes"] = uploaded_file.getvalue()
            st.session_state["safety_img_name"] = uploaded_file.name

        active_img_bytes = st.session_state.get("safety_image_bytes", None)

        if active_img_bytes:
            st.image(active_img_bytes, caption=f"Selected: {st.session_state.get('safety_img_name', 'Active Site Image')}", use_container_width=True)
            
            run_audit = st.button("🔍 Execute Multimodal Safety Audit", type="primary", use_container_width=True)
            if run_audit:
                with st.spinner("Analyzing site hazards, PPE compliance, and OSHA/IS code violations..."):
                    result = analyze_multimodal_vision(
                        image_bytes=active_img_bytes,
                        prompt=SAFETY_USER_PROMPT,
                        system_instruction=SAFETY_SYSTEM_INSTRUCTION,
                        api_key=api_key,
                        model_name=selected_model,
                        fallback_type="safety"
                    )
                    st.session_state["safety_audit_result"] = result
        else:
            st.info("👆 Please upload a construction site photo or click **'Load Benchmark Sample'** to test immediately.")

    with col_right:
        st.markdown("#### 📊 2. Safety Audit Scorecard & Analytics")
        result = st.session_state.get("safety_audit_result", None)

        if not result:
            st.markdown("""
                <div class="empty-state-card">
                    <div style="font-size: 2.8rem; margin-bottom: 8px;">🛡️</div>
                    <h3 style="color:#CBD5E1; margin:0 0 6px 0;">No Active Audit Logged</h3>
                    <p style="color:#94A3B8; max-width: 440px; margin: 0 auto; font-size: 0.92rem;">
                        Upload an image or load the benchmark sample on the left, then click 
                        <strong style="color:#F59E0B;">'Execute Multimodal Safety Audit'</strong> 
                        to extract real-time safety scores, PPE checklists, and IS 456 / OSHA corrective actions.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            return

        # Display source banner
        source = result.get("_source", "Gemini AI")
        notice = result.get("_notice", None)
        if "Demonstration" in source:
            st.markdown(f"""
                <div class="demo-banner">
                    ⚡ <strong>{source}</strong> — {notice if notice else 'Synthetic simulation active.'}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="live-banner">
                    🟢 <strong>{source}</strong> — Live multimodal visual reasoning executed.
                </div>
            """, unsafe_allow_html=True)

        # Top Metric Cards
        score = result.get("safety_score", 70)
        grade = result.get("compliance_grade", "B")
        status = result.get("overall_status", "Audited")
        workers = result.get("worker_count", 0)
        hazards = result.get("identified_hazards", [])
        critical_hazards = sum(1 for h in hazards if h.get("severity", "").lower() == "critical")

        # Color based on score
        score_color = "#10B981" if score >= 80 else ("#F59E0B" if score >= 60 else "#EF4444")

        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-card">
                    <div class="metric-title">SAFETY COMPLIANCE SCORE</div>
                    <div class="metric-value" style="color: {score_color};">{score}<span style="font-size:1.2rem; color:#94A3B8;">/100</span></div>
                    <div class="metric-subtitle">Grade: <strong style="color:#F8FAFC;">{grade}</strong> | Standard: OSHA 1926</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">WORKERS DETECTED</div>
                    <div class="metric-value" style="color: #38BDF8;">{workers}</div>
                    <div class="metric-subtitle">Active In-Frame Personnel</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">CRITICAL HAZARDS</div>
                    <div class="metric-value" style="color: {'#EF4444' if critical_hazards > 0 else '#10B981'};">{critical_hazards}</div>
                    <div class="metric-subtitle">Immediate Work-Stoppage Risks</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Overall Status Pill
        pill_class = "badge-danger" if "critical" in status.lower() or score < 60 else ("badge-warning" if "infraction" in status.lower() or score < 80 else "badge-success")
        st.markdown(f"""
            <div style="margin: 12px 0 18px 0; padding: 10px 14px; background: #1E293B; border-radius: 8px; border-left: 4px solid {score_color};">
                <span style="color:#94A3B8; font-size: 0.85rem; text-transform: uppercase; font-weight:600;">Overall Site Posture:</span>
                <span class="badge {pill_class}" style="font-size:0.9rem; margin-left: 8px;">{status}</span>
            </div>
        """, unsafe_allow_html=True)

        # Tabs for details
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["📋 PPE Checklist", "⚠️ Identified Hazards", "📄 Export & Code References"])

        with sub_tab1:
            st.markdown("##### 👷 Personal Protective Equipment (PPE) Compliance Matrix")
            ppe_data = result.get("ppe_detection", {})
            
            ppe_rows = []
            for item_name, details in ppe_data.items():
                label = item_name.replace("_", " ").title()
                st_val = details.get("status", "N/A")
                conf = details.get("confidence", 0.0)
                std = details.get("standard_ref", "OSHA / IS")
                det = details.get("detected_count", 0)
                miss = details.get("missing_count", 0)
                
                # Badge format
                if "compliant" in st_val.lower() and "partial" not in st_val.lower():
                    status_badge = "🟢 Compliant"
                elif "critical" in st_val.lower() or "missing" in st_val.lower():
                    status_badge = "🔴 Violation / Missing"
                elif "partial" in st_val.lower():
                    status_badge = "🟡 Partial"
                else:
                    status_badge = f"⚪ {st_val}"

                ppe_rows.append({
                    "PPE Equipment": label,
                    "Status": status_badge,
                    "Detected": det,
                    "Missing": miss,
                    "Confidence": f"{int(conf * 100)}%",
                    "Regulatory Standard": std
                })
            
            if ppe_rows:
                df_ppe = pd.DataFrame(ppe_rows)
                st.dataframe(df_ppe, use_container_width=True, hide_index=True)
            else:
                st.write("No specific PPE items reported.")

        with sub_tab2:
            st.markdown("##### ⚠️ Site Hazards & Corrective Engineering Remedies")
            hazards_list = result.get("identified_hazards", [])
            
            if not hazards_list:
                st.success("🎉 Zero critical hazards detected in this camera viewpoint.")
            else:
                for h in hazards_list:
                    sev = h.get("severity", "Medium")
                    sev_color = {
                        "critical": "#EF4444",
                        "high": "#F97316",
                        "medium": "#F59E0B",
                        "low": "#38BDF8"
                    }.get(sev.lower(), "#94A3B8")

                    st.markdown(f"""
                        <div class="hazard-card" style="border-left-color: {sev_color};">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                                <strong style="font-size:1.05rem; color:#F8FAFC;">{h.get('hazard', 'Unspecified Hazard')}</strong>
                                <span class="badge" style="background:{sev_color}22; color:{sev_color}; border:1px solid {sev_color}88;">
                                    {sev.upper()} SEVERITY
                                </span>
                            </div>
                            <div style="font-size: 0.88rem; color: #94A3B8; margin-bottom: 4px;">
                                📍 <strong>Location:</strong> {h.get('location_in_frame', 'General Scene')} | 
                                ⚖️ <strong>Code Reference:</strong> <span style="color:#F59E0B;">{h.get('osha_is_violation_reference', 'OSHA 1926')}</span>
                            </div>
                            <div style="font-size: 0.92rem; color: #E2E8F0; margin-bottom: 8px;">
                                {h.get('description', '')}
                            </div>
                            <div style="background:#0F172A; padding:8px 12px; border-radius:6px; font-size:0.88rem; border:1px dashed #475569;">
                                🛠️ <strong style="color:#38BDF8;">Mandatory Corrective Action:</strong> {h.get('corrective_remedy', 'Immediate site supervisor intervention.')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        with sub_tab3:
            st.markdown("##### 📜 Executive Summary & Audit Export")
            summary_text = result.get("osha_summary", "Site audit completed under OSHA 1926.")
            st.info(f"**Supervisor Summary:** {summary_text}")

            export_col1, export_col2 = st.columns([1, 1])
            with export_col1:
                json_str = json.dumps(result, indent=2)
                st.download_button(
                    label="📥 Download JSON Audit Report",
                    data=json_str,
                    file_name="Construction_Safety_Audit_OSHA_IS456.json",
                    mime="application/json",
                    use_container_width=True
                )
            with export_col2:
                # Flat CSV export for supervisor log
                csv_rows = []
                for h in hazards_list:
                    csv_rows.append({
                        "Hazard_ID": h.get("id", ""),
                        "Hazard_Name": h.get("hazard", ""),
                        "Severity": h.get("severity", ""),
                        "Location": h.get("location_in_frame", ""),
                        "Standard_Violation": h.get("osha_is_violation_reference", ""),
                        "Remedy": h.get("corrective_remedy", "")
                    })
                df_export = pd.DataFrame(csv_rows)
                st.download_button(
                    label="📊 Download CSV Incident Log",
                    data=df_export.to_csv(index=False),
                    file_name="Hazard_Log_Sheet.csv",
                    mime="text/csv",
                    use_container_width=True
                )
