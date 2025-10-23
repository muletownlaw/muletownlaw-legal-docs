from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
from datetime import datetime

def merge_runs_in_paragraph(paragraph):
    """Merge all runs to handle split placeholders"""
    if not paragraph.runs:
        return
    full_text = paragraph.text
    for run in paragraph.runs:
        run.text = ''
    if paragraph.runs:
        paragraph.runs[0].text = full_text

def replace_in_document(doc, replacements):
    """Replace all placeholders in document"""
    # Merge runs first
    for paragraph in doc.paragraphs:
        merge_runs_in_paragraph(paragraph)
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    merge_runs_in_paragraph(paragraph)
    
    # Do replacements
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

def insert_clause(main_doc, clause_filename):
    """Insert a clause document at the end of the main document"""
    clause_path = os.path.join(os.path.dirname(__file__), 'clauses', clause_filename)
    
    try:
        clause_doc = Document(clause_path)
        
        # Copy paragraphs from clause to main document
        for para in clause_doc.paragraphs:
            # Skip empty paragraphs and insertion markers
            if para.text.strip() and not para.text.strip().startswith('##'):
                new_para = main_doc.add_paragraph(para.text, style=para.style)
                # Copy formatting
                new_para.alignment = para.alignment
                if para.runs:
                    for run in para.runs:
                        if run.text:
                            new_run = new_para.runs[0] if new_para.runs else new_para.add_run(run.text)
                            new_run.bold = run.bold
                            new_run.italic = run.italic
        
        # Copy tables from clause if any
        for table in clause_doc.tables:
            # Create new table in main doc
            new_table = main_doc.add_table(rows=len(table.rows), cols=len(table.columns))
            for i, row in enumerate(table.rows):
                for j, cell in enumerate(row.cells):
                    new_table.rows[i].cells[j].text = cell.text
        
        return True
    except Exception as e:
        print(f"Error inserting clause {clause_filename}: {e}")
        return False

def format_children_list(children):
    """Format children array into text"""
    if not children:
        return ""
    
    if len(children) == 1:
        child = children[0]
        return f"{child['name']}, born {child['dob']}"
    
    result = []
    for i, child in enumerate(children):
        if i == len(children) - 1:
            result.append(f"and {child['name']}, born {child['dob']}")
        else:
            result.append(f"{child['name']}, born {child['dob']}")
    
    return ", ".join(result)

def number_to_words(num):
    """Convert number to words"""
    words = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    if num <= 10:
        return words[num - 1]
    return str(num)

