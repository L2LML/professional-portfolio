-- ============================================================
-- Life Insurance Claims Database — Seed Data
-- Realistic sample data for development and portfolio demo
-- ============================================================

-- ── POLICY TYPES ─────────────────────────────────────────────
INSERT INTO policy_types (type_name, description, has_cash_value) VALUES
('Term Life',        '10, 20, or 30-year fixed coverage. No cash value. Lowest premiums.',           FALSE),
('Whole Life',       'Permanent coverage with guaranteed cash value accumulation.',                   TRUE),
('Universal Life',   'Flexible permanent coverage with adjustable premiums and cash value.',          TRUE),
('Variable Life',    'Permanent coverage with investment-linked cash value. Higher risk/reward.',     TRUE),
('Final Expense',    'Small whole life policy covering funeral and burial costs. Simplified issue.',  TRUE);


-- ── AGENTS ───────────────────────────────────────────────────
INSERT INTO agents (first_name, last_name, license_number, email, phone, state, hire_date) VALUES
('James',    'Thornton',  'AGT-MI-10042', 'j.thornton@insure.com',   '248-555-0101', 'MI', '2015-03-12'),
('Patricia', 'Nguyen',    'AGT-MI-10078', 'p.nguyen@insure.com',     '248-555-0182', 'MI', '2017-07-01'),
('Robert',   'Alvarez',   'AGT-OH-20031', 'r.alvarez@insure.com',    '614-555-0233', 'OH', '2019-01-15'),
('Sandra',   'Williams',  'AGT-MI-10095', 's.williams@insure.com',   '313-555-0344', 'MI', '2016-09-20'),
('Kevin',    'Okafor',    'AGT-IN-30012', 'k.okafor@insure.com',     '317-555-0455', 'IN', '2020-04-05'),
('Diane',    'Kowalski',  'AGT-MI-10112', 'd.kowalski@insure.com',   '734-555-0566', 'MI', '2018-11-30'),
('Marcus',   'Jefferson', 'AGT-MI-10130', 'm.jefferson@insure.com',  '248-555-0677', 'MI', '2021-06-14'),
('Linda',    'Patel',     'AGT-OH-20058', 'l.patel@insure.com',      '614-555-0788', 'OH', '2022-02-28');


-- ── POLICYHOLDERS ────────────────────────────────────────────
INSERT INTO policyholders (first_name, last_name, date_of_birth, ssn_last4, email, phone, address_street, address_city, address_state, address_zip, gender, smoker) VALUES
('Harold',   'Bennett',    '1952-04-18', '4421', 'h.bennett@email.com',   '248-555-1001', '142 Maple Dr',       'Troy',          'MI', '48084', 'Male',   FALSE),
('Dorothy',  'Castillo',   '1948-09-30', '8834', 'd.castillo@email.com',  '313-555-1002', '78 Lakeview Blvd',   'Detroit',       'MI', '48201', 'Female', FALSE),
('Raymond',  'Foster',     '1965-02-14', '2267', 'r.foster@email.com',    '734-555-1003', '501 Birchwood Ln',   'Ann Arbor',     'MI', '48103', 'Male',   TRUE),
('Carol',    'Hutchinson', '1970-07-22', '6619', 'c.hutch@email.com',     '248-555-1004', '23 Orchard Hill Rd', 'Bloomfield',    'MI', '48302', 'Female', FALSE),
('Walter',   'Simmons',    '1958-11-05', '3345', 'w.simmons@email.com',   '614-555-1005', '890 Riverside Dr',   'Columbus',      'OH', '43215', 'Male',   FALSE),
('Barbara',  'Nguyen',     '1975-03-17', '7712', 'b.nguyen@email.com',    '614-555-1006', '34 Elm Street',      'Cleveland',     'OH', '44101', 'Female', FALSE),
('Thomas',   'O\'Brien',   '1944-12-01', '9981', 't.obrien@email.com',    '317-555-1007', '612 Sunset Ave',     'Indianapolis',  'IN', '46201', 'Male',   TRUE),
('Patricia', 'Washington', '1980-06-08', '5523', 'p.wash@email.com',      '248-555-1008', '100 Cherry Creek Rd','Royal Oak',     'MI', '48067', 'Female', FALSE),
('George',   'Martinez',   '1955-08-25', '1198', 'g.martinez@email.com',  '734-555-1009', '77 Pinecrest Blvd',  'Ypsilanti',     'MI', '48197', 'Male',   FALSE),
('Ruth',     'Thompson',   '1939-01-14', '4467', 'r.thompson@email.com',  '313-555-1010', '350 Warren Ave',     'Dearborn',      'MI', '48124', 'Female', FALSE),
('Dennis',   'Clarke',     '1968-05-30', '8890', 'd.clarke@email.com',    '248-555-1011', '19 Northwood Ct',    'Birmingham',    'MI', '48009', 'Male',   FALSE),
('Helen',    'Okafor',     '1990-10-12', '3312', 'h.okafor@email.com',    '317-555-1012', '455 Broad Ripple Ave','Indianapolis', 'IN', '46220', 'Female', FALSE),
('Frank',    'Deluca',     '1962-07-04', '6634', 'f.deluca@email.com',    '614-555-1013', '201 State Street',   'Akron',         'OH', '44302', 'Male',   TRUE),
('Gloria',   'Reed',       '1985-09-19', '2289', 'g.reed@email.com',      '248-555-1014', '72 Fieldstone Dr',   'Novi',          'MI', '48374', 'Female', FALSE),
('Arthur',   'Yamamoto',   '1950-03-07', '7745', 'a.yamamoto@email.com',  '734-555-1015', '900 Huron Pkwy',     'Ann Arbor',     'MI', '48104', 'Male',   FALSE);


