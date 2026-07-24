"""
generate_sample_data.py — Builds the dashboard's parquet tables.

Every static figure here (budget categories, schedule tasks, risks, issues,
vendors, stakeholders) is copied directly from the PM Tracking Workbooks in
../../dtw-it-center-pm-toolkit/01-construction-infrastructure-project/ and
02-technology-project/ — same source of truth as the published Word/Excel
documents, so the dashboard tells the same story as the artifacts it
visualizes rather than a separately-invented one.

The only *invented* data is the monthly time series (cumulative spend,
cumulative schedule %, open risk/issue counts): the workbooks only capture
two fixed points in time per project (current status-report month, and
final closeout), so a monthly history is synthesized between those known
anchors with a smoothstep ease + small seeded noise, purely so the burn-down
and schedule-curve charts have a trend to show.

Run: python data/generate_sample_data.py
"""

from pathlib import Path
import numpy as np
import pandas as pd

SAMPLE_DIR = Path(__file__).parent / "sample"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(42)

CONSTRUCTION = "Construction/Infrastructure"
TECHNOLOGY = "Technology"

# ───────────────────────── Projects ─────────────────────────
projects = pd.DataFrame([
    {
        "project_id": CONSTRUCTION,
        "project_name": "IT Center Data Center & NOC Build-Out",
        "project_type": CONSTRUCTION,
        "sponsor": "Director, Facilities & Infrastructure",
        "project_manager": "Lisa Lewandowski",
        "duration_months": 14,
        "current_month": 9,
        "total_budget": 4250000,
        "contingency": 340000,
        "current_actual_total": 3069000,
        "final_actual_total": 4168400,
        "overall_status": "Yellow",
        "schedule_status": "Yellow — 6 business days behind due to switchgear lead time",
        "budget_status": "Green — 2% under committed forecast",
        "current_pct_complete": 64,
    },
    {
        "project_id": TECHNOLOGY,
        "project_name": "IT Center Network & Airport Operations Systems Modernization",
        "project_type": TECHNOLOGY,
        "sponsor": "Director, Technology Services",
        "project_manager": "Lisa Lewandowski",
        "duration_months": 9,
        "current_month": 6,
        "total_budget": 2650000,
        "contingency": 185000,
        "current_actual_total": 2079000,
        "final_actual_total": 2611400,
        "overall_status": "Green",
        "schedule_status": "Green — on baseline",
        "budget_status": "Yellow — SIEM licensing scope addition tracked as Change Request",
        "current_pct_complete": 68,
    },
])
projects.to_parquet(SAMPLE_DIR / "projects.parquet", index=False)

