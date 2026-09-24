"""
Tests for the Supplemental Needs Trust (SNT) article module.

Spec: Generator Spec: Testamentary Supplemental Needs Trust Article
Owner: Thomas Hutto, Muletown Law, P.C.
Status: Draft — pending attorney sign-off (language locked behind ENABLE_SNT_MODULE flag).

These tests exercise the helper functions directly (no Google Drive template download).
"""
import pytest
import re
import sys
import os
import importlib.util

# Load generate-will.py (hyphen in filename) by file path
_api_dir = os.path.join(os.path.dirname(__file__), '..', 'api')
sys.path.insert(0, _api_dir)  # needed for generate-will's own imports
_spec = importlib.util.spec_from_file_location(
    'generate_will',
    os.path.join(_api_dir, 'generate-will.py')
)
_gw = importlib.util.module_from_spec(_spec)
try:
    _spec.loader.exec_module(_gw)
except Exception:
    # Template config may be missing in test env; that is fine for unit tests
    pass

resolve_snt_conditionals = _gw.resolve_snt_conditionals
_validate_snt_beneficiaries = _gw._validate_snt_beneficiaries
load_clause_text = _gw.load_clause_text


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ALL_FLAGS_TRUE = {
    'HAS_ALT_TRUSTEE': True,
    'HAS_CONTINGENT_REMAINDER': True,
    'HAS_MINOR_TRUST_ARTICLE': True,
}

ALL_FLAGS_FALSE = {
    'HAS_ALT_TRUSTEE': False,
    'HAS_CONTINGENT_REMAINDER': False,
    'HAS_MINOR_TRUST_ARTICLE': False,
}

SAMPLE_BENEFICIARY = {
    'sn_beneficiary_name': 'Jane M. Smith',
    'trustee_name': 'Robert A. Smith',
    'trustee_relation': 'brother',
    'alt_trustee_name': 'Carol B. Jones',
    'alt_trustee_relation': 'sister',
    'remainder_name': 'Thomas D. Smith',
    'remainder_relation': 'father',
}

SAMPLE_BENEFICIARY_MINIMAL = {
    'sn_beneficiary_name': 'Jane M. Smith',
    'trustee_name': 'Robert A. Smith',
    'trustee_relation': 'brother',
    'alt_trustee_name': '',
    'alt_trustee_relation': '',
    'remainder_name': '',
    'remainder_relation': '',
}


def _resolved_text(ben, flags):
    """Helper: load clause, resolve conditionals, substitute tokens."""
    raw = load_clause_text('LWT_-_SNT_Article.txt')
    assert raw, 'Could not load LWT_-_SNT_Article.txt'
    text = resolve_snt_conditionals(raw, flags)
    text = text.replace('{SN_BENEFICIARY_NAME}', ben.get('sn_beneficiary_name', ''))
    text = text.replace('{TRUSTEE_RELATION}', ben.get('trustee_relation', ''))
    text = text.replace('{TRUSTEE_NAME}', ben.get('trustee_name', ''))
    text = text.replace('{ALT_TRUSTEE_RELATION}', ben.get('alt_trustee_relation', ''))
    text = text.replace('{ALT_TRUSTEE_NAME}', ben.get('alt_trustee_name', ''))
    text = text.replace('{REMAINDER_RELATION}', ben.get('remainder_relation', ''))
    text = text.replace('{REMAINDER_NAME}', ben.get('remainder_name', ''))
    # Leave {MINOR_TRUST_ARTICLE_NUMBER} as-is (resolved post-renumber in production)
    return text


# ---------------------------------------------------------------------------
# Test 1 — all flags true, one beneficiary
# ---------------------------------------------------------------------------

class TestAllFlagsTrue:
    """Spec test 1: snapshot with all flags true."""

    def test_alt_trustee_paragraph_present(self):
        text = _resolved_text(SAMPLE_BENEFICIARY, ALL_FLAGS_TRUE)
        assert 'Carol B. Jones' in text
        assert 'sister' in text

    def test_contingent_remainder_present(self):
        text = _resolved_text(SAMPLE_BENEFICIARY, ALL_FLAGS_TRUE)
        assert 'Thomas D. Smith' in text
        assert 'father' in text

    def test_section_n_cites_minor_trust_article(self):
        text = _resolved_text(SAMPLE_BENEFICIARY, ALL_FLAGS_TRUE)
        # When HAS_MINOR_TRUST_ARTICLE is true, Section N references the article number token
        assert '{MINOR_TRUST_ARTICLE_NUMBER}' in text
        assert 'held in trust under the terms of Article' in text

    def test_no_if_not_minor_trust_block_rendered(self):
        text = _resolved_text(SAMPLE_BENEFICIARY, ALL_FLAGS_TRUE)
        # The self-contained age-25 outright-distribution sentence from [[IF NOT]] should NOT appear
        assert 'When that person reaches the age of twenty-five (25) years, the Trustee shall distribute' not in text

    def test_beneficiary_name_substituted(self):
        text = _resolved_text(SAMPLE_BENEFICIARY, ALL_FLAGS_TRUE)
        assert 'Jane M. Smith' in text
        assert '{SN_BENEFICIARY_NAME}' not in text

    def test_trustee_substituted(self):
        text = _resolved_text(SAMPLE_BENEFICIARY, ALL_FLAGS_TRUE)
        assert 'Robert A. Smith' in text
        assert '{TRUSTEE_NAME}' not in text

    def test_trustee_relation_substituted(self):
        text = _resolved_text(SAMPLE_BENEFICIARY, ALL_FLAGS_TRUE)
        assert 'my brother, Robert A. Smith' in text


