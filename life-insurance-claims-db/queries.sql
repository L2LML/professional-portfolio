-- ============================================================
-- Life Insurance Claims Database — Analytical Queries
-- Author: Lisa Lewandowski
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- 1. OPEN CLAIMS AGING REPORT
--    All active claims (pending/under_review) with days elapsed
-- ─────────────────────────────────────────────────────────────
SELECT
    c.claim_number,
    c.status,
    ph.first_name || ' ' || ph.last_name       AS policyholder,
    pt.type_name                                AS policy_type,
    c.cause_of_death,
    c.claim_amount,
    c.date_filed,
    c.assigned_examiner,
    CURRENT_DATE - c.date_filed                AS days_open,
    CASE
        WHEN CURRENT_DATE - c.date_filed > 60  THEN 'OVERDUE'
        WHEN CURRENT_DATE - c.date_filed > 30  THEN 'AGING'
        ELSE                                        'ON TRACK'
    END                                        AS aging_flag
FROM claims c
JOIN policies    p  ON c.policy_id         = p.policy_id
JOIN policyholders ph ON p.policyholder_id = ph.policyholder_id
JOIN policy_types pt  ON p.policy_type_id  = pt.policy_type_id
WHERE c.status IN ('pending', 'under_review')
ORDER BY days_open DESC;


-- ─────────────────────────────────────────────────────────────
-- 2. AVERAGE CLAIM PROCESSING TIME BY STATUS
--    How long does it take to approve or deny a claim?
-- ─────────────────────────────────────────────────────────────
SELECT
    status,
    COUNT(*)                                                    AS total_claims,
    ROUND(AVG(
        CASE
            WHEN date_approved IS NOT NULL THEN date_approved - date_filed
            WHEN date_denied   IS NOT NULL THEN date_denied   - date_filed
        END
    ), 1)                                                       AS avg_days_to_decision,
    MIN(
        CASE
            WHEN date_approved IS NOT NULL THEN date_approved - date_filed
            WHEN date_denied   IS NOT NULL THEN date_denied   - date_filed
        END
    )                                                           AS fastest_days,
    MAX(
        CASE
            WHEN date_approved IS NOT NULL THEN date_approved - date_filed
            WHEN date_denied   IS NOT NULL THEN date_denied   - date_filed
        END
    )                                                           AS slowest_days
FROM claims
WHERE status IN ('approved', 'paid', 'denied')
GROUP BY status
ORDER BY avg_days_to_decision;


-- ─────────────────────────────────────────────────────────────
-- 3. TOTAL PAYOUTS BY POLICY TYPE
--    Which product lines drive the most claim activity?
-- ─────────────────────────────────────────────────────────────
SELECT
    pt.type_name                                AS policy_type,
    COUNT(DISTINCT c.claim_id)                  AS total_claims,
    COUNT(DISTINCT CASE WHEN c.status = 'paid'
          THEN c.claim_id END)                  AS paid_claims,
    SUM(CASE WHEN c.status IN ('paid','approved')
          THEN c.claim_amount ELSE 0 END)       AS total_approved_amount,
    SUM(CASE WHEN c.status = 'paid'
          THEN cp.payment_amount ELSE 0 END)    AS total_paid_amount,
    ROUND(AVG(c.claim_amount), 2)               AS avg_claim_amount
FROM policy_types pt
LEFT JOIN policies p   ON pt.policy_type_id = p.policy_type_id
LEFT JOIN claims   c   ON p.policy_id       = c.policy_id
LEFT JOIN claim_payments cp ON c.claim_id   = cp.claim_id AND cp.status = 'cleared'
GROUP BY pt.policy_type_id, pt.type_name
ORDER BY total_approved_amount DESC;


-- ─────────────────────────────────────────────────────────────
-- 4. AGENT PORTFOLIO PERFORMANCE SUMMARY
--    Policy count, premiums, and claims per agent
-- ─────────────────────────────────────────────────────────────
SELECT
    a.first_name || ' ' || a.last_name          AS agent_name,
    a.state,
    COUNT(DISTINCT p.policy_id)                 AS total_policies,
    SUM(p.annual_premium)                       AS total_annual_premium,
    SUM(p.face_value)                           AS total_coverage_written,
    COUNT(DISTINCT c.claim_id)                  AS total_claims,
    SUM(CASE WHEN c.status IN ('paid','approved')
          THEN c.claim_amount ELSE 0 END)       AS total_claims_value,
    ROUND(
        COUNT(DISTINCT c.claim_id) * 100.0 /
        NULLIF(COUNT(DISTINCT p.policy_id), 0), 2
    )                                           AS claims_per_policy_pct