# ───────────────────────── Schedule tasks (WBS) ─────────────────────────
construction_schedule = [
    ("Design & Permitting", "1.0", "Schematic & design development", "MEP Engineer of Record", 1, 3, 100, "Complete"),
    ("Design & Permitting", "1.1", "Permit submission & AHJ approval", "PM", 2, 3, 100, "Complete"),
    ("Sitework & Foundation", "2.0", "Sitework, excavation, foundation pour", "General Contractor", 3, 5, 100, "Complete"),
    ("Structural & Shell", "3.0", "Structural steel, envelope, roof dry-in", "General Contractor", 5, 7, 100, "Complete"),
    ("MEP Rough-In", "4.0", "Electrical rough-in (power, UPS, generator)", "Electrical Subcontractor", 7, 9, 80, "In Progress"),
    ("MEP Rough-In", "4.1", "Mechanical rough-in (cooling, containment)", "Mechanical Subcontractor", 7, 9, 65, "In Progress"),
    ("MEP Rough-In", "4.2", "Fire suppression rough-in", "Fire Protection Subcontractor", 8, 9, 90, "In Progress"),
    ("Finishes & Security", "5.0", "Raised floor, cable tray, finishes", "General Contractor", 9, 11, 0, "Not Started"),
    ("Finishes & Security", "5.1", "Badge access, mantrap, CCTV install", "Security Systems Integrator", 10, 11, 0, "Not Started"),
    ("Commissioning", "6.0", "Level 1-2 Cx (startup, functional test)", "Commissioning Agent", 12, 13, 0, "Not Started"),
    ("Commissioning", "6.1", "Level 3-4 Cx (integrated systems test)", "Commissioning Agent", 13, 13, 0, "Not Started"),
    ("Handover", "7.0", "O&M training, as-built turnover, Substantial Completion", "PM", 14, 14, 0, "Not Started"),
]
technology_schedule = [
    ("Design", "1.0", "Requirements gathering & technical design", "Network Engineering Lead", 1, 1, 100, "Complete"),
    ("Design", "1.1", "Technical standards / change-control approval", "PM", 1, 1, 100, "Complete"),
    ("Procurement", "2.0", "Vendor procurement (switches, routers, SIEM)", "PM", 2, 2, 100, "Complete"),
    ("Backbone Install", "3.0", "Fiber backbone install (dependent on facility handover)", "Systems Integrator", 3, 4, 100, "Complete"),
    ("Backbone Install", "3.1", "Backbone testing & validation", "Network Engineering Lead", 4, 4, 100, "Complete"),
    ("Core Cutover", "4.0", "Core network cutover — all concourses", "Network Engineering Lead", 5, 5, 100, "Complete"),
    ("Systems Migration", "5.0", "Passenger processing system migration", "Systems Integrator", 6, 6, 100, "Complete"),
    ("Systems Migration", "5.1", "Baggage handling system migration", "Systems Integrator", 6, 7, 85, "In Progress"),
    ("Systems Migration", "5.2", "Access-control/security system migration", "Systems Integrator", 7, 7, 0, "Not Started"),
    ("Monitoring & Hardening", "6.0", "Monitoring/SIEM platform go-live", "Cybersecurity Lead", 7, 8, 40, "In Progress"),
    ("Monitoring & Hardening", "6.1", "Cybersecurity hardening checklist", "Cybersecurity Lead", 8, 8, 0, "Not Started"),
    ("Training & Closeout", "7.0", "Training, hypercare & project closeout", "PM", 9, 9, 0, "Not Started"),
]


def schedule_df(rows, project_id):
    df = pd.DataFrame(rows, columns=["phase", "wbs_id", "task", "owner", "start_month", "end_month", "pct_complete", "status"])
    df.insert(0, "project_id", project_id)
    return df


schedule = pd.concat([
    schedule_df(construction_schedule, CONSTRUCTION),
    schedule_df(technology_schedule, TECHNOLOGY),
], ignore_index=True)
schedule.to_parquet(SAMPLE_DIR / "schedule.parquet", index=False)

# ───────────────────────── Milestones ─────────────────────────
milestones = pd.DataFrame([
    (CONSTRUCTION, "Design Development & Permitting Complete", 3, "Complete"),
    (CONSTRUCTION, "Sitework & Foundation Complete", 5, "Complete"),
    (CONSTRUCTION, "Structural Shell & Building Dry-In", 7, "Complete"),
    (CONSTRUCTION, "MEP Rough-In Complete", 9, "In Progress"),
    (CONSTRUCTION, "Raised Floor, Security & Finishes Complete", 11, "Not Started"),
    (CONSTRUCTION, "Commissioning (Cx) Complete", 13, "Not Started"),
    (CONSTRUCTION, "Substantial Completion & Handover to Operations", 14, "Not Started"),
    (TECHNOLOGY, "Requirements & Technical Design Approved", 1, "Complete"),
    (TECHNOLOGY, "Vendor Procurement & Core Equipment Delivered", 2, "Complete"),
    (TECHNOLOGY, "Fiber Backbone Installed & Tested", 4, "Complete"),
    (TECHNOLOGY, "Core Network Cutover Complete", 5, "Complete"),
    (TECHNOLOGY, "Operations Systems Migration Complete", 7, "In Progress"),
    (TECHNOLOGY, "Monitoring & Cybersecurity Hardening Complete", 8, "Not Started"),
    (TECHNOLOGY, "Training, Hypercare & Project Closeout", 9, "Not Started"),
], columns=["project_id", "milestone", "month", "status"])
milestones.to_parquet(SAMPLE_DIR / "milestones.parquet", index=False)

