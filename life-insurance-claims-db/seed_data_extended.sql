-- ============================================================
-- Life Insurance Claims Database — Extended Seed Data
-- Adds policyholders, policies, beneficiaries, and historical
-- claims to bring total to 50+ claims for richer analytics.
-- Run AFTER seed_data.sql
-- ============================================================


-- ── ADDITIONAL POLICYHOLDERS (16–21) ─────────────────────────
INSERT INTO policyholders (first_name, last_name, date_of_birth, ssn_last4, email, phone, address_street, address_city, address_state, address_zip, gender, smoker) VALUES
('Sylvia',   'Hartman',    '1943-06-12', '5578', 's.hartman@email.com',  '248-555-1016', '14 Willowbrook Dr',  'Pontiac',      'MI', '48342', 'Female', FALSE),
('Jerome',   'Banks',      '1971-11-28', '2234', 'j.banks@email.com',    '313-555-1017', '520 Gratiot Ave',    'Detroit',      'MI', '48207', 'Male',   FALSE),
('Norma',    'Espinoza',   '1936-02-19', '9967', 'n.espinoza@email.com', '614-555-1018', '88 Dublin Rd',       'Columbus',     'OH', '43215', 'Female', FALSE),
('Calvin',   'Price',      '1978-04-03', '3389', 'c.price@email.com',    '317-555-1019', '237 Kessler Blvd',   'Indianapolis', 'IN', '46228', 'Male',   TRUE),
('Mildred',  'Grant',      '1929-09-07', '7701', NULL,                   '734-555-1020', '6 Huron Hills Ct',   'Ann Arbor',    'MI', '48103', 'Female', FALSE),
('Derek',    'Holloway',   '1983-07-15', '4456', 'd.holloway@email.com', '248-555-1021', '93 Inkster Rd',      'Garden City',  'MI', '48135', 'Male',   FALSE);


-- ── ADDITIONAL POLICIES (19–24) ──────────────────────────────
INSERT INTO policies (policy_number, policyholder_id, policy_type_id, agent_id, face_value, annual_premium, issue_date, expiration_date, status, riders) VALUES
('POL-2003-00037',  16, 2, 6,  150000.00, 2600.00, '2003-08-14', NULL,         'active',  'waiver of premium'),
('POL-2017-00391',  17, 1, 7,  350000.00,  870.00, '2017-05-01', '2037-05-01', 'active',  'accidental death'),
('POL-1995-00001',  18, 2, 2,   75000.00, 1950.00, '1995-01-10', NULL,         'active',  NULL),
('POL-2021-00558',  19, 3, 5,  500000.00, 3400.00, '2021-09-20', NULL,         'active',  'long-term care'),
('POL-2006-00061',  20, 5, 4,   15000.00,  720.00, '2006-03-01', NULL,         'active',  NULL),
('POL-2019-00474',  21, 1, 8,  250000.00,  610.00, '2019-11-15', '2039-11-15', 'active',  NULL);


-- ── ADDITIONAL BENEFICIARIES ──────────────────────────────────
INSERT INTO beneficiaries (policy_id, first_name, last_name, relationship, percentage, is_primary, date_of_birth, phone, email) VALUES
-- Policy 6 (Barbara Nguyen — no beneficiaries yet)
(6,  'Thomas',   'Nguyen',    'Spouse',  100.00, TRUE,  '1973-08-19', '614-555-2018', 't.nguyen@email.com'),
-- Policy 8 (Patricia Washington — no beneficiaries yet)
(8,  'Marcus',   'Washington','Spouse',  100.00, TRUE,  '1978-03-22', '248-555-2019', NULL),
-- Policy 12 (Helen Okafor — no beneficiaries yet)
(12, 'Samuel',   'Okafor',    'Spouse',  100.00, TRUE,  '1988-06-11', '317-555-2020', 's.okafor@email.com'),
-- Policy 14 (Gloria Reed — no beneficiaries yet)
(14, 'Jamal',    'Reed',      'Spouse',  100.00, TRUE,  '1983-02-07', '248-555-2021', 'j.reed@email.com'),
-- Policy 18 (Final Expense — George Martinez)
(18, 'Rosa',     'Martinez',  'Spouse',  100.00, TRUE,  '1958-12-03', '734-555-2011', 'rmartinez@email.com'),
-- Policy 19 (Sylvia Hartman)
(19, 'Robert',   'Hartman',   'Child',    50.00, TRUE,  '1968-04-15', '248-555-2022', 'r.hartman@email.com'),
(19, 'Janet',    'Hartman',   'Child',    50.00, TRUE,  '1971-09-20', '248-555-2023', NULL),
-- Policy 20 (Jerome Banks)
(20, 'Denise',   'Banks',     'Spouse',  100.00, TRUE,  '1974-07-30', '313-555-2024', 'd.banks@email.com'),
-- Policy 21 (Norma Espinoza)
(21, 'Luis',     'Espinoza',  'Child',    60.00, TRUE,  '1959-11-05', '614-555-2025', NULL),
(21, 'Elena',    'Espinoza',  'Child',    40.00, TRUE,  '1962-03-14', '614-555-2026', 'e.espinoza@email.com'),
-- Policy 22 (Calvin Price)
(22, 'Tanya',    'Price',     'Spouse',  100.00, TRUE,  '1980-01-19', '317-555-2027', 't.price@email.com'),
-- Policy 23 (Mildred Grant — Final Expense)
(23, 'Howard',   'Grant',     'Child',   100.00, TRUE,  '1952-08-22', '734-555-2028', NULL),
-- Policy 24 (Derek Holloway)
(24, 'Alicia',   'Holloway',  'Spouse',  100.00, TRUE,  '1985-11-03', '248-555-2029', 'a.holloway@email.com');


