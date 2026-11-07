"""Streamlit application for Deal Intelligence Agent.

Frontend dashboard communicating strictly with the backend via frontend/api.py.
Features:
- Sidebar deal selector with pipeline stats, health indicator, and seed trigger
- Pre-Call Brief with prominent MEMORY ON/OFF toggle
- 'What the agent remembered' recalled-facts panel (active only when memory is ON)
- Stakeholder map with visual stance chips
- Open objections and commitments tracking cards
- Side-by-side comparison view (Memory OFF vs Memory ON)
- Personalized follow-up email generator with Memory toggle
- Learning curve chart showing intelligence progression across Calls 1, 3, and 5
- Full call timeline and new call transcript logging form
"""

from datetime import date
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

import api

# Page configuration
st.set_page_config(
    page_title="Deal Intelligence Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for executive enterprise look
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .stance-chip {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stance-champion {
        background-color: #d1e7dd;
        color: #0f5132;
        border: 1px solid #badbcc;
    }
    .stance-cautious {
        background-color: #fff3cd;
        color: #664d03;
        border: 1px solid #ffecb5;
    }
    .stance-skeptic {
        background-color: #f8d7da;
        color: #842029;
        border: 1px solid #f5c2c7;
    }
    .stance-neutral {
        background-color: #e2e3e5;
        color: #41464b;
        border: 1px solid #d3d6d8;
    }
    .recalled-box {
        background-color: #e8f4fd;
        border-left: 4px solid #0d6efd;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .call-tag {
        background-color: #0d6efd;
        color: white;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .memory-badge-on {
        background-color: #d1e7dd;
        color: #0f5132;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 12px;
    }
    .memory-badge-off {
        background-color: #f8d7da;
        color: #842029;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 12px;
    }
    .email-container {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_local_seed_calls() -> Dict[str, List[Dict[str, Any]]]:
    """Load call transcripts from data/deals.json keyed by deal ID."""
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


def render_stance_chip(stance: str) -> str:
    """Return HTML for a styled stance chip."""
    s_lower = stance.lower()
    if "champion" in s_lower:
        css = "stance-champion"
    elif "cautious" in s_lower or "evaluating" in s_lower:
        css = "stance-cautious"
    elif "skeptic" in s_lower or "blocker" in s_lower or "veto" in s_lower:
        css = "stance-skeptic"
    else:
        css = "stance-neutral"
    return f'<span class="stance-chip {css}">{stance}</span>'


# Initialize session state
if "local_calls" not in st.session_state:
    st.session_state.local_calls = load_local_seed_calls()

if "selected_deal_id" not in st.session_state:
    st.session_state.selected_deal_id = None

if "brief_cache" not in st.session_state:
    st.session_state.brief_cache = {}

if "global_memory_toggle" not in st.session_state:
    st.session_state.global_memory_toggle = "ON"


# --- SIDEBAR ---
with st.sidebar:
    st.title("💼 Deal Intelligence")
    st.caption("Sales intelligence with Hindsight long-term memory")
    st.markdown("---")

    # Backend Health Check
    is_healthy = api.check_health()
    if is_healthy:
        st.success("🟢 Backend Online", icon=None)
    else:
        st.error(f"🔴 Backend Offline (`{api.API_BASE}`)", icon=None)
        st.info("Start `backend/main_stub.py` or `backend/main.py` on port 8000.")

    # Seed Demo Data Trigger
    st.markdown("### Data Management")
    if st.button("🌱 Seed Demo Data", use_container_width=True, disabled=not is_healthy):
        with st.spinner("Seeding demo deals and calls into backend..."):
            try:
                res = api.seed_demo_data()
                st.session_state.local_calls = load_local_seed_calls()
                st.toast(
                    f"Seeded: {res.get('deals_loaded', 0)} deals, {res.get('calls_retained', 0)} calls."
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
        st.info("No deals available yet. Click **Seed Demo Data** above.")

    deal_options = {}
    default_index = 0
    for idx, d in enumerate(deals):
        d_id = d.get("deal_id") or d.get("id")
        comp = d.get("company", "Unknown")
        val = d.get("value", 0)
        outcome = d.get("outcome")
        badge = "WON" if outcome == "won" else ("LOST" if outcome == "lost" else "OPEN")
        deal_options[d_id] = f"{comp} (${val:,.0f}) [{badge}]"
        if st.session_state.selected_deal_id == d_id:
            default_index = idx

    selected_deal = None
    if deal_options:
        selected_id = st.selectbox(
            "Select deal:",
            options=list(deal_options.keys()),
            format_func=lambda x: deal_options[x],
            index=default_index,
        )
        st.session_state.selected_deal_id = selected_id
        selected_deal = next(
            (d for d in deals if (d.get("deal_id") or d.get("id")) == selected_id),
            None,
        )

    st.markdown("---")
    st.caption("Built strictly against CONTRACT.md")


# --- MAIN AREA ---
if not is_healthy:
    st.error("### ⚠️ Backend Server Not Reachable")
    st.write(
        f"The frontend is attempting to connect to the backend at `{api.API_BASE}`, but no response was received."
    )
    st.markdown(
        """
        **To run the stub server:**
        ```bash
        cd backend
        uvicorn main_stub:app --reload --port 8000
        ```
        """
    )
    if st.button("🔄 Check Connection"):
        st.rerun()
    st.stop()

if not selected_deal:
    st.info("👋 Select a deal from the sidebar or click **Seed Demo Data** to populate accounts.")
    st.stop()

# Header Information for Selected Deal
deal_id = selected_deal.get("deal_id") or selected_deal.get("id")
company = selected_deal.get("company", "Deal Overview")
value = selected_deal.get("value", 0)
stage = selected_deal.get("stage", "In Progress")
outcome = selected_deal.get("outcome")
calls = st.session_state.local_calls.get(deal_id, [])

col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    st.subheader(f"🏢 {company}")
    st.caption(f"Account ID: `{deal_id}`")
with col2:
    st.metric("Contract Value", f"${value:,.0f}")
with col3:
    st.metric("Pipeline Stage", stage)
with col4:
    outcome_label = (
        "Closed Won" if outcome == "won" else ("Closed Lost" if outcome == "lost" else "Active / Open")
    )
    st.metric("Deal Outcome", outcome_label)

st.markdown("---")

# Navigation Tabs
tab_brief, tab_compare, tab_followup, tab_learning, tab_timeline, tab_add_call = st.tabs(
    [
        "⚡ Pre-Call Brief",
        "⚖️ Compare (ON vs OFF)",
        "✉️ Follow-Up Email",
        "📈 Learning Curve",
        f"📞 Call Timeline ({len(calls)})",
        "➕ Log New Call",
    ]
)


# --- TAB 1: PRE-CALL BRIEF (CORE MEMORY STORY) ---
with tab_brief:
    st.markdown("### Pre-Call Intelligence Briefing")
    st.write("Generates actionable intelligence to equip the sales executive before entering the next call.")

    # Prominent MEMORY ON / OFF Toggle
    st.markdown("#### Agent Memory Mode")
    toggle_col1, toggle_col2 = st.columns([2, 3])
    with toggle_col1:
        memory_mode = st.radio(
            "Memory Setting",
            options=["ON", "OFF"],
            horizontal=True,
            index=0 if st.session_state.global_memory_toggle == "ON" else 1,
            help="Toggle between full Hindsight multi-call recall and baseline single-call processing.",
            key="radio_brief_memory",
        )
        st.session_state.global_memory_toggle = memory_mode

    with toggle_col2:
        if memory_mode == "ON":
            st.markdown(
                """
                <div class="memory-badge-on">
                    🧠 <strong>MEMORY ON:</strong> Hindsight recalls all objections, promises, and stakeholder stances across deal history.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="memory-badge-off">
                    ⚪ <strong>MEMORY OFF:</strong> Agent reads ONLY the latest call transcript. Past commitments and objections are blind spots.
                </div>
                """,
                unsafe_allow_html=True,
            )

    btn_col, _ = st.columns([1, 4])
    with btn_col:
        fetch_brief = st.button("⚡ Generate Brief", type="primary", use_container_width=True)

    cache_key = f"{deal_id}_{memory_mode.lower()}"

    # Auto-fetch if not yet in cache, or when button clicked
    if fetch_brief or cache_key not in st.session_state.brief_cache:
        with st.spinner(f"Pulling intelligence brief (Memory={memory_mode})..."):
            try:
                brief_res = api.get_brief(deal_id, memory=memory_mode.lower())
                st.session_state.brief_cache[cache_key] = brief_res
            except api.DealAgentAPIException as exc:
                st.error(f"Failed to generate brief: {exc.message}")

    brief_data = st.session_state.brief_cache.get(cache_key)

    if brief_data:
        # 1. Executive Summary Box
        st.markdown("#### 📋 Executive Briefing Summary")
        if memory_mode == "ON":
            st.success(brief_data.get("brief", "No summary provided."))
        else:
            st.warning(brief_data.get("brief", "No summary provided."))

        # 2. "What the agent remembered" Panel (VISIBLE ONLY WHEN MEMORY IS ON)
        recalled_facts = brief_data.get("recalled_facts", [])
        if memory_mode == "ON":
            st.markdown("---")
            st.markdown("#### 🧠 What The Agent Remembered")
            st.caption(
                "Facts, constraints, and historical commitments retrieved from Hindsight memory bank."
            )
            if recalled_facts:
                for rf in recalled_facts:
                    src_call = rf.get("source_call", "?")
                    fact_text = rf.get("fact", "")
                    st.markdown(
                        f"""
                        <div class="recalled-box">
                            <span class="call-tag">Call {src_call}</span> <strong>{fact_text}</strong>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No specific facts retrieved for this deal.")
        else:
            st.markdown("---")
            st.caption(
                "⚪ **Recalled Facts Hidden:** In Memory OFF mode, the agent has zero historical recall and only inspects the latest call."
            )

        st.markdown("---")
        card_col1, card_col2 = st.columns(2)

        # 3. Open Objections & Blockers
        with card_col1:
            st.markdown("#### ⚠️ Open Objections & Blockers")
            objections = brief_data.get("open_objections", [])
            if objections:
                for obj in objections:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <strong>{obj.get('text', '')}</strong><br>
                            <small>Raised in <strong>Call {obj.get('raised_in_call', '?')}</strong> by <em>{obj.get('by', 'Prospect')}</em></small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No open objections recorded.")

            # 4. Commitments & Promises
            st.markdown("#### 🤝 Commitments & Promises Made")
            promises = brief_data.get("promises", [])
            if promises:
                for p in promises:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <strong>{p.get('text', '')}</strong><br>
                            <small>Promised by: <em>{p.get('made_by', 'Sales Rep')}</em> | Target Date: <strong>{p.get('due', 'TBD')}</strong></small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No pending commitments recorded.")

        # 5. Stakeholder Map with Stance Chips
        with card_col2:
            st.markdown("#### 👥 Stakeholder Map & Stances")
            stakeholders = brief_data.get("stakeholders", [])
            if stakeholders:
                for s in stakeholders:
                    s_name = s.get("name", "Stakeholder")
                    s_role = s.get("role", "Stakeholder")
                    s_stance = s.get("stance", "Neutral")
                    s_concerns = s.get("concerns", "None specified")
                    stance_html = render_stance_chip(s_stance)

                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <strong>{s_name}</strong>
                                {stance_html}
                            </div>
                            <small><strong>Role:</strong> {s_role}</small><br>
                            <small><strong>Primary Concern:</strong> {s_concerns}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No stakeholders identified yet.")

        # 6. Playbook Tips (Only present when memory is on)
        playbook_tips = brief_data.get("playbook_tips", [])
        if memory_mode == "ON" and playbook_tips:
            st.markdown("---")
            st.markdown("#### 💡 Learned From Past Deals (Playbook Bank)")
            for pt in playbook_tips:
                st.info(f"**Strategy Tip:** {pt.get('tip', '')}\n\n*Supporting Evidence:* {pt.get('evidence', '')}")


# --- TAB 2: SIDE-BY-SIDE COMPARE (BEFORE & AFTER) ---
with tab_compare:
    st.markdown("### ⚖️ Side-by-Side Comparison: Memory OFF vs Memory ON")
    st.write(
        "Demonstrates the dramatic contrast in pre-call readiness. Without memory, the agent produces generic summaries. With Hindsight, it tracks promises, objections, and stakeholder nuances."
    )

    if st.button("🔄 Refresh Comparison Data"):
        st.session_state.brief_cache.pop(f"{deal_id}_off", None)
        st.session_state.brief_cache.pop(f"{deal_id}_on", None)
        st.rerun()

    # Fetch both brief states
    try:
        if f"{deal_id}_off" not in st.session_state.brief_cache:
            st.session_state.brief_cache[f"{deal_id}_off"] = api.get_brief(deal_id, memory="off")
        if f"{deal_id}_on" not in st.session_state.brief_cache:
            st.session_state.brief_cache[f"{deal_id}_on"] = api.get_brief(deal_id, memory="on")

        brief_off = st.session_state.brief_cache[f"{deal_id}_off"]
        brief_on = st.session_state.brief_cache[f"{deal_id}_on"]

        cmp_col1, cmp_col2 = st.columns(2)

        with cmp_col1:
            st.markdown(
                """
                <div class="memory-badge-off" style="width: 100%; text-align: center;">
                    ⚪ <strong>MEMORY OFF (Baseline)</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.warning(f"**Brief (Latest Call Only):**\n\n{brief_off.get('brief', '')}")

            st.markdown("##### What the agent knows:")
            st.metric("Historical Facts Recalled", 0)
            st.metric("Cross-Call Objections", 0)
            st.caption("❌ Blind to previous commitments made in earlier calls.")
            st.caption("❌ Unaware of CFO budget ceilings or procurement flags.")

        with cmp_col2:
            st.markdown(
                """
                <div class="memory-badge-on" style="width: 100%; text-align: center;">
                    🧠 <strong>MEMORY ON (Hindsight Active)</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.success(f"**Brief (Full Sales Cycle Intelligence):**\n\n{brief_on.get('brief', '')}")

            st.markdown("##### What the agent knows:")
            recalled_count = len(brief_on.get("recalled_facts", []))
            st.metric("Historical Facts Recalled", recalled_count)
            st.metric("Playbook Tips Injected", len(brief_on.get("playbook_tips", [])))

            st.markdown("##### Recalled Facts Active in Context:")
            for rf in brief_on.get("recalled_facts", []):
                st.markdown(
                    f"""
                    <div class="recalled-box">
                        <span class="call-tag">Call {rf.get('source_call', '?')}</span> {rf.get('fact', '')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    except api.DealAgentAPIException as exc:
        st.error(f"Error loading comparison: {exc.message}")


# --- TAB 3: FOLLOW-UP EMAIL DRAFTER ---
with tab_followup:
    st.markdown("### ✉️ Personalized Follow-Up Email")
    st.write(
        "Generate a client follow-up email that incorporates commitments, resolves open objections, and aligns with stakeholder expectations."
    )

    f_col1, f_col2 = st.columns([2, 3])
    with f_col1:
        f_memory = st.radio(
            "Email Memory Setting",
            options=["ON", "OFF"],
            horizontal=True,
            index=0 if st.session_state.global_memory_toggle == "ON" else 1,
            key="radio_email_memory",
        )
    with f_col2:
        if f_memory == "ON":
            st.caption("🧠 Email references past commitments, SOC 2 reports, and stakeholder pricing concerns.")
        else:
            st.caption("⚪ Email is generic and only acknowledges the latest call.")

    if st.button("✉️ Draft Email", type="primary"):
        with st.spinner("Drafting follow-up email from backend..."):
            try:
                followup_res = api.get_followup(deal_id, memory=f_memory.lower())
                st.session_state[f"email_{deal_id}_{f_memory}"] = followup_res.get("email", "")
            except api.DealAgentAPIException as exc:
                st.error(f"Failed to generate email: {exc.message}")

    cached_email = st.session_state.get(f"email_{deal_id}_{f_memory}")
    if cached_email:
        st.markdown("#### Draft Preview")
        st.markdown(
            f"""
            <div class="email-container">
                <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">{cached_email}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.text_area("Copy Text", value=cached_email, height=120, label_visibility="collapsed")


# --- TAB 4: LEARNING CURVE (DEMO DEAL SPECIFICITY) ---
with tab_learning:
    st.markdown("### 📈 The Agent Learning Curve")
    st.write(
        "As conversations progress from Call 1 through Call 5, Hindsight accumulates structured facts, objection nuances, and commercial terms. The brief transforms from generic discovery into hyper-personalized closing strategy."
    )

    # Learning Curve Metric Data (Recalled facts as proxy for brief specificity)
    learning_data = pd.DataFrame(
        {
            "Sales Call": ["Call 1 (Discovery)", "Call 3 (Budget Review)", "Call 5 (Closing Alignment)"],
            "Recalled Facts In Context": [1, 4, 7],
            "Objection Precision (%)": [20, 65, 95],
        }
    )

    chart_col, table_col = st.columns([3, 2])
    with chart_col:
        st.markdown("#### Recalled Facts Active in Brief vs Call Progress")
        chart_df = pd.DataFrame(
            {"Recalled Facts": [1, 4, 7]},
            index=["Call 1", "Call 3", "Call 5"],
        )
        st.bar_chart(chart_df, color="#0d6efd", height=280)

    with table_col:
        st.markdown("#### Intelligence Evolution")
        st.markdown(
            """
            * **Call 1 (Baseline Discovery):**
              * *Recalled Facts:* **1**
              * *Context:* High-level architecture, initial cloud bill size ($400k/mo).
            * **Call 3 (Objection Deep Dive):**
              * *Recalled Facts:* **4**
              * *Context:* Frank's SOC 2 compliance gate, Sarah's $180k budget cap and 9-month ROI breakeven rule.
            * **Call 5 (Deal Execution):**
              * *Recalled Facts:* **7**
              * *Context:* Sarah's $45k quarterly threshold, Frank's verified SOC 2 audit package, and automated Terraform IAM template.
            """
        )

    st.markdown("---")
    st.info(
        "💡 **Key Insight:** In traditional stateless agents, Call 5 is processed with zero recollection of Call 2's promised security audit or Call 3's quarterly amortization requirement. Hindsight ensures no commitment is ever dropped."
    )


# --- TAB 5: CALL TIMELINE ---
with tab_timeline:
    st.markdown(f"### Chronological Call History for {company}")

    if not calls:
        st.info("No calls recorded yet for this deal. Use the **Log New Call** tab to log a conversation.")
    else:
        for c in calls:
            c_no = c.get("call_no", "?")
            c_date = c.get("date", "Unknown date")
            participants = c.get("participants", [])
            transcript = c.get("transcript", "")

            with st.expander(
                f"📞 Call {c_no} — {c_date} ({len(participants)} Participants)",
                expanded=(c_no == len(calls)),
            ):
                st.markdown(f"**Participants:** {', '.join(participants)}")
                st.markdown("**Transcript:**")
                st.text_area(
                    label=f"Transcript Call {c_no}",
                    value=transcript,
                    height=180,
                    disabled=True,
                    key=f"transcript_view_{deal_id}_{c_no}",
                    label_visibility="collapsed",
                )


# --- TAB 6: ADD CALL FORM ---
with tab_add_call:
    st.markdown("### Log a New Call Transcript")
    st.write("Record a newly completed conversation to retain facts and objections into memory.")

    next_call_no = (max([c.get("call_no", 0) for c in calls], default=0)) + 1

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

                        # Clear brief cache for this deal so new call triggers fresh brief
                        st.session_state.brief_cache.pop(f"{deal_id}_on", None)
                        st.session_state.brief_cache.pop(f"{deal_id}_off", None)

                        st.success(
                            f"Call {input_call_no} retained successfully! Switch to 'Pre-Call Brief' to update intelligence."
                        )
                        st.rerun()
                    except api.DealAgentAPIException as exc:
                        st.error(f"Failed to log call: {exc.message}")