-- ── POLICIES ─────────────────────────────────────────────────
INSERT INTO policies (policy_number, policyholder_id, policy_type_id, agent_id, face_value, annual_premium, issue_date, expiration_date, status, riders) VALUES
('POL-2010-00142',  1,  1, 1, 500000.00,  1850.00, '2010-06-01', '2030-06-01', 'active',      'accidental death'),
('POL-2008-00089',  2,  2, 2, 250000.00,  3200.00, '2008-03-15', NULL,         'active',      'waiver of premium'),
('POL-2015-00301',  3,  1, 1,  750000.00, 3100.00, '2015-09-10', '2035-09-10', 'active',      'accidental death, child rider'),
('POL-2012-00188',  4,  3, 4, 1000000.00, 5400.00, '2012-01-20', NULL,         'active',      'long-term care, waiver of premium'),
('POL-2005-00044',  5,  2, 3,  300000.00, 4100.00, '2005-07-08', NULL,         'active',      NULL),
('POL-2018-00412',  6,  1, 5,  250000.00,  780.00, '2018-11-01', '2038-11-01', 'active',      NULL),
('POL-2000-00011',  7,  2, 6,  100000.00, 2900.00, '2000-04-22', NULL,         'active',      'waiver of premium'),
('POL-2020-00521',  8,  1, 7,  500000.00,  950.00, '2020-02-14', '2040-02-14', 'active',      'accidental death'),
('POL-2009-00103',  9,  3, 4,  400000.00, 3800.00, '2009-08-30', NULL,         'active',      NULL),
('POL-2001-00022',  10, 2, 2,   75000.00, 1800.00, '2001-05-17', NULL,         'active',      NULL),
('POL-2016-00355',  11, 4, 8,  600000.00, 4200.00, '2016-03-05', NULL,         'active',      'accidental death'),
('POL-2022-00601',  12, 1, 7,  250000.00,  420.00, '2022-07-01', '2042-07-01', 'active',      NULL),
('POL-2011-00165',  13, 1, 3,  400000.00, 2200.00, '2011-10-12', '2031-10-12', 'active',      'accidental death'),
('POL-2019-00488',  14, 3, 5,  750000.00, 4900.00, '2019-04-18', NULL,         'active',      'waiver of premium'),
('POL-1998-00003',   15, 2, 6,  200000.00, 3500.00, '1998-11-30', NULL,         'active',      NULL),
('POL-2014-00277',   1,  1, 1,  250000.00,  990.00, '2014-08-01', '2024-08-01', 'expired',     NULL),
('POL-2007-00072',   5,  1, 3,  150000.00, 1100.00, '2007-06-15', '2017-06-15', 'expired',     NULL),
('POL-2013-00221',   9,  5, 4,   20000.00,  960.00, '2013-02-10', NULL,         'active',      NULL);


