"""
app.py

Streamlit interface for EcoGuide AI. Wraps the LangGraph multi-agent
orchestrator (orchestrator.py) in a chat-style UI with a preferences
sidebar, itinerary display, retrieved-document transparency panel,
and reflection/critique output.
"""

import streamlit as st
from orchestrator import run_ecoguide

# --- Page Configuration ---
st.set_page_config(
    page_title="EcoGuide AI",
    page_icon="🌿",
    layout="wide"
)

import os

# --- Auto-build the Chroma vector store on first run (needed for cloud deployment,
# since data/chroma_db/ is gitignored and won't exist in a fresh deployment) ---
CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "chroma_db")

if not os.path.exists(CHROMA_DIR):
    with st.spinner("🌿 First-time setup: building knowledge base (this takes ~1-2 minutes)..."):
        from rag.ingest import run_ingestion
        run_ingestion()

# --- Session State Initialization ---
# Streamlit re-runs the whole script on every interaction, so we use
# session_state to remember chat history across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Sidebar: Project Branding + Tour Preferences ---
with st.sidebar:
    st.markdown("# 🌿 EcoGuide AI")
    st.caption("Sustainable trip planning for Sri Lanka")
    st.divider()

    st.subheader("Tour Preferences")

    duration = st.slider(
        "Travel duration (days)",
        min_value=1, max_value=14, value=3
    )

    budget = st.number_input(
        "Budget (USD)",
        min_value=0, max_value=10000, value=500, step=50
    )

    interests = st.multiselect(
        "Travel interests",
        options=["wildlife", "hiking", "beaches", "culture", "relaxation",
                 "birdwatching", "rainforest", "hotels"],
        default=["wildlife"]
    )

    crowd_preference = st.radio(
        "Crowd preference",
        options=["No preference", "Prefer quiet/low-crowd spots"]
    )

    st.divider()
    st.caption("Built with LangGraph, LangChain, Groq & OpenRouter")


# --- Main Page Header ---
st.title("Plan Your Sustainable Sri Lanka Trip")
st.write("Describe your trip below, or use the sidebar preferences and click Generate.")


# --- Helper: Build a query string from sidebar inputs ---
def build_query_from_sidebar() -> str:
    """Combines sidebar preferences into a natural-language query for the agent pipeline."""
    parts = [f"Plan a {duration}-day sustainable trip"]
    if budget:
        parts.append(f"with a ${budget} budget")
    if interests:
        parts.append(f"focused on {', '.join(interests)}")
    if crowd_preference == "Prefer quiet/low-crowd spots":
        parts.append("preferring quiet, low-crowd locations")
    return " ".join(parts) + "."


# --- Generate Button (sidebar-driven planning) ---
if st.sidebar.button("🗺️ Generate Itinerary", use_container_width=True):
    query = build_query_from_sidebar()
    st.session_state.messages.append({"role": "user", "content": query})


# --- Chat Input (free-text alternative) ---
if user_input := st.chat_input("Or type your own trip request..."):
    st.session_state.messages.append({"role": "user", "content": user_input})


# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# --- Process the Latest User Message (if it hasn't been answered yet) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    latest_query = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        with st.spinner("🌿 Consulting the Router, Planner, and Critic agents..."):
            try:
                final_state = run_ecoguide(latest_query)
                error_occurred = False
            except Exception as e:
                error_occurred = True
                st.error(f"Something went wrong while planning your trip: {e}")
                st.info("Try rephrasing your request, or check that your API keys are set correctly in .env.")

        if not error_occurred:
            # --- Suggested Itinerary ---
            st.markdown("### 🗺️ Suggested Itinerary")
            st.markdown(final_state["final_answer"])

            # --- Reflection / Critic Output ---
            with st.expander("🔍 Reflection Agent Output (Critic's Review)"):
                critique = final_state.get("critique", {})
                if critique.get("passed"):
                    st.success("✅ Passed quality review — no issues found")
                else:
                    st.warning("⚠️ Issues found during review:")
                    for issue in critique.get("issues", []):
                        st.write(f"- {issue}")
                    if critique.get("suggestion"):
                        st.write(f"**Suggested fix applied:** {critique['suggestion']}")
                st.caption(f"Retry attempts used: {final_state.get('retry_count', 0)}")

            # --- Retrieved Documents Panel ---
            with st.expander("📚 Retrieved Documents (RAG Context)"):
                context = final_state.get("context", "")
                if context:
                    st.text(context)
                else:
                    st.caption("No context was retrieved for this query.")

            # --- Save assistant response to chat history ---
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_state["final_answer"]
            })