FROM agents a
LEFT JOIN policies p ON a.agent_id   = p.agent_id
LEFT JOIN claims   c ON p.policy_id  = c.policy_id
GROUP BY a.agent_id, a.first_name, a.last_name, a.state
ORDER BY total_annual_premium DESC;


-- ─────────────────────────────────────────────────────────────
-- 5. CLAIMS BY CAUSE OF DEATH
--    Distribution analysis for risk and actuarial review
-- ─────────────────────────────────────────────────────────────
SELECT
    cause_of_death,
    COUNT(*)                                    AS total_claims,
    SUM(claim_amount)                           AS total_claimed,
    ROUND(AVG(claim_amount), 2)                 AS avg_claim_amount,
    COUNT(CASE WHEN status = 'denied' THEN 1 END)  AS denied_count,
    ROUND(
        COUNT(CASE WHEN status = 'denied' THEN 1 END) * 100.0 / COUNT(*), 1
    )                                           AS denial_rate_pct
FROM claims
GROUP BY cause_of_death
ORDER BY total_claims DESC;


-- ─────────────────────────────────────────────────────────────
-- 6. HIGH-VALUE PENDING CLAIMS (over $250,000)
--    Priority queue for senior examiner review
-- ─────────────────────────────────────────────────────────────
SELECT
    c.claim_number,
    c.claim_amount,
    c.status,
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    pt.type_name                                 AS policy_type,
    p.face_value,
    c.cause_of_death,
    c.date_filed,
    CURRENT_DATE - c.date_filed                  AS days_open,
    c.assigned_examiner,
    c.notes
FROM claims c
JOIN policies      p   ON c.policy_id        = p.policy_id
JOIN policyholders ph  ON p.policyholder_id  = ph.policyholder_id
JOIN policy_types  pt  ON p.policy_type_id   = pt.policy_type_id
WHERE c.claim_amount > 250000
  AND c.status IN ('pending', 'under_review', 'approved')
ORDER BY c.claim_amount DESC;


-- ─────────────────────────────────────────────────────────────
-- 7. CLAIMS MISSING REQUIRED DOCUMENTS
--    Which open claims are still waiting on paperwork?
-- ─────────────────────────────────────────────────────────────
SELECT
    c.claim_number,
    c.status,
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    c.claim_amount,
    c.assigned_examiner,
    COUNT(cd.document_id)                        AS total_docs,
    SUM(CASE WHEN cd.is_verified = FALSE THEN 1 ELSE 0 END) AS unverified_docs,
    STRING_AGG(
        CASE WHEN cd.is_verified = FALSE
             THEN cd.document_type END,
        ', ' ORDER BY cd.document_type
    )                                            AS pending_documents
FROM claims c
JOIN policies      p  ON c.policy_id       = p.policy_id
JOIN policyholders ph ON p.policyholder_id = ph.policyholder_id
JOIN claim_documents cd ON c.claim_id      = cd.claim_id
WHERE c.status IN ('pending', 'under_review')
GROUP BY c.claim_id, c.claim_number, c.status, ph.first_name, ph.last_name,
         c.claim_amount, c.assigned_examiner
HAVING SUM(CASE WHEN cd.is_verified = FALSE THEN 1 ELSE 0 END) > 0
ORDER BY unverified_docs DESC;


-- ─────────────────────────────────────────────────────────────
-- 8. MONTHLY CLAIMS FILED — YEAR-TO-DATE TREND
--    Volume and value of claims by month
-- ─────────────────────────────────────────────────────────────
SELECT
    TO_CHAR(date_filed, 'YYYY-MM')              AS month,
    COUNT(*)                                    AS claims_filed,
    SUM(claim_amount)                           AS total_claim_value,
    ROUND(AVG(claim_amount), 2)                 AS avg_claim_value,
    COUNT(CASE WHEN status = 'denied' THEN 1 END)  AS denied,
    COUNT(CASE WHEN status IN ('approved','paid') THEN 1 END) AS approved_or_paid
