# Probate Module Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add probate document generation to scrivening.muletown.law with Lawmatics integration for case tracking.

**Architecture:** Three new HTML pages (opening intake, publication deadlines, closing intake) backed by Python serverless endpoints on Vercel. Each endpoint loads .docx templates, performs merge field replacement, and returns a ZIP file. A separate endpoint handles Lawmatics API calls for matter/task/calendar creation. No database — stays stateless like the existing estate planning tools.

**Tech Stack:** React 18 (CDN), Tailwind CSS (CDN), Python 3 + python-docx 1.1.0, Vercel serverless, Lawmatics API (via urllib).

**Source Spec:** `probate_scrivening_complete_spec.md` in the Probate Prep OneDrive folder — contains all data model, decision logic, merge field definitions, and template notes.

---

## Task 1: Copy Templates & Set Up Directory Structure

**Files:**
- Create: `api/probate-templates/` (directory)
- Modify: `requirements.txt` (no changes needed — zipfile is built-in)

**Step 1: Create probate template directory**

```bash
mkdir -p api/probate-templates
```

**Step 2: Copy all 28 templates from OneDrive to repo**

```bash
cp "/Users/muletownlaw/Library/CloudStorage/OneDrive-SharedLibraries-MuletownLawPC/Intranet - Documents/Law firm docs/AI Projects/Probate Prep/"*.docx api/probate-templates/
```

**Step 3: Verify all templates are present**

```bash
ls api/probate-templates/ | wc -l
# Expected: 28
```

**Step 4: Commit**

```bash
git add api/probate-templates/
git commit -m "feat(probate): add 28 probate document templates"
```

---

## Task 2: Build Shared Probate Utilities

**Files:**
- Create: `api/probate_utils.py`
- Create: `tests/test_probate_utils.py`

This module contains all shared logic: merge field replacement (with run-merging), pronoun/title derivation, date formatting, document selection, declination logic, ZIP assembly, and flags/warnings.

**Step 1: Write failing tests for pronoun and title derivation**

```python
# tests/test_probate_utils.py
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
from probate_utils import derive_pronouns, derive_pr_title

class TestDerivePronouns:
    def test_male_pronouns(self):
        result = derive_pronouns('Male')
        assert result == {'subject': 'he', 'possessive': 'his', 'object': 'him'}

    def test_female_pronouns(self):
        result = derive_pronouns('Female')
        assert result == {'subject': 'she', 'possessive': 'her', 'object': 'her'}

class TestDerivePRTitle:
    def test_testate_male(self):
        assert derive_pr_title('Testate', 'Male') == 'Executor'

    def test_testate_female(self):
        assert derive_pr_title('Testate', 'Female') == 'Executrix'

    def test_intestate_male(self):
        assert derive_pr_title('Intestate', 'Male') == 'Administrator'

    def test_intestate_female(self):
        assert derive_pr_title('Intestate', 'Female') == 'Administratrix'
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_probate_utils.py -v
# Expected: FAIL — module not found
```

**Step 3: Write probate_utils.py with core derivation functions**