def generate_will_document(data):
    """Generate will from template with optional clauses"""
    template_path = os.path.join(os.path.dirname(__file__), 'Simple_Will.docx')
    doc = Document(template_path)
    
    # Calculate derived values
    client_gender = data.get('CLIENT_GENDER', 'Male')
    spouse_gender = 'Female' if client_gender == 'Male' else 'Male'
    
    # Pronouns
    if client_gender == 'Male':
        client_pronoun_subj = 'he'
        client_pronoun_poss = 'his'
        testator_title = 'Testator'
        executor_title = 'Executor'
        spouse_type = 'wife'
    else:
        client_pronoun_subj = 'she'
        client_pronoun_poss = 'her'
        testator_title = 'Testatrix'
        executor_title = 'Executrix'
        spouse_type = 'husband'
    
    if spouse_gender == 'Male':
        spouse_pronoun_subj = 'he'
        spouse_pronoun_poss = 'his'
    else:
        spouse_pronoun_subj = 'she'
        spouse_pronoun_poss = 'her'
    
    # Children formatting
    children = data.get('children', [])
    num_children = len(children)
    children_list = format_children_list(children)
    child_or_children = 'child' if num_children == 1 else 'children'
    children_pronoun_subj = 'he' if num_children == 1 and children[0].get('gender') == 'Male' else 'she' if num_children == 1 else 'they'
    children_pronoun_poss = 'his' if num_children == 1 and children[0].get('gender') == 'Male' else 'her' if num_children == 1 else 'their'
    
    # Base replacements
    replacements = {
        '{CLIENT_NAME}': data.get('CLIENT_NAME', '').upper(),
        '{CLIENT_COUNTY}': data.get('CLIENT_COUNTY', 'Maury'),
        '{CLIENT_PRONOUN_SUBJECTIVE}': client_pronoun_subj,
        '{CLIENT_PRONOUN_POSSESSIVE}': client_pronoun_poss,
        '{CLIENT_SPOUSE_NAME}': data.get('CLIENT_SPOUSE_NAME', '').upper(),
        '{SPOUSE_TYPE}': spouse_type,
        '{SPOUSE_PRONOUN_SUBJECTIVE}': spouse_pronoun_subj,
        '{SPOUSE_PRONOUN_POSSESSIVE}': spouse_pronoun_poss,
        '{TESTATOR_TITLE}': testator_title,
        '{EXECUTOR_TITLE}': executor_title,
        '{ALTERNATE_EXECUTOR_NAME}': data.get('ALTERNATE_EXECUTOR_NAME', '').upper(),
        '{ALTERNATE_EXECUTOR_RELATION}': data.get('ALTERNATE_EXECUTOR_RELATION', ''),
        '{ALTERNATE_EXECUTOR_COUNTY}': data.get('ALTERNATE_EXECUTOR_COUNTY', data.get('CLIENT_COUNTY', 'Maury')),
        '{ALTERNATE_EXECUTOR_STATE}': data.get('ALTERNATE_EXECUTOR_STATE', 'Tennessee'),
        '{EXEC_MONTH}': data.get('EXEC_MONTH', 'October'),
        '{EXEC_YEAR}': data.get('EXEC_YEAR', '2025'),
        '{NUMBER_OF_CHILDREN}': number_to_words(num_children) if num_children > 0 else '',
        '{CHILDREN_LIST}': children_list,
        '{CHILD_OR_CHILDREN}': child_or_children,
        '{CHILDREN_PRONOUN_SUBJECTIVE}': children_pronoun_subj,
        '{CHILDREN_PRONOUN_POSSESSIVE}': children_pronoun_poss,
        '{CONTINGENT_BENEFICIARY_NAME}': data.get('CONTINGENT_BENEFICIARY_NAME', '').upper(),
        '{CONTINGENT_BENEFICIARY_RELATION}': data.get('CONTINGENT_BENEFICIARY_RELATION', ''),
    }
    
    # Optional clause variables
    if data.get('INCLUDE_DISINHERITANCE'):
        replacements['{DISINHERITED_NAME}'] = data.get('DISINHERITED_NAME', '').upper()
        replacements['{DISINHERITED_RELATION}'] = data.get('DISINHERITED_RELATION', '')
    
    if data.get('INCLUDE_TRUST'):
        replacements['{TRUSTEE_NAME}'] = data.get('TRUSTEE_NAME', '').upper()
        replacements['{TRUSTEE_RELATIONSHIP}'] = data.get('TRUSTEE_RELATIONSHIP', '')
        replacements['{ALTERNATE_TRUSTEE_NAME}'] = data.get('ALTERNATE_TRUSTEE_NAME', '').upper()
        replacements['{TRUST_DISTRIBUTION_AGE}'] = str(data.get('TRUST_DISTRIBUTION_AGE', '25'))
        replacements['{TRUST_DISTRIBUTION_AGE_TEXT}'] = data.get('TRUST_DISTRIBUTION_AGE_TEXT', 'Twenty-Five')
        replacements['{RESIDUARY_BENEFICIARY_NAME}'] = data.get('RESIDUARY_BENEFICIARY_NAME', '').upper()
        replacements['{RESIDUARY_BENEFICIARY_RELATION}'] = data.get('RESIDUARY_BENEFICIARY_RELATION', '')
    
    if data.get('INCLUDE_GUARDIAN'):
        replacements['{PRIMARY_GUARDIAN_NAME}'] = data.get('PRIMARY_GUARDIAN_NAME', '').upper()
        replacements['{PRIMARY_GUARDIAN_RELATION}'] = data.get('PRIMARY_GUARDIAN_RELATION', '')
        replacements['{ALTERNATE_GUARDIAN_1_NAME}'] = data.get('ALTERNATE_GUARDIAN_1_NAME', '').upper()
        replacements['{ALTERNATE_GUARDIAN_1_RELATION}'] = data.get('ALTERNATE_GUARDIAN_1_RELATION', '')
        replacements['{ALTERNATE_GUARDIAN_2_NAME}'] = data.get('ALTERNATE_GUARDIAN_2_NAME', '').upper()
        replacements['{ALTERNATE_GUARDIAN_2_RELATION}'] = data.get('ALTERNATE_GUARDIAN_2_RELATION', '')
    
    if data.get('INCLUDE_SPECIAL_NEEDS'):
        sn_gender = data.get('SPECIAL_NEEDS_BENEFICIARY_GENDER', 'Male')
        sn_pronoun = 'he' if sn_gender == 'Male' else 'she'
        replacements['{SPECIAL_NEEDS_BENEFICIARY_NAME}'] = data.get('SPECIAL_NEEDS_BENEFICIARY_NAME', '').upper()
        replacements['{SPECIAL_NEEDS_BENEFICIARY_RELATION}'] = data.get('SPECIAL_NEEDS_BENEFICIARY_RELATION', '')
        replacements['{SPECIAL_NEEDS_BENEFICIARY_PRONOUN_SUBJECTIVE}'] = sn_pronoun
    
    # Replace variables in main template
    replace_in_document(doc, replacements)
    
    # Handle conditional content - remove unmarried text if married
    if data.get('CLIENT_SPOUSE_NAME'):
        # Married - keep spouse references
        pass
    else:
        # Unmarried - remove spouse sentence
        for para in doc.paragraphs:
            if '##Delete first sentence if unmarried##' in para.text:
                # Find and remove the married sentence
                text = para.text
                if 'I am married to' in text:
                    # Remove everything before the marker
                    marker_pos = text.find('##Delete first sentence if unmarried##')
                    if marker_pos > 0:
                        # Keep everything after marker, remove marker
                        new_text = text[marker_pos:].replace('##Delete first sentence if unmarried##', '')
                        for run in para.runs:
                            run.text = ''
                        if para.runs:
                            para.runs[0].text = new_text.strip()
    
    # Insert optional clauses
    if data.get('INCLUDE_HANDWRITTEN_LIST'):
        insert_clause(doc, 'Handwritten_List.docx')
    
    if data.get('INCLUDE_DISINHERITANCE'):
        insert_clause(doc, 'Love_And_Affection.docx')
    
    if data.get('INCLUDE_NO_CONTEST'):
        insert_clause(doc, 'No_Contest.docx')
    
    if data.get('INCLUDE_REAL_ESTATE_DEBT'):
        insert_clause(doc, 'Real_Estate_Debt.docx')
    
    if data.get('INCLUDE_SELL_REAL_ESTATE'):
        insert_clause(doc, 'Sell_Real_Estate.docx')
    
    if data.get('INCLUDE_SPECIFIC_BEQUESTS'):
        insert_clause(doc, 'Specific_Bequests.docx')
        replace_in_document(doc, replacements)  # Replace variables in inserted clause
    
    if data.get('INCLUDE_TRUST'):
        trust_type = data.get('TRUST_TYPE', 'basic')
        if trust_type == 'basic':
            insert_clause(doc, 'Trust_Basic.docx')
        elif trust_type == 'sprinkling_standard':
            insert_clause(doc, 'Trust_Sprinkling_Standard.docx')
        elif trust_type == 'sprinkling_complex':
            insert_clause(doc, 'Trust_Sprinkling_Complex.docx')
        elif trust_type == 'spouse_lifetime':
            insert_clause(doc, 'Trust_Spouse_Lifetime.docx')
        elif trust_type == 'special_needs':
            insert_clause(doc, 'Trust_Special_Needs.docx')
        
        # Replace variables in trust clauses
        replace_in_document(doc, replacements)
    
    # Final pass to replace any remaining variables
    replace_in_document(doc, replacements)
    
    return doc

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            doc = generate_will_document(data)
            
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            client_name = data.get('CLIENT_NAME', 'Client').replace(' ', '_')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="Will_{client_name}.docx"')
            self.end_headers()
            self.wfile.write(buffer.getvalue())
            
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
