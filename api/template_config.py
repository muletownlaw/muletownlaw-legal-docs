# Template URLs Configuration
# Update these URLs when you upload new templates to Google Drive
# 
# How to get the FILE_ID:
# 1. Right-click file in Google Drive → Share → Copy link
# 2. Link looks like: https://drive.google.com/file/d/FILE_ID_HERE/view?usp=sharing
# 3. Copy the FILE_ID_HERE part
# 4. Use format: https://drive.google.com/uc?export=download&id=FILE_ID_HERE

TEMPLATE_URLS = {
    # Power of Attorney Template
    'poa': 'https://docs.google.com/document/d/1t1vfNzq1Ri6q7LqwM2-vmRtQm9i2wOY0/export?format=docx',
    
    # Last Will and Testament Template
    'will': 'https://drive.google.com/uc?export=download&id=1HEP_Zb9IZ8qxmM8dRupzd3HeG7a8Ecka',
    
    # Healthcare Power of Attorney Template
    'hcpoa': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_YOUR_HCPOA_FILE_ID',
    
    # Advance Care Plan Template
    'acp': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_YOUR_ACP_FILE_ID',
    
    # Additional clause templates
    'handwritten_list': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_FILE_ID',
    'love_affection': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_FILE_ID',
    'no_contest': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_FILE_ID',
    'real_estate_debt': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_FILE_ID',
    'sell_real_estate': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_FILE_ID',
    'guardian': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_FILE_ID',
    'trust_basic': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_FILE_ID',
    'trust_sprinkling': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_FILE_ID',
    'special_needs': 'https://drive.google.com/uc?export=download&id=REPLACE_WITH_FILE_ID'
}

# Placeholder format used in templates
# Use these exact placeholders in your Word templates
PLACEHOLDERS = {
    'client_name': '{CLIENT_NAME}',
    'client_gender': '{CLIENT_GENDER}',
    'spouse_name': '{SN_BENEFICIARY}',
    'spouse_gender': '{SN_BENEFICIARY_GENDER}',
    'county': '{COUNTY}',
    'executor_primary': '{PRIMARY_EXECUTOR}',
    'executor_alternate': '{ALTERNATE_EXECUTOR}',
    'exec_month': '{EXEC_MONTH}',
    'exec_year': '{EXEC_YEAR}',
    'exec_day': '{EXEC_DAY}',
    'aif_name': '{AIF_NAME}',
    'aif_relationship': '{AIF_RELATIONSHIP}',
    'alternate_aif_name': '{ALTERNATE_AIF_NAME}',
    'alternate_aif_relationship': '{ALTERNATE_AIF_RELATIONSHIP}',
    'pronoun_he_she': '{PRONOUN_SUBJECTIVE}',
    'pronoun_his_her': '{PRONOUN_POSSESSIVE}',
    'pronoun_him_her': '{PRONOUN_OBJECTIVE}'
}