```python
# api/probate_utils.py
"""Shared utilities for probate document generation."""
import os
import zipfile
from io import BytesIO
from datetime import datetime, timedelta
from docx import Document


# --- Pronoun & Title Derivation ---

def derive_pronouns(gender):
    """Return subject/possessive/object pronouns from gender."""
    if gender == 'Male':
        return {'subject': 'he', 'possessive': 'his', 'object': 'him'}
    return {'subject': 'she', 'possessive': 'her', 'object': 'her'}


def derive_pr_title(estate_type, pr_gender):
    """Return PR title: Executor/Executrix/Administrator/Administratrix."""
    titles = {
        ('Testate', 'Male'): 'Executor',
        ('Testate', 'Female'): 'Executrix',
        ('Intestate', 'Male'): 'Administrator',
        ('Intestate', 'Female'): 'Administratrix',
    }
    return titles[(estate_type, pr_gender)]


# --- Date Formatting ---

def format_date_legal(date_str):
    """Convert YYYY-MM-DD to 'January 1, 2026' format."""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%B %-d, %Y')


def ordinal_day(date_str):
    """Return ordinal day: '10th', '1st', '2nd', '3rd', etc."""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    day = dt.day
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return f"{day}{suffix}"


# --- Merge Field Replacement ---

def merge_runs_in_paragraph(paragraph):
    """Merge all runs to handle Word's split placeholders."""
    if not paragraph.runs:
        return
    full_text = paragraph.text
    for run in paragraph.runs:
        run.text = ''
    if paragraph.runs:
        paragraph.runs[0].text = full_text


def replace_in_document(doc, replacements):
    """Replace all placeholders in a document. Merges runs first."""
    for paragraph in doc.paragraphs:
        merge_runs_in_paragraph(paragraph)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    merge_runs_in_paragraph(paragraph)

    for paragraph in doc.paragraphs:
        for placeholder, value in replacements.items():
            if placeholder in paragraph.text:
                for run in paragraph.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, value)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for placeholder, value in replacements.items():
                        if placeholder in paragraph.text:
                            for run in paragraph.runs:
                                if placeholder in run.text:
                                    run.text = run.text.replace(placeholder, value)


def load_template(template_name):
    """Load a .docx template from api/probate-templates/."""
    template_dir = os.path.join(os.path.dirname(__file__), 'probate-templates')
    path = os.path.join(template_dir, template_name)
    return Document(path)


# --- ZIP Assembly ---

def build_zip(documents, date_str=None):
    """Build a ZIP file from a list of (filename, Document) tuples.

    Args:
        documents: list of (filename_without_date, docx.Document) tuples
        date_str: YYYY-MM-DD string for filename prefix. Defaults to today.

    Returns:
        BytesIO buffer containing the ZIP file.
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, doc in documents:
            doc_buffer = BytesIO()
            doc.save(doc_buffer)
            doc_buffer.seek(0)
            full_name = f"{date_str} {filename}.docx"
            zf.writestr(full_name, doc_buffer.getvalue())
    zip_buffer.seek(0)
    return zip_buffer


# --- Document Selection Logic (spec § 2.1) ---

def select_opening_documents(data):
    """Return list of (template_filename, output_title) for opening docs.

    Implements spec § 2.1 document selection logic.
    """
    estate_type = data['estate_type']
    docs = []

    if data.get('small_estate_election'):
        docs.append(('Small Estate - Affidavit as to Small Estate CURLY.docx',
                      'Affidavit as to Small Estate'))
        docs.append(('Small Estate - Order Approving Small Estate CURLY.docx',
                      'Order Approving Small Estate'))
        return docs

    if estate_type == 'Testate':
        if data.get('muniment_only'):
            docs.append(('Petition for Muniment of Title.docx',
                          'Petition for Muniment of Title'))
            docs.append(('Order for Muniment of Title.docx',
                          'Order for Muniment of Title'))
        elif data.get('will_type') == 'Standard Witnessed':
            docs.append(('Petition to Probate Will Ltrs Testamentary CURLY (1).docx',
                          'Petition to Probate Will and Letters Testamentary'))
            docs.append(('Order to Probate LWT CURLY.docx',
                          'Order to Probate Last Will and Testament'))
        elif data.get('will_type') == 'Holographic':
            docs.append(('Petition to Probate Holographic Will.docx',
                          'Petition to Probate Holographic Will'))
            docs.append(('Order Admitting Holographic LWT.docx',
                          'Order Admitting Holographic Last Will and Testament'))
        elif data.get('will_type') == 'Will + Codicil':
            docs.append(('Petition to Probate Will and Codicil.docx',
                          'Petition to Probate Will and Codicil'))
            docs.append(('Order Admitting Codicil and LWT.docx',
                          'Order Admitting Codicil and Last Will and Testament'))
    else:  # Intestate
        docs.append(('Petition for Appointment of Administrator CURLY.docx',
                      'Petition for Appointment of Administrator'))
        docs.append(('Order for Intestate Administration.docx',
                      'Order for Intestate Administration'))

    # Always add oath (for non-small-estate)
    docs.append(('Personal Representative Oath CURLY.docx',
                  'Personal Representative Oath'))

    return docs


# --- Declination Logic (spec § 2.2) ---

def determine_declinations(data):
    """Return list of dicts for people who need to sign declinations.

    Each dict: {name, relationship, gender, relation_to_pr}
    Implements spec § 2.2.
    """
    estate_type = data['estate_type']
    heirs = data.get('heirs', [])
    declinations = []

    if estate_type == 'Testate':
        if data.get('named_executor_can_serve', True):
            return []

        # Named executor can't serve — they must decline
        if data.get('will_executor_name'):
            declinations.append({
                'name': data['will_executor_name'],
                'relationship': 'Named Executor',
                'gender': data.get('will_executor_gender', 'Male'),
            })

        if data.get('will_names_alternate') and data.get('will_alternate_name'):
            # Alternate exists and presumably can serve — no further declinations
            return declinations

        # No one in will can serve — need consent from each adult devisee/legatee
        for heir in heirs:
            if heir.get('heir_is_beneficiary') and not heir.get('heir_is_minor'):
                if heir['heir_full_name'] != data.get('pr_full_name'):
                    declinations.append({
                        'name': heir['heir_full_name'],
                        'relationship': heir['heir_relationship'],
                        'gender': heir.get('heir_gender', 'Male'),
                    })

    else:  # Intestate
        pr_relationship = data.get('pr_relationship', '')

        if pr_relationship == 'Spouse':
            return []  # Highest priority — no declinations

        surviving_spouse = data.get('decedent_spouse_name') if data.get(
            'decedent_marital_status') == 'Married' else None

        # For any non-spouse PR, the surviving spouse must decline
        if surviving_spouse and pr_relationship != 'Spouse':
            declinations.append({
                'name': surviving_spouse,
                'relationship': 'Surviving Spouse',
                'gender': 'Female' if data.get('decedent_gender') == 'Male' else 'Male',
            })

        if pr_relationship == 'Child':
            # Siblings (other children) must decline
            for heir in heirs:
                if (heir['heir_relationship'] in ['Son', 'Daughter', 'Child']
                        and heir['heir_full_name'] != data.get('pr_full_name')
                        and not heir.get('heir_is_minor')):
                    declinations.append({
                        'name': heir['heir_full_name'],
                        'relationship': heir['heir_relationship'],
                        'gender': heir.get('heir_gender', 'Male'),
                    })
        elif pr_relationship in ['Grandchild', 'Sibling', 'Other Kin', 'Unrelated']:
            # All children of decedent must decline
            for heir in heirs:
                if (heir['heir_relationship'] in ['Son', 'Daughter', 'Child']
                        and heir['heir_full_name'] != data.get('pr_full_name')
                        and not heir.get('heir_is_minor')):
                    declinations.append({
                        'name': heir['heir_full_name'],
                        'relationship': heir['heir_relationship'],
                        'gender': heir.get('heir_gender', 'Male'),
                    })

    return declinations


# --- Closing Document Selection (spec § 2.4) ---

def select_closing_documents(data):
    """Return list of (template_filename, output_title) for closing docs."""
    estate_type = data['estate_type']
    docs = []

    if estate_type == 'Testate':
        if data.get('all_heirs_sui_juris', True):
            docs.append(('Petition to Close Estate CURLY.docx',
                          'Petition to Close Estate'))
        else:
            docs.append(('Petition to Close Estate-No sui juris.docx',
                          'Petition to Close Estate'))
        docs.append(('Order to Close Estate CURLY.docx',
                      'Order to Close Estate'))
    else:
        docs.append(('Petition to Close Intestate Estate CURLY.docx',
                      'Petition to Close Intestate Estate'))
        docs.append(('Order Closing Intestate Estate CURLY.docx',
                      'Order Closing Intestate Estate'))

    return docs


# --- Receipt & Waiver Selection (spec § 2.5) ---

def select_receipt_waiver_template(heir, data):
    """Return (template_filename, output_title) for one heir's receipt & waiver."""
    estate_type = data['estate_type']
    pr_name = data.get('pr_full_name', '')

    if estate_type == 'Intestate':
        return ('Receipt and Waiver for Intestate Estate.docx',
                f'Receipt and Waiver - {heir["heir_full_name"]}')

    # Testate paths
    is_pr = heir['heir_full_name'] == pr_name
    btype = heir.get('heir_beneficiary_type', 'General')

    if is_pr and btype == 'Residuary':
        return ('Receipt and Waiver  - Residuary and Executor.docx',
                f'Receipt and Waiver - {heir["heir_full_name"]}')
    elif btype == 'Residuary':
        return ('Receipt and Waiver  - Residuary CURLY.docx',
                f'Receipt and Waiver - {heir["heir_full_name"]}')
    elif btype == 'Specific':
        return ('Receipt & Waiver - Testate CURLY.docx',
                f'Receipt and Waiver - {heir["heir_full_name"]}')
    else:
        return ('Receipt and Waiver  - General CURLY.docx',
                f'Receipt and Waiver - {heir["heir_full_name"]}')


# --- Flags & Warnings (spec § 2.6) ---

def generate_flags(data):
    """Return list of {level: 'warning'|'info', message: str}."""
    flags = []
    heirs = data.get('heirs', [])

    if data.get('pr_state', 'Tennessee') != 'Tennessee':
        flags.append({'level': 'warning',
                       'message': 'Nonresident PR — may not be eligible under § 30-1-116'})

    if data.get('pr_criminal_history') or data.get('pr_penitentiary_sentence'):
        flags.append({'level': 'warning',
                       'message': 'PR criminal history disclosed — attorney review required per § 30-1-117(10)'})

    est_val = data.get('estimated_estate_value', 0)
    if est_val and float(est_val) <= 50000 and not data.get('small_estate_election'):
        flags.append({'level': 'info',
                       'message': 'Estate may qualify for small estate administration under § 30-4-103'})

    property_counties = [p.get('property_county', '') for p in data.get('properties', [])]
    dec_county = data.get('decedent_county', '')
    out_of_county = [c for c in property_counties if c and c != dec_county]
    if out_of_county:
        flags.append({'level': 'warning',
                       'message': f'Real property in {", ".join(out_of_county)} — ancillary probate may be needed'})

    has_minor = any(h.get('heir_is_minor') for h in heirs)
    has_disability = any(h.get('heir_has_disability') for h in heirs)
    if has_minor or has_disability:
        flags.append({'level': 'warning',
                       'message': 'Not all heirs are sui juris — affects closing documents and may require guardian appointment'})

    if data.get('decedent_had_business'):
        flags.append({'level': 'info',
                       'message': 'Decedent had business interest — include details in petition per § 30-1-117(11)'})

    if (data.get('estate_type') == 'Testate'
            and not data.get('will_waives_inventory')):
        flags.append({'level': 'info',
                       'message': 'Will does not waive inventory — inventory will be required'})

    return flags


# --- Deadline Calculations (spec § 3.2) ---

def calculate_deadlines(dod_str, publication_date_str=None):
    """Calculate statutory deadlines.

    Args:
        dod_str: Date of death as YYYY-MM-DD
        publication_date_str: Publication date as YYYY-MM-DD (optional)

    Returns:
        dict of deadline names → YYYY-MM-DD strings
    """
    dod = datetime.strptime(dod_str, '%Y-%m-%d')
    deadlines = {}

    # Absolute bar date: DOD + 12 months
    if dod.month == 12:
        bar_date = dod.replace(year=dod.year + 1, month=12)
    else:
        try:
            bar_date = dod.replace(year=dod.year + 1)
        except ValueError:
            # Handle leap year edge case (Feb 29 → Feb 28)
            bar_date = dod.replace(year=dod.year + 1, day=28)
    deadlines['absolute_bar_date'] = bar_date.strftime('%Y-%m-%d')

    if publication_date_str:
        pub = datetime.strptime(publication_date_str, '%Y-%m-%d')

        # Claims deadline: publication + 4 months
        month = pub.month + 4
        year = pub.year
        if month > 12:
            month -= 12
            year += 1
        try:
            claims = pub.replace(year=year, month=month)
        except ValueError:
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            claims = pub.replace(year=year, month=month, day=min(pub.day, last_day))
        deadlines['claims_deadline'] = claims.strftime('%Y-%m-%d')

        # Exception deadline: claims + 30 days
        exception = claims + timedelta(days=30)
        deadlines['exception_deadline'] = exception.strftime('%Y-%m-%d')

    return deadlines


# --- Build Common Replacements ---

def build_common_replacements(data):
    """Build the merge field replacement dict from intake data.

    Maps standardized spec field names AND legacy template field names
    to data values. This handles the inconsistent naming across templates.
    """
    dec_pronouns = derive_pronouns(data.get('decedent_gender', 'Male'))
    pr_pronouns = derive_pronouns(data.get('pr_gender', 'Male'))
    pr_title = derive_pr_title(data.get('estate_type', 'Testate'),
                                data.get('pr_gender', 'Male'))

    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')

    # Criminal history statement
    if data.get('pr_criminal_history') or data.get('pr_penitentiary_sentence'):
        criminal_stmt = data.get('pr_criminal_details',
                                  'has disclosed criminal history — see attached')
    else:
        criminal_stmt = ('has never been convicted of any felony or misdemeanor '
                         'and has never served any sentence of imprisonment in a penitentiary')

    # Business interest statement
    if data.get('decedent_had_business'):
        business_stmt = (f'was {data.get("decedent_business_details", "")} '
                         'the owner of or had a controlling interest in an ongoing '
                         'business or economic enterprise that is or may be part '
                         'of the estate to be administered')
    else:
        business_stmt = ('was not the owner of nor had a controlling interest in '
                         'any ongoing business or economic enterprise that is or '
                         'may be part of the estate to be administered')

    # Build heirs list block
    heirs = data.get('heirs', [])
    heirs_lines = []
    for h in heirs:
        age_str = f", Age {h.get('heir_age', 'unknown')}" if h.get('heir_age') else ''
        heirs_lines.append(
            f"{h['heir_full_name']}{age_str} — {h.get('heir_relationship', '')}\n"
            f"{h.get('heir_address', '')}, {h.get('heir_city', '')}"
        )
    heirs_list = '\n\n'.join(heirs_lines)

    # All heirs sui juris?
    all_sui_juris = all(
        not h.get('heir_is_minor') and not h.get('heir_has_disability')
        for h in heirs
    ) if heirs else True

    # Will waiver statement
    waivers = []
    if data.get('will_waives_bond'):
        waivers.append('making bond')
    if data.get('will_waives_inventory'):
        waivers.append('filing an inventory')
    if data.get('will_waives_accountings'):
        waivers.append('filing accountings')
    will_waiver_stmt = 'excused from ' + ', '.join(waivers) if waivers else ''

    dod_formatted = format_date_legal(data['decedent_dod']) if data.get('decedent_dod') else ''

    replacements = {
        # --- Decedent (both legacy and standardized) ---
        '{DECEDENT NAME}': data.get('decedent_full_name', ''),
        '{DECEDENT}': data.get('decedent_full_name', ''),
        '{Decedent name}': data.get('decedent_full_name', ''),
        '{Decedent Name}': data.get('decedent_full_name', ''),
        '{DECEDENT ADDRESS}': data.get('decedent_address', ''),
        '{CITY}': data.get('decedent_city', ''),
        '{COUNTY}': data.get('decedent_county', ''),
        '{COUNTY NAME}': data.get('decedent_county', ''),
        '{DATE OF DEATH}': dod_formatted,
        '{AGE OF DECEDENT}': str(data.get('decedent_age', '')),
        '{PLACE OF DEATH}': data.get('decedent_place_of_death', ''),
        '{HIS/HER}': dec_pronouns['possessive'],
        '{his/her}': dec_pronouns['possessive'],
        '{HE/SHE}': dec_pronouns['subject'],
        '{he/she}': dec_pronouns['subject'],
        '{him/her}': dec_pronouns['object'],
        '{was/was not CHOOSE ONE}': 'was' if data.get('decedent_had_business') else 'was not',

        # --- Personal Representative ---
        '{PETITIONER NAME}': data.get('pr_full_name', ''),
        '{PETITIONER}': data.get('pr_full_name', ''),
        '{Petitioner name}': data.get('pr_full_name', ''),
        '{EXECUTOR NAME}': data.get('pr_full_name', ''),
        '{Executor Name}': data.get('pr_full_name', ''),
        '{PETITIONER ADDRESS}': data.get('pr_address', ''),
        '{PETITIONER CITY}': data.get('pr_city', ''),
        '{PETITIONER AGE}': str(data.get('pr_age', '')),
        '{RELATIONSHIP OF PETITIONER TO DECEDENT}': data.get('pr_relationship', ''),
        '{Executor/Executrix/PR Title CHOOSE ONE}': pr_title,
        '{Executor/trix}': pr_title,
        '{Administrator/trix CHOOSE ONE}': pr_title,
        '{Title Executor/Executrix CHOOSE ONE}': pr_title,
        '{PETITIONER PRONOUNT – HE/SHE}': pr_pronouns['subject'],
        '{PETITIONER PRONOUN – HE/SHE}': pr_pronouns['subject'],

        # --- Will details ---
        '{Date of LWT}': format_date_legal(data['will_execution_date']) if data.get('will_execution_date') else '',
        '{WITNESS 1}': data.get('will_witness_1', ''),
        '{WITNESS 2}': data.get('will_witness_2', ''),
        '{PARAGRAPH # APPOINTING PETITIONER}': data.get('will_appointment_paragraph', ''),
        '{Paragraph/Article/etc}': data.get('will_appointment_paragraph', ''),

        # --- Heirs ---
        '{HEIRS_LIST}': heirs_list,

        # --- Case / Court ---
        '{COUNTY NAME}': data.get('decedent_county', ''),
        '{STATE}': data.get('decedent_state', 'Tennessee'),
        '{Docket Number}': data.get('case_number', ''),
        '{MONTH}': today.strftime('%B'),
        '{CURRENT YEAR}': str(today.year),
        '{current_date_day}': ordinal_day(today_str),

        # --- Firm ---
        '{ATTORNEY NAME}': data.get('attorney_full_name', ''),
        '{BPR}': data.get('attorney_bpr', ''),
        'Dale, Hutto & Lyle, PLLC': data.get('firm_name', 'Muletown Law, P.C.'),
    }

    return replacements
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_probate_utils.py -v
# Expected: all PASS
```

