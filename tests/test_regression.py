"""
Regression tests to prevent known bugs from recurring

These tests specifically target bugs that were identified and fixed,
to ensure they don't reappear in future changes.
"""
import pytest
import sys
import os

# Add api directory to path so we can import the generators
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from generate_will import format_children_list, calculate_age


@pytest.mark.regression
class TestOctober2Bug:
    """
    Regression tests for the October 2, 2025 bug where children's information
    was concatenated without proper separation, creating unreadable output.

    Original problematic output:
    "Francis, Bartoszewicz 03/31/1982Victoria Hetzel 05/06/1984Brian Tanner..."

    Expected output after fix:
    "Francis Bartoszewicz, born March 31, 1982; Victoria Hetzel, born May 6, 1984; ..."
    """

    def test_children_formatting_single_child(self):
        """Test formatting of single child"""
        children = [{'name': 'John Doe', 'dob': '2000-01-15'}]
        detailed, simple, num = format_children_list(children)

        assert 'John Doe' in detailed
        assert 'born January 15, 2000' in detailed
        assert simple == 'John Doe'
        assert num == 'one'
        # Should NOT have semicolons for single child
        assert ';' not in detailed

    def test_children_formatting_two_children(self):
        """Test formatting of two children with proper 'and' conjunction"""
        children = [
            {'name': 'John Doe', 'dob': '2000-01-15'},
            {'name': 'Jane Doe', 'dob': '2002-03-20'}
        ]
        detailed, simple, num = format_children_list(children)

        assert 'John Doe, born January 15, 2000' in detailed
        assert 'Jane Doe, born March 20, 2002' in detailed
        assert ' and ' in detailed
        assert num == 'two'
        # Two children should use "and", not semicolons
        assert ';' not in detailed

    def test_children_formatting_multiple_children_with_semicolons(self, sample_children_data):
        """
        Test formatting of multiple children (3+) uses semicolons for clarity

        This is the core regression test for the October 2, 2025 bug.
        The bug produced: "Francis, Bartoszewicz 03/31/1982Victoria Hetzel..."

        After fix, should produce: "Francis Bartoszewicz, born March 31, 1982;
        Victoria Hetzel, born May 6, 1984; Brian Tanner, born November 20, 1981;
        and Bradley Tanner, born April 9, 1985"
        """
        children = sample_children_data
        detailed, simple, num = format_children_list(children)

        # Check that all children are present
        assert 'Francis Bartoszewicz' in detailed
        assert 'Victoria Hetzel' in detailed
        assert 'Brian Tanner' in detailed
        assert 'Bradley Tanner' in detailed

        # Check dates are formatted properly
        assert 'March 31, 1982' in detailed
        assert 'May 6, 1984' in detailed
        assert 'November 20, 1981' in detailed
        assert 'April 9, 1985' in detailed

        # CRITICAL: Must use semicolons to separate entries for readability
        assert ';' in detailed, "Multiple children should be separated by semicolons"

        # Should have 3 semicolons for 4 children (last one uses "and")
        assert detailed.count(';') == 3

        # Last child should be preceded by "and"
        assert 'and Bradley Tanner' in detailed

        # Verify not all jammed together (the original bug)
        # Count separators - should have clear separation
        separator_count = detailed.count(';') + detailed.count(' and ')
        assert separator_count >= 3, "Children must be properly separated"

        # Check simple list format
        assert 'Francis Bartoszewicz' in simple
        assert ', and ' in simple or ' and ' in simple

        # Check number word
        assert num == 'four'

    def test_children_no_dates(self):
        """Test children without birthdates still format properly"""
        children = [
            {'name': 'Child One'},
            {'name': 'Child Two'},
            {'name': 'Child Three'}
        ]
        detailed, simple, num = format_children_list(children)

        assert 'Child One' in detailed
        assert 'Child Two' in detailed
        assert 'Child Three' in detailed
        # Should still use semicolons for multiple entries
        assert ';' in detailed
        assert num == 'three'

    def test_empty_children_list(self):
        """Test empty children list returns expected defaults"""
        detailed, simple, num = format_children_list([])

        assert detailed == ''
        assert simple == ''
        assert num == 'no'

    def test_children_with_invalid_dates(self):
        """Test graceful handling of invalid date formats"""
        children = [
            {'name': 'Valid Child', 'dob': '2000-01-15'},
            {'name': 'Invalid Child', 'dob': 'invalid-date'},
            {'name': 'Another Valid', 'dob': '2002-03-20'}
        ]
        detailed, simple, num = format_children_list(children)

        # Valid dates should be formatted
        assert 'Valid Child, born January 15, 2000' in detailed
        assert 'Another Valid, born March 20, 2002' in detailed

        # Invalid date should still include the name
        assert 'Invalid Child' in detailed

        # Should still use semicolons
        assert ';' in detailed


@pytest.mark.regression
class TestArticleNumbering:
    """
    Regression test for article numbering consistency

    The bug was: inconsistent numbering like "ARTICLE II → ARTICLE 3"
    Should always use Roman numerals: I, II, III, IV, V, VI, VII

    Note: This requires access to the actual document generation,
    so this is a placeholder for when we add integration tests.
    """

    def test_article_numbering_placeholder(self):
        """Placeholder for article numbering test"""
        # TODO: Implement when we add document parsing tests
        # This would load a generated document and verify:
        # - All articles use Roman numerals
        # - No mixed formats (e.g., "ARTICLE 3")
        # - Sequential numbering is correct
        pass


@pytest.mark.regression
class TestAgeCalculation:
    """Test age calculation for trust provisions"""

    def test_calculate_age_valid_date(self):
        """Test age calculation with valid date"""
        dob = '2000-01-15'
        age = calculate_age(dob)
        # Age will depend on current date, but should be reasonable
        assert 20 <= age <= 30, f"Age {age} seems unreasonable for DOB {dob}"

    def test_calculate_age_empty_string(self):
        """Test age calculation with empty string returns 0"""
        assert calculate_age('') == 0

    def test_calculate_age_none(self):
        """Test age calculation with None returns 0"""
        assert calculate_age(None) == 0

    def test_calculate_age_invalid_format(self):
        """Test age calculation with invalid format returns 0"""
        assert calculate_age('invalid-date') == 0
        assert calculate_age('01/15/2000') == 0  # Wrong format
        assert calculate_age('2000-13-45') == 0  # Invalid date values

    def test_calculate_age_under_25_boundary(self):
        """Test the boundary condition for trust insertion (< 25)"""
        from datetime import datetime, timedelta

        # Create DOB for someone exactly 24 years old
        today = datetime.now()
        dob_24 = (today - timedelta(days=365*24)).strftime('%Y-%m-%d')
        age_24 = calculate_age(dob_24)

        # Should be under 25 (trust should be included)
        assert age_24 < 25, "24-year-old should trigger trust provision"

        # Create DOB for someone exactly 25 years old
        dob_25 = (today - timedelta(days=365*25 + 1)).strftime('%Y-%m-%d')
        age_25 = calculate_age(dob_25)

        # Should be 25 or older (trust should NOT be included)
        assert age_25 >= 25, "25-year-old should NOT trigger trust provision"
