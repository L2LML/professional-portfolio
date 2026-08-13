# Amazon Marketplace SOP Framework & Validation Methodology

A self-directed operations documentation project — demonstrating **Ecommerce Process Improvement** capability — building a complete Standard Operating Procedure framework for an Amazon marketplace brand-management business, then independently stress-testing every SOP against a structured QA methodology rather than treating "written" as "done."

---

## What this is

Two deliverables:

1. **A 13-SOP operational manual** covering Brand Protection, Customer Service, Inventory Management, Listing Optimization, Logistics & Fulfillment, Performance Analytics, Promotions & Deals, Account Health & Suspension Appeals, FBA Reimbursements, Advertising/PPC, Product Compliance & Safety, Returns & Refunds, and Catalog Management — split into two templates: trigger-based "Response" SOPs (severity tiers, decision trees, escalation paths) for reactive work, and calendar-based "Process" SOPs (cadence, linear procedure, KPIs) for scheduled work.
2. **A validation methodology** — a 7-point checklist (blind execution test, real-incident audit, orphaned-branch check, independent-execution consistency check, SLA timing check, escalation stress test, deviation-rate tracking) run independently against every SOP in the set, with every confirmed defect fixed and logged in that SOP's own revision history.

## Why it's structured this way

Most SOP libraries stop at "written and approved." This one treats that as the starting point, not the finish line — the validation pass is the actual deliverable, not a formality wrapped around the writing.

## What the validation pass found

Running the same checklist against 13 independently-authored SOPs surfaced the same handful of defects repeatedly, which turned them from one-off mistakes into confirmed patterns:

| Pattern | Confirmed instances |
|---|---|
| RACI row with **two** Accountable roles (accountability diffused between a client and an internal lead) | 5 |
| RACI row with **zero** Accountable roles (nobody owns the outcome) | 3 |
| A role named in an escalation clause that never appears in that SOP's own RACI table | 4 |
| An escalation with a stated trigger but no resolution-time bound | Nearly every SOP, until fixed |
| Two SOPs sharing a trigger event with no cross-reference between them | 1 confirmed — with a real dollar-risk consequence (a shared inventory-discrepancy trigger where the receiving-side SOP could close its own ticket without ever surfacing the separate reimbursement claim, which carries a hard 60-day filing window) |

The most interesting catch: fixing one SOP to reference a second one **introduced a new contradiction** with that second SOP's existing wording — a timing mismatch that only surfaced because the second SOP was re-validated independently afterward, not assumed correct because it hadn't been touched. That's the actual argument for the methodology: a fix made to one document in isolation can silently break a document that depends on it, and only re-validation catches it.

## In this folder

| File | What it is |
|---|---|
| [`7-Point_SOP_Validation_Framework.docx`](./7-Point_SOP_Validation_Framework.docx) / `.pdf` | The named methodology itself — 7 SOP-writing principles, 7 validation checks, and the 4 confirmed defect patterns below, written as a standalone, reusable reference (no employer-specific content) |
| [`VALIDATION_LOG.md`](./VALIDATION_LOG.md) | The SOP-by-SOP discrepancy log — every defect found and every fix applied, pulled directly from each SOP's own revision history, not reconstructed from memory |

The 13-SOP operational manual itself is kept private — its content is written for a specific prospective employer's operations and isn't something this repo publishes — but the methodology and the full findings it produced are public, since neither references that employer.

## Format

The manual was built with a custom Node.js document generator (`docx` library) rather than assembled by hand — every SOP follows an identical structural template so the document stays consistent as it grows, and every fix could be applied programmatically and re-rendered rather than hand-edited into a Word file.

## Skills demonstrated

Process Documentation · RACI Design · Quality Assurance / Validation Methodology · Root-Cause Analysis · Cross-Functional Dependency Mapping · Technical Writing · Node.js (automated document generation) · Excel/Workbook Data Management