# ───────────────────────── Budget categories ─────────────────────────
construction_budget = [
    ("Sitework & Foundation", 650000, 650000, 645000),
    ("Structural / Shell", 850000, 850000, 838000),
    ("Electrical (Power/UPS/Generator)", 1000000, 903000, 810000),
    ("Mechanical (Cooling)", 780000, 573000, 507000),
    ("Fire Suppression", 170000, 166000, 160000),
    ("Raised Floor & Finishes", 210000, 0, 0),
    ("Security Systems", 150000, 0, 0),
    ("Permits & Fees", 50000, 50000, 48000),
    ("Commissioning", 50000, 0, 0),
    ("Contingency", 340000, 61000, 61000),
]
technology_budget = [
    ("Network Hardware (switches/routers)", 980000, 970000, 965000),
    ("Fiber/Cabling Installation", 310000, 300000, 298000),
    ("Systems Migration (Integrator Labor)", 540000, 420000, 385000),
    ("Monitoring / SIEM Platform", 260000, 268000, 268000),
    ("Cybersecurity Hardening", 150000, 40000, 20000),
    ("Training & Documentation", 90000, 0, 0),
    ("Vendor Support / Warranty (Yr 1)", 135000, 135000, 135000),
    ("Contingency", 185000, 8000, 8000),
]


def budget_df(rows, project_id):
    df = pd.DataFrame(rows, columns=["category", "budgeted", "committed", "actual"])
    df.insert(0, "project_id", project_id)
    df["variance"] = df["actual"] - df["budgeted"]
    df["pct_used"] = (df["actual"] / df["budgeted"]).replace([np.inf, -np.inf], 0).fillna(0)
    return df


budget = pd.concat([
    budget_df(construction_budget, CONSTRUCTION),
    budget_df(technology_budget, TECHNOLOGY),
], ignore_index=True)
budget.to_parquet(SAMPLE_DIR / "budget.parquet", index=False)

# ───────────────────────── Risks ─────────────────────────
construction_risks = [
    ("R1", "Utility feeder capacity insufficient for dual-feed design", "Technical/Utility", 2, 5, "Confirm capacity at Design Development; secure utility commitment letter before GMP lock", "PM / MEP Engineer", "Closed"),
    ("R2", "Long-lead equipment (generator, UPS, chillers) delayed", "Procurement", 3, 4, "Order at Notice to Proceed; track supplier milestones monthly", "PM", "Monitoring"),
    ("R3", "Medium-voltage switchgear lead time extends 4+ weeks", "Procurement", 4, 4, "Expedite fee approved; resequence rough-in to protect Cx start", "PM / MEP Engineer", "Open"),
    ("R4", "Weather delays to sitework/foundation", "Environmental", 3, 3, "Schedule float built into sitework phase; monitor forecast weekly", "General Contractor", "Closed"),
    ("R5", "Unforeseen underground utilities/soil conditions", "Site", 2, 4, "Geotechnical survey completed pre-GMP; contingency reserved", "General Contractor", "Closed"),
    ("R6", "AHJ inspection delays or repeat re-inspections", "Regulatory", 3, 3, "Pre-submission code walkthrough with AHJ at 60% design", "PM", "Monitoring"),
    ("R7", "Contractor badge/security clearance delays site access", "Security", 2, 3, "Submit badge requests 3 weeks ahead of trade mobilization", "PM / Security Liaison", "Monitoring"),
]
technology_risks = [
    ("R1", "Cutover causes unplanned outage to live operations systems", "Operational", 2, 5, "Overnight low-traffic windows; rollback plan rehearsed pre-cutover", "PM / Network Eng Lead", "Closed"),
    ("R2", "Vendor equipment delivery delayed post-PO", "Procurement", 2, 4, "PO issued with confirmed lead times; weekly vendor status check", "PM", "Closed"),
    ("R3", "Airline tenant testing availability conflicts compress migration window", "Coordination", 3, 2, "Build float into migration schedule; confirm liaison availability early", "PM", "Monitoring"),
    ("R4", "Cybersecurity hardening review surfaces additional licensing/scope needs", "Technical", 3, 3, "Change Request process; fund from contingency if approved", "Cybersecurity Lead", "Open"),
    ("R5", "Post-go-live ticket spike from training gaps", "Adoption", 3, 3, "Hypercare staffing plan sized per migrated system; 30-day exit review", "Help Desk Manager", "Monitoring"),
    ("R6", "Data migration integrity issue (records lost/corrupted in transfer)", "Technical", 2, 5, "Full backup before each migration event; acceptance test before decommissioning legacy system", "Systems Integrator", "Monitoring"),
]