FROM claims
WHERE date_filed >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY TO_CHAR(date_filed, 'YYYY-MM')
ORDER BY month;


-- ─────────────────────────────────────────────────────────────
-- 9. BENEFICIARY PAYMENT SUMMARY
--    What each beneficiary has received or is owed
-- ─────────────────────────────────────────────────────────────
SELECT
    b.first_name || ' ' || b.last_name          AS beneficiary,
    b.relationship,
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    p.policy_number,
    b.percentage                                AS benefit_pct,
    c.claim_amount                              AS claim_amount,
    cp.payment_amount,
    cp.status                                   AS payment_status,
    cp.payment_date,
    cp.payment_method
FROM beneficiaries b
JOIN policies      p  ON b.policy_id        = p.policy_id
JOIN policyholders ph ON p.policyholder_id  = ph.policyholder_id
JOIN claims        c  ON c.beneficiary_id   = b.beneficiary_id
LEFT JOIN claim_payments cp ON cp.claim_id  = c.claim_id
                            AND cp.beneficiary_id = b.beneficiary_id
WHERE c.status IN ('approved', 'paid')
ORDER BY cp.payment_date DESC NULLS FIRST;


-- ─────────────────────────────────────────────────────────────
-- 10. DENIAL RATE AND REASON ANALYSIS
--     What percentage of claims are denied and why?
-- ─────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                                    AS total_decisions,
    COUNT(CASE WHEN status = 'denied' THEN 1 END)               AS total_denied,
    ROUND(
        COUNT(CASE WHEN status = 'denied' THEN 1 END) * 100.0 / COUNT(*), 2
    )                                                           AS denial_rate_pct,
    SUM(CASE WHEN status = 'denied' THEN claim_amount ELSE 0 END) AS total_denied_value
FROM claims
WHERE status IN ('approved', 'paid', 'denied');

-- Denial reasons breakdown
SELECT
    denial_reason,
    COUNT(*)                                    AS occurrences,
    SUM(claim_amount)                           AS total_claim_value
FROM claims
WHERE status = 'denied'
GROUP BY denial_reason
ORDER BY occurrences DESC;


-- ─────────────────────────────────────────────────────────────
-- 11. POLICIES EXPIRING WITHIN 12 MONTHS
--     Proactive renewal outreach list for agents
-- ─────────────────────────────────────────────────────────────
SELECT
    p.policy_number,
    pt.type_name                                AS policy_type,
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    ph.email,
    ph.phone,
    a.first_name || ' ' || a.last_name          AS agent,
    a.email                                     AS agent_email,
    p.face_value,
    p.annual_premium,
    p.expiration_date,
    p.expiration_date - CURRENT_DATE            AS days_until_expiry
FROM policies p
JOIN policyholders ph ON p.policyholder_id = ph.policyholder_id
JOIN policy_types  pt ON p.policy_type_id  = pt.policy_type_id
LEFT JOIN agents    a ON p.agent_id        = a.agent_id
WHERE p.status = 'active'
  AND p.expiration_date IS NOT NULL
  AND p.expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '12 months'
ORDER BY p.expiration_date;


