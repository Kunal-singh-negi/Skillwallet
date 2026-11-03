"""
Module for Tab 3: Planning & Real Estate Valuation (Epic 3)
Calculates project budgets, CapEx incurred, current market valuations in INR (Lakhs/Crores),
material structural requirements (Steel MT, Cement Bags), milestone progress,
and integrates conceptual 3D architectural rendering via Pollinations AI.
"""

import urllib.parse
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.sample_data import CITY_TIER_DATA, STRUCTURE_TYPE_MULTIPLIERS, QUALITY_GRADE_MULTIPLIER

def format_inr(amount_in_rupees: float) -> str:
    """Formats numeric rupees into Lakhs or Crores."""
    if amount_in_rupees >= 10000000:
        crores = amount_in_rupees / 10000000.0
        return f"₹ {crores:.2f} Cr"
    elif amount_in_rupees >= 100000:
        lakhs = amount_in_rupees / 100000.0
        return f"₹ {lakhs:.2f} L"
    else:
        return f"₹ {amount_in_rupees:,.0f}"

def render_real_estate_valuation_tab():
    """Renders the Planning, Valuation & 3D Architectural Render view."""
    st.markdown("""
        <div class="section-banner">
            <div>
                <h2 style="margin:0; font-size: 1.55rem; color: #F8FAFC;">
                    🏛️ Planning & Real Estate Valuation (Epic 3)
                </h2>
                <p style="margin:4px 0 0 0; color: #94A3B8; font-size: 0.95rem;">
                    BIM Budget Forecasting, CapEx Run-Rate, Steel/Cement Metrics & 3D AI Architectural Synthesis
                </p>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-accent">Indian RERA Compliant</span>
                <span class="badge badge-warning">Pollinations 3D Render</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Interactive Inputs Layout
    st.markdown("#### ⚙️ 1. Project Specifications & Construction Parameters")
    
    col_input1, col_input2, col_input3, col_input4 = st.columns([3, 3, 3, 3], gap="medium")

    with col_input1:
        structure_type = st.selectbox(
            "Structure Typology:",
            list(STRUCTURE_TYPE_MULTIPLIERS.keys()),
            index=0,
            help="Select building functional typology to apply structural steel and concrete density indices"
        )
    
    with col_input2:
        tier_choice = st.selectbox(
            "Geographic Location Tier:",
            list(CITY_TIER_DATA.keys()),
            index=0,
            help="Defines base civil labor index, material transportation logistics, and local market sales realization"
        )
        cities_in_tier = CITY_TIER_DATA[tier_choice]["cities"]
        selected_city = st.selectbox("Benchmark City:", cities_in_tier, index=0)

    with col_input3:
        quality_grade = st.selectbox(
            "Specification / Quality Grade:",
            list(QUALITY_GRADE_MULTIPLIER.keys()),
            index=1,
            help="Select civil finishing grade, MEP redundancy, and LEED sustainability standards"
        )

    with col_input4:
        built_up_sqft = st.number_input(
            "Built-Up Area (Sq.Ft):",
            min_value=5000,
            max_value=2500000,
            value=85000,
            step=5000,
            help="Total gross permissible constructed area"
        )

    # Completion slider with milestone markers
    st.markdown("##### ⏱️ Construction Milestone Completion")
    completion_pct = st.slider(
        "Current Site Work Completion (%):",
        min_value=0,
        max_value=100,
        value=55,
        step=5,
        format="%d%%"
    )

    # Determine current milestone phase name
    if completion_pct < 15:
        milestone_phase = "Substructure: Excavation, Piling & Raft Foundation"
    elif completion_pct < 45:
        milestone_phase = "RCC Superstructure: Shear Walls & Floor Slabs Casting"
    elif completion_pct < 75:
        milestone_phase = "Enclosure & MEP: Blockwork, Conduit Piping & Glazing"
    elif completion_pct < 95:
        milestone_phase = "Finishing: Flooring, False Ceilings, Lift Installation & Painting"
    else:
        milestone_phase = "Commissioning & Handover: Snagging, Testing & Occupancy Certificate"

    st.markdown(f"""
        <div style="background:#1E293B; border-radius:8px; padding:10px 16px; margin-bottom: 20px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="color:#94A3B8; font-size:0.85rem;">Active Milestone Phase:</span>
                <strong style="color:#38BDF8; margin-left:6px; font-size:0.95rem;">{milestone_phase}</strong>
            </div>
            <div>
                <span class="badge badge-accent">{completion_pct}% Progress Incurred</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. Engineering Calculations
    tier_info = CITY_TIER_DATA[tier_choice]
    struct_info = STRUCTURE_TYPE_MULTIPLIERS[structure_type]
    grade_mult = QUALITY_GRADE_MULTIPLIER[quality_grade]

    # Civil construction cost per sqft
    unit_cost_sqft = tier_info["base_civil_cost_sqft"] * struct_info["cost_multiplier"] * grade_mult
    total_budget_inr = unit_cost_sqft * built_up_sqft
    capex_incurred_inr = total_budget_inr * (completion_pct / 100.0)
    balance_to_complete_inr = total_budget_inr - capex_incurred_inr

    # Real Estate Market Valuation
    base_market_rate_sqft = tier_info["base_market_rate_sqft"] * grade_mult
    finished_market_valuation_inr = base_market_rate_sqft * built_up_sqft
    # Current WIP Valuation accounts for work done + land value + partial appreciation
    land_equity_component = finished_market_valuation_inr * 0.35  # ~35% base land value
    construction_value_added = (finished_market_valuation_inr * 0.65) * (completion_pct / 100.0)
    current_asset_valuation_inr = land_equity_component + construction_value_added

    # Material Requirement Calculations
    steel_mt = (built_up_sqft * struct_info["steel_kg_per_sqft"]) / 1000.0
    cement_bags = built_up_sqft * struct_info["cement_bags_per_sqft"]
    sand_mt = (built_up_sqft * struct_info["sand_cft_per_sqft"] * 45) / 1000.0 # 45 kg/cft approx
    aggregate_mt = (built_up_sqft * struct_info["aggregate_cft_per_sqft"] * 48) / 1000.0

    # 3. Financial Metric Cards
    st.markdown("#### 💰 2. Financial Budget & Current Asset Valuation")
    
    m_col1, m_col2, m_col3, m_col4 = st.columns([3, 3, 3, 3], gap="medium")
    
    with m_col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">TOTAL PROJECT BUDGET</div>
                <div class="metric-value" style="color:#F8FAFC;">{format_inr(total_budget_inr)}</div>
                <div class="metric-subtitle">₹ {unit_cost_sqft:,.0f} / Sq.Ft Civil Cost</div>
            </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">CAPEX INCURRED (WIP)</div>
                <div class="metric-value" style="color:#38BDF8;">{format_inr(capex_incurred_inr)}</div>
                <div class="metric-subtitle">{completion_pct}% of Planned Outflow</div>
            </div>
        """, unsafe_allow_html=True)

    with m_col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">CURRENT ASSET VALUATION</div>
                <div class="metric-value" style="color:#10B981;">{format_inr(current_asset_valuation_inr)}</div>
                <div class="metric-subtitle">WIP Value ({selected_city})</div>
            </div>
        """, unsafe_allow_html=True)

    with m_col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">PROJECTED FINISHED VALUE</div>
                <div class="metric-value" style="color:#F59E0B;">{format_inr(finished_market_valuation_inr)}</div>
                <div class="metric-subtitle">₹ {base_market_rate_sqft:,.0f} / Sq.Ft Realization</div>
            </div>
        """, unsafe_allow_html=True)

    # Tabs for Materials & AI Render
    plan_tab1, plan_tab2 = st.tabs(["🏗️ Structural Bill of Quantities (BOQ)", "🎨 Conceptual 3D Architectural AI Render"])

    with plan_tab1:
        st.markdown("##### 📦 Primary Structural Material Forecast")
        mat_col1, mat_col2, mat_col3, mat_col4 = st.columns(4)
        
        with mat_col1:
            st.metric("Reinforcement TMT Steel", f"{steel_mt:,.1f} MT", delta=f"{struct_info['steel_kg_per_sqft']} kg/sqft")
        with mat_col2:
            st.metric("Cement Required", f"{cement_bags:,.0f} Bags", delta=f"{cement_bags/20:,.0f} MT (50kg bags)")
        with mat_col3:
            st.metric("M-Sand / Fine Aggregate", f"{sand_mt:,.0f} MT", delta=f"{struct_info['sand_cft_per_sqft']} cft/sqft")
        with mat_col4:
            st.metric("Coarse Aggregate (10/20mm)", f"{aggregate_mt:,.0f} MT", delta=f"{struct_info['aggregate_cft_per_sqft']} cft/sqft")

        # Interactive Budget Breakdown Donut Chart
        breakdown_col1, breakdown_col2 = st.columns([6, 6])
        
        with breakdown_col1:
            st.markdown("###### 📊 Cost Head Distribution")
            cost_labels = ["RCC Structure & Core", "Finishes & Glazing", "MEP & Firefighting", "External Development", "Contingency & Approvals"]
            cost_values = [
                total_budget_inr * 0.44,
                total_budget_inr * 0.22,
                total_budget_inr * 0.18,
                total_budget_inr * 0.09,
                total_budget_inr * 0.07
            ]
            fig = px.pie(
                names=cost_labels,
                values=cost_values,
                hole=0.45,
                color_discrete_sequence=["#F59E0B", "#38BDF8", "#10B981", "#818CF8", "#F43F5E"]
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#F8FAFC"},
                margin=dict(l=20, r=20, t=20, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

        with breakdown_col2:
            st.markdown("###### 📈 CapEx Deployment vs Residual Balance")
            balance_labels = ["CapEx Incurred (Paid)", "Balance Commitment to Complete"]
            balance_values = [capex_incurred_inr, balance_to_complete_inr]
            fig_bar = px.bar(
                x=balance_labels,
                y=balance_values,
                color=balance_labels,
                color_discrete_map={
                    "CapEx Incurred (Paid)": "#38BDF8",
                    "Balance Commitment to Complete": "#F59E0B"
                },
                labels={"x": "", "y": "Amount in INR"}
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": "#F8FAFC"},
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with plan_tab2:
        st.markdown("##### 🏛️ Conceptual 3D Architectural AI Rendering via Pollinations AI")
        st.markdown("""
            Automatically synthesizes a hyper-realistic architectural exterior visual based on your project typology,
            urban context, structural materials, and current construction progress stage.
        """)

        r_col1, r_col2 = st.columns([4, 8])

        with r_col1:
            arch_style = st.selectbox(
                "Architectural Design Style:",
                [
                    "Modern Minimalist Glass & Steel Facade",
                    "Biophilic Sustainable Green BIM Tower with Vertical Gardens",
                    "Brutalist Architectural Concrete & Geometric Louvers",
                    "Neo-Classical Luxury Podium with Cascading Terraces",
                    "Futuristic Aerodynamic Parametric Architecture"
                ]
            )

            lighting_mood = st.selectbox(
                "Lighting & Atmosphere:",
                ["Golden Hour Sunset Lighting", "Crisp Daylight Architectural Photography", "Blue Hour Twilight with Illuminated Interiors", "Overcast Soft Diffused Light"]
            )

            extra_keywords = st.text_input("Custom Design Keywords:", value="8k photorealistic, hyper-detailed facade, architectural digest")

            # Construct prompt for Pollinations
            stage_descriptor = f"{completion_pct}% complete construction with structural framing and sleek finishes" if completion_pct < 90 else "fully completed grand exterior architectural reveal"
            
            raw_prompt = (
                f"Award-winning architectural photograph of a {structure_type} in {selected_city}, "
                f"built-up {built_up_sqft:,} sqft, style {arch_style}, {stage_descriptor}, "
                f"{lighting_mood}, {extra_keywords}, unreal engine 5 architectural render, hyper-detailed, masterpiece"
            )

            st.text_area("Generated AI Prompt:", value=raw_prompt, height=100, key="prompt_display")

            gen_render = st.button("✨ Synthesize Conceptual 3D Render", type="primary", use_container_width=True)

        with r_col2:
            encoded_prompt = urllib.parse.quote(raw_prompt)
            # Default or active image URL
            pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=500&seed=42&nologo=true"

            if gen_render or st.session_state.get("has_rendered_pollinations", False):
                st.session_state["has_rendered_pollinations"] = True
                with st.spinner("Streaming conceptual render from Pollinations AI Engine..."):
                    st.image(
                        pollinations_url,
                        caption=f"Conceptual 3D AI Render: {structure_type} ({selected_city}) - {arch_style}",
                        use_container_width=True
                    )
                    st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                            <span style="font-size:0.85rem; color:#94A3B8;">Powered by Pollinations AI Neural Generator</span>
                            <a href="{pollinations_url}" target="_blank" style="text-decoration:none;">
                                <button style="background:#F59E0B; color:#0F172A; border:none; padding:6px 14px; border-radius:6px; font-weight:600; cursor:pointer;">
                                    🔗 Open Full-Resolution Image
                                </button>
                            </a>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="empty-state-card" style="padding: 40px 20px;">
                        <div style="font-size: 2.5rem; margin-bottom: 6px;">🏙️</div>
                        <h4 style="color:#CBD5E1; margin:0 0 6px 0;">3D AI Render Ready to Generate</h4>
                        <p style="color:#94A3B8; font-size: 0.9rem; margin-bottom: 12px;">
                            Click <strong style="color:#F59E0B;">'Synthesize Conceptual 3D Render'</strong> 
                            to call the Pollinations AI generator and view photorealistic architectural visualization.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
