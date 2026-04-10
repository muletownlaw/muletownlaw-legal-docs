# tests/test_probate_closing.py
import pytest
import sys
import os
import zipfile
import importlib.util
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

# Import the hyphenated module using importlib
_spec = importlib.util.spec_from_file_location(
    'generate_probate_closing',
    os.path.join(os.path.dirname(__file__), '..', 'api', 'generate-probate-closing.py')
)
generate_probate_closing = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generate_probate_closing)
generate_closing_package = generate_probate_closing.generate_closing_package

SAMPLE_TESTATE_CLOSING = {
    'estate_type': 'Testate',
    'decedent_full_name': 'Smith, John Robert',
    'decedent_gender': 'Male',
    'decedent_dod': '2026-03-01',
    'decedent_county': 'Maury',
    'decedent_address': '123 Main Street',
    'decedent_city': 'Columbia',
    'decedent_state': 'Tennessee',
    'decedent_place_of_death': 'Maury Regional Medical Center',
    'decedent_marital_status': 'Widowed',
    'decedent_had_business': False,
    'decedent_age': 80,
    'will_execution_date': '2020-01-15',
    'will_waives_bond': True,
    'will_waives_inventory': True,
    'will_waives_accountings': True,
    'pr_full_name': 'Jane Smith',
    'pr_address': '456 Oak Avenue',
    'pr_city': 'Columbia',
    'pr_state': 'Tennessee',
    'pr_gender': 'Female',
    'pr_age': 55,
    'pr_relationship': 'Daughter',
    'pr_criminal_history': False,
    'pr_penitentiary_sentence': False,
    'case_number': '2026-123',
    'all_heirs_sui_juris': True,
    'tenncare_asserted_claim': False,
    'tenncare_release_date': '2026-08-15',
    'claims_statement': 'There were no potential claimants of the Estate.',
    'attorney_full_name': 'R. Dale Thomas',
    'attorney_bpr': '12345',
    'attorney_fee_amount': '3,500.00',
    'executor_fee_amount': '2,000.00',
    'firm_name': 'Muletown Law, P.C.',
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
    'properties': [],
}

SAMPLE_INTESTATE_CLOSING = {
    'estate_type': 'Intestate',
    'decedent_full_name': 'Doe, James Allen',
    'decedent_gender': 'Male',
    'decedent_dod': '2026-02-10',
    'decedent_county': 'Maury',
    'decedent_address': '789 Elm Street',
    'decedent_city': 'Columbia',
    'decedent_state': 'Tennessee',
    'decedent_place_of_death': 'Maury Regional Medical Center',
    'decedent_marital_status': 'Married',
    'decedent_spouse_name': 'Mary Doe',
    'decedent_had_business': False,
    'decedent_age': 75,
    'pr_full_name': 'Robert Doe',
    'pr_address': '321 Pine Street',
    'pr_city': 'Columbia',
    'pr_state': 'Tennessee',
    'pr_gender': 'Male',
    'pr_age': 45,
    'pr_relationship': 'Child',
    'pr_criminal_history': False,
    'pr_penitentiary_sentence': False,
    'case_number': '2026-456',
    'all_heirs_sui_juris': True,
    'tenncare_asserted_claim': False,
    'claims_statement': 'There were no potential claimants of the Estate.',
    'attorney_full_name': 'R. Dale Thomas',
    'attorney_bpr': '12345',
    'attorney_fee_amount': '3,000.00',
    'executor_fee_amount': '1,500.00',
    'firm_name': 'Muletown Law, P.C.',
    'heirs': [
        {
            'heir_full_name': 'Robert Doe',
            'heir_address': '321 Pine Street',
            'heir_city': 'Columbia, TN 38401',
            'heir_relationship': 'Son',
            'heir_gender': 'Male',
            'heir_is_minor': False,
            'heir_has_disability': False,
        },
        {
            'heir_full_name': 'Susan Doe',
            'heir_address': '555 Maple Drive',
            'heir_city': 'Columbia, TN 38401',
            'heir_relationship': 'Daughter',
            'heir_gender': 'Female',
            'heir_is_minor': False,
            'heir_has_disability': False,
        },
    ],
    'properties': [],
}

