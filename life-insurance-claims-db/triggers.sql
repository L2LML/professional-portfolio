-- ============================================================
-- Life Insurance Claims Database — Triggers & Audit
-- Author: Lisa Lewandowski
-- ============================================================


-- ── AUDIT TABLE ──────────────────────────────────────────────
-- Tracks every status and examiner change on every claim
CREATE TABLE IF NOT EXISTS claims_audit (
    audit_id      SERIAL        PRIMARY KEY,
    claim_id      INT           NOT NULL,
    claim_number  VARCHAR(20)   NOT NULL,
    change_type   VARCHAR(20)   NOT NULL,   -- INSERT | STATUS_CHANGE | EXAMINER_CHANGE
    old_status    VARCHAR(30),
    new_status    VARCHAR(30),
    old_examiner  VARCHAR(100),
    new_examiner  VARCHAR(100),
    changed_by    VARCHAR(100)  DEFAULT CURRENT_USER,
    changed_at    TIMESTAMP     DEFAULT NOW(),
    change_notes  TEXT
);

COMMENT ON TABLE claims_audit IS 'Immutable audit log — every insert and status/examiner change on claims';


-- ── TRIGGER 1: AUTO-UPDATE updated_at ────────────────────────
-- Fires on every UPDATE to claims; sets updated_at = NOW()
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_claims_updated_at ON claims;
CREATE TRIGGER trg_claims_updated_at
    BEFORE UPDATE ON claims
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_updated_at();

COMMENT ON TRIGGER trg_claims_updated_at ON claims IS
    'Automatically refreshes updated_at timestamp on every row update';


-- ── TRIGGER 2: CLAIMS AUDIT TRAIL ────────────────────────────
-- Fires AFTER INSERT or UPDATE; logs every status/examiner change
CREATE OR REPLACE FUNCTION fn_claims_audit()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO claims_audit (
            claim_id, claim_number, change_type,
            new_status, new_examiner
        ) VALUES (
            NEW.claim_id, NEW.claim_number, 'INSERT',
            NEW.status, NEW.assigned_examiner
        );

    ELSIF TG_OP = 'UPDATE' THEN
        -- Only log if status or examiner actually changed
        IF OLD.status IS DISTINCT FROM NEW.status OR
           OLD.assigned_examiner IS DISTINCT FROM NEW.assigned_examiner THEN

            INSERT INTO claims_audit (
                claim_id, claim_number, change_type,
                old_status,    new_status,
                old_examiner,  new_examiner,
                change_notes
            ) VALUES (
                NEW.claim_id, NEW.claim_number,
                CASE WHEN OLD.status IS DISTINCT FROM NEW.status
                     THEN 'STATUS_CHANGE' ELSE 'EXAMINER_CHANGE' END,
                OLD.status,    NEW.status,
                OLD.assigned_examiner, NEW.assigned_examiner,
                CASE WHEN OLD.status IS DISTINCT FROM NEW.status
                     THEN OLD.status || ' → ' || NEW.status
                     ELSE 'Examiner reassigned' END
            );
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_claims_audit ON claims;
CREATE TRIGGER trg_claims_audit
    AFTER INSERT OR UPDATE ON claims
    FOR EACH ROW
    EXECUTE FUNCTION fn_claims_audit();

COMMENT ON TRIGGER trg_claims_audit ON claims IS
    'Writes an audit record on every claim insert and on any status or examiner change';


-- ── TRIGGER 3: BENEFICIARY PERCENTAGE VALIDATION ─────────────
-- Prevents total allocation exceeding 100% per policy per tier
-- (primary and contingent tracked separately)
CREATE OR REPLACE FUNCTION fn_validate_beneficiary_pct()
RETURNS TRIGGER AS $$
DECLARE
    v_total_pct NUMERIC(7,2);
BEGIN
    SELECT COALESCE(SUM(percentage), 0)
    INTO v_total_pct
    FROM beneficiaries
    WHERE policy_id  = NEW.policy_id
      AND is_primary = NEW.is_primary
      AND (TG_OP = 'INSERT' OR beneficiary_id != NEW.beneficiary_id);

    v_total_pct := v_total_pct + NEW.percentage;

    IF v_total_pct > 100 THEN
        RAISE EXCEPTION
            'Beneficiary allocation for policy % (% tier) would reach %% — maximum is 100%%',
            NEW.policy_id,
            CASE WHEN NEW.is_primary THEN 'primary' ELSE 'contingent' END,
            v_total_pct;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validate_beneficiary_pct ON beneficiaries;
CREATE TRIGGER trg_validate_beneficiary_pct
    BEFORE INSERT OR UPDATE ON beneficiaries
    FOR EACH ROW
    EXECUTE FUNCTION fn_validate_beneficiary_pct();

COMMENT ON TRIGGER trg_validate_beneficiary_pct ON beneficiaries IS
    'Prevents primary or contingent beneficiary allocations from exceeding 100% per policy';


-- ── TRIGGER 4: POLICY ACTIVE CHECK ON CLAIM INSERT ───────────
-- Warns (via NOTICE) if the policy was not active at date of death
-- Does NOT block — examiners may still accept with documentation
CREATE OR REPLACE FUNCTION fn_check_policy_active_at_death()
RETURNS TRIGGER AS $$
DECLARE
    v_policy_status VARCHAR(20);
    v_issue_date    DATE;
    v_expiry_date   DATE;
BEGIN
    SELECT status, issue_date, expiration_date
    INTO v_policy_status, v_issue_date, v_expiry_date
    FROM policies
    WHERE policy_id = NEW.policy_id;

    IF v_policy_status != 'active' THEN
        RAISE NOTICE
            'WARNING: Policy % has status "%" — claim % may not be payable. Examiner review required.',
            NEW.policy_id, v_policy_status, NEW.claim_number;
    END IF;

    IF NEW.date_of_death < v_issue_date THEN
        RAISE EXCEPTION
            'Date of death (%) precedes policy issue date (%) — claim cannot be filed.',
            NEW.date_of_death, v_issue_date;
    END IF;

    IF v_expiry_date IS NOT NULL AND NEW.date_of_death > v_expiry_date THEN
        RAISE NOTICE
            'WARNING: Date of death (%) is after policy expiration (%) — claim % flagged for review.',
            NEW.date_of_death, v_expiry_date, NEW.claim_number;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_policy_active_at_death ON claims;
CREATE TRIGGER trg_check_policy_active_at_death
    BEFORE INSERT ON claims
    FOR EACH ROW
    EXECUTE FUNCTION fn_check_policy_active_at_death();

COMMENT ON TRIGGER trg_check_policy_active_at_death ON claims IS
    'Raises an exception if date_of_death precedes policy issue; issues a NOTICE for expired/lapsed policies';
