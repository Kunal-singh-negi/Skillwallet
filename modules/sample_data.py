"""
Sample data, synthetic image generators, and mock engineering benchmarks
for the Multimodal Construction Intelligence Platform.
"""

import io
from PIL import Image, ImageDraw, ImageFont

# -------------------------------------------------------------------------
# Synthetic Image Generation (Ensures offline testability without external assets)
# -------------------------------------------------------------------------

def create_sample_safety_image() -> bytes:
    """
    Generates a realistic construction site diagram image depicting:
    - Scaffolding structure
    - Workers with high-vis vests and helmets
    - A worker at height missing a safety harness (OSHA violation)
    - Warning signage and hazard boundary
    """
    width, height = 800, 500
    img = Image.new("RGB", (width, height), color="#1E293B")
    draw = ImageDraw.Draw(img)

    # Sky gradient / background
    for y in range(250):
        r = int(15 + (y / 250) * 15)
        g = int(23 + (y / 250) * 20)
        b = int(42 + (y / 250) * 30)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Ground slab (concrete)
    draw.rectangle([0, 380, width, height], fill="#334155")
    # Ground lines
    for i in range(0, width, 40):
        draw.line([(i, 380), (i + 20, height)], fill="#475569", width=2)

    # Background Crane
    draw.line([(680, 50), (680, 380)], fill="#F59E0B", width=6)  # Mast
    draw.line([(550, 80), (780, 80)], fill="#F59E0B", width=4)   # Jib
    draw.line([(680, 50), (550, 80)], fill="#D97706", width=2)   # Cables
    draw.line([(680, 50), (780, 80)], fill="#D97706", width=2)
    draw.line([(620, 80), (620, 180)], fill="#94A3B8", width=2)  # Hoist cable
    draw.rectangle([615, 180, 625, 195], fill="#E2E8F0")         # Hook/load

    # Multi-tier Scaffolding (Left to Center)
    scaff_color = "#94A3B8"
    for x in [80, 180, 280, 380]:
        draw.line([(x, 100), (x, 380)], fill=scaff_color, width=4)
    # Platforms
    for y in [180, 260, 340]:
        draw.rectangle([70, y, 390, y + 8], fill="#64748B")
        # Diagonal bracings
        draw.line([(80, y - 80 if y > 180 else 100), (180, y)], fill="#475569", width=2)
        draw.line([(180, y), (280, y - 80 if y > 180 else 100)], fill="#475569", width=2)
        draw.line([(280, y), (380, y - 80 if y > 180 else 100)], fill="#475569", width=2)

    # Worker 1: On ground slab (Compliant: Hard Hat, High-Vis Vest, Steel-toe boots)
    # Head & Helmet
    draw.ellipse([450, 310, 470, 330], fill="#FFD166") # Helmet (Yellow)
    draw.ellipse([453, 317, 467, 331], fill="#D4A373") # Face
    # Body (High Vis Vest Orange)
    draw.rectangle([448, 331, 472, 360], fill="#FF6B35")
    draw.line([(453, 333), (453, 360)], fill="#E2E8F0", width=2) # Reflective strip
    draw.line([(467, 333), (467, 360)], fill="#E2E8F0", width=2)
    # Legs / Boots
    draw.line([(454, 360), (454, 385)], fill="#1E293B", width=4)
    draw.line([(466, 360), (466, 385)], fill="#1E293B", width=4)
    draw.rectangle([450, 382, 458, 388], fill="#3F2E21") # Steel-toe boot
    draw.rectangle([462, 382, 470, 388], fill="#3F2E21")

    # Worker 2: At height on 2nd platform (VIOLATION: No Safety Harness, Missing Mid-rail)
    # Location: x=220, y=140
    draw.ellipse([215, 130, 235, 150], fill="#FFFFFF") # White supervisor helmet
    draw.ellipse([218, 137, 232, 151], fill="#D4A373") # Face
    draw.rectangle([213, 150, 237, 175], fill="#10B981") # Green vest
    draw.line([(218, 175), (218, 180)], fill="#1E293B", width=3)
    draw.line([(232, 175), (232, 180)], fill="#1E293B", width=3)

    # Red Warning Box around Worker 2 (Hazard Hotspot)
    draw.rectangle([200, 120, 250, 185], outline="#EF4444", width=3)
    draw.text((205, 102), "HAZARD: NO HARNESS", fill="#EF4444")

    # Hazard tape / barricade
    for i in range(410, 520, 15):
        draw.polygon([(i, 370), (i + 10, 370), (i + 5, 378), (i - 5, 378)], fill="#F59E0B")

    # Title stamp overlay
    draw.rectangle([20, 20, 340, 70], fill="#0F172A")
    draw.rectangle([20, 20, 340, 70], outline="#38BDF8", width=1)
    draw.text((30, 28), "SITE CCTV CAM #04 - SECTOR 7B", fill="#38BDF8")
    draw.text((30, 48), "ELEVATION WORK ZONE | IS 456 & OSHA", fill="#94A3B8")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def create_sample_crack_image() -> bytes:
    """
    Generates a realistic concrete surface image depicting:
    - Reinforced concrete beam surface
    - Structural diagonal shear crack (2.5mm - 3.2mm width)
    - Concrete spalling exposing reinforcement rebar
    - Measurement gauge overlay
    """
    width, height = 750, 500
    img = Image.new("RGB", (width, height), color="#64748B")
    draw = ImageDraw.Draw(img)

    # Concrete texture / noise
    import random
    rng = random.Random(42)
    for _ in range(3000):
        px = rng.randint(0, width - 1)
        py = rng.randint(0, height - 1)
        gray = rng.randint(80, 140)
        draw.point((px, py), fill=(gray, gray, gray + 5))

    # Concrete formwork joint
    draw.line([(0, 150), (width, 150)], fill="#475569", width=2)
    draw.line([(0, 350), (width, 350)], fill="#475569", width=2)

    # Main Structural Shear Crack (Diagonal 45-degree angle, severe)
    crack_coords = [
        (150, 80), (190, 120), (240, 160), (280, 210),
        (330, 250), (370, 290), (430, 340), (490, 390), (550, 440)
    ]
    for i in range(len(crack_coords) - 1):
        p1 = crack_coords[i]
        p2 = crack_coords[i + 1]
        # Main crack line
        draw.line([p1, p2], fill="#0F172A", width=5)
        # Secondary micro-fissures branching off
        mid_x = (p1[0] + p2[0]) // 2
        mid_y = (p1[1] + p2[1]) // 2
        draw.line([(mid_x, mid_y), (mid_x + 18, mid_y - 12)], fill="#1E293B", width=2)
        draw.line([(mid_x, mid_y), (mid_x - 14, mid_y + 16)], fill="#1E293B", width=2)

    # Concrete Spalling zone with exposed rebar
    spall_box = [320, 230, 410, 310]
    draw.ellipse(spall_box, fill="#334155")
    # Exposed rebar (rusty ribbed steel bar)
    draw.line([(335, 270), (395, 270)], fill="#9A3412", width=8)
    draw.line([(335, 270), (395, 270)], fill="#EA580C", width=4)
    # Rebar ribs
    for rx in range(340, 395, 8):
        draw.line([(rx, 266), (rx, 274)], fill="#431407", width=2)

    # Crack measurement gauge / ruler marker
    draw.rectangle([250, 175, 290, 195], fill="#FEF08A", outline="#CA8A04")
    draw.text((254, 179), "2.8 mm", fill="#854D0E")

    # Diagnostic Overlay Banner
    draw.rectangle([20, 20, 370, 75], fill="#0F172A")
    draw.rectangle([20, 20, 370, 75], outline="#EF4444", width=2)
    draw.text((30, 28), "STRUCTURAL DEFECT SCAN #CRK-089", fill="#F87171")
    draw.text((30, 48), "ELEMENT: BEAM B-12 | SPAN: 6.2m | GRADE: M30", fill="#CBD5E1")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


