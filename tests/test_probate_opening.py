# tests/test_probate_opening.py
import pytest
import sys
import os
import json
import importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

# Test the generate function directly (not the HTTP handler)
# Templates must exist in api/probate-templates/ before running

# Import the hyphenated module using importlib
_spec = importlib.util.spec_from_file_location(
    'generate_probate_opening',
    os.path.join(os.path.dirname(__file__), '..', 'api', 'generate-probate-opening.py')
)
generate_probate_opening = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generate_probate_opening)
generate_opening_package = generate_probate_opening.generate_opening_package

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

SAMPLE_INTESTATE_DATA = {
    'estate_type': 'Intestate',
    'decedent_full_name': 'Doe, James Allen',
    'decedent_gender': 'Male',
    'decedent_dob': '1950-03-20',
    'decedent_dod': '2026-02-10',
    'decedent_age': 75,
    'decedent_address': '789 Elm Street',
    'decedent_city': 'Columbia',
    'decedent_county': 'Maury',
    'decedent_state': 'Tennessee',
    'decedent_place_of_death': 'Maury Regional Medical Center',
    'decedent_marital_status': 'Married',
    'decedent_spouse_name': 'Mary Doe',
    'decedent_had_business': False,
    'estimated_estate_value': 150000,
    'pr_full_name': 'Robert Doe',
    'pr_address': '321 Pine Street',
    'pr_city': 'Columbia',
    'pr_state': 'Tennessee',
    'pr_age': 45,
    'pr_gender': 'Male',
    'pr_relationship': 'Child',
    'pr_criminal_history': False,
    'pr_penitentiary_sentence': False,
    'pr_will_attend_probate': True,
    'heirs': [
        {
            'heir_full_name': 'Robert Doe',
            'heir_age': 45,
            'heir_address': '321 Pine Street, Columbia, TN 38401',
            'heir_city': 'Columbia',
            'heir_relationship': 'Son',
            'heir_gender': 'Male',
            'heir_is_minor': False,
            'heir_has_disability': False,
        },
        {
            'heir_full_name': 'Susan Doe',
            'heir_age': 42,
            'heir_address': '555 Maple Drive, Columbia, TN 38401',
            'heir_city': 'Columbia',
            'heir_relationship': 'Daughter',
            'heir_gender': 'Female',
            'heir_is_minor': False,
            'heir_has_disability': False,
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
        # generate_opening_package imported at module level via importlib
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
        # generate_opening_package imported at module level via importlib
        result = generate_opening_package(SAMPLE_TESTATE_DATA)
        import zipfile
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert not any('Declination' in n for n in names)

    def test_intestate_returns_correct_documents(self):
        """Verify intestate generates petition, order, and oath."""
        # generate_opening_package imported at module level via importlib
        result = generate_opening_package(SAMPLE_INTESTATE_DATA)
        import zipfile
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert any('Petition for Appointment of Administrator' in n for n in names)
        assert any('Order for Intestate Administration' in n for n in names)
        assert any('Oath' in n for n in names)

    def test_intestate_child_pr_married_decedent_declinations(self):
        """Verify declinations are generated for spouse and sibling
        when PR is a child and decedent was married."""
        # generate_opening_package imported at module level via importlib
        result = generate_opening_package(SAMPLE_INTESTATE_DATA)
        import zipfile
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        # Surviving spouse (Mary Doe) must decline
        assert any('Declination' in n and 'Mary Doe' in n for n in names)
        # Sibling (Susan Doe) must decline
        assert any('Declination' in n and 'Susan Doe' in n for n in names)
        # PR (Robert Doe) should NOT have a declination
        assert not any('Declination' in n and 'Robert Doe' in n for n in names)

    def test_zip_filenames_contain_expected_titles(self):
        """Open the ZIP and verify filenames contain expected document titles."""
        # generate_opening_package imported at module level via importlib
        result = generate_opening_package(SAMPLE_TESTATE_DATA)
        import zipfile
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        # All files should be .docx
        assert all(n.endswith('.docx') for n in names)
        # Should have exactly 3 docs: petition, order, oath (no declinations)
        assert len(names) == 3
        # Verify expected titles are present
        assert any('Petition to Probate Will and Letters Testamentary' in n for n in names)
        assert any('Order to Probate Last Will and Testament' in n for n in names)
        assert any('Personal Representative Oath' in n for n in names)

    def test_intestate_zip_filenames(self):
        """Verify intestate ZIP filenames include all expected docs and declinations."""
        # generate_opening_package imported at module level via importlib
        result = generate_opening_package(SAMPLE_INTESTATE_DATA)
        import zipfile
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        # Should have 5 docs: petition, order, oath, + 2 declinations
        assert len(names) == 5
        assert all(n.endswith('.docx') for n in names)