SAMPLE_MULTI_HEIR_TESTATE = {
    'estate_type': 'Testate',
    'decedent_full_name': 'Williams, Sarah Mae',
    'decedent_gender': 'Female',
    'decedent_dod': '2026-01-15',
    'decedent_county': 'Williamson',
    'decedent_address': '100 Church Street',
    'decedent_city': 'Franklin',
    'decedent_state': 'Tennessee',
    'decedent_place_of_death': 'Williamson Medical Center',
    'decedent_marital_status': 'Widowed',
    'decedent_had_business': False,
    'decedent_age': 90,
    'will_execution_date': '2018-06-01',
    'will_waives_bond': True,
    'will_waives_inventory': True,
    'will_waives_accountings': True,
    'pr_full_name': 'Tom Williams',
    'pr_address': '200 Main Street',
    'pr_city': 'Franklin',
    'pr_state': 'Tennessee',
    'pr_gender': 'Male',
    'pr_age': 60,
    'pr_relationship': 'Son',
    'pr_criminal_history': False,
    'pr_penitentiary_sentence': False,
    'case_number': '2026-789',
    'all_heirs_sui_juris': True,
    'attorney_full_name': 'R. Dale Thomas',
    'attorney_bpr': '12345',
    'attorney_fee_amount': '5,000.00',
    'executor_fee_amount': '3,000.00',
    'firm_name': 'Muletown Law, P.C.',
    'heirs': [
        {
            'heir_full_name': 'Tom Williams',
            'heir_address': '200 Main Street',
            'heir_city': 'Franklin, TN 37064',
            'heir_relationship': 'Son',
            'heir_gender': 'Male',
            'heir_is_minor': False,
            'heir_has_disability': False,
            'heir_is_beneficiary': True,
            'heir_beneficiary_type': 'Residuary',
        },
        {
            'heir_full_name': 'Lisa Williams',
            'heir_address': '300 Elm Street',
            'heir_city': 'Franklin, TN 37064',
            'heir_relationship': 'Daughter',
            'heir_gender': 'Female',
            'heir_is_minor': False,
            'heir_has_disability': False,
            'heir_is_beneficiary': True,
            'heir_beneficiary_type': 'Specific',
        },
        {
            'heir_full_name': 'Mark Williams',
            'heir_address': '400 Oak Drive',
            'heir_city': 'Nashville, TN 37201',
            'heir_relationship': 'Son',
            'heir_gender': 'Male',
            'heir_is_minor': False,
            'heir_has_disability': False,
            'heir_is_beneficiary': True,
            'heir_beneficiary_type': 'Residuary',
        },
    ],
    'properties': [],
}


class TestTestateCosing:
    def test_testate_returns_zip_with_petition_and_order(self):
        """Verify testate closing returns a ZIP with petition, order, and receipt per heir."""
        result = generate_closing_package(SAMPLE_TESTATE_CLOSING)
        assert result is not None
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert any('Petition to Close' in n for n in names)
        assert any('Order to Close' in n for n in names)
        assert any('Receipt and Waiver' in n for n in names)

    def test_testate_zip_has_correct_count(self):
        """Testate with 1 heir: petition + order + 1 receipt = 3 docs."""
        result = generate_closing_package(SAMPLE_TESTATE_CLOSING)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert len(names) == 3
        assert all(n.endswith('.docx') for n in names)

    def test_testate_filenames_contain_expected_titles(self):
        """Verify exact expected filenames are in the ZIP."""
        result = generate_closing_package(SAMPLE_TESTATE_CLOSING)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert any('Petition to Close Estate' in n for n in names)
        assert any('Order to Close Estate' in n for n in names)
        assert any('Receipt and Waiver - Jane Smith' in n for n in names)

    def test_testate_sui_juris_selects_standard_petition(self):
        """When all_heirs_sui_juris is True, uses standard petition template."""
        result = generate_closing_package(SAMPLE_TESTATE_CLOSING)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        # Should NOT contain "No sui juris" variant
        assert not any('No sui juris' in n for n in names)
        assert any('Petition to Close Estate' in n for n in names)

    def test_testate_not_sui_juris_selects_alternate_petition(self):
        """When all_heirs_sui_juris is False, uses non-sui-juris petition."""
        data = {**SAMPLE_TESTATE_CLOSING, 'all_heirs_sui_juris': False}
        result = generate_closing_package(data)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        # Still named "Petition to Close Estate" in output
        assert any('Petition to Close Estate' in n for n in names)