-- ── HISTORICAL PAID CLAIMS (2018–2023) ───────────────────────
-- Adds volume for trend analysis, aging, and aggregate queries

INSERT INTO claims (claim_number, policy_id, beneficiary_id, date_of_death, date_filed, cause_of_death, claim_amount, status, assigned_examiner, date_approved, date_paid, notes) VALUES
-- 2018
('CLM-2018-00003', 5,  7,  '2018-02-14', '2018-02-28', 'Heart disease',    150000.00, 'paid', 'James Whitfield','2018-03-25', '2018-03-30', 'Spouse 50% — Walter Simmons prior claim'),
('CLM-2018-00004', 5,  8,  '2018-02-14', '2018-02-28', 'Heart disease',     75000.00, 'paid', 'James Whitfield','2018-03-25', '2018-03-30', 'Child James 25%'),
('CLM-2018-00005', 5,  9,  '2018-02-14', '2018-02-28', 'Heart disease',     75000.00, 'paid', 'James Whitfield','2018-03-25', '2018-03-30', 'Child Karen 25%'),
('CLM-2018-00011', 7,  10, '2018-07-19', '2018-08-02', 'Stroke',           100000.00, 'paid', 'Sarah Donovan',  '2018-08-28', '2018-09-03', NULL),
-- 2019
('CLM-2019-00007', 9,  11, '2019-03-05', '2019-03-18', 'Cancer',           320000.00, 'paid', 'Michael Torres', '2019-04-20', '2019-04-25', 'Spouse Rosa 80%'),
('CLM-2019-00008', 9,  12, '2019-03-05', '2019-03-18', 'Cancer',            80000.00, 'paid', 'Michael Torres', '2019-04-20', '2019-04-25', 'Child Carlos 20%'),
('CLM-2019-00014', 15, 16, '2019-11-22', '2019-12-03', 'Cardiac arrest',   100000.00, 'paid', 'Sarah Donovan',  '2019-12-28', '2020-01-04', 'Spouse Yuki 50%'),
('CLM-2019-00015', 15, 17, '2019-11-22', '2019-12-03', 'Cardiac arrest',   100000.00, 'paid', 'Sarah Donovan',  '2019-12-28', '2020-01-04', 'Child Kenji 50%'),
-- 2020
('CLM-2020-00022', 2,  2,  '2020-05-08', '2020-05-19', 'COVID-19',         150000.00, 'paid', 'James Whitfield','2020-06-14', '2020-06-18', 'Spouse Luis 60% — expedited review'),
('CLM-2020-00023', 2,  3,  '2020-05-08', '2020-05-19', 'COVID-19',         100000.00, 'paid', 'James Whitfield','2020-06-14', '2020-06-18', 'Child Maria 40%'),
('CLM-2020-00031', 10, 13, '2020-09-30', '2020-10-10', 'Natural causes',    37500.00, 'paid', 'Michael Torres', '2020-11-01', '2020-11-05', 'Child Edward 50%'),
('CLM-2020-00032', 10, 14, '2020-09-30', '2020-10-10', 'Natural causes',    37500.00, 'paid', 'Michael Torres', '2020-11-01', '2020-11-05', 'Child Susan 50%'),
-- 2021
('CLM-2021-00044', 1,  1,  '2021-01-17', '2021-02-01', 'COVID-19',         500000.00, 'paid', 'Sarah Donovan',  '2021-02-28', '2021-03-05', 'Spouse Margaret 100% — accidental death rider N/A'),
('CLM-2021-00059', 13, 15, '2021-08-10', '2021-08-20', 'Cancer',           400000.00, 'paid', 'James Whitfield','2021-09-15', '2021-09-20', 'Spouse Marie 100%'),
-- 2022
('CLM-2022-00068', 3,  4,  '2022-03-22', '2022-04-01', 'Cardiac arrest',   525000.00, 'paid', 'Michael Torres', '2022-05-01', '2022-05-07', 'Accidental death rider — additional benefit included'),
('CLM-2022-00069', 3,  5,  '2022-03-22', '2022-04-01', 'Cardiac arrest',   225000.00, 'paid', 'Michael Torres', '2022-05-01', '2022-05-07', 'Child Tyler 30%'),
('CLM-2022-00078', 11, 18, '2022-11-05', '2022-11-15', 'Stroke',           600000.00, 'paid', 'Sarah Donovan',  '2022-12-10', '2022-12-15', 'Primary beneficiary'),
-- 2023
('CLM-2023-00041', 4,  6,  '2023-04-14', '2023-04-25', 'Cancer',          1000000.00, 'paid', 'James Whitfield','2023-05-28', '2023-06-02', 'Spouse David 100%'),
('CLM-2023-00055', 19, 25, '2023-06-30', '2023-07-10', 'Natural causes',    75000.00, 'paid', 'Michael Torres', '2023-08-05', '2023-08-10', 'Child Robert 50%'),
('CLM-2023-00056', 19, 26, '2023-06-30', '2023-07-10', 'Natural causes',    75000.00, 'paid', 'Michael Torres', '2023-08-05', '2023-08-10', 'Child Janet 50%'),
('CLM-2023-00062', 21, 28, '2023-09-18', '2023-09-28', 'Stroke',            45000.00, 'paid', 'Sarah Donovan',  '2023-10-20', '2023-10-25', 'Child Luis 60%'),
('CLM-2023-00063', 21, 29, '2023-09-18', '2023-09-28', 'Stroke',            30000.00, 'paid', 'Sarah Donovan',  '2023-10-20', '2023-10-25', 'Child Elena 40%'),
-- 2024 additional
('CLM-2024-00033', 20, 27, '2024-02-11', '2024-02-20', 'Natural causes',   350000.00, 'paid', 'James Whitfield','2024-03-18', '2024-03-22', 'Spouse Denise 100%'),
('CLM-2024-00047', 23, 32, '2024-04-05', '2024-04-14', 'Natural causes',    15000.00, 'paid', 'Michael Torres', '2024-05-01', '2024-05-05', 'Final Expense — Child Howard'),
('CLM-2024-00061', 18, 24, '2024-05-20', '2024-05-28', 'Cardiac arrest',    20000.00, 'paid', 'Sarah Donovan',  '2024-06-18', '2024-06-22', 'Final Expense — Spouse Rosa'),
('CLM-2024-00082', 6,  18, '2024-07-03', '2024-07-12', 'Cancer',           250000.00, 'paid', 'James Whitfield','2024-08-08', '2024-08-14', 'Spouse Thomas 100%'),
('CLM-2024-00091', 8,  19, '2024-07-28', '2024-08-05', 'Accidental',       500000.00, 'paid', 'Michael Torres', '2024-09-02', '2024-09-08', 'Accidental death — police report verified'),
-- Denied
('CLM-2024-00108', 22, 31, '2024-09-14', '2024-09-22', 'Suicide',          500000.00, 'denied', 'Sarah Donovan', NULL, NULL, 'Policy issued 2021 — within 2-year suicide exclusion'),
('CLM-2023-00079', 24, 33, '2023-12-01', '2023-12-10', 'Natural causes',   250000.00, 'denied', 'James Whitfield', NULL, NULL, 'Beneficiary contested — estate dispute pending');