# -------------------------------------------------------------------------
# Fallback / Demonstration Structured AI Results
# -------------------------------------------------------------------------

DEMO_SAFETY_AUDIT_RESULT = {
    "safety_score": 68,
    "overall_status": "Major Infractions Detected (OSHA / IS 456 Review Required)",
    "worker_count": 2,
    "compliance_grade": "C+",
    "ppe_detection": {
        "helmets": {
            "status": "Partial Compliance",
            "detected_count": 2,
            "missing_count": 0,
            "confidence": 0.96,
            "standard_ref": "IS 2925 / OSHA 1926.100"
        },
        "high_vis_vests": {
            "status": "Fully Compliant",
            "detected_count": 2,
            "missing_count": 0,
            "confidence": 0.98,
            "standard_ref": "EN ISO 20471 / OSHA 1926.201"
        },
        "steel_toe_boots": {
            "status": "Partial Compliance",
            "detected_count": 1,
            "missing_count": 1,
            "confidence": 0.89,
            "standard_ref": "IS 15298 / ASTM F2413"
        },
        "safety_harnesses": {
            "status": "CRITICAL VIOLATION",
            "detected_count": 0,
            "missing_count": 1,
            "confidence": 0.94,
            "standard_ref": "IS 3521 / OSHA 1926.502"
        },
        "eye_face_protection": {
            "status": "Missing",
            "detected_count": 0,
            "missing_count": 2,
            "confidence": 0.85,
            "standard_ref": "IS 5983 / OSHA 1926.102"
        }
    },
    "identified_hazards": [
        {
            "id": "HAZ-001",
            "hazard": "Fall Hazard at Elevated Platform (>2.0m)",
            "location_in_frame": "Upper Scaffolding Tier (Level 2, Platform Deck)",
            "severity": "Critical",
            "osha_is_violation_reference": "OSHA 1926.501(b)(1) & IS 3696 (Part 1)",
            "description": "Worker observed standing on un-tethered scaffolding tier without fall arrest harness or secure double-lanyard anchor point.",
            "corrective_remedy": "Immediately halt work at height. Issue Class A full-body safety harness tethered to an independent static lifeline (min 22.2 kN tensile strength)."
        },
        {
            "id": "HAZ-002",
            "hazard": "Missing Guardrail & Toe-board on Scaffolding Edge",
            "location_in_frame": "Platform Outboard Edge (x=210 to x=280)",
            "severity": "High",
            "osha_is_violation_reference": "OSHA 1926.451(g)(1) & IS 2750",
            "description": "Scaffold working platform lacks top-rail (105cm height) and 15cm toe-board to prevent material tool drops.",
            "corrective_remedy": "Erect certified guardrails consisting of top-rail, mid-rail, and toe-boards prior to any personnel accessing the platform."
        },
        {
            "id": "HAZ-003",
            "hazard": "Improper Danger Zone Barricading Below Crane Jib",
            "location_in_frame": "Ground Slab Zone below Crane radius",
            "severity": "Medium",
            "osha_is_violation_reference": "OSHA 1926.1424 & IS 13367 (Crane Safety)",
            "description": "Pedestrian pathway not fully cordoned off beneath mobile crane slewing perimeter.",
            "corrective_remedy": "Deploy high-contrast barricade tape, install overhead catch nets, and station a dedicated rigger/flagman."
        }
    ],
    "osha_summary": "Violations logged under Subpart M (Fall Protection) and Subpart L (Scaffolds). Mandatory re-induction required for sub-contractor crew before resuming shift."
}

