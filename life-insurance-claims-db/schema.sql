-- ============================================================
-- Life Insurance Claims Database
-- Author: Lisa Lewandowski
-- Description: Schema for managing life insurance policies,
--              policyholders, beneficiaries, claims, and payments.
-- Database: PostgreSQL 14+
-- ============================================================

-- ── Drop tables if rebuilding ─────────────────────────────────
DROP TABLE IF EXISTS claim_payments   CASCADE;
DROP TABLE IF EXISTS claim_documents  CASCADE;
DROP TABLE IF EXISTS claims           CASCADE;
DROP TABLE IF EXISTS beneficiaries    CASCADE;
DROP TABLE IF EXISTS policies         CASCADE;
DROP TABLE IF EXISTS policyholders    CASCADE;
DROP TABLE IF EXISTS agents           CASCADE;
DROP TABLE IF EXISTS policy_types     CASCADE;


-- ── 1. POLICY TYPES ──────────────────────────────────────────
CREATE TABLE policy_types (
    policy_type_id  SERIAL PRIMARY KEY,
    type_name       VARCHAR(50)  NOT NULL UNIQUE,
    description     TEXT,
    has_cash_value  BOOLEAN      DEFAULT FALSE,
    created_at      TIMESTAMP    DEFAULT NOW()
);

COMMENT ON TABLE  policy_types              IS 'Life insurance product categories';
COMMENT ON COLUMN policy_types.has_cash_value IS 'TRUE for whole/universal life — builds cash value over time';


-- ── 2. AGENTS ────────────────────────────────────────────────
CREATE TABLE agents (
    agent_id        SERIAL PRIMARY KEY,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    license_number  VARCHAR(30)  NOT NULL UNIQUE,
    email           VARCHAR(100) UNIQUE,
    phone           VARCHAR(20),
    state           CHAR(2),
    hire_date       DATE,
    is_active       BOOLEAN      DEFAULT TRUE,
    created_at      TIMESTAMP    DEFAULT NOW()
);

COMMENT ON TABLE agents IS 'Licensed insurance agents who sell and service policies';


-- ── 3. POLICYHOLDERS ─────────────────────────────────────────
CREATE TABLE policyholders (
    policyholder_id SERIAL PRIMARY KEY,
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    date_of_birth   DATE         NOT NULL,
    ssn_last4       CHAR(4),
    email           VARCHAR(100),
    phone           VARCHAR(20),
    address_street  VARCHAR(100),
    address_city    VARCHAR(50),
    address_state   CHAR(2),
    address_zip     VARCHAR(10),
    gender          VARCHAR(10),
    smoker              BOOLEAN      DEFAULT FALSE,
    policyholder_since  DATE,
    created_at          TIMESTAMP    DEFAULT NOW()
);

COMMENT ON TABLE  policyholders                    IS 'Insured individuals who hold life insurance policies';
COMMENT ON COLUMN policyholders.policyholder_since IS 'Date of first policy with this company — used for tenure analysis and loyalty segmentation';
COMMENT ON COLUMN policyholders.ssn_last4 IS 'Last 4 digits of SSN only — full SSN stored in secure vault';
COMMENT ON COLUMN policyholders.smoker    IS 'Smoking status affects premium calculation';


-- ── 4. POLICIES ──────────────────────────────────────────────
CREATE TABLE policies (
    policy_id       SERIAL PRIMARY KEY,
    policy_number   VARCHAR(20)  NOT NULL UNIQUE,
    policyholder_id INT          NOT NULL REFERENCES policyholders(policyholder_id),
    policy_type_id  INT          NOT NULL REFERENCES policy_types(policy_type_id),
    agent_id        INT          REFERENCES agents(agent_id),
    face_value      NUMERIC(12,2) NOT NULL,
    annual_premium  NUMERIC(10,2) NOT NULL,
    issue_date      DATE         NOT NULL,
    expiration_date DATE,
    status          VARCHAR(20)  NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active','lapsed','surrendered','matured','expired')),
    riders          TEXT,
    age_at_issue    INT,
    created_at      TIMESTAMP    DEFAULT NOW(),

    CONSTRAINT chk_face_value     CHECK (face_value > 0),
    CONSTRAINT chk_annual_premium CHECK (annual_premium > 0)
);

COMMENT ON TABLE  policies              IS 'Life insurance policies issued to policyholders';
COMMENT ON COLUMN policies.age_at_issue IS 'Snapshot of policyholder age at policy issuance — used for actuarial banding and premium analysis; does not change over time';
COMMENT ON COLUMN policies.face_value   IS 'Death benefit — amount paid to beneficiaries upon claim approval';
COMMENT ON COLUMN policies.riders       IS 'Optional add-ons, e.g. accidental death, waiver of premium';
COMMENT ON COLUMN policies.expiration_date IS 'NULL for permanent (whole/universal) policies';