def risk_df(rows, project_id):
    df = pd.DataFrame(rows, columns=["risk_id", "description", "category", "probability", "impact", "response", "owner", "status"])
    df.insert(0, "project_id", project_id)
    df["score"] = df["probability"] * df["impact"]
    return df


risks = pd.concat([
    risk_df(construction_risks, CONSTRUCTION),
    risk_df(technology_risks, TECHNOLOGY),
], ignore_index=True)
risks.to_parquet(SAMPLE_DIR / "risks.parquet", index=False)

# ───────────────────────── Quality Control Checklist ─────────────────────────
construction_quality = [
    ("Foundation / sitework inspection", "Structural", "Passes AHJ foundation inspection; geotechnical sign-off", "AHJ inspection", "Pass", "Month 5", "General Contractor"),
    ("MEP rough-in inspection (electrical, mechanical, fire)", "MEP", "Passes AHJ rough-in inspection; matches approved design", "AHJ inspection", "In Progress", "Month 9", "GC / Subcontractors"),
    ("Level 1-2 Commissioning (equipment startup, functional test)", "Commissioning", "Equipment operates to manufacturer spec under static and functional test", "Commissioning Agent witness test", "Not Started", "Month 12-13", "Commissioning Agent"),
    ("Level 3-4 Commissioning (integrated systems, simulated load/failure)", "Commissioning", "Power/cooling failover performs to design under simulated utility failure and full IT load", "Commissioning Agent witness test", "Not Started", "Month 13", "Commissioning Agent"),
    ("Final punch-list walkthrough", "Closeout", "No open life-safety items; all other items logged with an owner and due date", "Joint GC / IT Ops walkthrough", "Not Started", "Month 14", "PM"),
]
technology_quality = [
    ("Fiber backbone install & test", "Network", "Backbone validated at full design capacity with redundant failover", "Systems Integrator test + Network Eng witness", "Pass", "Month 4", "Network Engineering Lead"),
    ("Core network cutover", "Network", "All concourses live on new core with zero unplanned downtime", "Post-cutover monitoring review", "Pass", "Month 5", "Network Engineering Lead"),
    ("Operations system migration (passenger/baggage/access-control)", "Systems Migration", "Full backup taken; system passes functional acceptance test before legacy decommission", "Systems Integrator acceptance test", "In Progress", "Month 6-7", "Systems Integrator"),
    ("Cybersecurity hardening checklist", "Security", "Segmentation, MFA, and patch compliance verified against technical standards", "Cybersecurity Lead sign-off", "In Progress", "Month 8", "Cybersecurity Lead"),
    ("Go-live / hypercare exit review", "Closeout", "Support ticket volume returns to steady-state within 30 days", "Help Desk metrics review", "Not Started", "Month 9", "PM"),
]


def quality_df(rows, project_id):
    df = pd.DataFrame(rows, columns=["checkpoint", "category", "acceptance_criteria", "method", "status", "target", "owner"])
    df.insert(0, "project_id", project_id)
    return df


quality = pd.concat([
    quality_df(construction_quality, CONSTRUCTION),
    quality_df(technology_quality, TECHNOLOGY),
], ignore_index=True)
quality.to_parquet(SAMPLE_DIR / "quality.parquet", index=False)

