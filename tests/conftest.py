"""
Pytest configuration and fixtures for document generator tests
"""
import pytest
import json
from datetime import datetime, timedelta


@pytest.fixture
def sample_client_data():
    """Basic client data for testing"""
    return {
        'CLIENT_NAME': 'Test Client',
        'CLIENT_GENDER': 'Female',
        'COUNTY': 'Maury',
        'EXECUTION_MONTH': 'October',
        'EXECUTION_YEAR': '2025'
    }


@pytest.fixture
def sample_married_client():
    """Married client data"""
    return {
        'CLIENT_NAME': 'Jane Doe',
        'CLIENT_GENDER': 'Female',
        'COUNTY': 'Maury',
        'IS_MARRIED': True,
        'SN_BENEFICIARY': 'John Doe',
        'SPOUSE_GENDER': 'Male',
        'EXECUTION_MONTH': 'October',
        'EXECUTION_YEAR': '2025'
    }


@pytest.fixture
def sample_unmarried_client():
    """Unmarried client data"""
    return {
        'CLIENT_NAME': 'Jane Smith',
        'CLIENT_GENDER': 'Female',
        'COUNTY': 'Maury',
        'IS_MARRIED': False,
        'EXECUTION_MONTH': 'October',
        'EXECUTION_YEAR': '2025'
    }


@pytest.fixture
def sample_children_data():
    """Sample children data matching October 2, 2025 bug scenario"""
    return [
        {'name': 'Francis Bartoszewicz', 'dob': '1982-03-31'},
        {'name': 'Victoria Hetzel', 'dob': '1984-05-06'},
        {'name': 'Brian Tanner', 'dob': '1981-11-20'},
        {'name': 'Bradley Tanner', 'dob': '1985-04-09'}
    ]


@pytest.fixture
def sample_children_with_minor():
    """Sample children including one under 25"""
    today = datetime.now()
    minor_dob = (today - timedelta(days=365*20)).strftime('%Y-%m-%d')  # 20 years old
    adult_dob = (today - timedelta(days=365*30)).strftime('%Y-%m-%d')  # 30 years old

    return [
        {'name': 'Adult Child', 'dob': adult_dob},
        {'name': 'Minor Child', 'dob': minor_dob}
    ]


@pytest.fixture
def sample_poa_data():
    """Sample POA data"""
    return {
        'CLIENT_NAME': 'Test Client',
        'CLIENT_GENDER': 'Male',
        'COUNTY': 'Maury',
        'AIF_NAME': 'Primary Agent',
        'AIF_RELATIONSHIP': 'spouse',
        'ALTERNATE_AIF_NAME': 'Alternate Agent',
        'ALTERNATE_AIF_RELATIONSHIP': 'sibling',
        'EXEC_MONTH': 'October',
        'EXEC_YEAR': '2025'
    }


@pytest.fixture
def sample_hcpoa_data():
    """Sample HCPOA data"""
    return {
        'CLIENT_NAME': 'Test Client',
        'CLIENT_GENDER': 'Female',
        'CLIENT_COUNTY': 'Maury',
        'PRIMARY_AGENT_NAME': 'Primary Agent',
        'PRIMARY_AGENT_RELATION': 'daughter',
        'ALTERNATE_AGENT_NAME': 'Alternate Agent',
        'ALTERNATE_AGENT_RELATION': 'son',
        'EXEC_MONTH': 'October',
        'EXEC_YEAR': '2025'
    }


@pytest.fixture
def sample_acp_data():
    """Sample ACP data"""
    return {
        'CLIENT_NAME': 'Test Client',
        'CLIENT_GENDER': 'Male',
        'PRIMARY_AGENT_NAME': 'Primary Agent',
        'PRIMARY_AGENT_RELATION': 'spouse',
        'ALTERNATE_AGENT_NAME': 'Alternate Agent',
        'ALTERNATE_AGENT_RELATION': 'child',
        'EXEC_MONTH': 'October',
        'EXEC_YEAR': '2025'
    }