-- ── 5. BENEFICIARIES ─────────────────────────────────────────
CREATE TABLE beneficiaries (
    beneficiary_id  SERIAL PRIMARY KEY,
    policy_id       INT          NOT NULL REFERENCES policies(policy_id),
    first_name      VARCHAR(50)  NOT NULL,
    last_name       VARCHAR(50)  NOT NULL,
    relationship    VARCHAR(30),
    percentage      NUMERIC(5,2) NOT NULL
                        CHECK (percentage > 0 AND percentage <= 100),
    is_primary      BOOLEAN      DEFAULT TRUE,
    date_of_birth   DATE,
    ssn_last4       CHAR(4),
    phone           VARCHAR(20),
    email           VARCHAR(100),
    created_at      TIMESTAMP    DEFAULT NOW()
);

COMMENT ON TABLE  beneficiaries             IS 'Individuals or entities designated to receive policy proceeds';
COMMENT ON COLUMN beneficiaries.percentage   IS 'Percentage of face value allocated to this beneficiary';
COMMENT ON COLUMN beneficiaries.is_primary   IS 'TRUE = primary beneficiary; FALSE = contingent';


-- ── 6. CLAIMS ────────────────────────────────────────────────
CREATE TABLE claims (
    claim_id          SERIAL PRIMARY KEY,
    claim_number      VARCHAR(20)  NOT NULL UNIQUE,
    policy_id         INT          NOT NULL REFERENCES policies(policy_id),
    beneficiary_id    INT          NOT NULL REFERENCES beneficiaries(beneficiary_id),
    date_of_death     DATE         NOT NULL,
    date_filed        DATE         NOT NULL,
    cause_of_death    VARCHAR(100),
    claim_amount      NUMERIC(12,2) NOT NULL,
    status            VARCHAR(30)  NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending','under_review','approved','denied','paid','withdrawn')),
    assigned_examiner VARCHAR(100),
    denial_reason     VARCHAR(200),
    date_approved     DATE,
    date_denied       DATE,
    date_paid         DATE,
    notes             TEXT,
    created_at        TIMESTAMP    DEFAULT NOW(),
    updated_at        TIMESTAMP    DEFAULT NOW(),

    CONSTRAINT chk_claim_amount   CHECK (claim_amount > 0),
    CONSTRAINT chk_death_before_filed CHECK (date_of_death <= date_filed)
);

COMMENT ON TABLE  claims                IS 'Death benefit claims filed by beneficiaries';
COMMENT ON COLUMN claims.cause_of_death IS 'e.g. natural causes, accidental, cardiac, cancer — affects investigation scope';
COMMENT ON COLUMN claims.denial_reason  IS 'Required when status = denied';


-- ── 7. CLAIM DOCUMENTS ───────────────────────────────────────
CREATE TABLE claim_documents (
    document_id     SERIAL PRIMARY KEY,
    claim_id        INT          NOT NULL REFERENCES claims(claim_id),
    document_type   VARCHAR(60)  NOT NULL,
    file_name       VARCHAR(150),
    received_date   DATE,
    is_verified     BOOLEAN      DEFAULT FALSE,
    notes           TEXT,
    created_at      TIMESTAMP    DEFAULT NOW()
);

COMMENT ON TABLE  claim_documents              IS 'Supporting documents submitted with or requested for a claim';
COMMENT ON COLUMN claim_documents.document_type IS 'e.g. death_certificate, autopsy_report, medical_records, beneficiary_id, policy_copy';
COMMENT ON COLUMN claim_documents.is_verified   IS 'TRUE once examiner confirms document is authentic and complete';


-- ── 8. CLAIM PAYMENTS ────────────────────────────────────────
CREATE TABLE claim_payments (
    payment_id      SERIAL PRIMARY KEY,
    claim_id        INT          NOT NULL REFERENCES claims(claim_id),
    beneficiary_id  INT          NOT NULL REFERENCES beneficiaries(beneficiary_id),
    payment_amount  NUMERIC(12,2) NOT NULL CHECK (payment_amount > 0),
    payment_date    DATE,
    payment_method  VARCHAR(30)  CHECK (payment_method IN ('check','wire_transfer','ach','escrow')),
    check_number    VARCHAR(20),
    status          VARCHAR(20)  DEFAULT 'pending'
                        CHECK (status IN ('pending','processed','cleared','returned')),
    created_at      TIMESTAMP    DEFAULT NOW()
);

COMMENT ON TABLE claim_payments IS 'Disbursement records for approved claims';


-- ── INDEXES ──────────────────────────────────────────────────
CREATE INDEX idx_policies_policyholder  ON policies(policyholder_id);
CREATE INDEX idx_policies_status        ON policies(status);
CREATE INDEX idx_claims_policy          ON claims(policy_id);
CREATE INDEX idx_claims_status          ON claims(status);
CREATE INDEX idx_claims_date_filed      ON claims(date_filed);
CREATE INDEX idx_beneficiaries_policy   ON beneficiaries(policy_id);
CREATE INDEX idx_payments_claim         ON claim_payments(claim_id);