# ───────────────────────── Issues & Changes ─────────────────────────
construction_issues = [
    ("I1", "Issue", "Switchgear supplier confirmed 4-week lead-time extension", 8, "PM", "High", "Open"),
    ("I2", "Issue", "AHJ requested additional egress-lighting detail before rough-in sign-off", 9, "General Contractor", "Medium", "Resolved"),
    ("C1", "Change", "Add emergency egress lighting circuit not in original electrical design (+$18,200)", 9, "MEP Engineer", "Medium", "Approved"),
]
technology_issues = [
    ("I3", "Issue", "Airline tenant requested a later testing slot, compressing migration window", 6, "PM", "Low", "Resolved"),
    ("C2", "Change", "Additional SIEM log-source licensing required after hardening review (+$8,000)", 6, "Cybersecurity Lead", "Medium", "Approved"),
]


def issues_df(rows, project_id):
    df = pd.DataFrame(rows, columns=["item_id", "type", "description", "month_raised", "owner", "priority", "status"])
    df.insert(0, "project_id", project_id)
    return df


issues = pd.concat([
    issues_df(construction_issues, CONSTRUCTION),
    issues_df(technology_issues, TECHNOLOGY),
], ignore_index=True)
issues.to_parquet(SAMPLE_DIR / "issues.parquet", index=False)

# ───────────────────────── Vendors ─────────────────────────
construction_vendors = [
    ("General Contractor", "Design-build GC services; site supervision", 2450000, "Meets expectations"),
    ("Electrical Subcontractor", "Power distribution, UPS, generator install", 1450000, "Meets expectations"),
    ("Mechanical Subcontractor", "Precision cooling, chillers, containment", 980000, "Meets expectations"),
    ("Security Systems Integrator", "Badge access, mantrap, CCTV, monitoring", 190000, "Not yet rated"),
    ("Commissioning Agent", "Level 1-4 commissioning oversight", 130000, "Meets expectations"),
    ("Generator/UPS Equipment Vendor", "Long-lead equipment supply", 890000, "Watch — lead-time slip"),
]
technology_vendors = [
    ("Network Equipment OEM", "Core/distribution switches, routers, licensing", 980000, "Meets expectations"),
    ("Systems Integrator", "Fiber install, systems migration, cutover execution", 850000, "Meets expectations"),
    ("SIEM/Monitoring Platform Vendor", "Monitoring platform license & implementation support", 268000, "Meets expectations"),
    ("Fiber/Cabling Contractor", "Backbone cable install & termination", 300000, "Meets expectations"),
]


def vendor_df(rows, project_id):
    df = pd.DataFrame(rows, columns=["vendor", "scope", "contract_value", "rating"])
    df.insert(0, "project_id", project_id)
    return df


vendors = pd.concat([
    vendor_df(construction_vendors, CONSTRUCTION),
    vendor_df(technology_vendors, TECHNOLOGY),
], ignore_index=True)
vendors.to_parquet(SAMPLE_DIR / "vendors.parquet", index=False)

# ───────────────────────── Stakeholders ─────────────────────────
construction_stakeholders = [
    ("Director, Facilities & Infrastructure", "Executive sponsor; capital budget owner", "H", "H"),
    ("IT Center Operations Manager", "Receiving owner; will operate the facility", "H", "M"),
    ("General Contractor Project Manager", "Delivers construction on schedule/budget", "H", "M"),
    ("MEP Engineer of Record", "Design authority for power/cooling/fire systems", "M", "M"),
    ("Airport Security / Badging Office", "Controls contractor site access", "M", "L"),
    ("Local Building Department (AHJ)", "Permit approval and inspections", "M", "L"),
    ("Airport Authority Capital Committee", "Approves capital funding, monitors GMP", "H", "H"),
]
technology_stakeholders = [
    ("Director, Technology Services", "Executive sponsor; budget owner", "H", "H"),
    ("Network Engineering Lead", "Owns technical design & cutover execution", "H", "M"),
    ("Cybersecurity Lead", "Owns hardening standards & sign-off", "M", "M"),
    ("Airport Operations Director", "Approves cutover windows; receiving owner", "H", "H"),
    ("Airline Tenant IT Liaisons", "Coordinate shared-system testing", "M", "L"),
    ("Systems Integrator Project Manager", "Delivers migration & cutover work", "M", "M"),
    ("Help Desk Manager", "Owns end-user support & hypercare", "M", "L"),
]