DEMO_CRACK_DIAGNOSIS_RESULT = {
    "defect_type": "Structural Shear Diagonal Crack with Spalling",
    "crack_classification": "Active Structural Shear",
    "estimated_width_mm": 2.8,
    "width_tolerance_range": "2.5 mm - 3.2 mm",
    "crack_depth": "Deep (Penetrating concrete cover reaching tensile reinforcement)",
    "structural_risk_index": 8.5,
    "risk_level": "High / Urgent Risk",
    "urgency": "Urgent (Intervene within 48 hours)",
    "root_causes": [
        "Diagonal tensile stress exceeding concrete shear strength under flexural load (IS 456 Clause 40)",
        "Inadequate or corroded stirrup reinforcement spacing at high-shear zone near beam support",
        "Carbonation and chloride ingress causing rebar oxidation and subsequent concrete cover spalling",
        "Possible localized overload or structural settlement at support column"
    ],
    "recommended_repairs": [
        {
            "step": 1,
            "technique": "Non-Destructive Testing (NDT) & Crack Mapping",
            "protocol": "Deploy Ultrasonic Pulse Velocity (UPV) per IS 13311 (Part 1) to determine 3D internal void depth and sound concrete boundary."
        },
        {
            "step": 2,
            "technique": "Pressure Epoxy Resin Injection",
            "protocol": "Install injection nipples along crack at 150mm intervals. Seal surface with thixotropic epoxy putty. Inject low-viscosity structural epoxy resin (ASTM C881 Type I/IV) at 0.3-0.5 MPa until refusal."
        },
        {
            "step": 3,
            "technique": "Rebar Passivation & Polymer Modified Mortar (PMM)",
            "protocol": "Mechanically remove loose spalled concrete. Grit-blast exposed rebar and apply zinc-rich anti-corrosion primer. Patch with high-strength PMM per ACI 546R."
        },
        {
            "step": 4,
            "technique": "Carbon Fiber Reinforced Polymer (CFRP) Strengthening",
            "protocol": "Wrap beam web with bi-directional CFRP laminates (minimum 300 g/m²) bonded with structural saturant resin to restore nominal shear capacity."
        }
    ],
    "is_code_compliance": "Conforms to IS 456:2000 (Plain and Reinforced Concrete - Code of Practice) & IS 15988:2013 (Seismic Evaluation and Strengthening).",
    "safety_precautions": "Install temporary propping (Acro props) underneath beam B-12 prior to structural chipping to relieve dead load stresses."
}

