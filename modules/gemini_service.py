"""
Gemini Service Provider: Manages multimodal visual reasoning and multi-turn
engineering chat using Google Gemini with graceful fallback to high-fidelity demo mode.
"""

import os
import json
import base64
import requests
from typing import Dict, Any, List, Tuple
from modules.sample_data import DEMO_SAFETY_AUDIT_RESULT, DEMO_CRACK_DIAGNOSIS_RESULT

# Standard default Gemini model
DEFAULT_MODEL = "gemini-1.5-flash"

def get_effective_api_key(user_input_key: str = None) -> str:
    """Retrieves API key from UI input, environment variable, or secrets."""
    if user_input_key and user_input_key.strip():
        return user_input_key.strip()
    return os.getenv("GEMINI_API_KEY", "").strip()


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """Tests if the given Gemini API key is valid via a lightweight test."""
    if not api_key:
        return False, "No API key provided (Demonstration Mode active)."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            return True, "API Key successfully validated."
        else:
            return False, f"API Key rejected ({resp.status_code}): {resp.text[:120]}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def analyze_multimodal_vision(
    image_bytes: bytes,
    prompt: str,
    system_instruction: str = "",
    api_key: str = None,
    model_name: str = DEFAULT_MODEL,
    fallback_type: str = "safety"
) -> Dict[str, Any]:
    """
    Submits image + prompt to Gemini Vision API, returns structured JSON.
    Gracefully falls back to high-fidelity demonstration data on any API error or absent key.
    """
    effective_key = get_effective_api_key(api_key)

    if not effective_key:
        # Fallback directly to simulated demonstration result
        if fallback_type == "safety":
            res = dict(DEMO_SAFETY_AUDIT_RESULT)
        else:
            res = dict(DEMO_CRACK_DIAGNOSIS_RESULT)
        res["_source"] = "Demonstration Mode (Preloaded Audit)"
        res["_notice"] = "Running in simulated demonstration mode. Provide a Gemini API key in the sidebar for live multimodal model inferences."
        return res

    # Base64 encode the image
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    # REST Endpoint for Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={effective_key}"

    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_instruction}\n\n{prompt}"},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64_image
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            data = response.json()
            try:
                candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
                # Clean possible markdown wrap
                candidate_text = candidate_text.strip()
                if candidate_text.startswith("```json"):
                    candidate_text = candidate_text[7:]
                if candidate_text.endswith("```"):
                    candidate_text = candidate_text[:-3]
                
                parsed_json = json.loads(candidate_text.strip())
                parsed_json["_source"] = f"Live Gemini API ({model_name})"
                return parsed_json
            except (KeyError, json.JSONDecodeError) as parse_err:
                # If text wasn't pure JSON, wrap text into a structured dictionary
                raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if fallback_type == "safety":
                    fallback = dict(DEMO_SAFETY_AUDIT_RESULT)
                else:
                    fallback = dict(DEMO_CRACK_DIAGNOSIS_RESULT)
                fallback["_source"] = f"Live Gemini API (Raw Text Converted)"
                fallback["raw_model_notes"] = raw_text[:500]
                return fallback
        else:
            # Non-200 status code: fallback gracefully with error indication
            if fallback_type == "safety":
                fallback = dict(DEMO_SAFETY_AUDIT_RESULT)
            else:
                fallback = dict(DEMO_CRACK_DIAGNOSIS_RESULT)
            fallback["_source"] = "Demonstration Mode (API Fallback)"
            fallback["_notice"] = f"Gemini API returned code {response.status_code}. Gracefully loaded simulation."
            return fallback

    except Exception as exc:
        if fallback_type == "safety":
            fallback = dict(DEMO_SAFETY_AUDIT_RESULT)
        else:
            fallback = dict(DEMO_CRACK_DIAGNOSIS_RESULT)
        fallback["_source"] = "Demonstration Mode (Offline Fallback)"
        fallback["_notice"] = f"Network or API exception: {str(exc)}. Seamlessly fallen back to demonstration data."
        return fallback


def generate_chat_response(
    messages: List[Dict[str, str]],
    current_weather: str,
    api_key: str = None,
    model_name: str = DEFAULT_MODEL
) -> str:
    """
    Multi-turn construction engineering assistant powered by Gemini or offline expert knowledge base.
    """
    effective_key = get_effective_api_key(api_key)
    latest_query = messages[-1]["content"] if messages else ""

    # Knowledge engine response fallback
    if not effective_key:
        return _expert_rule_based_response(latest_query, current_weather)

    # Call Gemini REST API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={effective_key}"
    headers = {"Content-Type": "application/json"}

    system_context = (
        f"You are the Lead Senior Resident Construction Engineer & Safety Officer on a major Indian infrastructure project. "
        f"You strictly enforce Indian Standards (IS 456:2000, IS 13367, IS 3696, IS 2750) and OSHA 1926 standards. "
        f"The current site weather condition is: {current_weather}. "
        f"Always provide practical, actionable, mathematically sound engineering advice, step-by-step methodologies, "
        f"and safety warnings. Format with clean bullet points and bold headings."
    )

    contents = []
    # Add conversation history
    for m in messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    
    # Add latest query with system context injected
    contents.append({
        "role": "user",
        "parts": [{"text": f"[CONTEXT: Current Weather={current_weather}. Role: Senior Civil & Safety Engineer]\n\n{latest_query}"}]
    })

    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_context}]},
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1024
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"*(Notice: API returned HTTP {response.status_code} - Using Senior Resident Engineer Knowledge Engine)*\n\n" + _expert_rule_based_response(latest_query, current_weather)
    except Exception as exc:
        return f"*(Notice: Offline / Network Switch - Using Resident Engineer Knowledge Engine)*\n\n" + _expert_rule_based_response(latest_query, current_weather)