class TestIntestateCosing:
    def test_intestate_returns_correct_document_types(self):
        """Verify intestate closing returns intestate-specific petition and order."""
        result = generate_closing_package(SAMPLE_INTESTATE_CLOSING)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert any('Petition to Close Intestate Estate' in n for n in names)
        assert any('Order Closing Intestate Estate' in n for n in names)

    def test_intestate_includes_receipt_per_heir(self):
        """Verify intestate with 2 heirs produces 2 receipt & waiver documents."""
        result = generate_closing_package(SAMPLE_INTESTATE_CLOSING)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        receipt_files = [n for n in names if 'Receipt and Waiver' in n]
        assert len(receipt_files) == 2

    def test_intestate_receipt_names_match_heirs(self):
        """Each receipt filename includes the heir's name."""
        result = generate_closing_package(SAMPLE_INTESTATE_CLOSING)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert any('Receipt and Waiver - Robert Doe' in n for n in names)
        assert any('Receipt and Waiver - Susan Doe' in n for n in names)

    def test_intestate_zip_has_correct_count(self):
        """Intestate with 2 heirs: petition + order + 2 receipts = 4 docs."""
        result = generate_closing_package(SAMPLE_INTESTATE_CLOSING)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert len(names) == 4
        assert all(n.endswith('.docx') for n in names)


class TestReceiptPerHeir:
    def test_multi_heir_testate_generates_one_receipt_per_heir(self):
        """3 heirs should produce 3 receipt & waiver documents."""
        result = generate_closing_package(SAMPLE_MULTI_HEIR_TESTATE)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        receipt_files = [n for n in names if 'Receipt and Waiver' in n]
        assert len(receipt_files) == 3

    def test_multi_heir_receipt_filenames(self):
        """Each receipt filename includes the correct heir name."""
        result = generate_closing_package(SAMPLE_MULTI_HEIR_TESTATE)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert any('Receipt and Waiver - Tom Williams' in n for n in names)
        assert any('Receipt and Waiver - Lisa Williams' in n for n in names)
        assert any('Receipt and Waiver - Mark Williams' in n for n in names)

    def test_multi_heir_total_doc_count(self):
        """3 heirs testate: petition + order + 3 receipts = 5 docs."""
        result = generate_closing_package(SAMPLE_MULTI_HEIR_TESTATE)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert len(names) == 5


class TestZipFilenames:
    def test_all_files_are_docx(self):
        """Every file in the ZIP should be .docx."""
        result = generate_closing_package(SAMPLE_TESTATE_CLOSING)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert all(n.endswith('.docx') for n in names)

    def test_filenames_contain_date_prefix(self):
        """ZIP filenames should have a date prefix."""
        data = {**SAMPLE_TESTATE_CLOSING, 'generation_date': '2026-04-10'}
        result = generate_closing_package(data)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert all(n.startswith('2026-04-10') for n in names)

    def test_intestate_filenames_are_docx(self):
        """Intestate ZIP files should all be .docx."""
        result = generate_closing_package(SAMPLE_INTESTATE_CLOSING)
        zf = zipfile.ZipFile(result)
        names = zf.namelist()
        assert all(n.endswith('.docx') for n in names)
