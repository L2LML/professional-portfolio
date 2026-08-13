# Validation Log — 7-Point SOP Validation Framework

This is the SOP-by-SOP discrepancy log referenced in [`7-Point_SOP_Validation_Framework.docx`](./7-Point_SOP_Validation_Framework.docx). Every entry below is pulled directly from that SOP's own Revision History — not reconstructed from memory — so this log matches the actual change record inside the source documents.

Each SOP is one of two templates: **Response** (trigger-based — severity tiers, decision tree, escalation path) or **Process** (calendar-based — cadence, linear procedure, KPIs). Both get the same 7-point checklist; the defects that surface differ by shape, which is part of the finding.

---

### BP-001 — Brand Protection *(Response)*
- **Found:** Unauthorized-seller-not-holding-Buy-Box was an orphaned decision-tree branch — it had a severity tier but no resolution path.
- **Found:** P2/P3 severity split relied on non-testable language.
- **Found:** Test-buy evidence gathering had no reserved time against the P1 filing SLA.
- **Fixed:** Added Path D for the orphaned branch; split P2/P3 on a testable trailing-30-day sales threshold; added a test-buy initiation step to Immediate Actions and clarified the P1 filing SLA starts from evidence-received, not detection.

### CS-001 — Customer Service *(Response)*
- **Found:** Out-of-policy return requests were an orphaned trigger with no matching resolution path.
- **Found:** P2/P3 return-dispute severity used the word "escalated" as a criterion rather than a testable field.
- **Found:** P1 had no fixed resolution target for safety complaints, unlike P2/P3.
- **Fixed:** Added Path E for out-of-policy returns; split P2/P3 on a testable prior-denial field; clarified P1 resolution is case-by-case with Legal for safety complaints versus A-to-z claims' ~3-day Amazon window.

### IM-001 — Inventory Management *(Process)*
- **Found:** A seasonal-adjustment step gave no decision criteria — a judgment call disguised as an instruction.
- **Found:** Aged inventory was acted on in a later step without ever being included in the review step that was supposed to surface it.
- **Found:** The RACI's Accountable designation for reorder decisions had no matching approval step in the actual procedure.
- **Found:** Account Manager was named in an escalation clause but never defined in the RACI table.
- **Fixed:** Replaced the seasonal step with a testable forecast-lift rule; added aged inventory to the review scope; inserted an explicit approval step matching the RACI's existing "A"; added Account Manager to the RACI with a new escalation row.

### LO-001 — Listing Optimization *(Process)*
- **Found:** A "flag needed creative updates" step had no owner and no follow-through — the flag went nowhere.
- **Found:** The RACI's Account Manager assignment for client submission wasn't reflected in the procedure, which never named who submits.
- **Found:** Two of four trigger types (new-launch, conversion-drop) had no stated priority.
- **Found:** The P1 escalation had a trigger but no resolution bound.
- **Fixed:** Added a Creative/image-updates RACI row and a procedure step producing the flagged work before client submission; named Account Manager as the explicit submitter; added an expedited SLA for the two under-specified triggers; added a resolution bound to the P1 escalation.

### LF-001 — Logistics & Fulfillment *(Process)*
- **Found:** Step 8 resolved discrepancies "per discrepancy resolution process" — a circular reference to itself.
- **Found:** A receiving-shortage trigger was identical to a separate SOP's (FBA Reimbursements) trigger, with no cross-reference between the two — a real risk that a shortage could be closed on one side while its reimbursement claim window quietly expired.
- **Found:** Account Manager was named in a discrepancy-escalation clause but absent from the RACI.
- **Found:** Both Section 10 escalation clauses stated triggers with no resolution bounds.
- **Fixed:** Replaced the circular reference with an explicit rule routing Amazon-side shortages to the reimbursement SOP (same trigger, 60-day claim window) versus resolving pre-receipt discrepancies directly; added the cross-reference; added Account Manager to the RACI; added resolution-target bounds to both escalation clauses.

### PA-001 — Performance Analytics *(Process)*
- **Found:** Stockout was one of four named anomaly root causes, but the only one with no defined escalation route.
- **Found:** A RACI row (client review call) had **two** Accountable roles (Account Manager and Client) — accountability diffused between them.
- **Found:** A 30-day action-item KPI had no checkpoint between monthly review calls, leaving effectively zero buffer if a call slipped.
- **Fixed:** Added stockout as an explicit escalation route; fixed the dual-Accountable RACI row by dropping Client to Informed; added a weekly action-item aging check.

### PD-001 — Promotions & Deals *(Process)*
- **Found:** A RACI row (promo calendar planning) had two Accountable roles (Promotions Lead and Client).
- **Found:** Live-promotion monitoring/adjustment — a real decision with real consequences — had no RACI owner at all.
- **Found:** An underperformance rule had a testable threshold; the mirror-image overperformance/stockout-risk case did not.
- **Found:** A 100%-of-the-time submission SLA depended on client budget-approval turnaround with no stated target for that dependency.
- **Fixed:** Fixed the dual-Accountable row (Client → Consulted); added a RACI row for live-promotion monitoring; added a testable overperformance threshold mirroring the existing underperformance rule; added a client budget-approval turnaround target.

