-- ============================================================
-- Life Insurance Claims Database — Stored Procedures
-- Author: Lisa Lewandowski
-- ============================================================

-- Claim number sequence (avoids collisions with seed data)
CREATE SEQUENCE IF NOT EXISTS claim_number_seq START 500;


-- ─────────────────────────────────────────────────────────────
-- FUNCTION 1: file_new_claim()
-- Validates policy status, coverage dates, and beneficiary
-- ownership before inserting a new claim. Returns claim number.
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION file_new_claim(
    p_policy_id       INT,
    p_beneficiary_id  INT,
    p_date_of_death   DATE,
    p_cause_of_death  VARCHAR,
    p_notes           TEXT DEFAULT NULL
)
RETURNS VARCHAR(20) AS $$
DECLARE
    v_claim_number   VARCHAR(20);
    v_policy_status  VARCHAR(20);
    v_issue_date     DATE;
    v_expiry_date    DATE;
    v_face_value     NUMERIC(12,2);
    v_ben_policy_id  INT;
    v_benefit_pct    NUMERIC(5,2);
    v_claim_amount   NUMERIC(12,2);
BEGIN
    -- ── Validate policy ──────────────────────────────────────
    SELECT status, issue_date, expiration_date, face_value
    INTO   v_policy_status, v_issue_date, v_expiry_date, v_face_value
    FROM   policies
    WHERE  policy_id = p_policy_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Policy ID % does not exist.', p_policy_id;
    END IF;

    IF v_policy_status != 'active' THEN
        RAISE EXCEPTION 'Policy % is not active (status: %). Cannot file claim.',
            p_policy_id, v_policy_status;
    END IF;

    IF p_date_of_death < v_issue_date THEN
        RAISE EXCEPTION 'Date of death (%) is before policy issue date (%).',
            p_date_of_death, v_issue_date;
    END IF;

    IF v_expiry_date IS NOT NULL AND p_date_of_death > v_expiry_date THEN
        RAISE EXCEPTION 'Date of death (%) is after policy expiration (%). Policy: %.',
            p_date_of_death, v_expiry_date, p_policy_id;
    END IF;

    -- ── Validate beneficiary belongs to this policy ──────────
    SELECT policy_id, percentage
    INTO   v_ben_policy_id, v_benefit_pct
    FROM   beneficiaries
    WHERE  beneficiary_id = p_beneficiary_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Beneficiary ID % does not exist.', p_beneficiary_id;
    END IF;

    IF v_ben_policy_id != p_policy_id THEN
        RAISE EXCEPTION 'Beneficiary % does not belong to policy %.',
            p_beneficiary_id, p_policy_id;
    END IF;

    -- ── Calculate claim amount ───────────────────────────────
    v_claim_amount := ROUND(v_face_value * (v_benefit_pct / 100.0), 2);

    -- ── Generate unique claim number ─────────────────────────
    v_claim_number := 'CLM-' || TO_CHAR(CURRENT_DATE, 'YYYY') || '-' ||
                      LPAD(CAST(nextval('claim_number_seq') AS VARCHAR), 5, '0');

    -- ── Insert the claim ─────────────────────────────────────
    INSERT INTO claims (
        claim_number, policy_id, beneficiary_id,
        date_of_death, date_filed, cause_of_death,
        claim_amount, status, notes
    ) VALUES (
        v_claim_number, p_policy_id, p_beneficiary_id,
        p_date_of_death, CURRENT_DATE, p_cause_of_death,
        v_claim_amount, 'pending', p_notes
    );

    RAISE NOTICE 'Claim % filed successfully. Amount: $%.', v_claim_number, v_claim_amount;
    RETURN v_claim_number;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION file_new_claim IS
    'Validates and files a new life insurance claim. Checks policy status, coverage dates, and beneficiary ownership. Returns the new claim number.';