**Step 5: Write tests for document selection and declination logic**

```python
# Add to tests/test_probate_utils.py

from probate_utils import (select_opening_documents, determine_declinations,
                           calculate_deadlines, generate_flags, format_date_legal,
                           ordinal_day)

class TestFormatDateLegal:
    def test_standard_date(self):
        assert format_date_legal('2026-04-10') == 'April 10, 2026'

    def test_single_digit_day(self):
        assert format_date_legal('2026-01-5') or format_date_legal('2026-01-05') == 'January 5, 2026'

class TestOrdinalDay:
    def test_10th(self):
        assert ordinal_day('2026-04-10') == '10th'

    def test_1st(self):
        assert ordinal_day('2026-04-01') == '1st'

    def test_2nd(self):
        assert ordinal_day('2026-04-02') == '2nd'

    def test_3rd(self):
        assert ordinal_day('2026-04-03') == '3rd'

    def test_11th(self):
        assert ordinal_day('2026-04-11') == '11th'

    def test_12th(self):
        assert ordinal_day('2026-04-12') == '12th'

    def test_13th(self):
        assert ordinal_day('2026-04-13') == '13th'

    def test_21st(self):
        assert ordinal_day('2026-04-21') == '21st'

class TestSelectOpeningDocuments:
    def test_testate_standard_witnessed(self):
        data = {'estate_type': 'Testate', 'will_type': 'Standard Witnessed'}
        docs = select_opening_documents(data)
        filenames = [d[0] for d in docs]
        assert 'Petition to Probate Will Ltrs Testamentary CURLY (1).docx' in filenames
        assert 'Order to Probate LWT CURLY.docx' in filenames
        assert 'Personal Representative Oath CURLY.docx' in filenames

    def test_intestate(self):
        data = {'estate_type': 'Intestate'}
        docs = select_opening_documents(data)
        filenames = [d[0] for d in docs]
        assert 'Petition for Appointment of Administrator CURLY.docx' in filenames
        assert 'Order for Intestate Administration.docx' in filenames

    def test_small_estate(self):
        data = {'estate_type': 'Testate', 'small_estate_election': True}
        docs = select_opening_documents(data)
        assert len(docs) == 2  # Affidavit + Order only, no oath

    def test_holographic(self):
        data = {'estate_type': 'Testate', 'will_type': 'Holographic'}
        docs = select_opening_documents(data)
        filenames = [d[0] for d in docs]
        assert 'Petition to Probate Holographic Will.docx' in filenames

    def test_muniment(self):
        data = {'estate_type': 'Testate', 'muniment_only': True}
        docs = select_opening_documents(data)
        filenames = [d[0] for d in docs]
        assert 'Petition for Muniment of Title.docx' in filenames

class TestDetermineDeclinations:
    def test_testate_named_executor_can_serve(self):
        data = {'estate_type': 'Testate', 'named_executor_can_serve': True}
        assert determine_declinations(data) == []

    def test_intestate_spouse_pr(self):
        data = {'estate_type': 'Intestate', 'pr_relationship': 'Spouse'}
        assert determine_declinations(data) == []

    def test_intestate_child_pr_married_decedent(self):
        data = {
            'estate_type': 'Intestate',
            'pr_relationship': 'Child',
            'pr_full_name': 'Jane Doe',
            'decedent_marital_status': 'Married',
            'decedent_spouse_name': 'Mary Smith',
            'decedent_gender': 'Male',
            'heirs': [
                {'heir_full_name': 'Jane Doe', 'heir_relationship': 'Daughter',
                 'heir_gender': 'Female', 'heir_is_minor': False},
                {'heir_full_name': 'John Doe Jr', 'heir_relationship': 'Son',
                 'heir_gender': 'Male', 'heir_is_minor': False},
            ]
        }
        decls = determine_declinations(data)
        names = [d['name'] for d in decls]
        assert 'Mary Smith' in names      # Spouse must decline
        assert 'John Doe Jr' in names     # Sibling must decline
        assert 'Jane Doe' not in names    # PR doesn't decline

class TestCalculateDeadlines:
    def test_absolute_bar_date(self):
        result = calculate_deadlines('2026-04-10')
        assert result['absolute_bar_date'] == '2027-04-10'

    def test_with_publication_date(self):
        result = calculate_deadlines('2026-04-10', '2026-05-01')
        assert result['claims_deadline'] == '2026-09-01'
        assert 'exception_deadline' in result

    def test_exception_is_30_days_after_claims(self):
        result = calculate_deadlines('2026-04-10', '2026-05-01')
        from datetime import datetime, timedelta
        claims = datetime.strptime(result['claims_deadline'], '%Y-%m-%d')
        exception = datetime.strptime(result['exception_deadline'], '%Y-%m-%d')
        assert (exception - claims).days == 30

class TestGenerateFlags:
    def test_nonresident_pr(self):
        data = {'pr_state': 'Alabama'}
        flags = generate_flags(data)
        assert any('Nonresident' in f['message'] for f in flags)

    def test_small_estate_eligible(self):
        data = {'estimated_estate_value': 25000, 'small_estate_election': False}
        flags = generate_flags(data)
        assert any('small estate' in f['message'] for f in flags)

    def test_no_flags_for_clean_case(self):
        data = {'pr_state': 'Tennessee', 'decedent_county': 'Maury'}
        flags = generate_flags(data)
        assert len(flags) == 0
```