-- ─────────────────────────────────────────────────────────────
-- 13. RUNNING TOTAL OF CLAIM PAYMENTS  [WINDOW: SUM OVER]
--     Cumulative payout amount over time — cash flow view
-- ─────────────────────────────────────────────────────────────
SELECT
    cp.payment_date,
    c.claim_number,
    b.first_name || ' ' || b.last_name          AS beneficiary,
    pt.type_name                                AS policy_type,
    cp.payment_amount,
    SUM(cp.payment_amount)
        OVER (ORDER BY cp.payment_date
              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                                                AS running_total_paid,
    SUM(cp.payment_amount)
        OVER (PARTITION BY pt.type_name
              ORDER BY cp.payment_date
              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                                                AS running_total_by_product
FROM claim_payments cp
JOIN claims        c  ON cp.claim_id        = c.claim_id
JOIN beneficiaries b  ON cp.beneficiary_id  = b.beneficiary_id
JOIN policies      p  ON c.policy_id        = p.policy_id
JOIN policy_types  pt ON p.policy_type_id   = pt.policy_type_id
WHERE cp.status = 'cleared'
  AND cp.payment_date IS NOT NULL
ORDER BY cp.payment_date;


-- ─────────────────────────────────────────────────────────────
-- 14. CLAIMS RANKED BY AMOUNT WITHIN EACH POLICY TYPE
--     [WINDOW: RANK + DENSE_RANK OVER PARTITION BY]
--     Which claims are the largest exposure per product line?
-- ─────────────────────────────────────────────────────────────
SELECT
    c.claim_number,
    pt.type_name                                AS policy_type,
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    c.claim_amount,
    c.status,
    RANK()
        OVER (PARTITION BY pt.policy_type_id
              ORDER BY c.claim_amount DESC)     AS rank_in_product,
    DENSE_RANK()
        OVER (ORDER BY c.claim_amount DESC)     AS overall_rank,
    ROUND(
        c.claim_amount * 100.0 /
        SUM(c.claim_amount) OVER (PARTITION BY pt.policy_type_id), 2
    )                                           AS pct_of_product_total
FROM claims c
JOIN policies      p  ON c.policy_id        = p.policy_id
JOIN policy_types  pt ON p.policy_type_id   = pt.policy_type_id
JOIN policyholders ph ON p.policyholder_id  = ph.policyholder_id
ORDER BY pt.type_name, rank_in_product;


-- ─────────────────────────────────────────────────────────────
-- 15. EXAMINER WORKLOAD QUEUE WITH MONTH-OVER-MONTH TREND
--     [WINDOW: ROW_NUMBER, LAG, COUNT OVER PARTITION BY]
--     Prioritized queue per examiner + volume trend vs. prior month
-- ─────────────────────────────────────────────────────────────
-- Examiner queue — claims numbered by value (highest first)
SELECT
    c.assigned_examiner,
    ROW_NUMBER()
        OVER (PARTITION BY c.assigned_examiner
              ORDER BY c.claim_amount DESC)     AS queue_position,
    c.claim_number,
    c.status,
    c.claim_amount,
    c.date_filed,
    CURRENT_DATE - c.date_filed                 AS days_open,
    COUNT(*)
        OVER (PARTITION BY c.assigned_examiner) AS total_in_queue
FROM claims c
WHERE c.status IN ('pending', 'under_review')
  AND c.assigned_examiner IS NOT NULL
ORDER BY c.assigned_examiner, queue_position;

-- Month-over-month claim volume using LAG
WITH monthly AS (
    SELECT
        TO_CHAR(date_filed, 'YYYY-MM')          AS month,
        COUNT(*)                                AS claims_filed,
        SUM(claim_amount)                       AS total_value
    FROM claims
    GROUP BY TO_CHAR(date_filed, 'YYYY-MM')
)
SELECT
    month,
    claims_filed,
    total_value,
    LAG(claims_filed)  OVER (ORDER BY month)    AS prev_month_count,
    LAG(total_value)   OVER (ORDER BY month)    AS prev_month_value,
    claims_filed - LAG(claims_filed) OVER (ORDER BY month)
                                                AS volume_change,
    ROUND(
        (claims_filed - LAG(claims_filed) OVER (ORDER BY month))
        * 100.0 / NULLIF(LAG(claims_filed) OVER (ORDER BY month), 0), 1
    )                                           AS pct_change
FROM monthly
ORDER BY month;


-- ─────────────────────────────────────────────────────────────
-- 16. FULL CLAIM DETAIL VIEW
--     Complete picture of a single claim (parameterized)
-- ─────────────────────────────────────────────────────────────
SELECT
    c.claim_number,
    c.status,
    c.date_of_death,
    c.date_filed,
    c.cause_of_death,
    c.claim_amount,
    c.assigned_examiner,
    c.denial_reason,
    c.date_approved,
    c.date_paid,
    c.notes                                     AS claim_notes,
    -- Policy
    p.policy_number,
    pt.type_name                                AS policy_type,
    p.face_value,
    p.annual_premium,
    p.issue_date,
    p.riders,
    -- Policyholder
    ph.first_name || ' ' || ph.last_name        AS policyholder,
    ph.date_of_birth,
    ph.smoker,
    -- Beneficiary
    b.first_name  || ' ' || b.last_name         AS beneficiary,
    b.relationship,
    b.percentage                                AS benefit_pct,
    -- Payment
    cp.payment_amount,
    cp.payment_method,
    cp.payment_date,
    cp.status                                   AS payment_status
FROM claims c
JOIN policies      p   ON c.policy_id        = p.policy_id
JOIN policy_types  pt  ON p.policy_type_id   = pt.policy_type_id
JOIN policyholders ph  ON p.policyholder_id  = ph.policyholder_id
JOIN beneficiaries b   ON c.beneficiary_id   = b.beneficiary_id
LEFT JOIN claim_payments cp ON c.claim_id    = cp.claim_id
WHERE c.claim_number = 'CLM-2024-00011';   -- swap in any claim number


-- ─────────────────────────────────────────────────────────────
-- 17. FULL OUTER JOIN — COVERAGE GAP ANALYSIS
--     Find agents with no policies AND policies with no agent
-- ─────────────────────────────────────────────────────────────
SELECT
    COALESCE(a.first_name || ' ' || a.last_name, '— No Agent —')  AS agent,
    a.license_number,
    a.state,
    COALESCE(p.policy_number, '— No Policy —')                    AS policy_number,
    ph.first_name || ' ' || ph.last_name                          AS policyholder,
    CASE
        WHEN a.agent_id  IS NULL THEN 'Policy has no assigned agent'
        WHEN p.policy_id IS NULL THEN 'Agent has no active policies'
        ELSE 'Matched'
    END                                                           AS gap_type
FROM agents a
FULL OUTER JOIN policies p  ON a.agent_id        = p.agent_id
                            AND p.status          = 'active'
FULL OUTER JOIN policyholders ph ON p.policyholder_id = ph.policyholder_id
WHERE a.agent_id IS NULL OR p.policy_id IS NULL
ORDER BY gap_type, agent;


-- ─────────────────────────────────────────────────────────────
-- 18. UNION — COMPLETE OUTREACH CONTACT LIST
--     Combines policyholders + beneficiaries into one list;
--     useful for notifications, renewals, and payment follow-up
-- ─────────────────────────────────────────────────────────────
SELECT 'Policyholder' AS contact_type,
       first_name, last_name, email, phone,
       address_city, address_state
FROM   policyholders
WHERE  email IS NOT NULL

UNION

SELECT 'Beneficiary',
       first_name, last_name, email, phone,
       NULL, NULL
FROM   beneficiaries
WHERE  email IS NOT NULL

ORDER BY last_name, first_name;


-- ─────────────────────────────────────────────────────────────
-- 19. EXCEPT — POLICYHOLDERS WHO HAVE NEVER FILED A CLAIM
--     Useful for identifying low-risk, long-tenure customers
-- ─────────────────────────────────────────────────────────────
SELECT
    ph.policyholder_id,
    ph.first_name || ' ' || ph.last_name  AS policyholder,
    ph.address_state                      AS state,
    MIN(p.issue_date)                     AS earliest_policy_date,
    COUNT(p.policy_id)                    AS total_policies,
    SUM(p.face_value)                     AS total_coverage,
    SUM(p.annual_premium)                 AS total_annual_premium
FROM policyholders ph
JOIN policies p ON ph.policyholder_id = p.policyholder_id
WHERE ph.policyholder_id NOT IN (
    SELECT DISTINCT p2.policyholder_id
    FROM   claims  c
    JOIN   policies p2 ON c.policy_id = p2.policy_id
)
GROUP BY ph.policyholder_id, ph.first_name, ph.last_name, ph.address_state
ORDER BY earliest_policy_date;


-- ─────────────────────────────────────────────────────────────
-- 20. MULTI-STEP CTE — CLAIMS FUNNEL ANALYSIS
--     Tracks drop-off rate at each stage of the claims process
-- ─────────────────────────────────────────────────────────────
WITH
filed AS (
    SELECT COUNT(*)        AS cnt,
           SUM(claim_amount) AS total_value
    FROM claims
),
reviewed AS (
    SELECT COUNT(*)        AS cnt,
           SUM(claim_amount) AS total_value
    FROM claims
    WHERE status IN ('under_review','approved','paid','denied','withdrawn')
),
decided AS (
    SELECT COUNT(*)        AS cnt,
           SUM(claim_amount) AS total_value
    FROM claims
    WHERE status IN ('approved','paid','denied')
),
approved AS (
    SELECT COUNT(*)        AS cnt,
           SUM(claim_amount) AS total_value
    FROM claims
    WHERE status IN ('approved','paid')
),
paid AS (
    SELECT COUNT(*)        AS cnt,
           SUM(claim_amount) AS total_value
    FROM claims
    WHERE status = 'paid'
),
denied AS (
    SELECT COUNT(*)        AS cnt,
           SUM(claim_amount) AS total_value
    FROM claims
    WHERE status = 'denied'
)
SELECT
    stage,
    cnt                                          AS claim_count,
    total_value                                  AS total_claim_value,
    ROUND(cnt * 100.0 / NULLIF(f.cnt, 0), 1)    AS pct_of_filed,
    ROUND(cnt * 100.0 / NULLIF(LAG(cnt) OVER (ORDER BY sort_order), 0), 1)
                                                 AS stage_conversion_pct
FROM (
    SELECT 1 AS sort_order, 'Filed'    AS stage, f.cnt, f.total_value FROM filed    f
    UNION ALL
    SELECT 2, 'In Review',   r.cnt, r.total_value FROM reviewed r
    UNION ALL
    SELECT 3, 'Decided',     d.cnt, d.total_value FROM decided  d
    UNION ALL
    SELECT 4, 'Approved',    a.cnt, a.total_value FROM approved a
    UNION ALL
    SELECT 5, 'Paid',        p.cnt, p.total_value FROM paid     p
    UNION ALL
    SELECT 6, 'Denied',      dn.cnt, dn.total_value FROM denied dn
) stages
CROSS JOIN filed f
ORDER BY sort_order;


-- ─────────────────────────────────────────────────────────────
-- 21. EXPLAIN ANALYZE — INDEX PERFORMANCE CHECK
--     Shows the query execution plan for the open claims report.
--     Confirms idx_claims_status index is being used.
-- ─────────────────────────────────────────────────────────────
EXPLAIN ANALYZE
SELECT
    c.claim_number,
    c.status,
    c.claim_amount,
    ph.first_name || ' ' || ph.last_name  AS policyholder,
    pt.type_name                          AS policy_type,
    CURRENT_DATE - c.date_filed           AS days_open
FROM claims c
JOIN policies      p  ON c.policy_id        = p.policy_id
JOIN policyholders ph ON p.policyholder_id  = ph.policyholder_id
JOIN policy_types  pt ON p.policy_type_id   = pt.policy_type_id
WHERE c.status IN ('pending', 'under_review')
  AND c.claim_amount > 250000
ORDER BY c.claim_amount DESC;


-- ─────────────────────────────────────────────────────────────
-- 22. AGE BAND SEGMENTATION
--     Claim rates, premiums, and average coverage by age
--     at time of policy issuance — actuarial banding view
-- ─────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN p.age_at_issue BETWEEN 18 AND 35 THEN '18–35  Young Adult'
        WHEN p.age_at_issue BETWEEN 36 AND 50 THEN '36–50  Middle Age'
        WHEN p.age_at_issue BETWEEN 51 AND 65 THEN '51–65  Pre-Retirement'
        WHEN p.age_at_issue > 65              THEN '65+    Senior'
        ELSE 'Unknown'
    END                                         AS age_band,
    COUNT(DISTINCT p.policy_id)                 AS total_policies,
    COUNT(DISTINCT ph.policyholder_id)          AS unique_customers,
    ROUND(AVG(p.annual_premium), 2)             AS avg_annual_premium,
    ROUND(AVG(p.face_value), 0)                 AS avg_face_value,
    SUM(p.annual_premium)                       AS total_premium_revenue,
    COUNT(DISTINCT c.claim_id)                  AS total_claims,
    ROUND(
        COUNT(DISTINCT c.claim_id) * 100.0 /
        NULLIF(COUNT(DISTINCT p.policy_id), 0), 1
    )                                           AS claim_rate_pct,
    ROUND(AVG(c.claim_amount), 0)               AS avg_claim_amount,
    COUNT(DISTINCT CASE WHEN ph.smoker THEN ph.policyholder_id END)
                                                AS smoker_count
FROM policies p
JOIN policyholders ph ON p.policyholder_id = ph.policyholder_id
LEFT JOIN claims   c  ON p.policy_id       = c.policy_id
                      AND c.status NOT IN ('withdrawn', 'denied')
WHERE p.age_at_issue IS NOT NULL
GROUP BY age_band
ORDER BY age_band;


-- ─────────────────────────────────────────────────────────────
-- 23. CUSTOMER TENURE ANALYSIS
--     Claim rates and revenue by years held with the company
--     — longer tenure = lower lapse risk and claim rate?
-- ─────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since)) < 3
            THEN '0–2 yrs   New'
        WHEN DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since)) < 6
            THEN '3–5 yrs   Establishing'
        WHEN DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since)) < 11
            THEN '6–10 yrs  Loyal'
        ELSE    '11+ yrs   Long-Term'
    END                                         AS tenure_tier,
    COUNT(DISTINCT ph.policyholder_id)          AS customers,
    COUNT(DISTINCT p.policy_id)                 AS total_policies,
    SUM(p.annual_premium)                       AS total_annual_premium,
    SUM(p.face_value)                           AS total_coverage,
    COUNT(DISTINCT c.claim_id)                  AS total_claims,
    ROUND(
        COUNT(DISTINCT c.claim_id) * 100.0 /
        NULLIF(COUNT(DISTINCT p.policy_id), 0), 1
    )                                           AS claim_rate_pct,
    ROUND(AVG(
        DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since))
    ), 1)                                       AS avg_years_with_company