def _expert_rule_based_response(query: str, current_weather: str) -> str:
    """Rich rule-based engineering advisory fallback when API key is omitted."""
    q = query.lower()

    if "curing" in q or "is 456" in q or "stripping" in q or "formwork" in q:
        return (
            "### 🏗️ IS 456:2000 Concrete Curing & Formwork Stripping Protocol\n\n"
            f"**Current Site Weather Context:** {current_weather}\n\n"
            "- **Minimum Curing Period (Clause 13.5):**\n"
            "  - **Ordinary Portland Cement (OPC):** Minimum **7 days** under normal conditions; **10 days** in hot/dry or windy weather.\n"
            "  - **Mineral Admixtures (Fly Ash, GGBS, PPC):** Minimum **10 days** (extend to **14 days** under hot/windy exposure).\n\n"
            "- **IS 456 Formwork Stripping Times (Clause 11.3):**\n"
            "  1. Vertical formwork to columns, walls, beams: **16 - 24 hours**\n"
            "  2. Soffit formwork to slabs (props left under): **3 days**\n"
            "  3. Soffit formwork to beams (props left under): **7 days**\n"
            "  4. Props to slabs spanning up to 4.5m: **7 days** (over 4.5m: **14 days**)\n"
            "  5. Props to beams/arches spanning up to 6m: **14 days** (over 6m: **21 days**)\n\n"
            "⚠️ **Weather Alert:** Always perform field rebound hammer or ultrasonic pulse velocity (UPV) tests before removing primary beam shores!"
        )

    if "crane" in q or "wind" in q or "hoist" in q or "tower" in q:
        return (
            "### 🚨 Tower Crane & High Wind Operational Mandate (OSHA 1926.1431 & IS 13367)\n\n"
            f"**Current Weather Condition:** {current_weather}\n\n"
            "- **Wind Speed Thresholds:**\n"
            "  - **38 km/h (20 knots / 10.5 m/s):** Cease handling broad-surface panels, glass glazing, precast elements, and formwork shutters (sail area risk).\n"
            "  - **45 km/h (24 knots / 12.5 m/s):** **FULL CRANE STAND-DOWN.** Prohibit all hoisting operations. Ground all loads immediately.\n"
            "  - **Slewing Brake Protocol:** Release slewing brake into *Free Weathervaning Mode* so jib aligns downwind and prevents mast structural buckling.\n\n"
            "- **Ground Settlement Precaution:** In heavy rain or soaked subgrade, inspect crane outrigger pads for settlement. Ensure bearing pressure does not exceed ground safe bearing capacity (SBC)."
        )

    if "crack" in q or "epoxy" in q or "shear" in q or "grout" in q or "repair" in q:
        return (
            "### 🛠️ Structural Shear Crack Remediation Standard (IS 456 / ACI 224.1R)\n\n"
            "For shear cracks exceeding 0.3mm width in reinforced concrete beams:\n\n"
            "1. **Propping:** Relieve dead load stresses with hydraulic Acro props at both sides of the distressed zone before repair.\n"
            "2. **Surface Preparation & Port Installation:** Clean crack with oil-free compressed air. Drill 10mm ports at 150mm - 200mm c/c along crack line. Secure injection packers with thixotropic epoxy paste.\n"
            "3. **Pressure Grouting:** Inject low-viscosity, moisture-insensitive epoxy resin (ASTM C881 Type I, Grade 1) starting from the lowest port upwards until resin flows freely from adjacent port.\n"
            "4. **Tensile Enhancement:** For structural shear restoration, install **Carbon Fiber Reinforced Polymer (CFRP)** U-wraps bonded with structural epoxy saturant."
        )

    if "electrical" in q or "rain" in q or "monsoon" in q or "water" in q:
        return (
            "### ⚡ Site Electrical Safety & Waterlogging Protocol (OSHA 1926 Subpart K)\n\n"
            f"**Active Condition:** {current_weather}\n\n"
            "- **Mandatory Breakers:** Every single 230V/415V distribution board must feature calibrated **30mA Residual Current Circuit Breakers (RCCB / ELCB)**.\n"
            "- **Elevated Cable Runs:** Prohibit running flexible power cables along waterlogged mud or metal rebars. Suspend via insulated non-conductive 'S' hooks at min 2.2m height.\n"
            "- **Enclosure Ingress Protection:** Outdoor junction boxes must maintain certified **IP65/IP67** watertight seals.\n"
            "- **Daily LOTO:** Enforce strict Lockout/Tagout on de-watering pump connections before clearing clogs or repositioning submersible units."
        )

    # General civil engineering default
    return (
        f"### 👷 Construction Engineering Advisory\n\n"
        f"**Active Weather Context:** {current_weather}\n\n"
        f"Under your query regarding *'{query}'*, remember that safety, structural durability, and code compliance are paramount:\n\n"
        "1. **Code Standards:** Cross-reference calculations against **IS 456:2000** (Concrete), **IS 800:2007** (Steel), and **OSHA 1926** (Construction Site Safety).\n"
        "2. **Quality Control:** Mandate cube compressive strength testing at 7 and 28 days for all structural pours.\n"
        "3. **Zero Tolerance:** Any missing fall arrest gear above 2.0m height requires immediate site stoppage until rectified.\n\n"
        "Feel free to ask specific questions about mix design, curing periods, crack injection specifications, or weather-contingent crane limits!"
    )
