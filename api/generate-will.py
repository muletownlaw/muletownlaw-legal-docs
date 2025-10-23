from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
import re

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
                        run.text = run.text.replace(placeholder, str(value))
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for placeholder, value in replacements.items():
                        if placeholder in paragraph.text:
                            for run in paragraph.runs:
                                if placeholder in run.text:
                                    run.text = run.text.replace(placeholder, str(value))

def clean_markers(doc):
    """Remove all ## insertion markers"""
    for para in doc.paragraphs:
        if '##' in para.text:
            text = para.text
            # Remove markers
            text = re.sub(r'##[^#]*##', '', text)
            text = text.strip()
            
            if text:
                for run in para.runs:
                    run.text = ''
                if para.runs:
                    para.runs[0].text = text
            else:
                # Empty paragraph after removing marker
                for run in para.runs:
                    run.text = ''

def handle_unmarried(doc, is_married):
    """Handle married/unmarried conditional content"""
    if is_married:
        # Just remove markers
        clean_markers(doc)
        return
    
    # Unmarried - need to modify content
    for i, para in enumerate(doc.paragraphs):
        text = para.text
        
        # Handle married declaration with marker
        if '##Delete first sentence if unmarried##' in text:
            # Remove everything before the marker
            parts = text.split('##Delete first sentence if unmarried##')
            if len(parts) > 1:
                # Keep only what's after the marker
                new_text = parts[1].strip()
                for run in para.runs:
                    run.text = ''
                if para.runs and new_text:
                    para.runs[0].text = new_text
            else:
                # Just remove the marker
                for run in para.runs:
                    run.text = run.text.replace('##Delete first sentence if unmarried##', '')
        
        # Remove standalone married declarations
        elif 'I am married to' in text and '{CLIENT_SPOUSE_NAME}' not in text:
            for run in para.runs:
                run.text = ''
        
        # Fix spouse appointments that now have empty names
        elif ('I appoint my wife, ,' in text or 'I appoint my husband, ,' in text or 
              'my wife, , as Executor' in text.lower() or 'my husband, , as Executor' in text.lower()):
            # This is a spouse appointment with blank name - skip it
            for run in para.runs:
                run.text = ''

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
    words = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
             6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    return words.get(num, str(num))

def insert_new_article_clauses(doc, clauses_data):
    """Insert new article clauses after Article V and renumber"""
    # Find Article V end (start of Article VI or end of doc)
    article_v_end = None
    roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
    
    for i, para in enumerate(doc.paragraphs):
        if para.text.strip().startswith('ARTICLE V'):
            # Found Article V, now find where it ends
            for j in range(i + 1, len(doc.paragraphs)):
                if doc.paragraphs[j].text.strip().startswith('ARTICLE'):
                    article_v_end = j
                    break
            if article_v_end is None:
                article_v_end = len(doc.paragraphs)
            break
    
    if article_v_end is None:
        article_v_end = len(doc.paragraphs)
    
    # Load and insert clauses
    insertion_point = article_v_end
    for clause_file in clauses_data:
        clause_path = os.path.join(os.path.dirname(__file__), 'clauses', clause_file)
        try:
            clause_doc = Document(clause_path)
            # Insert at the specific position
            for para in clause_doc.paragraphs:
                if para.text.strip() and not para.text.strip().startswith('##'):
                    # Create new paragraph - we'll add content then reorganize
                    doc.add_paragraph(para.text, style=para.style)
        except Exception as e:
            print(f"Error loading clause {clause_file}: {e}")
    
    # Now renumber all articles
    roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
    article_num = 0
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if text.startswith('ARTICLE'):
            article_num += 1
            # Replace article number
            if '###' in text:
                new_text = text.replace('###', roman_numerals[article_num - 1] if article_num <= len(roman_numerals) else str(article_num))
            else:
                # Match any existing roman numeral and replace
                new_text = re.sub(r'ARTICLE [IVXLCDM]+', f'ARTICLE {roman_numerals[article_num - 1]}', text)
            
            for run in para.runs:
                run.text = ''
            if para.runs:
                para.runs[0].text = new_text

def generate_will_document(data):
    """Generate will from template with optional clauses"""
    template_path = os.path.join(os.path.dirname(__file__), 'Simple_Will.docx')
    doc = Document(template_path)
    
    # Determine if married
    is_married = bool(data.get('CLIENT_SPOUSE_NAME', '').strip())
    
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
    
    # Base replacements
    replacements = {
        '{CLIENT_NAME}': data.get('CLIENT_NAME', '').upper(),
        '{CLIENT_COUNTY}': data.get('CLIENT_COUNTY', 'Maury'),
        '{CLIENT_PRONOUN_SUBJECTIVE}': client_pronoun_subj,
        '{CLIENT_PRONOUN_POSSESSIVE}': client_pronoun_poss,
        '{CLIENT_SPOUSE_NAME}': data.get('CLIENT_SPOUSE_NAME', '').upper() if is_married else '',
        '{SPOUSE_TYPE}': spouse_type if is_married else '',
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
        '{NUMBER_OF_CHILDREN}': number_to_words(num_children),
        '{CHILDREN_LIST}': children_list,
        '{CHILD_OR_CHILDREN}': child_or_children,
        '{CONTINGENT_BENEFICIARY_NAME}': data.get('CONTINGENT_BENEFICIARY_NAME', '').upper(),
        '{CONTINGENT_BENEFICIARY_RELATION}': data.get('CONTINGENT_BENEFICIARY_RELATION', ''),
    }
    
    # Optional clause variables
    if data.get('INCLUDE_DISINHERITANCE'):
        replacements['{DISINHERITED_NAME}'] = data.get('DISINHERITED_NAME', '').upper()
        replacements['{DISINHERITED_RELATION}'] = data.get('DISINHERITED_RELATION', '')
    
    # Replace variables in main template
    replace_in_document(doc, replacements)
    
    # Handle married/unmarried content
    handle_unmarried(doc, is_married)
    
    # Insert new article clauses after Article V
    clauses_to_insert = []
    if data.get('INCLUDE_NO_CONTEST'):
        clauses_to_insert.append('No_Contest.docx')
    if data.get('INCLUDE_DISINHERITANCE'):
        clauses_to_insert.append('Love_And_Affection.docx')
    
    if clauses_to_insert:
        insert_new_article_clauses(doc, clauses_to_insert)
        # Replace variables in inserted clauses
        replace_in_document(doc, replacements)
    
    # Clean any remaining markers
    clean_markers(doc)
    
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