def stakeholder_df(rows, project_id):
    df = pd.DataFrame(rows, columns=["stakeholder", "interest_note", "influence", "interest"])
    df.insert(0, "project_id", project_id)
    infl_map = {"H": 3, "M": 2, "L": 1}
    df["influence_score"] = df["influence"].map(infl_map)
    df["interest_score"] = df["interest"].map(infl_map)
    return df


stakeholders = pd.concat([
    stakeholder_df(construction_stakeholders, CONSTRUCTION),
    stakeholder_df(technology_stakeholders, TECHNOLOGY),
], ignore_index=True)
stakeholders.to_parquet(SAMPLE_DIR / "stakeholders.parquet", index=False)

# ───────────────────────── Closeout: final summary vs. baseline ─────────────
final_summary = pd.DataFrame([
    (CONSTRUCTION, "Schedule", "Month 14 Substantial Completion", "Month 14 + 6 business days", "+6 business days (switchgear lead time; recovered via compression)"),
    (CONSTRUCTION, "Budget", "$4,250,000 GMP", "$4,168,400", "-$81,600 (1.9% under GMP)"),
    (CONSTRUCTION, "Scope", "9,000 sq. ft. data center/NOC shell + N+1 MEP + security rough-in", "Delivered as baselined; one approved Change Order for added egress lighting", "1 Change Order, $18,200 (within contingency)"),
    (TECHNOLOGY, "Schedule", "Month 9 closeout", "Month 9 (on baseline)", "On time"),
    (TECHNOLOGY, "Budget", "$2,650,000", "$2,611,400", "-$38,600 (1.5% under budget)"),
    (TECHNOLOGY, "Scope", "Network refresh + systems migration + monitoring/security hardening + training", "Delivered as baselined; one approved Change Request (SIEM licensing, +$8,000)", "1 Change Request, within contingency"),
], columns=["project_id", "dimension", "baseline", "final", "variance"])
final_summary.to_parquet(SAMPLE_DIR / "final_summary.parquet", index=False)

# ───────────────────────── Closeout: lessons learned ─────────────
construction_lessons = {
    "Went Well": [
        "Ordering long-lead electrical/mechanical equipment at Notice to Proceed absorbed most supply-chain risk before it could hit the critical path.",
        "Weekly GC site meetings with a standing RFI/submittal log kept design clarifications from stalling rough-in work.",
        "Early, direct coordination with Airport Security on contractor badging avoided access delays during the finishes phase.",
    ],
    "Could Improve": [
        "Switchgear lead time should have been reconfirmed with the supplier at the 60%-design milestone, not only at order placement.",
        "AHJ egress-lighting requirements surfaced late; a pre-submission code walkthrough with the AHJ earlier in Design Development would have caught this.",
    ],
    "Recommendations": [
        "For future data-center builds, add a supplier lead-time reconfirmation checkpoint at each design milestone for all long-lead MEP equipment.",
        "Schedule an informal AHJ pre-review at 60% design for any project with life-safety systems (egress, fire suppression) to reduce re-inspection cycles.",
    ],
    "Outstanding / Transition": [
        "Two minor punch-list items (door hardware adjustment, label plate reorder) — owner: GC, due within 30 days of handover.",
        "Transition of the facility to the companion Network & Systems Modernization project for technology fit-out — owner: PM, kickoff scheduled next reporting period.",
    ],
}
technology_lessons = {
    "Went Well": [
        "Scheduling cutovers in coordination with Airport Operations' event calendar, rather than a fixed date, avoided every high-traffic conflict.",
        "Bringing the Systems Integrator into technical design early reduced rework during the migration phase.",
        "A written cutover runbook shared with airline tenant IT liaisons in advance kept coordination issues to scheduling only, not technical surprises.",
    ],
    "Could Improve": [
        "Cybersecurity hardening requirements (SIEM log sources) should have been scoped against the full system inventory during Technical Design, not discovered during hardening.",
        "Hypercare staffing was sized for baggage/passenger systems; access-control ticket volume ran slightly higher than planned in week one.",
    ],
    "Recommendations": [
        "For future migrations, include a full log-source inventory pass as a Technical Design deliverable, not a hardening-phase task.",
        "Size hypercare Help Desk coverage per migrated system independently, rather than as a single blended estimate.",
    ],
    "Outstanding / Transition": [
        "Monitor SIEM licensing Change Request cost against contingency through the 90-day warranty window — owner: PM.",
        "Airline tenant IT liaisons to complete their own internal sign-off on shared-system connectivity — owner: Airline tenant IT (tracked, not owned, by PM).",
    ],
}