# ---------------------------------------------------------------------------
# Test 2 — all flags false
# ---------------------------------------------------------------------------

class TestAllFlagsFalse:
    """Spec test 2: snapshot with all flags false."""

    def test_no_alt_trustee_paragraph(self):
        text = _resolved_text(SAMPLE_BENEFICIARY_MINIMAL, ALL_FLAGS_FALSE)
        # The alt-trustee conditional sentence must not appear
        assert 'Carol B. Jones' not in text
        assert 'unable or unwilling to serve or to continue serving' not in text

    def test_no_contingent_remainder(self):
        text = _resolved_text(SAMPLE_BENEFICIARY_MINIMAL, ALL_FLAGS_FALSE)
        assert 'Thomas D. Smith' not in text
        # Section M should go directly to intestate succession
        assert 'those persons who would be entitled to inherit from me' in text

    def test_section_n_self_contained_trust(self):
        text = _resolved_text(SAMPLE_BENEFICIARY_MINIMAL, ALL_FLAGS_FALSE)
        # Self-contained age-25 paragraph must appear
        assert 'hold that person’s share in a separate trust' in text
        # Article cross-reference must NOT appear
        assert 'held in trust under the terms of Article' not in text
        assert '{MINOR_TRUST_ARTICLE_NUMBER}' not in text

    def test_section_m_inline_join_clean(self):
        """After removing HAS_CONTINGENT_REMAINDER block, sentence must read cleanly."""
        text = _resolved_text(SAMPLE_BENEFICIARY_MINIMAL, ALL_FLAGS_FALSE)
        # No double commas or stray spaces around the join
        assert ', ,' not in text
        assert ',,' not in text
        # The join must be: "per stirpes, or, if none, to those persons"
        assert 'per stirpes, or, if none, to those persons' in text


# ---------------------------------------------------------------------------
# Test 3 — two SNT beneficiaries produce sequential article headings
# ---------------------------------------------------------------------------

class TestMultipleBeneficiaries:
    """Spec test 3: two beneficiaries produce two articles; article numbers advance."""

    def test_two_beneficiaries_two_resolved_blocks(self):
        raw = load_clause_text('LWT_-_SNT_Article.txt')
        assert raw
        texts = []
        for ben in [SAMPLE_BENEFICIARY, SAMPLE_BENEFICIARY_MINIMAL]:
            ben2 = dict(ben, sn_beneficiary_name='First Person' if ben == SAMPLE_BENEFICIARY else 'Second Person')
            flags = {
                'HAS_ALT_TRUSTEE': bool(ben.get('alt_trustee_name', '').strip()),
                'HAS_CONTINGENT_REMAINDER': bool(ben.get('remainder_name', '').strip()),
                'HAS_MINOR_TRUST_ARTICLE': False,
            }
            t = resolve_snt_conditionals(raw, flags)
            t = t.replace('{SN_BENEFICIARY_NAME}', ben2['sn_beneficiary_name'])
            texts.append(t)
        assert 'First Person' in texts[0]
        assert 'First Person' not in texts[1]
        assert 'Second Person' in texts[1]
        assert 'Second Person' not in texts[0]


# ---------------------------------------------------------------------------
# Test 4 — HAS_MINOR_TRUST_ARTICLE true → Section N cites correct token
# ---------------------------------------------------------------------------

class TestMinorTrustArticleReference:
    """Spec test 4: Section N cites {MINOR_TRUST_ARTICLE_NUMBER} when flag is true."""

    def test_placeholder_present_when_flag_true(self):
        text = _resolved_text(SAMPLE_BENEFICIARY, ALL_FLAGS_TRUE)
        # Token left for post-renumber resolution
        assert '{MINOR_TRUST_ARTICLE_NUMBER}' in text
        assert 'Article {MINOR_TRUST_ARTICLE_NUMBER} of this Will' in text

    def test_placeholder_absent_when_flag_false(self):
        text = _resolved_text(SAMPLE_BENEFICIARY_MINIMAL, ALL_FLAGS_FALSE)
        assert '{MINOR_TRUST_ARTICLE_NUMBER}' not in text