FROM policyholders ph
JOIN policies p   ON ph.policyholder_id = p.policyholder_id
LEFT JOIN claims c ON p.policy_id = c.policy_id
                   AND c.status NOT IN ('withdrawn', 'denied')
WHERE ph.policyholder_since IS NOT NULL
GROUP BY tenure_tier
ORDER BY tenure_tier;


-- ─────────────────────────────────────────────────────────────
-- 24. AGE × TENURE MATRIX  (the killer combo)
--     Cross-tabs age band against tenure tier to find the
--     most and least profitable customer segments
-- ─────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN p.age_at_issue BETWEEN 18 AND 35 THEN '18–35'
        WHEN p.age_at_issue BETWEEN 36 AND 50 THEN '36–50'
        WHEN p.age_at_issue BETWEEN 51 AND 65 THEN '51–65'
        WHEN p.age_at_issue > 65              THEN '65+'
        ELSE 'Unknown'
    END                                         AS age_band,
    CASE
        WHEN DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since)) < 3
            THEN '0–2 yrs'
        WHEN DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since)) < 6
            THEN '3–5 yrs'
        WHEN DATE_PART('year', AGE(CURRENT_DATE, ph.policyholder_since)) < 11
            THEN '6–10 yrs'
        ELSE    '11+ yrs'
    END                                         AS tenure_tier,
    COUNT(DISTINCT ph.policyholder_id)          AS customers,
    ROUND(AVG(p.annual_premium), 0)             AS avg_premium,
    ROUND(AVG(p.face_value), 0)                 AS avg_coverage,
    COUNT(DISTINCT c.claim_id)                  AS claims,
    ROUND(
        COUNT(DISTINCT c.claim_id) * 100.0 /
        NULLIF(COUNT(DISTINCT p.policy_id), 0), 1
    )                                           AS claim_rate_pct,
    -- Profitability proxy: premiums collected vs claims exposure
    ROUND(
        SUM(p.annual_premium) /
        NULLIF(SUM(CASE WHEN c.status NOT IN ('withdrawn','denied')
                        THEN c.claim_amount ELSE 0 END), 0), 2
    )                                           AS premium_to_claim_ratio
FROM policyholders ph
JOIN policies p    ON ph.policyholder_id = p.policyholder_id
LEFT JOIN claims c ON p.policy_id        = c.policy_id
WHERE p.age_at_issue IS NOT NULL
  AND ph.policyholder_since IS NOT NULL
GROUP BY age_band, tenure_tier
ORDER BY age_band, tenure_tier;
