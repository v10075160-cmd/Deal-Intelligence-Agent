# Deal Intelligence Agent — 60-Second Rehearsed Demo Script

**Theme:** AI Agents That Learn Using Hindsight  
**Target Time:** 60 seconds  
**Objective:** Deliver a clear, visceral before/after demonstration showing how persistent Hindsight memory transforms a generic sales assistant into an executive deal-closer that gets smarter with every call.

---

### Prerequisites & Setup (Before the Demo Starts)
1. Backend running: `uvicorn main:app --reload --port 8000` (or `main_stub:app`)
2. Frontend running: `streamlit run app.py` from `frontend/`
3. Click **"Seed Demo Data"** in the sidebar once to populate the 6 enterprise deals.
4. Select **Northwind Logistics** in the sidebar.

---

## The 60-Second Script

### [0:00 - 0:12] Act 1: The Problem — Rep Joins Call 5 Cold
* **Action:** Presenter clicks **Pre-Call Brief** on **Northwind Logistics**. Ensure **Memory is set to OFF**.
* **Spoken Narration (12 sec):**
  > *"Meet Alice, an enterprise account executive joining Call 5 with Northwind Logistics. She's jumping between back-to-back meetings and has 30 seconds to prep. Without long-term memory, here is what her AI assistant gives her..."*
* **On-Screen Visual:**
  - Executive Briefing Summary shows a bland, 2-line summary of Call 4.
  - Recalled facts count is **0**. Past promises and objections from Calls 1, 2, and 3 are missing.

---

### [0:12 - 0:24] Act 2: The Breakthrough — Memory ON
* **Action:** Flip the **Agent Memory Mode** toggle from **OFF** to **ON**.
* **Spoken Narration (12 sec):**
  > *"Now watch what happens when we flip Hindsight Memory ON. Instantly, the agent connects the dots across the entire deal history. It remembers David Chen's SAP latency requirement from Call 1, surfaces that Alice promised a SOC 2 audit report to procurement in Call 2 that was never sent, and flags Sarah Jenkins's $150k board sign-off threshold from Call 4."*
* **On-Screen Visual:**
  - **"What The Agent Remembered"** panel expands with facts tagged `Call 1`, `Call 2`, and `Call 3`.
  - Open Objections highlight the CFO's budget ceiling and procurement's InfoSec gate.
  - Promises card flags the pending SOC 2 security delivery.

---

### [0:24 - 0:38] Act 3: Live Ingestion — Adding Call 5
* **Action:** Click **"Log New Call"** tab. Click **"Pre-fill Demo Call 5 Data"**, then click **"Retain & Log Call"**. Switch back to **"Pre-Call Brief"**.
* **Spoken Narration (14 sec):**
  > *"During Call 5, Alice uses this intelligence: she delivers the SOC 2 report to procurement and structures a quarterly payment plan of $45,000 to fit under the CFO's signing limit. We log the transcript live. Hindsight immediately retains the newly resolved terms, updates the stakeholder stances, and generates a personalized follow-up email confirming the close."*
* **On-Screen Visual:**
  - Call 5 is retained live.
  - Timeline updates to 5 calls.
  - Follow-up email drafts with specific references to Sarah's quarterly schedule and Frank's SOC 2 package.

---

### [0:38 - 0:48] Act 4: Closing the Deal & Training the Global Playbook
* **Action:** Click **"Mark Outcome"** tab. Select **Closed Won**, select objections handled (*CFO budget ceiling*, *Security compliance*), click **"Save Outcome to Playbook Bank"**.
* **Spoken Narration (10 sec):**
  > *"Alice closes the $180,000 deal. When she marks it won, Hindsight doesn't just archive it—it retains the winning strategy into our global organizational Playbook bank."*
* **On-Screen Visual:**
  - Toast confirmation: *"Outcome and strategy retained into Playbook bank."*
  - Deal outcome badge updates to **WON**.

---

### [0:48 - 1:00] Act 5: Cross-Deal Learning — The Next Deal Wins Faster
* **Action:** In the sidebar navigation, click **"📚 Playbook Bank"**, then switch back to a new open deal (e.g. **Solaria Renewable Tech**).
* **Spoken Narration (12 sec):**
  > *"Look at our Playbook: Hindsight synthesized that structuring amortized quarterly payments against CFO budget objections increases close rates by 28%. When a new rep opens an open deal like Solaria Renewable Tech, that exact playbook tip appears directly in their brief under 'Learned From Past Deals.' That is an agent that doesn't just remember—it learns."*
* **On-Screen Visual:**
  - Playbook Bank displays evidence-backed **"What Works"** cards and mental models.
  - Pre-Call Brief for Solaria displays the injected **"Learned From Past Deals"** playbook recommendation with supporting win-rate data.

---

## Quick Reference Checklist
- [x] Time: Exactly 60 seconds spoken pace
- [x] Visual before/after contrast within first 15 seconds
- [x] Live transcript ingestion using `data/demo_call_5.json`
- [x] Clear demonstration of both deal-level isolation and global playbook reflection