**Step 6: Run all tests**

```bash
pytest tests/test_probate_utils.py -v
# Expected: all PASS
```

**Step 7: Commit**

```bash
git add api/probate_utils.py tests/test_probate_utils.py
git commit -m "feat(probate): add shared utilities — pronouns, doc selection, declinations, deadlines, flags"
```

---

## Task 3: Build Opening Document Generator Endpoint

**Files:**
- Create: `api/generate-probate-opening.py`
- Create: `tests/test_probate_opening.py`

This endpoint receives JSON intake data, selects documents per § 2.1, generates each one with merge field replacement, builds declinations, and returns a ZIP file.

**Step 1: Write test for the endpoint**

```python
# tests/test_probate_opening.py
import pytest
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

# Test the generate function directly (not the HTTP handler)
# Templates must exist in api/probate-templates/ before running

SAMPLE_TESTATE_DATA = {
    'estate_type': 'Testate',
    'will_type': 'Standard Witnessed',
    'decedent_full_name': 'Smith, John Robert',
    'decedent_gender': 'Male',
    'decedent_dob': '1945-06-15',
    'decedent_dod': '2026-03-01',
    'decedent_age': 80,
    'decedent_address': '123 Main Street',
    'decedent_city': 'Columbia',
    'decedent_county': 'Maury',
    'decedent_state': 'Tennessee',
    'decedent_place_of_death': 'Maury Regional Medical Center',
    'decedent_marital_status': 'Widowed',
    'decedent_had_business': False,
    'will_execution_date': '2020-01-15',
    'will_witness_1': 'Alice Jones',
    'will_witness_2': 'Bob Williams',
    'will_names_executor': True,
    'will_executor_name': 'Jane Smith',
    'named_executor_can_serve': True,
    'will_waives_bond': True,
    'will_waives_inventory': True,
    'will_waives_accountings': True,
    'will_appointment_paragraph': 'Article III',
    'estimated_estate_value': 250000,
    'pr_full_name': 'Jane Smith',
    'pr_address': '456 Oak Avenue',
    'pr_city': 'Columbia',
    'pr_state': 'Tennessee',
    'pr_age': 55,
    'pr_gender': 'Female',
    'pr_relationship': 'Daughter',
    'pr_criminal_history': False,
    'pr_penitentiary_sentence': False,
    'pr_will_attend_probate': True,
    'heirs': [
        {
            'heir_full_name': 'Jane Smith',
            'heir_age': 55,
            'heir_address': '456 Oak Avenue, Columbia, TN 38401',
            'heir_city': 'Columbia',
            'heir_relationship': 'Daughter',
            'heir_gender': 'Female',
            'heir_is_minor': False,
            'heir_has_disability': False,
            'heir_is_beneficiary': True,
            'heir_beneficiary_type': 'Residuary',
        },
    ],
    'properties': [],
    'attorney_full_name': 'R. Dale Thomas',
    'attorney_bpr': '12345',
    'firm_name': 'Muletown Law, P.C.',
}

class TestOpeningDocumentSelection:
    def test_testate_standard_returns_zip(self):
        """Verify the generator returns a valid ZIP buffer."""
        from generate_probate_opening import generate_opening_package
        result = generate_opening_package(SAMPLE_TESTATE_DATA)
        assert result is not None
        # result should be a BytesIO with ZIP content
        import zipfile
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert any('Petition' in n for n in names)
        assert any('Order' in n for n in names)
        assert any('Oath' in n for n in names)

    def test_no_declinations_when_named_executor_serves(self):
        from generate_probate_opening import generate_opening_package
        result = generate_opening_package(SAMPLE_TESTATE_DATA)
        import zipfile
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert not any('Declination' in n for n in names)
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/test_probate_opening.py -v
# Expected: FAIL — module not found
```

