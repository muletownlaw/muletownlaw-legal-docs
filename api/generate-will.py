from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
from docx.shared import Inches
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
from datetime import datetime
import re

def add_page_numbers(doc):
    """Add page numbers to footer"""
    for section in doc.sections:
        footer = section.footer
        footer_para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        footer_para.alignment = 1  # Center
        footer_para.text = "Page "
        run = footer_para.add_run()
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        run._r.append(fldChar1)
        instrText = OxmlElement('w:instrText')
        instrText.text = "PAGE"
        run._r.append(instrText)
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar2)

def load_clause_text(clause_filename):
    """Load clause text from text file"""
    clause_path = os.path.join(os.path.dirname(__file__), 'clauses', clause_filename)
    try:
        with open(clause_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading clause {clause_filename}: {e}")
        return None

def replace_in_runs(para, old_text, new_text):
    """Replace text while preserving formatting"""
    if old_text not in para.text:
        return
    
    # Get full text
    full_text = para.text
    new_full_text = full_text.replace(old_text, new_text)
    
    # Find all runs and their text
    runs = para.runs
    if not runs:
        return
    
    # Clear all run text
    for run in runs:
        run.text = ''
    
    # Put all text in first run to preserve its formatting
    if runs:
        runs[0].text = new_full_text

def replace_in_document(doc, replacements):
    """Replace all placeholders in document while preserving formatting"""
    for para in doc.paragraphs:
        para_text = para.text
        for key, value in replacements.items():
            if key in para_text:
                replace_in_runs(para, key, str(value))
    
    # Also replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    para_text = para.text
                    for key, value in replacements.items():
                        if key in para_text:
                            replace_in_runs(para, key, str(value))

def handle_conditional_blocks(doc, data):
    """Handle ##IF_MARRIED## and similar conditional blocks"""
    is_married = data.get('IS_MARRIED', True)
    
    paragraphs_to_remove = []
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text
        
        # Handle ##Delete first sentence if unmarried##
        if '##Delete first sentence if unmarried##' in text and not is_married:
            # Remove everything before this marker
            sentences = text.split('.')
            if len(sentences) > 1:
                # Keep everything after the marker
                new_text = text.split('##Delete first sentence if unmarried##')[1]
                para.text = new_text.strip()
        
        # Handle ##IF_MARRIED## blocks
        if '##IF_MARRIED##' in text and not is_married:
            paragraphs_to_remove.append(para)
        
        # Clean up any remaining ## markers
        if '##' in text:
            # Remove all ## markers
            cleaned = re.sub(r'##[^#]+##', '', text)
            if cleaned.strip():
                para.text = cleaned
            elif not cleaned.strip() and '##INSERT' not in text:
                paragraphs_to_remove.append(para)
    
    # Remove marked paragraphs
    for para in paragraphs_to_remove:
        p = para._element
        p.getparent().remove(p)

def insert_article_iii_clauses(doc, data):
    """Insert optional clauses at ##INSERT_ARTICLE_III_CLAUSES## marker"""
    # Find the insertion point
    insert_index = None
    for i, para in enumerate(doc.paragraphs):
        if '##INSERT_ARTICLE_III_CLAUSES##' in para.text:
            insert_index = i
            # Remove the marker paragraph
            p = para._element
            p.getparent().remove(p)
            break
    
    if insert_index is None:
        return
    
    # Build list of clauses to insert
    clauses_to_insert = []
    
    # 1. Love and Affection (Disinheritance) - FIRST
    if data.get('INCLUDE_DISINHERITANCE'):
        clause_text = load_clause_text('LWT_-_Clause_-_Love_and_Affection.txt')
        if clause_text:
            clause_text = clause_text.replace('{DISINHERITED_RELATION}', data.get('DISINHERITED_RELATION', ''))
            clause_text = clause_text.replace('{DISINHERITED_NAME}', data.get('DISINHERITED_NAME', ''))
            clauses_to_insert.append(clause_text)
    
    # 2. Handwritten List - SECOND
    if data.get('INCLUDE_HANDWRITTEN_LIST'):
        clause_text = load_clause_text('LWT_-_Clause_-_Handwritten_List.txt')
        if clause_text:
            clauses_to_insert.append(clause_text)
    
    # 3. Real Estate Debt - THIRD
    if data.get('INCLUDE_REAL_ESTATE_DEBT'):
        clause_text = load_clause_text('LWT_-_Clause_-_Real_Estate_Indebtedness.txt')
        if clause_text:
            clauses_to_insert.append(clause_text)
    
    # 4. No Contest - FOURTH
    if data.get('INCLUDE_NO_CONTEST'):
        clause_text = load_clause_text('LWT_-_Clause_-_No_Contest_Provision.txt')
        if clause_text:
            clauses_to_insert.append(clause_text)
    
    # Insert clauses
    for clause_text in clauses_to_insert:
        # Create new paragraph with Pleading Body style
        new_para = doc.add_paragraph(clause_text)
        try:
            new_para.style = 'Pleading Body'
        except:
            pass  # Style might not exist
        
        # Move paragraph to correct position
        new_para._element.getparent().remove(new_para._element)
        doc.paragraphs[insert_index]._element.addprevious(new_para._element)
        insert_index += 1
        
        # Add spacing
        spacing_para = doc.add_paragraph()
        spacing_para._element.getparent().remove(spacing_para._element)
        doc.paragraphs[insert_index]._element.addprevious(spacing_para._element)
        insert_index += 1

def insert_trust_for_minors(doc, data, children):
    """Insert trust for minors at ##INSERT_NEW_ARTICLES## marker if needed"""
    # Check if any child is under 25
    has_minor = False
    for child in children:
        age = calculate_age(child.get('dob', ''))
        if age < 25:
            has_minor = True
            break
    
    if not has_minor:
        return
    
    # Find the insertion point
    insert_index = None
    for i, para in enumerate(doc.paragraphs):
        if '##INSERT_NEW_ARTICLES##' in para.text:
            insert_index = i
            # Remove the marker
            p = para._element
            p.getparent().remove(p)
            break
    
    if insert_index is None:
        return
    
    # Load trust template
    trust_text = load_clause_text('LWT_-_Trust_for_Minor_Children.txt')
    if not trust_text:
        return
    
    # Replace trustee variable
    trust_text = trust_text.replace('{TRUSTEE_NAME}', data.get('TRUSTEE_NAME', ''))
    
    # Add Article header
    article_para = doc.add_paragraph('Article VI - Trust for Minor Children')
    try:
        article_para.style = 'Pleading Heading'
    except:
        pass
    
    article_para._element.getparent().remove(article_para._element)
    doc.paragraphs[insert_index]._element.addprevious(article_para._element)
    insert_index += 1
    
    # Add trust text paragraphs
    for paragraph_text in trust_text.split('\n\n'):
        if paragraph_text.strip():
            new_para = doc.add_paragraph(paragraph_text.strip())
            try:
                new_para.style = 'Pleading Body'
            except:
                pass
            
            new_para._element.getparent().remove(new_para._element)
            doc.paragraphs[insert_index]._element.addprevious(new_para._element)
            insert_index += 1

def calculate_age(dob_string):
    """Calculate age from birthdate string"""
    if not dob_string:
        return 0
    try:
        dob = datetime.strptime(dob_string, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except (ValueError, TypeError) as e:
        # If date parsing fails, return 0 (treat as no DOB)
        return 0

def format_children_list(children):
    """Format children for the will with proper readability"""
    if not children:
        return '', '', 'no'

    detailed_list = []
    simple_list = []

    for child in children:
        name = child.get('name', '')
        dob = child.get('dob', '')

        if name:
            simple_list.append(name)
            if dob:
                # Format date nicely
                try:
                    date_obj = datetime.strptime(dob, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%B %d, %Y')
                    detailed_list.append(f"{name}, born {formatted_date}")
                except (ValueError, TypeError) as e:
                    # If date parsing fails, just use the name
                    detailed_list.append(name)
            else:
                detailed_list.append(name)

    # Format detailed list with semicolons for better readability in legal documents
    # Example: "John Doe, born January 15, 2000; Jane Doe, born March 20, 2002; and Michael Doe, born June 10, 2005"
    if len(detailed_list) == 0:
        detailed = ''
    elif len(detailed_list) == 1:
        detailed = detailed_list[0]
    elif len(detailed_list) == 2:
        detailed = f"{detailed_list[0]} and {detailed_list[1]}"
    else:
        # Multiple children: use semicolons to separate entries for clarity
        detailed = '; '.join(detailed_list[:-1]) + f'; and {detailed_list[-1]}'

    # Format simple list with commas and "and" for the last item
    if len(simple_list) == 0:
        simple = ''
    elif len(simple_list) == 1:
        simple = simple_list[0]
    elif len(simple_list) == 2:
        simple = f"{simple_list[0]} and {simple_list[1]}"
    else:
        simple = ', '.join(simple_list[:-1]) + f', and {simple_list[-1]}'

    # Convert number to word
    num_words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
    if len(children) <= 10:
        num_word = num_words[len(children)]
    else:
        num_word = str(len(children))

    return detailed, simple, num_word

def generate_will_document(data):
    """Generate Last Will and Testament using the template"""
    
    # Load the actual template
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'will_template.docx')
    
    try:
        doc = Document(template_path)
    except Exception as e:
        return {'error': f'Could not load template: {str(e)}'}
    
    # Parse children data
    children = []
    if data.get('children'):
        children = json.loads(data['children']) if isinstance(data['children'], str) else data['children']
    
    # Format children
    children_detailed, children_simple, num_children_word = format_children_list(children)
    
    # Determine pronouns and titles
    is_male = data.get('CLIENT_GENDER', 'Male') == 'Male'
    spouse_is_male = data.get('SPOUSE_GENDER', 'Female') == 'Male'
    
    # Build replacements dictionary with the template's variable names
    replacements = {
        '{CLIENT_NAME}': data.get('CLIENT_NAME', ''),
        '{CLIENT_COUNTY}': data.get('COUNTY', ''),
        '{COUNTY}': data.get('COUNTY', ''),
        '{SPOUSE_NAME}': data.get('SPOUSE_NAME', ''),
        '{NUMBER_OF_CHILDREN}': str(len(children)),
        '{CHILDREN_LIST}': children_simple,
        '{SPOUSE_TYPE}': 'husband' if spouse_is_male else 'wife',
        '{CLIENT_PRONOUN_SUBJECTIVE}': 'he' if is_male else 'she',
        '{CLIENT_PRONOUN_POSSESSIVE}': 'his' if is_male else 'her',
        '{he/she}': 'he' if is_male else 'she',
        '{his/her}': 'his' if is_male else 'her',
        '{SPOUSE_PRONOUN}': 'he' if spouse_is_male else 'she',
        '{SPOUSE_PRONOUN_POSSESSIVE}': 'his' if spouse_is_male else 'her',
        '{TESTATOR_TITLE}': 'Testator' if is_male else 'Testatrix',
        '{EXECUTOR_TITLE}': 'Executor' if is_male else 'Executrix',
        '{PRIMARY_EXECUTOR}': data.get('PRIMARY_EXECUTOR', ''),
        '{ALTERNATE_EXECUTOR}': data.get('ALTERNATE_EXECUTOR', ''),
        '{ALTERNATE_EXECUTOR_NAME}': data.get('ALTERNATE_EXECUTOR', ''),
        '{ALTERNATE_EXECUTOR_RELATION}': data.get('ALTERNATE_EXECUTOR_RELATION', ''),
        '{ALTERNATE_EXECUTOR_COUNTY}': data.get('ALTERNATE_EXECUTOR_COUNTY', ''),
        '{ALTERNATE_EXECUTOR_STATE}': data.get('ALTERNATE_EXECUTOR_STATE', 'Tennessee'),
        '{CONTINGENT_BENEFICIARY_NAME}': data.get('CONTINGENT_BENEFICIARY_NAME', ''),
        '{CONTINGENT_BENEFICIARY_RELATION}': data.get('CONTINGENT_BENEFICIARY_RELATION', ''),
        '{EXEC_MONTH}': data.get('EXECUTION_MONTH', ''),
        '{EXEC_YEAR}': data.get('EXECUTION_YEAR', ''),
        '{EXECUTION_MONTH}': data.get('EXECUTION_MONTH', ''),
        '{EXECUTION_YEAR}': data.get('EXECUTION_YEAR', ''),
    }
    
    # For the family status line, use detailed list
    replacements['{NUM_CHILDREN}'] = f"{num_children_word} ({len(children)})" if children else "no"

    # If children exist, build the detailed description
    if children:
        replacements['{CHILDREN_DESCRIPTION}'] = children_detailed
        replacements['{CHILDREN_DETAILED}'] = children_detailed
    else:
        replacements['{CHILDREN_DESCRIPTION}'] = ''
        replacements['{CHILDREN_DETAILED}'] = ''
    
    # Step 1: Handle conditional blocks
    handle_conditional_blocks(doc, data)
    
    # Step 2: Replace all variables
    replace_in_document(doc, replacements)
    
    # Step 3: Insert Article III clauses
    insert_article_iii_clauses(doc, data)
    
    # Step 4: Insert trust for minors if needed
    if children:
        insert_trust_for_minors(doc, data, children)
    
    # Step 5: Add page numbers if not already there
    add_page_numbers(doc)
    
    # Save to BytesIO
    doc_io = BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    
    return doc_io

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Generate document
            result = generate_will_document(data)
            
            if isinstance(result, dict) and 'error' in result:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="Will_{data.get("CLIENT_NAME", "Document").replace(" ", "_")}.docx"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(result.getvalue())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = json.dumps({'error': str(e)})
            self.wfile.write(error_response.encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
