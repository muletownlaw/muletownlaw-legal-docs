# Probate Module Design
## Scrivening — scrivening.muletown.law
### April 10, 2026

## Overview

Add probate document generation to the existing Scrivening platform with Lawmatics integration for case tracking. Keeps the existing stateless architecture (no database) while offloading workflow tracking to Lawmatics.

## Three Touchpoints

### 1. Opening Generator (`probate.html`)
Multi-step intake wizard → ZIP of opening documents + Lawmatics matter/tasks.

**Form Steps:**
1. Decedent — name, AKA, gender, DOB, DOD, address, county, marital status, spouse, business interest
2. Estate Type — testate/intestate, will type, execution date, witnesses, executor naming, bond/inventory waivers, estimated value
3. Personal Representative — name, address, age, gender, relationship, criminal history, will attend probate
4. Heirs (repeatable) — name, age, address, relationship, gender, minor, disability, beneficiary type
5. Real Property (repeatable) — address, county, map/parcel, value, description
6. Review & Generate — summary display, flags/warnings, generate button

**Documents Generated (per spec § 2.1–2.3):**
- Petition (type selected by estate_type + will_type + muniment logic)
- Order (matching petition type)
- Personal Representative Oath (clerk or notary variant)
- Declinations (per § 2.2 priority logic)
- TennCare Release Request
- Invoice

**Lawmatics Sync:**
- Create or find matter for decedent's estate
- Create initial task checklist (review docs, have PR sign, file petition, publish notice, send TennCare letter, enter publication date)
- Calendar: absolute bar date (DOD + 12 months)

### 2. Publication Deadlines (`probate-deadlines.html`)
Lightweight form: case/matter ID + publication date → pushes statutory deadlines.

**Lawmatics Calendar Events:**
- Claims deadline (publication + 4 months) — last day creditor WITH notice can file
- Exception deadline (claims deadline + 30 days) — deadline to file exceptions
- Absolute bar date (DOD + 12 months) — last day creditor WITHOUT notice can file
- Estate eligible to close (after exception deadline)

### 3. Closing Generator (`probate-closing.html`)
Closing intake form → ZIP of closing documents.

**Inputs:** Case number, TennCare status, claims status, fee amounts, distribution plan per heir.

**Documents Generated (per spec § 2.4–2.5):**
- Closing petition (testate/intestate, sui juris/non-sui juris variant)
- Closing order
- Receipt & waiver per heir (type selected by § 2.5 logic)

## Backend Architecture

| Endpoint | Purpose |
|----------|---------|
| `api/generate-probate-opening.py` | Generates ZIP of opening docs from 28 .docx templates |
| `api/generate-probate-closing.py` | Generates ZIP of closing docs |
| `api/lawmatics-probate.py` | Lawmatics API: create matter, tasks, calendar events |

**Document Generation Method:** Template-based with merge field replacement (like existing HCPOA/ACP generators). Python loads .docx template, replaces standardized merge fields, handles conditional logic (pronouns, CHOOSE ONE sections, bond/inventory waivers), returns populated document.

**ZIP Output:** Files named `YYYY-MM-DD Document Title.docx`.

## Template Inventory (28 files)

**Opening:** Petition (5 variants), Order (5 variants), Oath, Declination
**Closing:** Closing Petition (3 variants), Closing Order (2 variants), Receipt & Waiver (5 variants)
**Other:** Small Estate Affidavit, Small Estate Order, Exception to Claim, Executor's Deed, Administrator's Deed

Templates use `{FIELD NAME}` merge fields with inconsistent naming. Backend will map spec-standardized fields (§ Part 4) to template placeholders.

## Decision Logic

All decision logic from spec § 2.1–2.6 runs in the Python backend at generation time:
- Document selection (estate type + will type → petition/order variant)
- Declination logic (kinship priority per § 30-1-106)
- Bond determination (will waiver, sole beneficiary, consent)
- Closing document selection (sui juris status)
- Receipt & waiver type selection
- Flags and warnings (nonresident PR, criminal history, small estate eligibility, out-of-county property, minors/disabilities, business interests)

## Landing Page Update

Add "Probate" section to `index.html` with three cards linking to the three probate pages.