**Step 3: Write the opening generator endpoint**

```python
# api/generate-probate-opening.py
"""Generate probate opening documents as a ZIP file."""
from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from probate_utils import (
    load_template, replace_in_document, build_common_replacements,
    select_opening_documents, determine_declinations, derive_pronouns,
    derive_pr_title, build_zip, generate_flags
)


def generate_declination_doc(decliner, data):
    """Generate a single declination document for one person."""
    doc = load_template('Declination to Serve CURLY.docx')
    pr_title = derive_pr_title(data.get('estate_type', 'Testate'),
                                data.get('pr_gender', 'Male'))
    dec_pronouns = derive_pronouns(decliner.get('gender', 'Male'))

    replacements = {
        '{DECLINER NAME}': decliner['name'],
        '{DECEDENT}': data.get('decedent_full_name', ''),
        '{Decedent Name}': data.get('decedent_full_name', ''),
        '{PETITIONER}': data.get('pr_full_name', ''),
        '{RELATION TO DECEDENT}': decliner.get('relationship', ''),
        '{HIS/HER}': dec_pronouns['possessive'],
        '{his/her}': dec_pronouns['possessive'],
        '{Administrator/trix CHOOSE ONE}': pr_title,
        '{Title Executor/Executrix CHOOSE ONE}': pr_title,
        '{COUNTY}': data.get('decedent_county', ''),
        '{COUNTY NAME}': data.get('decedent_county', ''),
        'Dale, Hutto & Lyle, PLLC': data.get('firm_name', 'Muletown Law, P.C.'),
    }
    replace_in_document(doc, replacements)
    return doc


def generate_opening_package(data):
    """Generate all opening documents and return as ZIP BytesIO."""
    replacements = build_common_replacements(data)
    documents = []

    # 1. Generate petition, order, oath per selection logic
    selected = select_opening_documents(data)
    for template_name, output_title in selected:
        doc = load_template(template_name)
        replace_in_document(doc, replacements)
        documents.append((output_title, doc))

    # 2. Generate declinations
    declinations = determine_declinations(data)
    for decliner in declinations:
        doc = generate_declination_doc(decliner, data)
        title = f"Declination to Serve - {decliner['name']}"
        documents.append((title, doc))

    # 3. Build ZIP
    date_str = data.get('generation_date') or None
    return build_zip(documents, date_str)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            zip_buffer = generate_opening_package(data)

            decedent_name = data.get('decedent_full_name', 'Unknown').replace(' ', '_')
            filename = f"Probate_Opening_{decedent_name}.zip"

            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition',
                             f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(zip_buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

**Step 4: Run tests**

```bash
pytest tests/test_probate_opening.py -v
# Expected: PASS (if templates are in api/probate-templates/)
```

**Step 5: Commit**

```bash
git add api/generate-probate-opening.py tests/test_probate_opening.py
git commit -m "feat(probate): add opening document generator endpoint — ZIP of petition, order, oath, declinations"
```

---

## Task 4: Build Opening Intake Form (probate.html)

**Files:**
- Create: `probate.html`

This is a multi-step React wizard with 6 steps. Follows the same patterns as `index.html` and `will.html` — React 18 via CDN, Tailwind CSS, Babel transpiler.

**Step 1: Create probate.html**

Build a React app with these sections:

1. **Step 1 — Decedent**: decedent_full_name, decedent_aka, decedent_gender (select), decedent_dob, decedent_dod, decedent_ssn, decedent_place_of_death, decedent_address, decedent_city, decedent_county (select from tennesseeCounties), decedent_state (default Tennessee), decedent_marital_status (select: Married/Widowed/Single/Divorced), conditional decedent_spouse_name and decedent_spouse_dod, decedent_had_business (checkbox), conditional decedent_business_details.

2. **Step 2 — Estate Type**: estate_type (Testate/Intestate), conditional will_type (Standard Witnessed/Holographic/Will + Codicil), conditional will fields (execution_date, witnesses, codicil fields), will_names_executor, will_executor_name, named_executor_can_serve, will_names_alternate, will_alternate_name, will_waives_bond, will_waives_inventory, will_waives_accountings, will_appointment_paragraph, muniment_only, estimated_estate_value, small_estate_election checkbox (show only if value ≤ 50000).

3. **Step 3 — Personal Representative**: pr_full_name, pr_address, pr_city, pr_state, pr_age, pr_gender, pr_relationship, pr_phone, pr_email, pr_criminal_history (checkbox), conditional pr_criminal_details, pr_penitentiary_sentence (checkbox), pr_will_attend_probate.

4. **Step 4 — Heirs** (repeatable): Add/remove heirs. Each: heir_full_name, heir_age, heir_address, heir_city, heir_relationship, heir_gender, heir_is_minor, heir_has_disability, conditional heir_is_beneficiary and heir_beneficiary_type (Specific/Residuary/Both).

5. **Step 5 — Real Property** (repeatable): Add/remove properties. Each: property_address, property_county, property_map_parcel, property_estimated_value, property_description.

6. **Step 6 — Review & Generate**: Display summary of all entered data. Show flags/warnings (call generate_flags logic in JS). System config section: attorney_full_name, attorney_bpr (defaults from firm constants). Generate button → POST to `/api/generate-probate-opening` → download ZIP.

**Key implementation details:**
- Use `useState` for all form state
- Show/hide conditional fields with `&&` rendering
- Tennessee counties array (reuse from index.html)
- Step navigation with Next/Back buttons + step indicator
- Firm defaults hardcoded: Muletown Law, P.C., 1109 South Garden Street, Columbia, TN 38401, (931) 388-2822
- POST JSON to endpoint, receive ZIP blob, trigger download
- Show flags/warnings panel at Review step with yellow (warning) and blue (info) badges

**Step 2: Test manually in browser**

```bash
# Start Vercel dev server
cd /Users/muletownlaw/Documents/muletownlaw-legal-docs
npx vercel dev
# Open http://localhost:3000/probate.html
```

**Step 3: Commit**

```bash
git add probate.html
git commit -m "feat(probate): add opening intake form — 6-step wizard with conditional fields"
```

---

## Task 5: Build Closing Document Generator Endpoint

**Files:**
- Create: `api/generate-probate-closing.py`
- Create: `tests/test_probate_closing.py`

**Step 1: Write failing test**

```python
# tests/test_probate_closing.py
import pytest
import sys
import os
import zipfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

