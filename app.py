"""Streamlit Web UI for Solo Travel Intelligence Platform."""
import sys
import os

# Ensure local src directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import streamlit as st
from pydantic import ValidationError
from solo_travel.config import LLMProviderType, get_settings
from solo_travel.models.state import UserTravelRequest, TravelStyle
from solo_travel.agents.crew import create_solo_travel_crew

# Streamlit Page Config
st.set_page_config(
    page_title="Solo Travel Intelligence Platform",
    page_icon="🎒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        width: 100%;
        transition: transform 0.1s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎒 Solo Travel Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Budget-first AI Planner for Solo Explorers • India & Global • Local or Cloud LLM</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Model & Engine Controls")

    provider_choice = st.selectbox(
        "LLM Provider",
        options=[LLMProviderType.OLLAMA.value, LLMProviderType.GROQ.value, LLMProviderType.GEMINI.value],
        index=0,
        help="Local Ollama runs 100% offline on your GPU without API keys."
    )

    if provider_choice == LLMProviderType.OLLAMA.value:
        model_name = st.selectbox(
            "🧠 Ollama Model",
            options=["llama3.1:8b", "qwen2.5:7b", "llama3.2:3b"],
            index=0
        )
    elif provider_choice == LLMProviderType.GROQ.value:
        model_name = st.selectbox(
            "🧠 Groq Model",
            options=["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
            index=0
        )
    else:
        model_name = st.selectbox(
            "🧠 Gemini Model",
            options=["gemini-2.0-flash", "gemini-1.5-flash"],
            index=0
        )

    st.markdown("---")
    st.markdown("### 🛡️ Guardrails & Safety")
    st.markdown("""
    - **Deterministic Budget Checks**: Hard floor validation in INR.
    - **Bounded Tool Queries**: Strict iteration limits against search loops.
    - **Solo-Travel Profiling**: Female dorm options, transit safety checks.
    """)
    st.caption("🔒 Architecture ready for local offline inference.")

# User Input Form
col1, col2 = st.columns(2)

with col1:
    origin = st.text_input("📍 Origin Station / City", value="New Delhi", placeholder="e.g. New Delhi, Mumbai, Bengaluru")
    destination = st.text_input("🎯 Destination", value="Varanasi", placeholder="e.g. Varanasi, Rishikesh, Hampi, Gokarna")
    duration = st.slider("📅 Trip Duration (Days)", min_value=1, max_value=10, value=3)

with col2:
    total_budget = st.number_input("💰 Total Budget (INR ₹)", min_value=1000, max_value=200000, value=6000, step=500)
    
    col_style, col_hostel = st.columns(2)
    with col_style:
        style_selection = st.selectbox(
            "🎒 Travel Style",
            options=["cheapest", "balanced", "comfort_budget"],
            index=0,
            format_func=lambda s: {
                "cheapest": "Absolute Cheapest",
                "balanced": "Balanced Value",
                "comfort_budget": "Comfort Budget"
            }[s]
        )
    with col_hostel:
        prefer_hostels = st.checkbox("Prefer Backpacker Hostels", value=True)

col_solo1, col_solo2 = st.columns(2)
with col_solo1:
    allow_overnight = st.checkbox("Allow Overnight Sleeper Transit (Saves 1 night hostel)", value=True)
with col_solo2:
    female_dorm = st.checkbox("Require Female-Only Dormitories", value=False)

interests_raw = st.text_area(
    "🎨 Interests & Preferences (comma-separated)",
    value="Heritage ghats, evening boat ride, local street food, quiet cafe work spot",
    placeholder="e.g. Trekking, photography, temples, yoga, night markets"
)

# Execution Flow
if st.button("🚀 Plan My Solo Trip"):
    interests_list = [i.strip() for i in interests_raw.split(",") if i.strip()]

    # Deterministic Input Validation via Pydantic Schema
    try:
        req = UserTravelRequest(
            origin=origin,
            destination=destination,
            duration_days=duration,
            total_budget_inr=float(total_budget),
            travel_style=TravelStyle(style_selection),
            interests=interests_list,
            allow_overnight_travel=allow_overnight,
            hostel_preference=prefer_hostels,
            require_female_dorm=female_dorm,
        )
    except ValidationError as e:
        for err in e.errors():
            msg = err.get("msg", "Validation error")
            st.error(f"❌ Input Validation Error: {msg}")
        st.stop()

    # Layered Guardrails: Prompt-injection defense, sanitization, and budget limits
    from solo_travel.guardrails import evaluate_travel_request_guardrails
    guard_result = evaluate_travel_request_guardrails(req)
    if not guard_result.is_safe:
        st.error("🛡️ **Safety Guardrail Blocked Request:**")
        for reason in guard_result.rejection_reasons:
            st.warning(f"• {reason}")
        st.stop()

    # Use sanitized interests
    req.interests = guard_result.sanitized_interests

    st.info(f"Targeting: **{req.origin}** ➔ **{req.destination}** | Budget: **₹{req.total_budget_inr:,.0f}** ({req.duration_days} days)")

    status_box = st.status("🧠 Multi-Agent Crew Collaborating...", expanded=True)
    with status_box:
        st.write("🔍 Logistics Scout identifying budget transit...")
        st.write("🏠 Hostel Specialist searching safe backpacker stays...")
        st.write("✍️ Synthesizer building itinerary and checking INR budget balance...")

        try:
            from solo_travel.flow.solo_flow import SoloTravelFlow
            flow = SoloTravelFlow(
                request=req,
                provider=LLMProviderType(provider_choice),
                model_name=model_name
            )

            # Kick off Flow lifecycle: Validation -> Data Retrieval -> Crew Synthesis -> Budget Verification
            final_state = flow.kickoff()

            status_box.update(label="✅ Solo Travel Flow Successfully Executed!", state="complete", expanded=False)
            st.success("🎉 Multi-Agent Pipeline & Flow Completed!")

            # Display deterministic budget breakdown banner
            if final_state.budget_breakdown:
                bb = final_state.budget_breakdown
                c_b1, c_b2, c_b3, c_b4 = st.columns(4)
                c_b1.metric("🚆 Est. Transit (Round Trip)", f"₹{bb.transport_total_inr:,.0f}")
                c_b2.metric("🏠 Stays & Hostels", f"₹{bb.accommodation_total_inr:,.0f}")
                c_b3.metric("🍲 Food & Local Transit", f"₹{(bb.food_total_inr + bb.local_transit_inr):,.0f}")
                c_b4.metric("💰 Total Est. Cost", f"₹{bb.grand_total_inr:,.0f}", delta=f"Budget: ₹{req.total_budget_inr:,.0f}")

            # Fetch live weather for environment markers
            from solo_travel.providers.weather import WeatherProvider
            from solo_travel.maps.osm import create_route_map
            weather_data = WeatherProvider().search(req.destination)

            if weather_data.get("status") == "success":
                st.markdown(
                    f"🌤️ **Live Destination Weather ({req.destination}):** "
                    f"Current: **{weather_data['current_temp_c']}°C** | "
                    f"Daily Range: **{weather_data['temp_min_c']}°C to {weather_data['temp_max_c']}°C** | "
                    f"Rain Chance: **{weather_data['rain_prob_percent']}%** "
                    f"*(Source: {weather_data['source']})*"
                )

            tab1, tab2, tab3 = st.tabs(["🗺️ Route & Environment Map", "📋 Complete Itinerary", "💾 Raw Markdown"])

            with tab1:
                st.markdown(f"### 📍 Solo Travel Corridor: {req.origin} ➔ {req.destination}")
                deck_map = create_route_map(req.origin, req.destination, weather_data)
                if deck_map:
                    st.pydeck_chart(deck_map)
                else:
                    st.info("Route visualization coordinates unavailable for this corridor.")

            itinerary_text = final_state.itinerary_markdown or "No itinerary text returned."

            with tab2:
                st.markdown(itinerary_text)

            with tab3:
                st.code(itinerary_text, language="markdown")

            st.download_button(
                label="📥 Download Itinerary (.md)",
                data=itinerary_text,
                file_name=f"{req.destination.replace(' ', '_')}_{req.duration_days}day_solo_plan.md",
                mime="text/markdown"
            )

        except Exception as e:
            status_box.update(label="❌ Execution Error", state="error", expanded=True)
            st.error(f"Error during agent execution: {str(e)}")