-- ── BENEFICIARIES ────────────────────────────────────────────
INSERT INTO beneficiaries (policy_id, first_name, last_name, relationship, percentage, is_primary, date_of_birth, phone, email) VALUES
-- POL-2010-00142 (Harold Bennett)
(1,  'Margaret', 'Bennett',    'Spouse',   100.00, TRUE,  '1954-02-11', '248-555-2001', 'mbennett@email.com'),
-- POL-2008-00089 (Dorothy Castillo)
(2,  'Luis',     'Castillo',   'Spouse',    60.00, TRUE,  '1946-06-04', '313-555-2002', NULL),
(2,  'Maria',    'Castillo',   'Child',     40.00, TRUE,  '1972-09-15', '313-555-2003', 'mcastillo@email.com'),
-- POL-2015-00301 (Raymond Foster)
(3,  'Angela',   'Foster',     'Spouse',    70.00, TRUE,  '1967-05-22', '734-555-2004', 'afoster@email.com'),
(3,  'Tyler',    'Foster',     'Child',     30.00, TRUE,  '1995-03-10', '734-555-2005', NULL),
-- POL-2012-00188 (Carol Hutchinson)
(4,  'David',    'Hutchinson', 'Spouse',   100.00, TRUE,  '1968-11-30', '248-555-2006', 'd.hutch@email.com'),
-- POL-2005-00044 (Walter Simmons)
(5,  'Evelyn',   'Simmons',    'Spouse',    50.00, TRUE,  '1960-04-17', '614-555-2007', NULL),
(5,  'James',    'Simmons',    'Child',     25.00, TRUE,  '1985-07-28', '614-555-2008', NULL),
(5,  'Karen',    'Simmons',    'Child',     25.00, TRUE,  '1988-01-09', '614-555-2009', NULL),
-- POL-2000-00011 (Thomas O'Brien)
(7,  'Colleen',  'O''Brien',   'Spouse',   100.00, TRUE,  '1947-08-15', '317-555-2010', NULL),
-- POL-2009-00103 (George Martinez)
(9,  'Rosa',     'Martinez',   'Spouse',    80.00, TRUE,  '1958-12-03', '734-555-2011', 'rmartinez@email.com'),
(9,  'Carlos',   'Martinez',   'Child',     20.00, TRUE,  '1984-04-21', '734-555-2012', NULL),
-- POL-2001-00022 (Ruth Thompson)
(10, 'Edward',   'Thompson',   'Child',     50.00, TRUE,  '1962-10-30', '313-555-2013', NULL),
(10, 'Susan',    'Thompson',   'Child',     50.00, TRUE,  '1965-03-14', '313-555-2014', NULL),
-- POL-2011-00165 (Frank Deluca)
(13, 'Marie',    'Deluca',     'Spouse',   100.00, TRUE,  '1964-09-02', '614-555-2015', 'mdeluca@email.com'),
-- POL-1998-00003 (Arthur Yamamoto)
(15, 'Yuki',     'Yamamoto',   'Spouse',    50.00, TRUE,  '1952-07-18', '734-555-2016', NULL),
(15, 'Kenji',    'Yamamoto',   'Child',     50.00, TRUE,  '1978-11-25', '734-555-2017', 'kyamamoto@email.com');


-- ── CLAIMS ───────────────────────────────────────────────────
INSERT INTO claims (claim_number, policy_id, beneficiary_id, date_of_death, date_filed, cause_of_death, claim_amount, status, assigned_examiner, denial_reason, date_approved, date_denied, date_paid, notes) VALUES
-- Paid claims
('CLM-2024-00011', 2,  2,  '2024-01-10', '2024-01-25', 'Cardiac arrest',        150000.00, 'paid',         'Sarah Donovan',  NULL,                               '2024-02-15', NULL,         '2024-02-20', 'Primary beneficiary — spouse 60%'),
('CLM-2024-00012', 2,  3,  '2024-01-10', '2024-01-25', 'Cardiac arrest',        100000.00, 'paid',         'Sarah Donovan',  NULL,                               '2024-02-15', NULL,         '2024-02-20', 'Primary beneficiary — child 40%'),
('CLM-2023-00088', 7,  10, '2023-10-02', '2023-10-18', 'Natural causes',        100000.00, 'paid',         'Michael Torres', NULL,                               '2023-11-05', NULL,         '2023-11-10', NULL),
('CLM-2022-00055', 5,  7,  '2022-06-14', '2022-06-30', 'Cancer',                150000.00, 'paid',         'Sarah Donovan',  NULL,                               '2022-07-28', NULL,         '2022-08-02', 'Spouse 50%'),
('CLM-2022-00056', 5,  8,  '2022-06-14', '2022-06-30', 'Cancer',                 75000.00, 'paid',         'Sarah Donovan',  NULL,                               '2022-07-28', NULL,         '2022-08-02', 'Child 25%'),
('CLM-2022-00057', 5,  9,  '2022-06-14', '2022-06-30', 'Cancer',                 75000.00, 'paid',         'Sarah Donovan',  NULL,                               '2022-07-28', NULL,         '2022-08-02', 'Child 25%'),
('CLM-2021-00031', 15, 16, '2021-03-20', '2021-04-01', 'Stroke',                100000.00, 'paid',         'James Whitfield',NULL,                               '2021-04-25', NULL,         '2021-04-30', 'Spouse 50%'),
('CLM-2021-00032', 15, 17, '2021-03-20', '2021-04-01', 'Stroke',                100000.00, 'paid',         'James Whitfield',NULL,                               '2021-04-25', NULL,         '2021-04-30', 'Child 50%'),
-- Approved (pending payment)
('CLM-2024-00098', 10, 13, '2024-08-15', '2024-08-28', 'Natural causes',         37500.00, 'approved',     'Michael Torres', NULL,                               '2024-09-20', NULL,         NULL,         'Child 50%'),
('CLM-2024-00099', 10, 14, '2024-08-15', '2024-08-28', 'Natural causes',         37500.00, 'approved',     'Michael Torres', NULL,                               '2024-09-20', NULL,         NULL,         'Child 50%'),
('CLM-2024-00104', 13, 15, '2024-09-01', '2024-09-10', 'Accidental',            400000.00, 'approved',     'Sarah Donovan',  NULL,                               '2024-10-05', NULL,         NULL,         'Accidental death rider triggered — full face value'),
-- Under review
('CLM-2024-00115', 1,  1,  '2024-10-05', '2024-10-12', 'Undetermined',          500000.00, 'under_review', 'James Whitfield',NULL,                               NULL,         NULL,         NULL,         'Awaiting autopsy report and toxicology'),
('CLM-2024-00118', 9,  11, '2024-10-18', '2024-10-22', 'Cardiac arrest',        320000.00, 'under_review', 'Sarah Donovan',  NULL,                               NULL,         NULL,         NULL,         'Medical records requested from treating physician'),
('CLM-2024-00121', 3,  4,  '2024-11-01', '2024-11-05', 'Accidental',            525000.00, 'under_review', 'Michael Torres', NULL,                               NULL,         NULL,         NULL,         'Accidental death rider — police report obtained, waiting coroner'),
-- Pending
('CLM-2024-00125', 4,  6,  '2024-11-08', '2024-11-14', 'Cancer',               1000000.00, 'pending',      NULL,             NULL,                               NULL,         NULL,         NULL,         'Recently filed — examiner not yet assigned'),
('CLM-2024-00127', 11, NULL,'2024-11-10', '2024-11-15', 'Natural causes',        600000.00, 'pending',      NULL,             NULL,                               NULL,         NULL,         NULL,         'Beneficiary not yet filed — policy lookup initiated'),
-- Denied claims
('CLM-2023-00071', 3,  5,  '2023-07-14', '2023-07-20', 'Suicide',               750000.00, 'denied',       'James Whitfield','Policy within 2-year suicide exclusion period — claim not payable under contestability clause', NULL, '2023-08-10', NULL, 'Policy issued 2015 — outside 2yr window — RECALCULATE'),
('CLM-2020-00019', 1,  1,  '2020-03-05', '2020-03-12', 'Accidental',            500000.00, 'denied',       'Sarah Donovan',  'Policy lapsed due to non-payment at time of death — reinstated 3 months later but death occurred during lapse', NULL, '2020-04-01', NULL, 'Lapse period: Feb 1 – May 15 2020');


-- ── CLAIM DOCUMENTS ──────────────────────────────────────────
INSERT INTO claim_documents (claim_id, document_type, file_name, received_date, is_verified, notes) VALUES
(1,  'death_certificate',  'castillo_death_cert.pdf',    '2024-01-26', TRUE,  NULL),
(1,  'beneficiary_id',     'luis_castillo_id.pdf',       '2024-01-26', TRUE,  NULL),
(1,  'medical_records',    'castillo_cardiac_records.pdf','2024-02-01', TRUE,  NULL),
(2,  'death_certificate',  'castillo_death_cert.pdf',    '2024-01-26', TRUE,  'Same certificate as CLM-2024-00011'),
(2,  'beneficiary_id',     'maria_castillo_id.pdf',      '2024-01-28', TRUE,  NULL),
(3,  'death_certificate',  'obrien_death_cert.pdf',      '2023-10-19', TRUE,  NULL),
(3,  'beneficiary_id',     'colleen_obrien_id.pdf',      '2023-10-19', TRUE,  NULL),
(12, 'death_certificate',  'bennett_death_cert.pdf',     '2024-10-13', TRUE,  NULL),
(12, 'beneficiary_id',     'margaret_bennett_id.pdf',    '2024-10-13', TRUE,  NULL),
(12, 'autopsy_report',     'bennett_autopsy.pdf',        NULL,         FALSE, 'PENDING — county coroner office, estimated 6-8 weeks'),
(12, 'toxicology_report',  'bennett_toxicology.pdf',     NULL,         FALSE, 'PENDING — results expected with autopsy'),
(13, 'death_certificate',  'martinez_death_cert.pdf',    '2024-10-23', TRUE,  NULL),
(13, 'medical_records',    'martinez_cardiac_records.pdf',NULL,        FALSE, 'Requested from St. Joseph Hospital — awaiting'),
(14, 'death_certificate',  'foster_death_cert.pdf',      '2024-11-06', TRUE,  NULL),
(14, 'police_report',      'foster_accident_report.pdf', '2024-11-07', TRUE,  NULL),
(14, 'autopsy_report',     'foster_autopsy.pdf',         NULL,         FALSE, 'PENDING'),
(15, 'death_certificate',  'hutchinson_death_cert.pdf',  '2024-11-14', TRUE,  NULL),
(15, 'medical_records',    'hutchinson_oncology.pdf',    NULL,         FALSE, 'Requested — not yet received');


-- ── CLAIM PAYMENTS ───────────────────────────────────────────
INSERT INTO claim_payments (claim_id, beneficiary_id, payment_amount, payment_date, payment_method, check_number, status) VALUES
(1,  2,  150000.00, '2024-02-20', 'wire_transfer', NULL,         'cleared'),
(2,  3,  100000.00, '2024-02-20', 'wire_transfer', NULL,         'cleared'),
(3,  10, 100000.00, '2023-11-10', 'check',         'CHK-0044871','cleared'),
(4,  7,  150000.00, '2022-08-02', 'check',         'CHK-0038812','cleared'),
(5,  8,   75000.00, '2022-08-02', 'check',         'CHK-0038813','cleared'),
(6,  9,   75000.00, '2022-08-02', 'check',         'CHK-0038814','cleared'),
(7,  16, 100000.00, '2021-04-30', 'ach',            NULL,         'cleared'),
(8,  17, 100000.00, '2021-04-30', 'ach',            NULL,         'cleared'),
-- Approved but not yet paid
(9,  13,  37500.00, NULL,         'check',          NULL,         'pending'),
(10, 14,  37500.00, NULL,         'check',          NULL,         'pending'),
(11, 15, 400000.00, NULL,         'wire_transfer',  NULL,         'pending');


-- ── POPULATE age_at_issue ON POLICIES ────────────────────────
-- Snapshot of policyholder's age at time policy was written
UPDATE policies p SET age_at_issue =
    DATE_PART('year', AGE(p.issue_date, ph.date_of_birth))::INT
FROM policyholders ph
WHERE p.policyholder_id = ph.policyholder_id;


-- ── POPULATE policyholder_since ON POLICYHOLDERS ─────────────
-- Date of first policy with the company — basis for tenure calculation
UPDATE policyholders ph SET policyholder_since = (
    SELECT MIN(p.issue_date)
    FROM policies p
    WHERE p.policyholder_id = ph.policyholder_id
);