# -------------------------------------------------------------------------
# Planning & Real Estate Benchmark Constants (Indian Construction Industry)
# -------------------------------------------------------------------------

CITY_TIER_DATA = {
    "Tier 1 (Metro)": {
        "cities": ["Mumbai MMR", "Delhi-NCR", "Bengaluru", "Hyderabad"],
        "base_civil_cost_sqft": 2450,
        "base_market_rate_sqft": 14500,
        "appreciation_factor": 1.15
    },
    "Tier 2 (Growth Hub)": {
        "cities": ["Pune", "Ahmedabad", "Chennai", "Kolkata", "Jaipur", "Lucknow"],
        "base_civil_cost_sqft": 1950,
        "base_market_rate_sqft": 7800,
        "appreciation_factor": 1.10
    },
    "Tier 3 (Emerging)": {
        "cities": ["Indore", "Coimbatore", "Bhubaneswar", "Nagpur", "Kochi", "Chandigarh"],
        "base_civil_cost_sqft": 1650,
        "base_market_rate_sqft": 4800,
        "appreciation_factor": 1.06
    }
}

STRUCTURE_TYPE_MULTIPLIERS = {
    "Residential High-rise (15-40 floors)": {
        "cost_multiplier": 1.25,
        "steel_kg_per_sqft": 4.5,
        "cement_bags_per_sqft": 0.45,
        "sand_cft_per_sqft": 1.6,
        "aggregate_cft_per_sqft": 2.2
    },
    "Commercial Complex / IT Park": {
        "cost_multiplier": 1.35,
        "steel_kg_per_sqft": 4.8,
        "cement_bags_per_sqft": 0.42,
        "sand_cft_per_sqft": 1.5,
        "aggregate_cft_per_sqft": 2.4
    },
    "Industrial Warehouse / PEB Structure": {
        "cost_multiplier": 0.85,
        "steel_kg_per_sqft": 3.2,
        "cement_bags_per_sqft": 0.30,
        "sand_cft_per_sqft": 1.2,
        "aggregate_cft_per_sqft": 1.8
    },
    "Luxury Villa / Gated Community": {
        "cost_multiplier": 1.45,
        "steel_kg_per_sqft": 4.0,
        "cement_bags_per_sqft": 0.48,
        "sand_cft_per_sqft": 1.8,
        "aggregate_cft_per_sqft": 2.0
    },
    "Infrastructure / Metro Station": {
        "cost_multiplier": 1.80,
        "steel_kg_per_sqft": 6.5,
        "cement_bags_per_sqft": 0.60,
        "sand_cft_per_sqft": 2.0,
        "aggregate_cft_per_sqft": 3.0
    }
}

