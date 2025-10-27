"""
Unit tests for Power of Attorney generator

Tests the POA generator module to ensure proper document generation
and pronoun handling.
"""
import pytest
import sys
import os
from io import BytesIO

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from generate_poa import generate_poa_document


@pytest.mark.unit
class TestPOAGeneration:
    """Test POA document generation"""

    def test_generate_poa_basic(self, sample_poa_data):
        """Test basic POA generation returns a Document object"""
        doc = generate_poa_document(sample_poa_data)

        # Should return a Document object
        assert doc is not None
        assert hasattr(doc, 'paragraphs')
        assert len(doc.paragraphs) > 0

    def test_poa_contains_client_name(self, sample_poa_data):
        """Test that generated POA contains client name"""
        doc = generate_poa_document(sample_poa_data)

        # Search through all paragraphs for client name
        full_text = '\n'.join([p.text for p in doc.paragraphs])
        assert 'TEST CLIENT' in full_text.upper()

    def test_poa_contains_required_articles(self, sample_poa_data):
        """Test that POA contains all 9 required articles"""
        doc = generate_poa_document(sample_poa_data)

        full_text = '\n'.join([p.text for p in doc.paragraphs])

        # Check for all article headers
        required_articles = [
            'GENERAL AUTHORITY',
            'PROPERTY YOU OWN',
            'PROPERTY YOU CONTROL',
            'PROPERTY IN ACCOUNTS',
            'BORROWING AND CREDIT',
            'INSURANCE',
            'TAX AND GOVERNMENT BENEFITS',
            'PERSONAL MATTERS',
            'LEGAL AND ADMINISTRATIVE'
        ]

        for article in required_articles:
            assert article in full_text, f"Missing required article: {article}"

    def test_poa_male_pronouns(self):
        """Test that male client gets correct pronouns (he/his/him)"""
        data = {
            'CLIENT_NAME': 'John Doe',
            'CLIENT_GENDER': 'Male',
            'COUNTY': 'Maury',
            'AIF_NAME': 'Agent Name',
            'AIF_RELATIONSHIP': 'spouse',
            'ALTERNATE_AIF_NAME': 'Alt Agent',
            'ALTERNATE_AIF_RELATIONSHIP': 'sibling',
            'EXEC_MONTH': 'October',
            'EXEC_YEAR': '2025'
        }

        doc = generate_poa_document(data)
        full_text = '\n'.join([p.text for p in doc.paragraphs]).lower()

        # Should contain masculine pronouns
        assert ' he ' in full_text or 'that he ' in full_text
        assert ' his ' in full_text
        assert ' him ' in full_text

        # Should NOT contain feminine pronouns in pronoun contexts
        # (Note: 'her' might appear in other contexts like 'other')
        pronoun_sections = [p.text.lower() for p in doc.paragraphs if 'personally appeared' in p.text.lower()]
        if pronoun_sections:
            assert 'she' not in pronoun_sections[0]

    def test_poa_female_pronouns(self):
        """Test that female client gets correct pronouns (she/her/her)"""
        data = {
            'CLIENT_NAME': 'Jane Doe',
            'CLIENT_GENDER': 'Female',
            'COUNTY': 'Maury',
            'AIF_NAME': 'Agent Name',
            'AIF_RELATIONSHIP': 'daughter',
            'ALTERNATE_AIF_NAME': 'Alt Agent',
            'ALTERNATE_AIF_RELATIONSHIP': 'son',
            'EXEC_MONTH': 'October',
            'EXEC_YEAR': '2025'
        }

        doc = generate_poa_document(data)
        full_text = '\n'.join([p.text for p in doc.paragraphs]).lower()

        # Should contain feminine pronouns
        assert ' she ' in full_text or 'that she ' in full_text
        assert ' her ' in full_text

    def test_poa_contains_agents(self, sample_poa_data):
        """Test that POA contains both primary and alternate agents"""
        doc = generate_poa_document(sample_poa_data)
        full_text = '\n'.join([p.text for p in doc.paragraphs])

        assert 'PRIMARY AGENT' in full_text.upper()
        assert 'ALTERNATE AGENT' in full_text.upper()

    def test_poa_contains_signature_block(self, sample_poa_data):
        """Test that POA contains signature and notary blocks"""
        doc = generate_poa_document(sample_poa_data)
        full_text = '\n'.join([p.text for p in doc.paragraphs])

        # Check for signature section
        assert 'WITNESS MY SIGNATURE' in full_text.upper()

        # Check for notary section
        assert 'STATE OF TENNESSEE' in full_text
        assert 'COUNTY OF MAURY' in full_text
        assert 'NOTARY PUBLIC' in full_text

    def test_poa_contains_county(self, sample_poa_data):
        """Test that POA contains the correct county"""
        doc = generate_poa_document(sample_poa_data)
        full_text = '\n'.join([p.text for p in doc.paragraphs])

        assert 'Maury County' in full_text or 'MAURY' in full_text

    def test_poa_contains_execution_date(self, sample_poa_data):
        """Test that POA contains execution month and year"""
        doc = generate_poa_document(sample_poa_data)
        full_text = '\n'.join([p.text for p in doc.paragraphs])

        assert 'OCTOBER' in full_text.upper()
        assert '2025' in full_text

    def test_poa_has_header_footer(self, sample_poa_data):
        """Test that POA has header and footer configured"""
        doc = generate_poa_document(sample_poa_data)

        # Check that document has sections
        assert len(doc.sections) > 0

        # Check that first section has header
        section = doc.sections[0]
        assert section.header is not None
        assert section.footer is not None

        # Check header contains firm info
        header_text = '\n'.join([p.text for p in section.header.paragraphs])
        assert 'Muletown Law' in header_text or 'MULETOWN' in header_text.upper()
