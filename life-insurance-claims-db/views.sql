-- ============================================================
-- Life Insurance Claims Database — Views
-- Author: Lisa Lewandowski
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- vw_open_claims
-- All claims currently in progress with policyholder & aging
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW vw_open_claims AS
SELECT
    c.claim_id,
    c.claim_number,
    c.status,
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    p.policy_number,
    pt.type_name                                AS policy_type,
    c.cause_of_death,
    c.claim_amount,
    c.date_filed,
    c.assigned_examiner,
    CURRENT_DATE - c.date_filed                 AS days_open,
    CASE
        WHEN CURRENT_DATE - c.date_filed > 60   THEN 'OVERDUE'
        WHEN CURRENT_DATE - c.date_filed > 30   THEN 'AGING'
        ELSE                                         'ON TRACK'
    END                                         AS aging_status
FROM claims c
JOIN policies      p   ON c.policy_id        = p.policy_id
JOIN policyholders ph  ON p.policyholder_id  = ph.policyholder_id
JOIN policy_types  pt  ON p.policy_type_id   = pt.policy_type_id
WHERE c.status IN ('pending', 'under_review');


-- ─────────────────────────────────────────────────────────────
-- vw_claims_summary
-- One row per claim with full context and processing metrics
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW vw_claims_summary AS
SELECT
    c.claim_number,
    c.status,
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    p.policy_number,
    pt.type_name                                AS policy_type,
    b.first_name || ' ' || b.last_name          AS beneficiary,
    b.relationship,
    c.cause_of_death,
    c.claim_amount,
    c.date_of_death,
    c.date_filed,
    c.date_approved,
    c.date_paid,
    c.assigned_examiner,
    CASE
        WHEN c.date_approved IS NOT NULL THEN c.date_approved - c.date_filed
        WHEN c.date_denied   IS NOT NULL THEN c.date_denied   - c.date_filed
        ELSE CURRENT_DATE - c.date_filed
    END                                         AS days_to_decision,
    c.denial_reason
FROM claims c
JOIN policies      p  ON c.policy_id        = p.policy_id
JOIN policyholders ph ON p.policyholder_id  = ph.policyholder_id
JOIN policy_types  pt ON p.policy_type_id   = pt.policy_type_id
JOIN beneficiaries b  ON c.beneficiary_id   = b.beneficiary_id;


-- ─────────────────────────────────────────────────────────────
-- vw_agent_performance
-- Agent-level metrics: policies, premiums, claims exposure
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW vw_agent_performance AS
SELECT
    a.agent_id,
    a.first_name || ' ' || a.last_name          AS agent_name,
    a.state,
    a.license_number,
    COUNT(DISTINCT p.policy_id)                 AS total_policies,
    SUM(p.annual_premium)                       AS total_annual_premium,
    SUM(p.face_value)                           AS total_coverage_written,
    COUNT(DISTINCT c.claim_id)                  AS total_claims,
    SUM(CASE WHEN c.status IN ('paid','approved')
          THEN c.claim_amount ELSE 0 END)       AS total_approved_claims,
    ROUND(
        COUNT(DISTINCT c.claim_id) * 100.0 /
        NULLIF(COUNT(DISTINCT p.policy_id), 0), 2
    )                                           AS claim_rate_pct
FROM agents a
LEFT JOIN policies p ON a.agent_id  = p.agent_id
LEFT JOIN claims   c ON p.policy_id = c.policy_id
GROUP BY a.agent_id, a.first_name, a.last_name, a.state, a.license_number;


-- ─────────────────────────────────────────────────────────────
-- vw_payments_pending
-- Approved claims where payment has not yet been issued
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW vw_payments_pending AS
SELECT
    c.claim_number,
    b.first_name || ' ' || b.last_name          AS beneficiary,
    b.relationship,
    b.email                                     AS beneficiary_email,
    b.phone                                     AS beneficiary_phone,
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    p.policy_number,
    cp.payment_amount,
    cp.payment_method,
    c.date_approved,
    CURRENT_DATE - c.date_approved              AS days_since_approval
FROM claim_payments cp
JOIN claims        c  ON cp.claim_id         = c.claim_id
JOIN beneficiaries b  ON cp.beneficiary_id   = b.beneficiary_id
JOIN policies      p  ON c.policy_id         = p.policy_id
JOIN policyholders ph ON p.policyholder_id   = ph.policyholder_id
WHERE cp.status = 'pending'
ORDER BY days_since_approval DESC;


-- ─────────────────────────────────────────────────────────────
-- vw_customer_segments
-- One row per policyholder with age band, tenure tier,
-- and key metrics — ready for dashboards and reporting
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW vw_customer_segments AS
SELECT
    ph.policyholder_id,
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    ph.address_state                            AS state,
    ph.smoker,
    ph.policyholder_since,
    DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since))::INT
                                                AS years_with_company,
    CASE
        WHEN DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since)) < 3
            THEN 'New (0–2 yrs)'
        WHEN DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since)) < 6
            THEN 'Establishing (3–5 yrs)'
        WHEN DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since)) < 11
            THEN 'Loyal (6–10 yrs)'
        ELSE    'Long-Term (11+ yrs)'
    END                                         AS tenure_tier,
    CASE
        WHEN MIN(p.age_at_issue) BETWEEN 18 AND 35 THEN '18–35 Young Adult'
        WHEN MIN(p.age_at_issue) BETWEEN 36 AND 50 THEN '36–50 Middle Age'
        WHEN MIN(p.age_at_issue) BETWEEN 51 AND 65 THEN '51–65 Pre-Retirement'
        WHEN MIN(p.age_at_issue) > 65              THEN '65+ Senior'
        ELSE 'Unknown'
    END                                         AS age_band_at_first_policy,
    DATE_PART('year', AGE(CURRENT_DATE, ph.date_of_birth))::INT
                                                AS current_age,
    COUNT(DISTINCT p.policy_id)                 AS total_policies,
    SUM(p.annual_premium)                       AS total_annual_premium,
    SUM(p.face_value)                           AS total_coverage,
    COUNT(DISTINCT c.claim_id)                  AS total_claims_filed
FROM policyholders ph
JOIN  policies p   ON ph.policyholder_id = p.policyholder_id
LEFT JOIN claims c ON p.policy_id        = c.policy_id
WHERE ph.policyholder_since IS NOT NULL
GROUP BY ph.policyholder_id, ph.first_name, ph.last_name,
         ph.address_state, ph.smoker, ph.policyholder_since,
         ph.date_of_birth;