SAMPLE_CLOSING_DATA = {
    'estate_type': 'Testate',
    'decedent_full_name': 'Smith, John Robert',
    'decedent_county': 'Maury',
    'decedent_dod': '2026-03-01',
    'pr_full_name': 'Jane Smith',
    'pr_gender': 'Female',
    'pr_relationship': 'Daughter',
    'case_number': '2026-123',
    'all_heirs_sui_juris': True,
    'tenncare_asserted_claim': False,
    'tenncare_release_date': '2026-08-15',
    'claims_statement': 'There were no potential claimants of the Estate.',
    'attorney_full_name': 'R. Dale Thomas',
    'attorney_bpr': '12345',
    'attorney_fee_amount': '3,500.00',
    'heirs': [
        {
            'heir_full_name': 'Jane Smith',
            'heir_address': '456 Oak Avenue',
            'heir_city': 'Columbia, TN 38401',
            'heir_relationship': 'Daughter',
            'heir_gender': 'Female',
            'heir_is_minor': False,
            'heir_has_disability': False,
            'heir_is_beneficiary': True,
            'heir_beneficiary_type': 'Residuary',
        },
    ],
}

class TestClosingGenerator:
    def test_returns_zip_with_petition_and_order(self):
        from generate_probate_closing import generate_closing_package
        result = generate_closing_package(SAMPLE_CLOSING_DATA)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert any('Petition to Close' in n for n in names)
        assert any('Order' in n for n in names)

    def test_includes_receipt_per_heir(self):
        from generate_probate_closing import generate_closing_package
        result = generate_closing_package(SAMPLE_CLOSING_DATA)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert any('Receipt and Waiver' in n for n in names)