-- ─────────────────────────────────────────────────────────────
-- FUNCTION 2: update_claim_status()
-- Enforces valid status transitions, sets decision dates,
-- and requires a denial reason when denying a claim.
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_claim_status(
    p_claim_number   VARCHAR,
    p_new_status     VARCHAR,
    p_examiner       VARCHAR DEFAULT NULL,
    p_denial_reason  VARCHAR DEFAULT NULL,
    p_notes          TEXT    DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    v_claim_id     INT;
    v_old_status   VARCHAR(30);
BEGIN
    SELECT claim_id, status
    INTO   v_claim_id, v_old_status
    FROM   claims
    WHERE  claim_number = p_claim_number
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Claim % not found.', p_claim_number;
    END IF;

    -- ── Enforce status transition rules ──────────────────────
    IF v_old_status = 'paid' THEN
        RAISE EXCEPTION 'Claim % is already paid and cannot be modified.', p_claim_number;
    END IF;

    IF v_old_status = 'withdrawn' THEN
        RAISE EXCEPTION 'Claim % has been withdrawn and cannot be reactivated.', p_claim_number;
    END IF;

    IF v_old_status = 'denied' AND p_new_status NOT IN ('under_review', 'withdrawn') THEN
        RAISE EXCEPTION 'Denied claim % can only be moved to under_review (for appeal) or withdrawn.',
            p_claim_number;
    END IF;

    IF p_new_status = 'denied' AND (p_denial_reason IS NULL OR TRIM(p_denial_reason) = '') THEN
        RAISE EXCEPTION 'A denial_reason is required when denying a claim. Claim: %.',
            p_claim_number;
    END IF;

    IF p_new_status = 'approved' AND v_old_status NOT IN ('under_review', 'pending') THEN
        RAISE EXCEPTION 'Claim % must be under_review or pending before it can be approved.',
            p_claim_number;
    END IF;

    -- ── Apply the update ─────────────────────────────────────
    UPDATE claims SET
        status            = p_new_status,
        assigned_examiner = COALESCE(p_examiner, assigned_examiner),
        denial_reason     = CASE WHEN p_new_status = 'denied'
                                 THEN p_denial_reason
                                 ELSE denial_reason END,
        date_approved     = CASE WHEN p_new_status = 'approved' AND date_approved IS NULL
                                 THEN CURRENT_DATE ELSE date_approved END,
        date_denied       = CASE WHEN p_new_status = 'denied'   AND date_denied   IS NULL
                                 THEN CURRENT_DATE ELSE date_denied   END,
        date_paid         = CASE WHEN p_new_status = 'paid'     AND date_paid     IS NULL
                                 THEN CURRENT_DATE ELSE date_paid     END,
        notes             = CASE WHEN p_notes IS NOT NULL
                                 THEN COALESCE(notes, '') ||
                                      E'\n[' || TO_CHAR(NOW(), 'YYYY-MM-DD') || '] ' || p_notes
                                 ELSE notes END
    WHERE claim_id = v_claim_id;

    RAISE NOTICE 'Claim % updated: % → %.', p_claim_number, v_old_status, p_new_status;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_claim_status IS
    'Updates claim status with full transition validation. Enforces business rules: paid claims locked, denial requires reason, approved requires review stage.';


-- ─────────────────────────────────────────────────────────────
-- FUNCTION 3: assign_examiner()
-- Automatically assigns the examiner with the lowest current
-- open-claim workload. Moves claim to under_review.
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION assign_examiner(
    p_claim_number VARCHAR
)
RETURNS VARCHAR(100) AS $$
DECLARE
    v_claim_id   INT;
    v_old_status VARCHAR(30);
    v_examiner   VARCHAR(100);
BEGIN
    SELECT claim_id, status
    INTO   v_claim_id, v_old_status
    FROM   claims
    WHERE  claim_number = p_claim_number
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Claim % not found.', p_claim_number;
    END IF;

    IF v_old_status NOT IN ('pending') THEN
        RAISE EXCEPTION 'Claim % must be in pending status to assign an examiner (current: %).',
            p_claim_number, v_old_status;
    END IF;

    -- Find the active examiner with the fewest open claims
    SELECT assigned_examiner
    INTO   v_examiner
    FROM   claims
    WHERE  status IN ('under_review', 'pending')
      AND  assigned_examiner IS NOT NULL
    GROUP  BY assigned_examiner
    ORDER  BY COUNT(*) ASC
    LIMIT  1;

    -- Fallback if no existing examiners found
    IF v_examiner IS NULL THEN
        v_examiner := 'Sarah Donovan';
    END IF;

    UPDATE claims SET
        assigned_examiner = v_examiner,
        status            = 'under_review'
    WHERE claim_id = v_claim_id;

    RAISE NOTICE 'Claim % assigned to % and moved to under_review.', p_claim_number, v_examiner;
    RETURN v_examiner;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION assign_examiner IS
    'Assigns the examiner with the lowest current workload to a pending claim and advances status to under_review.';


-- ─────────────────────────────────────────────────────────────
-- FUNCTION 4: process_claim_payment()
-- Creates a payment record for an approved claim and marks
-- the claim as paid. Validates claim is approved first.
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION process_claim_payment(
    p_claim_number   VARCHAR,
    p_payment_method VARCHAR,
    p_check_number   VARCHAR DEFAULT NULL
)
RETURNS INT AS $$
DECLARE
    v_claim_id       INT;
    v_status         VARCHAR(30);
    v_beneficiary_id INT;
    v_claim_amount   NUMERIC(12,2);
    v_payment_id     INT;
BEGIN
    SELECT claim_id, status, beneficiary_id, claim_amount
    INTO   v_claim_id, v_status, v_beneficiary_id, v_claim_amount
    FROM   claims
    WHERE  claim_number = p_claim_number
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Claim % not found.', p_claim_number;
    END IF;

    IF v_status != 'approved' THEN
        RAISE EXCEPTION 'Claim % must be approved before payment can be processed (current status: %).',
            p_claim_number, v_status;
    END IF;

    IF p_payment_method NOT IN ('check', 'wire_transfer', 'ach', 'escrow') THEN
        RAISE EXCEPTION 'Invalid payment method: %. Must be check, wire_transfer, ach, or escrow.',
            p_payment_method;
    END IF;

    -- Insert payment record
    INSERT INTO claim_payments (
        claim_id, beneficiary_id, payment_amount,
        payment_date, payment_method, check_number, status
    ) VALUES (
        v_claim_id, v_beneficiary_id, v_claim_amount,
        CURRENT_DATE, p_payment_method, p_check_number, 'processed'
    )
    RETURNING payment_id INTO v_payment_id;

    -- Mark claim as paid
    UPDATE claims SET
        status    = 'paid',
        date_paid = CURRENT_DATE
    WHERE claim_id = v_claim_id;

    RAISE NOTICE 'Payment of $% processed for claim % via %. Payment ID: %.',
        v_claim_amount, p_claim_number, p_payment_method, v_payment_id;
    RETURN v_payment_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION process_claim_payment IS
    'Creates a payment record for an approved claim and advances its status to paid. Returns the new payment_id.';


-- ─────────────────────────────────────────────────────────────
-- EXAMPLE USAGE
-- ─────────────────────────────────────────────────────────────
/*
-- File a new claim
SELECT file_new_claim(
    6,                          -- policy_id
    6,                          -- beneficiary_id
    '2024-12-01',               -- date_of_death
    'Natural causes',           -- cause_of_death
    'Beneficiary contacted by phone 2024-12-03'
);

-- Move through the workflow
SELECT assign_examiner('CLM-2024-00500');

SELECT update_claim_status(
    'CLM-2024-00500',
    'approved',
    'Michael Torres',
    NULL,
    'All documents verified. Claim approved.'
);

SELECT process_claim_payment('CLM-2024-00500', 'wire_transfer');

-- Deny a claim (requires reason)
SELECT update_claim_status(
    'CLM-2024-00501',
    'denied',
    'Sarah Donovan',
    'Policy lapsed due to non-payment at time of death',
    'Non-payment confirmed via billing records'
);
*/
