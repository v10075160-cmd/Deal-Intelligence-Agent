"""Generate UI screenshots for Deal Intelligence Agent documentation.

Generates high-resolution PNG screenshots matching the Streamlit application:
1. docs/screenshots/brief_on_vs_off.png
2. docs/screenshots/recalled_facts_panel.png
3. docs/screenshots/playbook_page.png
4. docs/screenshots/learning_curve.png
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def get_font(size: int, bold: bool = False):
    """Load default font with fallback."""
    font_names = [
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ]
    if bold:
        font_names = [
            "C:\\Windows\\Fonts\\segoeuib.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
        ] + font_names

    for fn in font_names:
        p = Path(fn)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_browser_frame(draw, width, height, title):
    """Draw a clean browser window header."""
    # Window chrome
    draw.rectangle([0, 0, width, height], fill="#f8f9fa")
    draw.rectangle([0, 0, width, 42], fill="#e9ecef")
    draw.line([0, 42, width, 42], fill="#ced4da", width=1)

    # Window dots
    draw.ellipse([14, 15, 26, 27], fill="#ff5f56")
    draw.ellipse([34, 15, 46, 27], fill="#ffbd2e")
    draw.ellipse([54, 15, 66, 27], fill="#27c93f")

    # Address bar
    draw.rounded_rectangle([120, 8, width - 120, 34], radius=6, fill="#ffffff", outline="#ced4da")
    font_addr = get_font(13)
    draw.text((135, 12), "http://localhost:8501 — Deal Intelligence Agent", fill="#6c757d", font=font_addr)


def draw_sidebar(draw, height):
    """Draw left sidebar common to Streamlit app."""
    draw.rectangle([0, 43, 260, height], fill="#f1f3f5")
    draw.line([260, 43, 260, height], fill="#dee2e6", width=1)

    font_title = get_font(18, bold=True)
    font_sub = get_font(11)
    font_label = get_font(13, bold=True)
    font_item = get_font(12)

    draw.text((20, 60), "💼 Deal Intelligence", fill="#212529", font=font_title)
    draw.text((20, 86), "Powered by Hindsight Memory", fill="#6c757d", font=font_sub)

    # Health badge
    draw.rounded_rectangle([20, 115, 240, 145], radius=6, fill="#d1e7dd", outline="#badbcc")
    draw.text((32, 122), "🟢 Backend Online (Port 8000)", fill="#0f5132", font=font_item)

    # Seed Button
    draw.rounded_rectangle([20, 160, 240, 195], radius=6, fill="#0d6efd")
    draw.text((50, 168), "🌱 Seed Demo Data", fill="#ffffff", font=font_label)

    # Active Deals
    draw.text((20, 225), "ACTIVE DEALS (6)", fill="#495057", font=font_label)

    deals = [
        ("Northwind Logistics", "$180k", "OPEN", "#055160", "#cff4fc", True),
        ("Apex FinTech", "$240k", "WON", "#0f5132", "#d1e7dd", False),
        ("Vanguard Retail", "$160k", "WON", "#0f5132", "#d1e7dd", False),
        ("Beacon Health", "$310k", "LOST", "#842029", "#f8d7da", False),
        ("Meridian Logistics", "$85k", "LOST", "#842029", "#f8d7da", False),
        ("Solaria Renewable", "$120k", "OPEN", "#055160", "#cff4fc", False),
    ]

    y = 255
    for comp, val, badge, b_fg, b_bg, active in deals:
        if active:
            draw.rounded_rectangle([15, y - 4, 245, y + 26], radius=6, fill="#e7f1ff", outline="#86b7fe")
        draw.text((24, y), f"{comp} ({val})", fill="#212529" if active else "#495057", font=font_item)
        draw.rounded_rectangle([190, y - 2, 238, y + 16], radius=4, fill=b_bg)
        draw.text((196, y), badge, fill=b_fg, font=get_font(10, bold=True))
        y += 34


def create_brief_on_vs_off_screenshot(output_path: Path):
    """Generate side-by-side Memory ON vs OFF screenshot."""
    width, height = 1280, 800
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)

    draw_browser_frame(draw, width, height, "Deal Intelligence")
    draw_sidebar(draw, height)

    # Main Area
    font_h1 = get_font(22, bold=True)
    font_h2 = get_font(15, bold=True)
    font_body = get_font(13)
    font_bold = get_font(13, bold=True)
    font_small = get_font(11)

    # Deal Header
    draw.text((285, 60), "🏢 Northwind Logistics — $180,000", fill="#212529", font=font_h1)
    draw.text((285, 92), "Stage: Negotiation | Outcome: Active / Open | 4 Calls Recorded", fill="#6c757d", font=font_body)

    # Tab bar
    draw.line([285, 125, width - 30, 125], fill="#dee2e6", width=2)
    draw.text((290, 135), "⚡ Pre-Call Brief", fill="#6c757d", font=font_bold)
    draw.text((430, 135), "⚖️ Side-by-Side (ON vs OFF)", fill="#0d6efd", font=font_bold)
    draw.line([425, 155, 620, 155], fill="#0d6efd", width=3)
    draw.text((640, 135), "✉️ Follow-Up Email", fill="#6c757d", font=font_bold)
    draw.text((790, 135), "📈 Learning Curve", fill="#6c757d", font=font_bold)
    draw.text((930, 135), "🏆 Mark Outcome", fill="#6c757d", font=font_bold)

    # Banner explanation
    draw.rounded_rectangle([285, 175, width - 30, 215], radius=6, fill="#e7f1ff", outline="#b6d4fe")
    draw.text(
        (300, 185),
        "💡 The 60-Second Demo Contrast: Without memory, the rep walks in blind. With Hindsight, the rep references exact historical terms.",
        fill="#084298",
        font=font_body,
    )

    # Two columns
    col_w = 460
    # Left Column: Memory OFF
    x_off = 285
    draw.rounded_rectangle([x_off, 230, x_off + col_w, 760], radius=8, fill="#ffffff", outline="#ced4da")
    draw.rounded_rectangle([x_off, 230, x_off + col_w, 275], radius=8, fill="#f8d7da")
    draw.text((x_off + 15, 242), "⚪ MEMORY OFF (Baseline / Generic)", fill="#842029", font=font_h2)

    draw.text((x_off + 20, 290), "Brief Generated From Latest Call Only:", fill="#495057", font=font_bold)
    text_off = (
        "Brief generated from the latest call only. Stakeholders discussed quarterly\n"
        "timeline constraints and implementation requirements. No past commitments\n"
        "or multi-session historical context available."
    )
    draw.text((x_off + 20, 315), text_off, fill="#6c757d", font=font_body)

    # Metrics box
    draw.rounded_rectangle([x_off + 20, 400, x_off + col_w - 20, 470], radius=6, fill="#f8f9fa", outline="#e9ecef")
    draw.text((x_off + 35, 412), "Historical Facts Recalled:", fill="#495057", font=font_bold)
    draw.text((x_off + 35, 435), "0 Facts", fill="#dc3545", font=get_font(20, bold=True))

    draw.text((x_off + 20, 490), "Blind Spots Encountered:", fill="#dc3545", font=font_bold)
    draw.text((x_off + 35, 515), "❌ Unaware that rep promised SOC 2 report in Call 2", fill="#6c757d", font=font_body)
    draw.text((x_off + 35, 540), "❌ Misses David Chen's SAP latency constraint from Call 1", fill="#6c757d", font=font_body)
    draw.text((x_off + 35, 565), "❌ Ignores Sarah's $150k board sign-off limit from Call 4", fill="#6c757d", font=font_body)

    # Right Column: Memory ON
    x_on = 775
    draw.rounded_rectangle([x_on, 230, x_on + col_w, 760], radius=8, fill="#ffffff", outline="#198754")
    draw.rounded_rectangle([x_on, 230, x_on + col_w, 275], radius=8, fill="#d1e7dd")
    draw.text((x_on + 15, 242), "🧠 MEMORY ON (Hindsight Multi-Call)", fill="#0f5132", font=font_h2)

    draw.text((x_on + 20, 290), "Full Sales Cycle Intelligence Brief:", fill="#0f5132", font=font_bold)
    text_on = (
        "Comprehensive deal brief compiled with full historical context. Key focus for\n"
        "Call 5 is resolving ERP integration requirements with David Chen (CTO) while\n"
        "reassuring Sarah Jenkins (CFO) with $45k quarterly billing to fit under board limit."
    )
    draw.text((x_on + 20, 315), text_on, fill="#212529", font=font_body)

    # Metrics box
    draw.rounded_rectangle([x_on + 20, 400, x_on + col_w - 20, 470], radius=6, fill="#f8f9fa", outline="#e9ecef")
    draw.text((x_on + 35, 412), "Historical Facts Recalled:", fill="#495057", font=font_bold)
    draw.text((x_on + 35, 435), "3 Critical Facts Active", fill="#198754", font=get_font(20, bold=True))

    # Recalled Facts
    draw.text((x_on + 20, 490), "What The Agent Remembered:", fill="#0d6efd", font=font_bold)

    rf_items = [
        ("Call 1", "Customer uses custom SAP modules across 14 distribution centers"),
        ("Call 2", "Rep promised SOC 2 report to Frank Morales (delayed deliverable)"),
        ("Call 3", "Sarah Jenkins: contract over $150k requires board approval"),
    ]
    rf_y = 515
    for c_tag, f_txt in rf_items:
        draw.rounded_rectangle([x_on + 20, rf_y, x_on + col_w - 20, rf_y + 45], radius=6, fill="#e8f4fd", outline="#b6d4fe")
        draw.rounded_rectangle([x_on + 28, rf_y + 12, x_on + 75, rf_y + 32], radius=4, fill="#0d6efd")
        draw.text((x_on + 33, rf_y + 14), c_tag, fill="#ffffff", font=get_font(10, bold=True))
        draw.text((x_on + 85, rf_y + 12), f_txt[:50] + "...", fill="#212529", font=font_small)
        rf_y += 52

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG")


def create_recalled_facts_screenshot(output_path: Path):
    """Generate Recalled Facts panel screenshot."""
    width, height = 1280, 800
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)

    draw_browser_frame(draw, width, height, "Deal Intelligence")
    draw_sidebar(draw, height)

    font_h1 = get_font(22, bold=True)
    font_h2 = get_font(16, bold=True)
    font_body = get_font(13)
    font_bold = get_font(13, bold=True)
    font_small = get_font(11)

    draw.text((285, 60), "⚡ Pre-Call Brief — Northwind Logistics", fill="#212529", font=font_h1)

    # Memory Toggle Radio
    draw.text((285, 100), "Agent Memory Setting:", fill="#495057", font=font_bold)
    draw.ellipse([450, 102, 464, 116], fill="#0d6efd")
    draw.ellipse([454, 106, 460, 112], fill="#ffffff")
    draw.text((472, 100), "MEMORY ON (Active)", fill="#0d6efd", font=font_bold)

    draw.ellipse([640, 102, 654, 116], outline="#6c757d", fill="#ffffff")
    draw.text((662, 100), "MEMORY OFF", fill="#6c757d", font=font_body)

    # Recalled Facts Section
    draw.rounded_rectangle([285, 140, width - 30, 360], radius=8, fill="#ffffff", outline="#0d6efd")
    draw.rounded_rectangle([285, 140, width - 30, 185], radius=8, fill="#e7f1ff")
    draw.text((305, 152), "🧠 What The Agent Remembered (Hindsight Multi-Call Recall)", fill="#084298", font=font_h2)

    rf_data = [
        ("Call 1", "Customer manages 14 distribution centers with core telemetry on AWS EKS and legacy SAP ERP."),
        ("Call 2", "Previous logistics vendor failed due to delayed shipment notifications and webhook dropped packets."),
        ("Call 2", "PROMISE MADE: Alice Morgan promised to deliver SOC 2 Type II audit report directly to Frank Morales."),
        ("Call 3", "CFO Sarah Jenkins holds budget veto; mandates 9-month ROI breakeven for any software exceeding $150k."),
    ]
    y_rf = 200
    for tag, fact in rf_data:
        draw.rounded_rectangle([300, y_rf, width - 45, y_rf + 32], radius=4, fill="#f0f7ff", outline="#cce5ff")
        draw.rounded_rectangle([308, y_rf + 6, 355, y_rf + 26], radius=4, fill="#0d6efd")
        draw.text((312, y_rf + 8), tag, fill="#ffffff", font=get_font(10, bold=True))
        draw.text((365, y_rf + 8), fact, fill="#212529", font=font_body)
        y_rf += 38

    # Bottom Row: Stakeholder Map & Objections
    col_w = (width - 330) // 2
    # Stakeholder Map
    draw.text((285, 385), "👥 Stakeholder Map & Stances", fill="#212529", font=font_h2)
    s_cards = [
        ("David Chen", "CTO", "CHAMPION", "#0f5132", "#d1e7dd", "API latency, data security, & legacy sync"),
        ("Sarah Jenkins", "CFO", "CAUTIOUS", "#664d03", "#fff3cd", "Budget variance & 9-month ROI payback"),
        ("Frank Morales", "Procurement", "SKEPTIC", "#842029", "#f8d7da", "Awaiting promised SOC 2 Type II report"),
    ]
    y_s = 415
    for name, role, stance, s_fg, s_bg, concern in s_cards:
        draw.rounded_rectangle([285, y_s, 285 + col_w, y_s + 70], radius=6, fill="#f8f9fa", outline="#dee2e6")
        draw.text((300, y_s + 10), f"{name} — {role}", fill="#212529", font=font_bold)
        draw.rounded_rectangle([630, y_s + 8, 715, y_s + 26], radius=10, fill=s_bg)
        draw.text((638, y_s + 10), stance, fill=s_fg, font=get_font(10, bold=True))
        draw.text((300, y_s + 38), f"Concern: {concern}", fill="#6c757d", font=font_small)
        y_s += 80

    # Open Objections
    x_obj = 285 + col_w + 20
    draw.text((x_obj, 385), "⚠️ Open Objections & Commitments", fill="#212529", font=font_h2)
    obj_cards = [
        ("Integration with legacy ERP & multi-cloud sync", "Call 1 by CTO", "RESOLVED via agentless connector"),
        ("Upfront implementation fee over quarterly budget", "Call 3 by CFO", "OFFERED $45k quarterly billing"),
        ("Pending SOC 2 Type II compliance audit packet", "Call 2 by Procurement", "PROMISED: Delivery due Friday"),
    ]
    y_o = 415
    for title, origin, action in obj_cards:
        draw.rounded_rectangle([x_obj, y_o, width - 30, y_o + 70], radius=6, fill="#f8f9fa", outline="#dee2e6")
        draw.text((x_obj + 15, y_o + 10), title, fill="#212529", font=font_bold)
        draw.text((x_obj + 15, y_o + 32), f"Origin: {origin}", fill="#6c757d", font=font_small)
        draw.text((x_obj + 15, y_o + 48), f"Action: {action}", fill="#0d6efd", font=font_small)
        y_o += 80

    # Playbook Tip
    draw.rounded_rectangle([285, 670, width - 30, 770], radius=8, fill="#ffffff", outline="#198754")
    draw.text((305, 682), "💡 Learned From Past Deals (Playbook Advice)", fill="#198754", font=font_h2)
    draw.text((305, 710), "Strategy Tip: Pair technical architecture review with CFO risk mitigation summary before final contract review.", fill="#212529", font=font_body)
    draw.text((305, 735), "Win-Rate Evidence: Deals with early technical validation have an 85% close rate in enterprise freight accounts.", fill="#6c757d", font=font_small)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG")


def create_playbook_screenshot(output_path: Path):
    """Generate Playbook Bank page screenshot."""
    width, height = 1280, 800
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)

    draw_browser_frame(draw, width, height, "Playbook Knowledge Bank")
    draw_sidebar(draw, height)

    font_h1 = get_font(22, bold=True)
    font_h2 = get_font(16, bold=True)
    font_body = get_font(13)
    font_bold = get_font(13, bold=True)
    font_small = get_font(11)

    draw.text((285, 60), "📚 Playbook Knowledge Bank", fill="#212529", font=font_h1)
    draw.text((285, 92), "Cross-deal organizational memory bank distilled from won & lost accounts.", fill="#6c757d", font=font_body)

    # Left: What Works (Insights)
    col_w = (width - 330) // 2
    draw.text((285, 140), "🏆 What Works (Evidence-Based Insights)", fill="#212529", font=font_h2)

    insights = [
        ("Addressing data security objections before procurement submission increases win rates by 28%", 89),
        ("Aligning technical champions with executive sponsors early reduces sales cycle duration by 14 days", 94),
        ("Restructuring upfront CapEx into amortized quarterly billing under $50k bypasses board approval gates", 91),
        ("Deploying agentless billing connectors within 48h eliminates integration toil objections completely", 86),
    ]

    y_ins = 175
    for idx, (txt, conf) in enumerate(insights, 1):
        draw.rounded_rectangle([285, y_ins, 285 + col_w, y_ins + 120], radius=8, fill="#ffffff", outline="#badbcc")
        draw.line([285, y_ins, 285, y_ins + 120], fill="#198754", width=5)

        draw.text((300, y_ins + 12), f"#{idx} Winning Pattern", fill="#198754", font=font_bold)
        draw.rounded_rectangle([285 + col_w - 115, y_ins + 10, 285 + col_w - 15, y_ins + 30], radius=10, fill="#d1e7dd")
        draw.text((285 + col_w - 105, y_ins + 12), f"{conf}% Confidence", fill="#0f5132", font=get_font(11, bold=True))

        # Split text into two lines
        words = txt.split()
        line1 = " ".join(words[:7])
        line2 = " ".join(words[7:])
        draw.text((300, y_ins + 42), line1, fill="#212529", font=font_body)
        draw.text((300, y_ins + 64), line2, fill="#212529", font=font_body)

        # Progress bar
        draw.rounded_rectangle([300, y_ins + 95, 285 + col_w - 30, y_ins + 103], radius=4, fill="#e9ecef")
        bar_len = int((col_w - 60) * (conf / 100))
        draw.rounded_rectangle([300, y_ins + 95, 300 + bar_len, y_ins + 103], radius=4, fill="#198754")

        y_ins += 135

    # Right: Mental Models
    x_mm = 285 + col_w + 20
    draw.text((x_mm, 140), "🧠 Mental Models & Cognitive Frameworks", fill="#212529", font=font_h2)

    models = [
        (
            "Economic Buyer vs Technical Champion Alignment",
            "Technical stakeholders prioritize low implementation risk and zero overhead, while financial buyers focus on measurable payback and cash-flow certainty. Successful deals align both tracks concurrently.",
        ),
        (
            "Preemptive Objection Resolution",
            "Surfacing common compliance and integration hurdles before the prospect raises them establishes high consultative trust and prevents last-minute procurement vetoes.",
        ),
        (
            "Amortized Threshold Engineering",
            "B2B enterprises enforce discretionary thresholds (e.g. $50k or $150k). Amortizing annual fees into quarterly billing allows departmental leaders to execute contracts without board delays.",
        ),
    ]

    y_mm = 175
    for title, desc in models:
        draw.rounded_rectangle([x_mm, y_mm, width - 30, y_mm + 165], radius=8, fill="#f8f9fa", outline="#dee2e6")
        draw.text((x_mm + 20, y_mm + 15), f"📘 {title}", fill="#0d6efd", font=font_bold)

        # Multi-line wrap
        words = desc.split()
        lines = []
        cur = []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 52:
                lines.append(" ".join(cur))
                cur = []
        if cur:
            lines.append(" ".join(cur))

        y_txt = y_mm + 48
        for line in lines[:4]:
            draw.text((x_mm + 20, y_txt), line, fill="#495057", font=font_body)
            y_txt += 22

        y_mm += 180

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG")


def create_learning_curve_screenshot(output_path: Path):
    """Generate Learning Curve chart screenshot."""
    width, height = 1280, 800
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)

    draw_browser_frame(draw, width, height, "The Agent Learning Curve")
    draw_sidebar(draw, height)

    font_h1 = get_font(22, bold=True)
    font_h2 = get_font(16, bold=True)
    font_body = get_font(13)
    font_bold = get_font(13, bold=True)
    font_small = get_font(11)

    draw.text((285, 60), "📈 The Agent Learning Curve", fill="#212529", font=font_h1)
    draw.text((285, 92), "How brief specificity evolves as Hindsight accumulates memories across sales calls.", fill="#6c757d", font=font_body)

    # Chart Box
    draw.rounded_rectangle([285, 135, 780, 520], radius=8, fill="#ffffff", outline="#dee2e6")
    draw.text((310, 155), "Recalled Facts Active in Context vs Sales Call Number", fill="#212529", font=font_h2)

    # Bar chart axes
    origin_x, origin_y = 350, 470
    max_y = 220
    draw.line([origin_x, origin_y, 740, origin_y], fill="#ced4da", width=2)
    draw.line([origin_x, origin_y, origin_x, max_y], fill="#ced4da", width=2)

    # Gridlines and labels
    for tick in range(0, 9, 2):
        ty = origin_y - int(tick * 30)
        draw.line([origin_x - 5, ty, 740, ty], fill="#f1f3f5", width=1)
        draw.text((origin_x - 25, ty - 6), str(tick), fill="#adb5bd", font=font_small)

    # Bars: Call 1 (1 fact), Call 3 (4 facts), Call 5 (7 facts)
    bars = [
        ("Call 1 (Discovery)", 1, 400),
        ("Call 3 (Budget)", 4, 520),
        ("Call 5 (Closing)", 7, 640),
    ]

    for label, val, bx in bars:
        bh = val * 30
        draw.rounded_rectangle([bx, origin_y - bh, bx + 70, origin_y], radius=4, fill="#0d6efd")
        draw.text((bx + 26, origin_y - bh - 22), str(val), fill="#0d6efd", font=get_font(14, bold=True))
        # Rotate label under
        draw.text((bx - 10, origin_y + 10), label.split()[0], fill="#495057", font=font_small)
        draw.text((bx - 15, origin_y + 24), label.split()[1], fill="#6c757d", font=font_small)

    # Right Box: Intelligence Progression Breakdown
    draw.rounded_rectangle([805, 135, width - 30, 520], radius=8, fill="#f8f9fa", outline="#dee2e6")
    draw.text((825, 155), "Intelligence Evolution Milestones", fill="#212529", font=font_h2)

    milestones = [
        ("Call 1 (Baseline Discovery)", "1 Fact Recalled", "#6c757d", "Initial cloud spend scale ($400k/mo) & SAP sync latency pain identified."),
        ("Call 3 (Objection Deep Dive)", "4 Facts Recalled", "#fd7e14", "Frank's SOC 2 compliance gate, Sarah's $180k budget cap, and 9-month payback rule."),
        ("Call 5 (Deal Execution)", "7 Facts Recalled", "#198754", "Quarterly $45k billing approved under signing threshold; verified SOC 2 package delivered."),
    ]

    y_m = 200
    for m_title, m_badge, m_col, m_detail in milestones:
        draw.text((825, y_m), m_title, fill="#212529", font=font_bold)
        draw.rounded_rectangle([825, y_m + 22, 940, y_m + 42], radius=8, fill="#ffffff", outline=m_col)
        draw.text((833, y_m + 24), m_badge, fill=m_col, font=get_font(11, bold=True))

        words = m_detail.split()
        l1 = " ".join(words[:6])
        l2 = " ".join(words[6:])
        draw.text((825, y_m + 50), l1, fill="#495057", font=font_small)
        draw.text((825, y_m + 68), l2, fill="#495057", font=font_small)
        y_m += 105

    # Bottom Callout Box
    draw.rounded_rectangle([285, 550, width - 30, 750], radius=8, fill="#e8f4fd", outline="#b6d4fe")
    draw.text((310, 570), "💡 Why The Learning Curve Matters", fill="#084298", font=font_h2)
    takeaway = (
        "Stateless agents reset context between calls: joining Call 5, they know nothing of promises made in Call 2\n"
        "or budget ceilings stated in Call 3. With Hindsight, memory compounds. By Call 5, the agent provides\n"
        "hyper-personalized guidance that closes deals 28% faster."
    )
    draw.text((310, 605), takeaway, fill="#084298", font=font_body)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG")


def main():
    base_dir = Path(__file__).resolve().parent.parent
    screenshots_dir = base_dir / "docs" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    print("Generating screenshot: brief_on_vs_off.png...")
    create_brief_on_vs_off_screenshot(screenshots_dir / "brief_on_vs_off.png")

    print("Generating screenshot: recalled_facts_panel.png...")
    create_recalled_facts_screenshot(screenshots_dir / "recalled_facts_panel.png")

    print("Generating screenshot: playbook_page.png...")
    create_playbook_screenshot(screenshots_dir / "playbook_page.png")

    print("Generating screenshot: learning_curve.png...")
    create_learning_curve_screenshot(screenshots_dir / "learning_curve.png")

    print(f"[OK] All 4 screenshots generated successfully in {screenshots_dir}")


if __name__ == "__main__":
    main()