QUALITY_GRADE_MULTIPLIER = {
    "Economy Grade": 0.85,
    "Standard IS 456 Grade": 1.00,
    "Premium Grade-A": 1.20,
    "Ultra-Luxury / LEED Platinum": 1.45
}

# -------------------------------------------------------------------------
# Weather Protocol Matrices (OSHA + IS 456 Engineering Rules)
# -------------------------------------------------------------------------

WEATHER_PROTOCOLS = {
    "High Wind (>45 km/h)": {
        "alert_level": "SEVERE DANGER",
        "color": "#EF4444",
        "crane_operations": "MANDATORY SUSPENSION: High wind speed (>38 km/h or 20 knots) triggers immediate tower crane and boom lift halt per OSHA 1926.1431 and IS 13367.",
        "scaffolding_work": "Evacuate personnel from all perimeter scaffolding tiers >3 meters height. Remove or secure wind mesh/tarpaulins to prevent scaffolding overturning.",
        "electrical_safety": "Inspect overhead temporary power distribution cables for swinging clearance from steel rebar columns and mobile plant.",
        "concrete_curing": "Wind accelerates plastic shrinkage cracks. Apply aliphatic alcohol moisture retentive film or continuous wet hessian curing."
    },
    "Heavy Monsoon Rain / Waterlogging": {
        "alert_level": "HIGH RISK",
        "color": "#F97316",
        "crane_operations": "Check ground bearing capacity under outriggers! Saturated soil causes crane tip-overs. Deploy timber or steel spreader mats.",
        "scaffolding_work": "Inspect base jacks on mudsills for differential soil settlement. Prohibit work during active downpours due to slip hazards.",
        "electrical_safety": "CRITICAL: De-energize all non-IP67 temporary switchboards. Test Residual Current Circuit Breakers (RCCB / 30mA). Elevate cables above standing water.",
        "concrete_curing": "SUSPEND open-air concreting! Rain alters Water-Cement (w/c) ratio, severely reducing compressive strength. If pouring in progress, cover immediately with 500-micron plastic sheeting."
    },
    "Extreme Heat (>42°C)": {
        "alert_level": "HEAT ADVISORY",
        "color": "#F59E0B",
        "crane_operations": "Monitor hydraulic oil fluid temperatures. Cabin AC must remain operational to prevent operator heat exhaustion.",
        "scaffolding_work": "Metal scaffold tubes reach >60°C; mandatory thermal gloves. Implement mandatory 15-minute shaded rest breaks every 60 minutes.",
        "electrical_safety": "Check transformer and portable generator overheating. Prevent cables running directly over burning hot metal deck plates.",
        "concrete_curing": "HOT WEATHER CONCRETING PROTOCOL (IS 456 / ACI 305R): Batch concrete with chilled water or shaved ice. Concrete placement temp must not exceed 32°C. Cure continuously with ponding or wet burlap."
    },
    "Dense Fog & Low Visibility (<100m)": {
        "alert_level": "CAUTION",
        "color": "#38BDF8",
        "crane_operations": "Halt blind tandem lifts. Two-way radio communication mandatory with dedicated spotters equipped with high-lumen strobes.",
        "scaffolding_work": "Prohibit working at heights on towers where ground visibility is lost.",
        "electrical_safety": "Condensation hazard in junction boxes; verify rubber gaskets and IP55 weather sealing.",
        "concrete_curing": "High relative humidity slows initial setting time; delay finishing operations until bleed water evaporates."
    },
    "Normal / Favorable (24°C - 30°C)": {
        "alert_level": "OPTIMAL WORKING CONDITIONS",
        "color": "#10B981",
        "crane_operations": "Normal operations permitted. Execute routine daily pre-shift inspection checklist (wire rope, anti-two-block limit switch).",
        "scaffolding_work": "Standard daily tag inspection (Green Scafftag valid). Ensure 100% harness hook-up above 2.0 meters.",
        "electrical_safety": "Maintain routine Lockout/Tagout (LOTO) protocols and earth pit resistance checks (<5 ohms).",
        "concrete_curing": "Standard IS 456 curing: Maintain moist curing for minimum 7 days for OPC and 10 days for mineral admixed concrete."
    }
}