```

**Step 2: Run test to verify failure**

```bash
pytest tests/test_probate_closing.py -v
```

**Step 3: Write the closing generator**

```python
# api/generate-probate-closing.py
"""Generate probate closing documents as a ZIP file."""
from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from probate_utils import (
    load_template, replace_in_document, build_common_replacements,
    select_closing_documents, select_receipt_waiver_template,
    derive_pronouns, build_zip
)


def generate_receipt_waiver(heir, data):
    """Generate receipt & waiver for one heir."""
    template_name, output_title = select_receipt_waiver_template(heir, data)
    doc = load_template(template_name)
    heir_pronouns = derive_pronouns(heir.get('heir_gender', 'Female'))

    replacements = {
        '{Beneficiary Name}': heir['heir_full_name'],
        '{BENEFICIARY NAME}': heir['heir_full_name'],
        '{Beneficiary Address}': heir.get('heir_address', ''),
        '{Beneficiary City, State Zip}': heir.get('heir_city', ''),
        '{Beneficiary Pronoun}': heir_pronouns['subject'],
        '{Decedent Name}': data.get('decedent_full_name', ''),
        '{DECEDENT}': data.get('decedent_full_name', ''),
        '{Executor Name}': data.get('pr_full_name', ''),
        '{Executor/trix}': data.get('pr_title', 'Executor'),
        '{AttorneyFeeAmount}': data.get('attorney_fee_amount', ''),
        '{ExecutorFeeTotal}': data.get('executor_fee_amount', ''),
        '{Docket Number}': data.get('case_number', ''),
        '{COUNTY}': data.get('decedent_county', ''),
        'Dale, Hutto & Lyle, PLLC': data.get('firm_name', 'Muletown Law, P.C.'),
    }
    replace_in_document(doc, replacements)
    return output_title, doc


def generate_closing_package(data):
    """Generate all closing documents and return as ZIP BytesIO."""
    replacements = build_common_replacements(data)
    documents = []

    # 1. Closing petition and order
    selected = select_closing_documents(data)
    for template_name, output_title in selected:
        doc = load_template(template_name)
        replace_in_document(doc, replacements)
        documents.append((output_title, doc))

    # 2. Receipt & waiver per heir
    for heir in data.get('heirs', []):
        title, doc = generate_receipt_waiver(heir, data)
        documents.append((title, doc))

    # 3. Build ZIP
    return build_zip(documents)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            zip_buffer = generate_closing_package(data)

            decedent_name = data.get('decedent_full_name', 'Unknown').replace(' ', '_')
            filename = f"Probate_Closing_{decedent_name}.zip"

            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition',
                             f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(zip_buffer.getvalue())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