def lessons_df(lessons_dict, project_id):
    rows = []
    for section, items in lessons_dict.items():
        for order, text in enumerate(items):
            rows.append({"project_id": project_id, "section": section, "order": order, "text": text})
    return pd.DataFrame(rows)


LESSON_SECTION_ORDER = ["Went Well", "Could Improve", "Recommendations", "Outstanding / Transition"]

lessons_learned = pd.concat([
    lessons_df(construction_lessons, CONSTRUCTION),
    lessons_df(technology_lessons, TECHNOLOGY),
], ignore_index=True)
lessons_learned.to_parquet(SAMPLE_DIR / "lessons_learned.parquet", index=False)


# ───────────────────────── Monthly progress (synthesized trend) ─────────────
def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def anchored_curve(duration, anchor_month, anchor_value, final_value, noise_scale, rng):
    """Monotonic curve from (0, 0) through (anchor_month, anchor_value) to (duration, final_value)."""
    months = np.arange(0, duration + 1)
    values = np.zeros(duration + 1)
    for m in months:
        if m <= anchor_month:
            t = smoothstep(m / anchor_month) if anchor_month else 1.0
            values[m] = anchor_value * t
        else:
            t = smoothstep((m - anchor_month) / (duration - anchor_month))
            values[m] = anchor_value + (final_value - anchor_value) * t
    noise = rng.normal(0, noise_scale, size=duration + 1)
    noise[0] = 0
    noise[anchor_month] = 0
    noise[duration] = 0
    values = np.maximum.accumulate(values + noise)
    return values


def planned_curve(duration, total):
    months = np.arange(0, duration + 1)
    return total * smoothstep(months / duration)


rows = []
for proj_id, duration, anchor_month, anchor_spend, final_spend, anchor_pct, total_budget, open_risks_start, open_risks_end, open_issues_start in [
    (CONSTRUCTION, 14, 9, 3069000, 4168400, 64, 4250000, 5, 2, 1),
    (TECHNOLOGY, 9, 6, 2079000, 2611400, 68, 2650000, 4, 1, 1),
]:
    actual_spend = anchored_curve(duration, anchor_month, anchor_spend, final_spend, noise_scale=total_budget * 0.004, rng=RNG)
    planned_spend = planned_curve(duration, total_budget)
    actual_pct = anchored_curve(duration, anchor_month, anchor_pct, 100, noise_scale=1.2, rng=RNG)
    actual_pct = np.minimum(actual_pct, 100)
    planned_pct = smoothstep(np.arange(0, duration + 1) / duration) * 100
    open_risks = np.linspace(open_risks_start, open_risks_end, duration + 1).round().astype(int)
    open_issues = np.clip(np.linspace(open_issues_start, 0, duration + 1) + RNG.normal(0, 0.3, duration + 1), 0, None).round().astype(int)
    for m in range(0, duration + 1):
        rows.append({
            "project_id": proj_id,
            "month": m,
            "planned_cum_spend": round(planned_spend[m], 0),
            "actual_cum_spend": round(actual_spend[m], 0) if m <= anchor_month or True else None,
            "planned_cum_pct": round(planned_pct[m], 1),
            "actual_cum_pct": round(actual_pct[m], 1),
            "open_risks": int(open_risks[m]),
            "open_issues": int(open_issues[m]),
            "is_status_report_month": m == anchor_month,
        })

monthly_progress = pd.DataFrame(rows)
monthly_progress.to_parquet(SAMPLE_DIR / "monthly_progress.parquet", index=False)

print("Sample data written to", SAMPLE_DIR)
for f in sorted(SAMPLE_DIR.glob("*.parquet")):
    print(" -", f.name)
