# Implementation Plan — A/B Test Checkout Flow Analysis

---

## Phase 0 — Environment Setup
**Delivers:** Git identity, folder structure, `.gitattributes`, `.gitignore`, `requirements.txt`, `README.md`

**Steps:**
- [ ] 0.1 Set git global identity (`user.name`, `user.email`)
- [ ] 0.2 Confirm git config
- [ ] 0.3 Create folder structure: `data/raw/`, `notebooks/`, `app/`, `charts/`, `outputs/`
- [ ] 0.4 Create `.gitattributes` (`*.py linguist-vendored=true`)
- [ ] 0.5 Create `.gitignore` (Python, Jupyter, OS artifacts)
- [ ] 0.6 Create `requirements.txt`
- [ ] 0.7 Create `README.md` (project overview, setup instructions, how to run notebook + app)
- [ ] 0.8 Confirm final `ls -la`

**Files created:** `.gitattributes`, `.gitignore`, `requirements.txt`, `README.md`, all directories
**Dependencies:** None — first step

---

## Phase 1 — Synthetic Dataset Generation
**Delivers:** `data/raw/checkout_ab_test.csv` with all specified columns and realistic variation

**Steps:**
- [ ] 1.1 Generate 10,000 rows with:
  - 50/50 control/treatment split
  - Device type distribution (60% mobile / 30% desktop / 10% tablet)
  - User type distribution (40% new / 40% returning / 20% loyal)
  - Log-normal cart values ($10–$500)
  - Completion rates ~45% control / ~52% treatment
  - Mobile −15% completion modifier, loyal +25% modifier
  - Higher cart value → slightly lower completion rate
  - `reached_step2`, `reached_step3` (control group only)
  - `time_to_complete` (completions only — control avg 180s, treatment avg 110s)
  - `abandoned_reason` field
- [ ] 1.2 Save to `data/raw/checkout_ab_test.csv`
- [ ] 1.3 Print first 5 rows + group counts for review

**Files created:** `data/raw/checkout_ab_test.csv`
**Dependencies:** Phase 0 complete

---

## Phase 2 — Data Validation
**Delivers:** Verified dataset — confirms no issues before analysis begins

**Steps:**
- [ ] 2.1 Check sample sizes (n per group)
- [ ] 2.2 Verify 50/50 split (within tolerance)
- [ ] 2.3 Chi-square balance check on `device_type` and `user_type` across groups
- [ ] 2.4 Mann-Whitney U on `cart_value` by group (verify randomization)
- [ ] 2.5 Confirm baseline completion rates match targets (~45% / ~52%)

**Output:** Printed summary — go/no-go for proceeding
**Dependencies:** Phase 1 complete

---

## Phase 3 — Jupyter Notebook (`notebooks/ab_test_analysis.ipynb`)
**Delivers:** Full analysis notebook — 6 sections, 7 charts, all stats explained in plain English

**Steps:**
- [ ] 3.1 **Section 0** — Business Context (markdown only, Baymard stat included)
- [ ] 3.2 **Section 1** — Data Loading & Validation (group sizes, balance table)
- [ ] 3.3 **Section 2** — EDA + 6 charts saved to `charts/` as PNG
  - Chart 1: Completion rate by group (bar)
  - Chart 2: Completion rate by device x group (grouped bar)
  - Chart 3: Completion rate by user type x group (grouped bar)
  - Chart 4: Abandonment funnel — control only (step drop-off)
  - Chart 5: Time-to-complete histogram overlay
  - Chart 6: Cart value box plot by group
- [ ] 3.4 **Section 3** — Statistical Testing
  - Chi-square test
  - Z-test for proportions (one-tailed)
  - p-value, 95% CI, statistical power, MDE
  - Mann-Whitney U on time-to-complete
  - Clean summary table + plain-English explanations
- [ ] 3.5 **Section 4** — Business Impact
  - Revenue calculations with editable assumption variables
  - Payback period, 3-year ROI
  - Formatted summary table
- [ ] 3.6 **Section 5** — Subgroup Analysis
  - Lift by device type, lift by user type
  - Chart 7: Heatmap of lift % (device x user type), saved to `charts/`
- [ ] 3.7 **Section 6** — Recommendation (plain English, structured verdict)
- [ ] 3.8 Verify notebook runs top-to-bottom without errors

**Files created:** `notebooks/ab_test_analysis.ipynb`, `charts/` (7 PNG files)
**Dependencies:** Phase 1 complete

---

## Phase 4 — Streamlit App (`app/ab_test_app.py`)
**Delivers:** Interactive app — upload CSV, get instant go/no-go with business impact

**Steps:**
- [ ] 4.1 Build sidebar: file upload, column selectors, significance slider, business inputs
- [ ] 4.2 Build Row 1: 3 metric cards (Control Rate, Treatment Rate, Lift %)
- [ ] 4.3 Build Row 2: Bar chart comparison
- [ ] 4.4 Build Row 3: Statistical results box (p-value color-coded, CI, sample sizes, test used)
- [ ] 4.5 Build Row 4: Traffic light verdict (Green/Yellow/Red)
- [ ] 4.6 Build Section 3: Business impact calculations + ROI bar chart
- [ ] 4.7 Verify app loads with generated dataset without errors

**Files created:** `app/ab_test_app.py`
**Dependencies:** Phase 1 complete

---

## Phase 5 — Final QA
**Delivers:** Everything confirmed working end-to-end

**Steps:**
- [ ] 5.1 Confirm all 7 charts saved to `charts/`
- [ ] 5.2 Confirm `ls -la` on all directories
- [ ] 5.3 Confirm `requirements.txt` covers all imports used
- [ ] 5.4 Confirm notebook cell outputs look clean

**Dependencies:** Phases 3 + 4 complete

---

## Dependency Map

```
Phase 0 --> Phase 1 --> Phase 2
                    --> Phase 3 --> Phase 5
                    --> Phase 4 --> Phase 5
```

Phases 3 and 4 can run in parallel after Phase 1 is confirmed.

---

## Color Palette
- Primary blue: `#1B4F72`
- Orange: `#E67E22`

## Key Numbers to Hit
- Control completion rate: ~45%
- Treatment completion rate: ~52%
- Control avg time to complete: 180s
- Treatment avg time to complete: 110s
- Monthly visitors assumption: 500,000
- Average order value assumption: $85
- Implementation cost assumption: $25,000
