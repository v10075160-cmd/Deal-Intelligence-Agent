"""Streamlit application for Deal Intelligence Agent.

Frontend dashboard strictly communicating with the backend via frontend/api.py.
Handles all empty and error states:
- Backend offline or unreachable
- Empty deals lists
- HTTP error responses
- Loading states with spinners
"""

from datetime import date
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st

import api

# Page configuration
st.set_page_config(
    page_title="Deal Intelligence Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for clean enterprise design
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-won {
        background-color: #d1e7dd;
        color: #0f5132;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .badge-lost {
        background-color: #f8d7da;
        color: #842029;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .badge-open {
        background-color: #cff4fc;
        color: #055160;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .timeline-item {
        border-left: 3px solid #0d6efd;
        padding-left: 16px;
        margin-bottom: 20px;
    }
    .recalled-card {
        background-color: #f0f7ff;
        border-left: 4px solid #0d6efd;
        padding: 10px 14px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Helper functions for local dataset caching (for transcripts and timeline)
@st.cache_data
def load_local_seed_calls() -> Dict[str, List[Dict[str, Any]]]:
    """Load transcripts from data/deals.json keyed by deal id."""
    deals_file = Path(__file__).resolve().parent.parent / "data" / "deals.json"
    if not deals_file.exists():
        return {}
    try:
        deals_data = json.loads(deals_file.read_text(encoding="utf-8"))
        call_map = {}
        for d in deals_data:
            d_id = d.get("id") or d.get("deal_id")
            if d_id:
                call_map[d_id] = d.get("calls", [])
        return call_map
    except Exception:
        return {}


def get_demo_call_5_data() -> Optional[Dict[str, Any]]:
    """Load data/demo_call_5.json if available."""
    demo_file = Path(__file__).resolve().parent.parent / "data" / "demo_call_5.json"
    if not demo_file.exists():
        return None
    try:
        return json.loads(demo_file.read_text(encoding="utf-8"))
    except Exception:
        return None


# Initialize session state stores
if "local_calls" not in st.session_state:
    st.session_state.local_calls = load_local_seed_calls()

if "selected_deal_id" not in st.session_state:
    st.session_state.selected_deal_id = None

if "brief_cache" not in st.session_state:
    st.session_state.brief_cache = {}

if "error_message" not in st.session_state:
    st.session_state.error_message = None


# --- SIDEBAR ---
with st.sidebar:
    st.title("💼 Deal Intelligence")
    st.caption("Sales memory powered by Hindsight Cloud")
    st.markdown("---")

    # Backend health indicator
    is_healthy = api.check_health()
    if is_healthy:
        st.success("🟢 Backend Online", icon=None)
    else:
        st.error(f"🔴 Backend Offline (`{api.API_BASE}`)", icon=None)
        st.info("Start `backend/main_stub.py` or `backend/main.py` on port 8000.")

    # Seed demo data button
    st.markdown("### Data Management")
    if st.button("🌱 Seed Demo Data", use_container_width=True, disabled=not is_healthy):
        with st.spinner("Seeding demo deals and calls into backend..."):
            try:
                res = api.seed_demo_data()
                st.session_state.local_calls = load_local_seed_calls()
                st.toast(
                    f"Seeded successfully: {res.get('deals_loaded', 0)} deals, {res.get('calls_retained', 0)} calls."
                )
                st.rerun()
            except api.DealAgentAPIException as err:
                st.error(f"Seeding failed: {err.message}")

    st.markdown("---")
    st.markdown("### Active Deals")

    deals = []
    if is_healthy:
        try:
            with st.spinner("Loading deals..."):
                deals = api.get_deals()
        except api.DealAgentAPIException as exc:
            st.warning(f"Could not load deals: {exc.message}")
    else:
        st.caption("Connect backend to load deals.")

    if not deals and is_healthy:
        st.info("No deals available yet. Click **Seed Demo Data** above to populate.")

    # Deal Selector
    deal_options = {}
    default_index = 0
    for idx, d in enumerate(deals):
        d_id = d.get("deal_id") or d.get("id")
        comp = d.get("company", "Unknown")
        val = d.get("value", 0)
        outcome = d.get("outcome")
        badge = "WON" if outcome == "won" else ("LOST" if outcome == "lost" else "OPEN")
        label = f"{comp} (${val:,.0f}) [{badge}]"
        deal_options[d_id] = label
        if st.session_state.selected_deal_id == d_id:
            default_index = idx

    selected_deal = None
    if deal_options:
        selected_id = st.selectbox(
            "Select a deal to inspect:",
            options=list(deal_options.keys()),
            format_func=lambda x: deal_options[x],
            index=default_index,
        )
        st.session_state.selected_deal_id = selected_id
        selected_deal = next((d for d in deals if (d.get("deal_id") or d.get("id")) == selected_id), None)

    st.markdown("---")
    st.caption("Deal Intelligence Agent | Built against CONTRACT.md")


# --- MAIN AREA ---
if not is_healthy:
    st.error("### ⚠️ Backend Server Not Reachable")
    st.write(
        f"The frontend is attempting to connect to the backend at `{api.API_BASE}`, but no response was received."
    )
    st.markdown(
        """
        **To start the stub backend:**
        ```bash
        cd backend
        uvicorn main_stub:app --reload --port 8000
        ```
        Once running, refresh this page or click **Check Health**.
        """
    )
    if st.button("🔄 Retry Connection"):
        st.rerun()
    st.stop()

if not selected_deal:
    st.info("👋 Welcome! Please select a deal from the sidebar or click **Seed Demo Data** to get started.")
    st.stop()


# Render Selected Deal Overview
deal_id = selected_deal.get("deal_id") or selected_deal.get("id")
company = selected_deal.get("company", "Deal Overview")
value = selected_deal.get("value", 0)
stage = selected_deal.get("stage", "In Progress")
outcome = selected_deal.get("outcome")
calls_count = selected_deal.get("calls_count", 0)

col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    st.subheader(f"🏢 {company}")
    st.caption(f"Deal ID: `{deal_id}`")
with col2:
    st.metric("Deal Value", f"${value:,.0f}")
with col3:
    st.metric("Pipeline Stage", stage)
with col4:
    outcome_label = "Closed Won" if outcome == "won" else ("Closed Lost" if outcome == "lost" else "Active / Open")
    st.metric("Outcome", outcome_label)

st.markdown("---")

# Retrieve calls for selected deal
calls = st.session_state.local_calls.get(deal_id, [])

# Tabs for Main Deal Workflow
tab_brief, tab_timeline, tab_add_call = st.tabs(
    ["⚡ Pre-Call Brief", f"📞 Call Timeline ({len(calls)})", "➕ Log New Call"]
)

# --- TAB 1: PRE-CALL BRIEF ---
with tab_brief:
    st.markdown("### Pre-Call Executive Briefing")
    st.write("Generate real-time intelligence for the rep before joining the next call.")

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        brief_clicked = st.button("⚡ Brief Me", type="primary", use_container_width=True)

    if brief_clicked:
        with st.spinner("Generating deal brief from backend..."):
            try:
                brief_data = api.get_brief(deal_id, memory="on")
                st.session_state.brief_cache[deal_id] = brief_data
            except api.DealAgentAPIException as exc:
                st.error(f"Failed to generate brief: {exc.message}")

    brief_data = st.session_state.brief_cache.get(deal_id)

    if brief_data:
        # Executive Summary Box
        st.markdown("#### Executive Summary")
        st.info(brief_data.get("brief", "No brief text provided."))

        col_left, col_right = st.columns(2)

        # Open Objections Card
        with col_left:
            st.markdown("#### ⚠️ Open Objections & Blockers")
            objections = brief_data.get("open_objections", [])
            if objections:
                for obj in objections:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <strong>{obj.get('text', '')}</strong><br>
                            <small>Raised in Call {obj.get('raised_in_call', '?')} by <em>{obj.get('by', 'Unknown')}</em></small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No open objections recorded.")

            # Promises Card
            st.markdown("#### 🤝 Commitments & Promises")
            promises = brief_data.get("promises", [])
            if promises:
                for p in promises:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <strong>{p.get('text', '')}</strong><br>
                            <small>Made by: <em>{p.get('made_by', 'Rep')}</em> | Due: <strong>{p.get('due', 'TBD')}</strong></small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No open commitments.")

        # Stakeholders Map Card
        with col_right:
            st.markdown("#### 👥 Key Stakeholders & Stances")
            stakeholders = brief_data.get("stakeholders", [])
            if stakeholders:
                for s in stakeholders:
                    stance = s.get("stance", "Neutral")
                    stance_color = (
                        "green"
                        if "champion" in stance.lower()
                        else ("orange" if "cautious" in stance.lower() else "red")
                    )
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <strong>{s.get('name', 'Stakeholder')}</strong> — <em>{s.get('role', 'Stakeholder')}</em><br>
                            <span style="color: {stance_color}; font-weight: bold;">Stance: {stance}</span><br>
                            <small>Key Concerns: {s.get('concerns', 'None recorded')}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No stakeholders mapped yet.")

            # Recalled Facts
            recalled = brief_data.get("recalled_facts", [])
            if recalled:
                st.markdown("#### 🧠 What The Agent Remembered")
                for r in recalled:
                    st.markdown(
                        f"""
                        <div class="recalled-card">
                            <strong>Call {r.get('source_call', '?')}:</strong> {r.get('fact', '')}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        # Playbook Tips
        tips = brief_data.get("playbook_tips", [])
        if tips:
            st.markdown("---")
            st.markdown("#### 💡 Learned From Past Deals (Playbook Advice)")
            for tip in tips:
                st.success(f"**Tip:** {tip.get('tip', '')}\n\n*Evidence:* {tip.get('evidence', '')}")

    else:
        st.write("Click **Brief Me** above to pull real-time intelligence for this deal.")


# --- TAB 2: CALL TIMELINE ---
with tab_timeline:
    st.markdown(f"### Call Timeline for {company}")

    if not calls:
        st.info("No calls recorded yet for this deal. Use the **Log New Call** tab to log a transcript.")
    else:
        for c in calls:
            c_no = c.get("call_no", "?")
            c_date = c.get("date", "Unknown date")
            participants = c.get("participants", [])
            transcript = c.get("transcript", "")

            with st.expander(f"📞 Call {c_no} — {c_date} ({len(participants)} Participants)", expanded=False):
                st.write(f"**Participants:** {', '.join(participants)}")
                st.markdown("**Transcript:**")
                st.text_area(
                    label=f"Transcript Call {c_no}",
                    value=transcript,
                    height=180,
                    disabled=True,
                    key=f"transcript_view_{deal_id}_{c_no}",
                    label_visibility="collapsed",
                )


# --- TAB 3: ADD CALL FORM ---
with tab_add_call:
    st.markdown("### Log a New Call Transcript")
    st.write("Record a newly completed conversation to retain facts and objections into memory.")

    next_call_no = (max([c.get("call_no", 0) for c in calls], default=0)) + 1

    # Demo Deal Helper: Allow quick pre-fill of Call 5 for Northwind Logistics
    demo_call_5 = get_demo_call_5_data()
    is_northwind = "northwind" in company.lower() and next_call_no == 5

    if is_northwind and demo_call_5:
        st.success(
            "💡 **Demo Mode Ready:** You can pre-fill Call 5 for Northwind Logistics to test live ingestion!"
        )
        if st.button("📋 Pre-fill Demo Call 5 Data"):
            st.session_state.prefill_call_no = demo_call_5.get("call_no", 5)
            st.session_state.prefill_date = demo_call_5.get("date", str(date.today()))
            st.session_state.prefill_participants = ", ".join(demo_call_5.get("participants", []))
            st.session_state.prefill_transcript = demo_call_5.get("transcript", "")
            st.rerun()

    with st.form("add_call_form"):
        form_col1, form_col2 = st.columns(2)
        with form_col1:
            input_call_no = st.number_input(
                "Call Number",
                min_value=1,
                value=st.session_state.get("prefill_call_no", next_call_no),
                step=1,
            )
        with form_col2:
            input_date = st.text_input(
                "Date (YYYY-MM-DD)",
                value=st.session_state.get("prefill_date", str(date.today())),
            )

        input_participants = st.text_input(
            "Participants (comma-separated)",
            value=st.session_state.get(
                "prefill_participants",
                "Alice Morgan (Sales Rep), David Chen (VP Infrastructure & Engineering)",
            ),
        )

        input_transcript = st.text_area(
            "Call Transcript",
            value=st.session_state.get("prefill_transcript", ""),
            height=200,
            placeholder="Alice Morgan: Hi David... David Chen: We need...",
        )

        submitted = st.form_submit_button("💾 Retain & Log Call", type="primary")

        if submitted:
            if not input_transcript.strip():
                st.error("Transcript cannot be empty.")
            else:
                participants_list = [p.strip() for p in input_participants.split(",") if p.strip()]
                with st.spinner("Retaining call transcript in backend..."):
                    try:
                        res = api.add_call(
                            deal_id=deal_id,
                            call_no=int(input_call_no),
                            date=input_date.strip(),
                            participants=participants_list,
                            transcript=input_transcript.strip(),
                        )
                        # Append locally to timeline
                        new_call = {
                            "call_no": int(input_call_no),
                            "date": input_date.strip(),
                            "participants": participants_list,
                            "transcript": input_transcript.strip(),
                        }
                        if deal_id not in st.session_state.local_calls:
                            st.session_state.local_calls[deal_id] = []
                        st.session_state.local_calls[deal_id].append(new_call)

                        # Clear prefill state
                        st.session_state.pop("prefill_call_no", None)
                        st.session_state.pop("prefill_date", None)
                        st.session_state.pop("prefill_participants", None)
                        st.session_state.pop("prefill_transcript", None)

                        # Clear cached brief so user re-briefs with new call retained
                        st.session_state.brief_cache.pop(deal_id, None)

                        st.success(f"Call {input_call_no} retained successfully! Switch to 'Pre-Call Brief' to update intelligence.")
                        st.rerun()
                    except api.DealAgentAPIException as exc:
                        st.error(f"Failed to log call: {exc.message}")