-- Set denial dates
UPDATE claims SET date_denied = '2024-10-15' WHERE claim_number = 'CLM-2024-00108';
UPDATE claims SET date_denied = '2024-01-10' WHERE claim_number = 'CLM-2023-00079';

-- Set denial reasons
UPDATE claims SET denial_reason = 'Policy within 2-year suicide exclusion period — claim not payable under contestability clause'
WHERE claim_number = 'CLM-2024-00108';

UPDATE claims SET denial_reason = 'Beneficiary designation disputed by estate — claim held pending probate court ruling'
WHERE claim_number = 'CLM-2023-00079';


-- ── HISTORICAL PAYMENTS ───────────────────────────────────────
INSERT INTO claim_payments (claim_id, beneficiary_id, payment_amount, payment_date, payment_method, check_number, status)
SELECT c.claim_id, c.beneficiary_id, c.claim_amount, c.date_paid,
       CASE WHEN c.claim_amount > 100000 THEN 'wire_transfer'
            WHEN c.claim_amount > 50000  THEN 'ach'
            ELSE 'check' END,
       CASE WHEN c.claim_amount <= 50000 THEN 'CHK-' || LPAD(CAST(c.claim_id + 40000 AS VARCHAR), 7, '0') ELSE NULL END,
       'cleared'
FROM claims c
WHERE c.status = 'paid'
  AND c.date_paid IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM claim_payments cp WHERE cp.claim_id = c.claim_id
  );