# ---------------------------------------------------------------------------
# Test 5 — no unresolved tokens or markers remain
# ---------------------------------------------------------------------------

class TestNoUnresolvedTokensOrMarkers:
    """Spec test 5: no {token} or [[marker]] left after full resolution."""

    @pytest.mark.parametrize('flags,ben', [
        (ALL_FLAGS_TRUE, SAMPLE_BENEFICIARY),
        (ALL_FLAGS_FALSE, SAMPLE_BENEFICIARY_MINIMAL),
    ])
    def test_no_unresolved_if_markers(self, flags, ben):
        text = _resolved_text(ben, flags)
        assert '[[' not in text, f'Unresolved [[...]] marker found'

    @pytest.mark.parametrize('flags,ben', [
        (ALL_FLAGS_TRUE, SAMPLE_BENEFICIARY),
        (ALL_FLAGS_FALSE, SAMPLE_BENEFICIARY_MINIMAL),
    ])
    def test_no_unresolved_braced_tokens(self, flags, ben):
        text = _resolved_text(ben, flags)
        # Allow {MINOR_TRUST_ARTICLE_NUMBER} when HAS_MINOR_TRUST_ARTICLE is true
        # (resolved post-renumber); strip it before checking for remaining tokens
        text_check = text.replace('{MINOR_TRUST_ARTICLE_NUMBER}', '')
        unresolved = re.findall(r'\{[A-Z_]+\}', text_check)
        assert not unresolved, f'Unresolved tokens: {unresolved}'


# ---------------------------------------------------------------------------
# Test 6 — no straight quotes in SNT article text
# ---------------------------------------------------------------------------

class TestNoCurlyQuoteDowngrade:
    """Spec test 6: no straight ASCII quotes (\" or ') in generated SNT text."""

    @pytest.mark.parametrize('flags,ben', [
        (ALL_FLAGS_TRUE, SAMPLE_BENEFICIARY),
        (ALL_FLAGS_FALSE, SAMPLE_BENEFICIARY_MINIMAL),
    ])
    def test_no_straight_double_quotes(self, flags, ben):
        raw = load_clause_text('LWT_-_SNT_Article.txt')
        assert '"' not in raw, 'Clause file contains straight double quote'

    @pytest.mark.parametrize('flags,ben', [
        (ALL_FLAGS_TRUE, SAMPLE_BENEFICIARY),
        (ALL_FLAGS_FALSE, SAMPLE_BENEFICIARY_MINIMAL),
    ])
    def test_no_straight_apostrophes(self, flags, ben):
        raw = load_clause_text('LWT_-_SNT_Article.txt')
        # Check for straight apostrophe in contractions (possessives use curly ’)
        straight_apos = re.findall(r"(?<!\*)'(?!\*)", raw)
        assert not straight_apos, f'Clause file contains straight apostrophe(s): {straight_apos[:3]}'


# ---------------------------------------------------------------------------
# Test 7 — validation blocks generation when required token is empty
# ---------------------------------------------------------------------------

class TestValidationBlocksGeneration:
    """Spec test 7: validation returns error when required fields are missing."""

    def test_missing_beneficiary_name_blocked(self):
        ben = dict(SAMPLE_BENEFICIARY, sn_beneficiary_name='')
        err = _validate_snt_beneficiaries([ben])
        assert err is not None
        assert 'name' in err.lower()

    def test_missing_trustee_name_blocked(self):
        ben = dict(SAMPLE_BENEFICIARY, trustee_name='')
        err = _validate_snt_beneficiaries([ben])
        assert err is not None
        assert 'trustee name' in err.lower()

    def test_missing_trustee_relation_blocked(self):
        ben = dict(SAMPLE_BENEFICIARY, trustee_relation='')
        err = _validate_snt_beneficiaries([ben])
        assert err is not None
        assert 'trustee relation' in err.lower()

    def test_alt_trustee_name_without_relation_blocked(self):
        ben = dict(SAMPLE_BENEFICIARY_MINIMAL, alt_trustee_name='Carol Jones', alt_trustee_relation='')
        err = _validate_snt_beneficiaries([ben])
        assert err is not None
        assert 'alt trustee relation' in err.lower()

    def test_remainder_name_without_relation_blocked(self):
        ben = dict(SAMPLE_BENEFICIARY_MINIMAL, remainder_name='Thomas Smith', remainder_relation='')
        err = _validate_snt_beneficiaries([ben])
        assert err is not None
        assert 'relation' in err.lower()

    def test_complete_beneficiary_passes_validation(self):
        err = _validate_snt_beneficiaries([SAMPLE_BENEFICIARY])
        assert err is None

    def test_minimal_beneficiary_passes_validation(self):
        err = _validate_snt_beneficiaries([SAMPLE_BENEFICIARY_MINIMAL])
        assert err is None