### AH-001 — Account Health & Suspension Appeals *(Response)*
- **Found:** Standalone performance notifications (not yet a suspension/deactivation/AHR movement) were an orphaned trigger with no decision-tree branch.
- **Found:** Two RACI rows (AHR monitoring, violation triage) had **zero** Accountable roles — the inverse defect from the dual-Accountable pattern seen elsewhere.
- **Found:** Account Manager was named in Immediate Actions but absent from the RACI.
- **Found:** The P1 escalation to Legal/Compliance Counsel had a trigger but no resolution bound.
- **Fixed:** Added a decision-tree branch for standalone notifications; assigned Account Health Lead as Accountable for both zero-Accountable rows; added Account Manager to the RACI with a new row; added a resolution-time bound for Legal/Compliance Counsel's post-escalation response.

### FR-001 — FBA Reimbursements *(Response)*
- **Found:** The RACI named a "High-value claim review" activity with real Accountable authority (Finance Lead) — but no procedure step ever actually triggered that review. The inverse of the usual gap: authority with nothing to do.
- **Found:** "Discrepancy identification" had no Accountable role at all.
- **Found:** The P1 escalation had a trigger but no resolution bound.
- **Fixed:** Added an explicit >$500 threshold to the Decision Tree and every filing path, routing to Finance Lead sign-off; assigned Reimbursements Lead as Accountable for discrepancy identification; added a resolution-time bound for the P1 escalation.

### AD-001 — Advertising / PPC Campaign Management *(Process)*
- **Found:** A RACI row (above-cap budget approval) had two Accountable roles (Account Manager and Client).
- **Found:** A new-listing go-live trigger referenced a companion SOP (Catalog Management) with no cross-reference actually defined.
- **Found:** Both Section 10 escalation clauses had triggers but no resolution bounds.
- **Fixed:** Fixed the dual-Accountable row (Client → Consulted); added the explicit cross-reference to Catalog Management; added resolution-time bounds to both escalation clauses.

### PC-001 — Product Compliance & Safety *(Process)*
- **Found:** Step 1 told analysts to coordinate with Listing Optimization for pre-listing-creation compliance checks — but Listing Optimization only touches *existing* listings. The correct owner (Catalog Management) was never referenced, even though Catalog Management's own SOP already referenced this one back.
- **Found:** Account Manager was named in a repeated-non-compliance escalation but absent from the RACI.
- **Found:** Both Section 10 escalation clauses had triggers but no resolution bounds.
- **Fixed:** Corrected the cross-reference to Catalog Management, matching the direction it already pointed; added Account Manager to the RACI with a new escalation row; added resolution-time bounds to both clauses.

### RR-001 — Returns & Refunds Management *(Process)*
- **Found:** A RACI row (return settings configuration) had two Accountable roles (Returns Lead and Client).
- **Found:** Return-rate monitoring/investigation — the step that decides which of two other SOPs to route a problem to — had no RACI owner.
- **Found:** Out-of-policy returns were checked weekly, but the SLA required action within 2 business days — the cadence couldn't structurally meet the SLA.
- **Found:** A routing rule named Brand Protection as a destination, but none of its listed causes actually justified that routing.
- **Fixed:** Fixed the dual-Accountable row (Client → Consulted); added a RACI row for return-rate monitoring; moved out-of-policy checks from weekly to daily; added counterfeit/authenticity complaint as the missing cause that justifies the Brand Protection route; added a resolution-time bound to the return-rate escalation.

### CM-001 — Catalog Management / New Listing Creation *(Process)*
- **Found:** A RACI row (product intake) had two Accountable roles (Catalog Lead and Client).
- **Found:** The most consequential finding in the series — a **self-introduced regression**: an earlier fix to the Advertising SOP added a reference assuming Catalog Management would notify it at a "scheduled go-live" date, ahead of actual launch. Catalog Management's own wording still said "once live," directly contradicting the fix and giving Advertising's launch-campaign SLA no early signal to work from. This was only caught because Catalog Management was re-validated independently after the Advertising fix, not assumed correct because it hadn't been touched.
- **Fixed:** Fixed the dual-Accountable row (Client → Consulted); split the single handoff step into two — Advertising is now notified at scheduled go-live, matching the Advertising SOP's wording exactly — and Listing Optimization is still notified once the listing is actually live; added a resolution-time bound to the repeated-rejections escalation.

---

## What this log demonstrates

Four defect classes repeated across unrelated SOPs, confirming they're systemic rather than one-off:

| Pattern | Instances |
|---|---|
| RACI row with two Accountable roles | 5 (PA-001, PD-001, AD-001, RR-001, CM-001) |
| RACI row with zero Accountable roles | 3 (AH-001 ×2, FR-001) |
| Role named in escalation but missing from the RACI | 4 (IM-001, LF-001, AH-001, PC-001) |
| Escalation trigger with no resolution bound | Nearly every SOP, until fixed |

And one that isn't a pattern, but is the actual argument for the methodology: **a fix made to one document in isolation introduced a defect in a document it now depended on (CM-001), caught only by re-validating after the fact.** Validating once, at the start, isn't enough — dependencies drift every time something connected to them changes.