```

**Step 4: Run tests**

```bash
pytest tests/test_probate_closing.py -v
```

**Step 5: Commit**

```bash
git add api/generate-probate-closing.py tests/test_probate_closing.py
git commit -m "feat(probate): add closing document generator — petition, order, receipts & waivers"
```

---

## Task 6: Build Closing Intake Form (probate-closing.html)

**Files:**
- Create: `probate-closing.html`

Simpler form than the opening intake. Fields:

1. **Case Info**: decedent_full_name, case_number, estate_type, decedent_county, pr_full_name, pr_gender
2. **Status**: tenncare_release_date, tenncare_asserted_claim, claims_statement (dropdown: no claimants / all resolved), all_heirs_sui_juris
3. **Heirs & Distribution** (repeatable): heir_full_name, heir_address, heir_city, heir_gender, heir_relationship, heir_beneficiary_type (for testate), attorney_fee_amount, executor_fee_amount
4. **Generate**: POST to `/api/generate-probate-closing` → download ZIP

Follow same React/Tailwind/CDN pattern as probate.html.

**Step 1: Create probate-closing.html**

Build the React form per the field list above. Much shorter than probate.html — approximately 4 sections.

**Step 2: Test manually**

```bash
npx vercel dev
# Open http://localhost:3000/probate-closing.html
```

**Step 3: Commit**

```bash
git add probate-closing.html
git commit -m "feat(probate): add closing intake form"
```

---

## Task 7: Research Lawmatics API & Build Integration Endpoint

**Files:**
- Create: `api/lawmatics-probate.py`

**Step 1: Research Lawmatics API**

Check Lawmatics API documentation for:
- Authentication method (API key header? Bearer token?)
- Create matter endpoint
- Create task/checklist endpoint
- Create calendar event endpoint
- Search/find existing matter endpoint

Reference: Check Lawmatics settings for API docs URL, or search their developer docs.

**Step 2: Write the integration endpoint**

The endpoint should accept JSON with:
```json
{
  "action": "create_matter" | "push_deadlines" | "create_tasks",
  "matter_data": { ... },
  "deadlines": [ ... ],
  "tasks": [ ... ]
}
```

Use Python's `urllib.request` (built-in) for API calls to avoid adding dependencies.

Store the API key as a Vercel environment variable (`LAWMATICS_API_KEY`).

**Step 3: Configure Vercel environment variable**

```bash
npx vercel env add LAWMATICS_API_KEY
# Enter the API key when prompted
```

**Step 4: Commit**

```bash
git add api/lawmatics-probate.py
git commit -m "feat(probate): add Lawmatics API integration — matter creation, tasks, calendar events"
```

---

## Task 8: Build Publication Deadlines Page (probate-deadlines.html)

**Files:**
- Create: `probate-deadlines.html`

Very simple page — just 3 fields:
1. **Matter/Case identifier** (text — to find the Lawmatics matter)
2. **Date of Death** (date — for absolute bar date calculation)
3. **Publication Date** (date — for claims/exception deadlines)

On submit:
1. Calculate all 4 deadlines using the same logic as `calculate_deadlines()`
2. Display the calculated dates for review
3. "Push to Lawmatics" button → POST to `/api/lawmatics-probate` with `action: "push_deadlines"`

**Step 1: Create probate-deadlines.html**

Simple React form with date inputs and a results display panel showing:
- Claims deadline (publication + 4 months) — "Last day creditor WITH notice can file"
- Exception deadline (claims + 30 days) — "Deadline to file exceptions to claims"
- Absolute bar date (DOD + 12 months) — "Last day creditor WITHOUT notice can file"
- Estate eligible to close — "After exception deadline passes"

Calculate dates in JavaScript (same formulas as Python). Display before pushing.

**Step 2: Test manually**

```bash
npx vercel dev
# Open http://localhost:3000/probate-deadlines.html
```

**Step 3: Commit**

```bash
git add probate-deadlines.html
git commit -m "feat(probate): add publication deadlines calculator with Lawmatics sync"
```

---

## Task 9: Update Landing Page (index.html)

**Files:**
- Modify: `index.html`

**Step 1: Add Probate section to the landing page**

Add a third section/card after the existing "Power of Attorney Package" and "Last Will & Testament" options. The Probate section should have three cards/links:

1. **Open Probate Estate** → `/probate.html`
   Description: "Generate petition, order, oath, declinations, and TennCare letter"

2. **Publication Deadlines** → `/probate-deadlines.html`
   Description: "Calculate and push statutory deadlines to Lawmatics"

3. **Close Probate Estate** → `/probate-closing.html`
   Description: "Generate closing petition, order, and receipts & waivers"

Match the existing card styling (Tailwind classes, color scheme).

**Step 2: Test manually**

```bash
npx vercel dev
# Open http://localhost:3000/
```

**Step 3: Commit**

```bash
git add index.html
git commit -m "feat(probate): add probate section to landing page"
```

---

## Task 10: End-to-End Testing & Template Verification

**Step 1: Test opening flow end-to-end**

Using Vercel dev server:
1. Fill out probate.html with sample testate data (standard witnessed will)
2. Generate and download ZIP
3. Open each .docx and verify merge fields are replaced
4. Check: correct petition type, order type, oath included, no declinations (named executor can serve)

**Step 2: Test intestate flow**

1. Fill out probate.html with intestate data, child as PR, married decedent
2. Verify ZIP includes: intestate petition, intestate order, oath, declination from spouse

**Step 3: Test holographic and codicil variants**

Verify correct template selected for each will type.

**Step 4: Test closing flow**

1. Fill out probate-closing.html with testate data
2. Verify ZIP includes: closing petition, closing order, receipt & waiver per heir

**Step 5: Test flags and warnings**

Verify these scenarios show correct flags at Review step:
- Nonresident PR
- Criminal history
- Small estate eligible
- Out-of-county property
- Minor heir

**Step 6: Test publication deadlines page**

1. Enter DOD and publication date
2. Verify calculated dates match manual calculation
3. Test Lawmatics push (if API configured)

**Step 7: Fix any issues found and commit**

```bash
git add -A
git commit -m "fix(probate): address issues found in end-to-end testing"
```

---

## Execution Order Summary

| Task | Dependencies | Est. Complexity |
|------|-------------|-----------------|
| 1. Copy templates | None | Low |
| 2. Shared utilities | Task 1 | High — core logic |
| 3. Opening endpoint | Tasks 1, 2 | Medium |
| 4. Opening form | Task 3 | High — large form |
| 5. Closing endpoint | Tasks 1, 2 | Medium |
| 6. Closing form | Task 5 | Medium |
| 7. Lawmatics integration | None (parallel) | Medium — API research |
| 8. Deadlines page | Task 7 | Low |
| 9. Landing page update | Tasks 4, 6, 8 | Low |
| 10. E2E testing | All | Medium |

Tasks 1–4 are the critical path. Task 7 can run in parallel once Task 2 is done.
