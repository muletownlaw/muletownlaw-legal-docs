from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os
from datetime import datetime

def add_header_footer(doc, client_name):
    """Add header and footer to document"""
    section = doc.sections[0]
    header = section.header
    header_para = header.paragraphs[0]
    header_para.text = "Prepared by:\nMuletown Law, P.C.\n1109 S Garden Street\nColumbia, TN 38401"
    header_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Footer with page number
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
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
    """Load clause text from text file (not .docx)"""
    clause_path = os.path.join(os.path.dirname(__file__), 'clauses', clause_filename)
    try:
        with open(clause_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return None

def replace_in_document(doc, replacements):
    """Replace all placeholders in document"""
    for para in doc.paragraphs:
        for key, value in replacements.items():
            if key in para.text:
                para.text = para.text.replace(key, value)
    
    # Also replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for key, value in replacements.items():
                        if key in para.text:
                            para.text = para.text.replace(key, value)

def calculate_age(birth_date_str):
    """Calculate age from birth date string (MM/DD/YYYY)"""
    try:
        birth_date = datetime.strptime(birth_date_str, '%m/%d/%Y')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return 0

def insert_article_iii_clauses(doc, data):
    """Insert optional clauses into Article III in correct order"""
    # Find Article III in the document
    article_iii_index = None
    for i, para in enumerate(doc.paragraphs):
        if 'Article III - Disposition of Property' in para.text or 'ARTICLE III' in para.text:
            article_iii_index = i
            break
    
    if article_iii_index is None:
        return
    
    # Build list of clauses to insert in correct order
    clauses_to_insert = []
    
    # 1. Love and Affection (Disinheritance) - FIRST
    if data.get('INCLUDE_DISINHERITANCE'):
        clause_text = load_clause_text('LWT_-_Clause_-_Love_and_Affection.txt')
        if clause_text:
            # Replace variables in clause
            clause_text = clause_text.replace('(relation)', data.get('DISINHERITED_RELATION', ''))
            clause_text = clause_text.replace('________________', data.get('DISINHERITED_NAME', ''))
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
    
    # Find position after first beneficiary section (usually after "To My Spouse" or "To My Children")
    insert_position = article_iii_index + 4  # Default position
    
    # Look for better insertion point
    for i in range(article_iii_index, min(article_iii_index + 20, len(doc.paragraphs))):
        text = doc.paragraphs[i].text
        if 'Contingent Beneficiaries' in text or 'Article IV' in text:
            insert_position = i
            break
    
    # Insert clauses as separate paragraphs
    for clause_text in reversed(clauses_to_insert):  # Reverse because we're inserting at same position
        # Split clause into paragraphs if it contains newlines
        paragraphs = clause_text.split('\n\n') if '\n\n' in clause_text else [clause_text]
        for para_text in reversed(paragraphs):
            if para_text.strip():
                p = doc.paragraphs[insert_position]._element
                new_p = OxmlElement('w:p')
                new_p_text = OxmlElement('w:r')
                new_p_t = OxmlElement('w:t')
                new_p_t.text = para_text.strip()
                new_p_text.append(new_p_t)
                new_p.append(new_p_text)
                p.addnext(new_p)
        
        # Add spacing paragraph
        p = doc.paragraphs[insert_position]._element
        new_p = OxmlElement('w:p')
        p.addnext(new_p)

def insert_trust_for_minors(doc, data, children):
    """Insert trust for minor children if any child under 25"""
    # Check if any child is under 25
    has_minor = False
    for child in children:
        age = calculate_age(child.get('dob', ''))
        if age < 25:
            has_minor = True
            break
    
    if not has_minor and not data.get('FORCE_TRUST_MINORS'):
        return
    
    # Load trust template
    trust_text = load_clause_text('LWT_-_Trust_for_Minor_Children.txt')
    if not trust_text:
        return
    
    # Find Article VI or create it
    article_vi_index = None
    for i, para in enumerate(doc.paragraphs):
        if 'Article VI' in para.text or 'ARTICLE VI' in para.text:
            article_vi_index = i
            break
    
    # If Article VI not found, add it before Article on Executor
    if article_vi_index is None:
        for i, para in enumerate(doc.paragraphs):
            if 'Article IV - Appointment of Executor' in para.text or 'Executor' in para.text:
                # Insert Article VI header
                p = doc.paragraphs[i-1]._element
                
                # Add spacing
                new_p = OxmlElement('w:p')
                p.addnext(new_p)
                
                # Add header
                new_p2 = OxmlElement('w:p')
                new_p_text = OxmlElement('w:r')
                new_p_t = OxmlElement('w:t')
                new_p_t.text = "Article VI - Trust for Minor Children"
                new_p_text.append(new_p_t)
                new_p2.append(new_p_text)
                new_p.addnext(new_p2)
                
                article_vi_index = i
                break
    
    # Insert trust text
    if article_vi_index:
        paragraphs = trust_text.split('\n\n') if '\n\n' in trust_text else [trust_text]
        for para_text in reversed(paragraphs):
            if para_text.strip():
                p = doc.paragraphs[article_vi_index + 1]._element
                new_p = OxmlElement('w:p')
                new_p_text = OxmlElement('w:r')
                new_p_t = OxmlElement('w:t')
                new_p_t.text = para_text.strip()
                new_p_text.append(new_p_t)
                new_p.append(new_p_text)
                p.addnext(new_p)

def generate_will_document(data):
    """Generate Last Will and Testament with all features"""
    
    # Load template
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'will_template.docx')
    
    try:
        doc = Document(template_path)
    except:
        # If template doesn't exist, create basic document
        doc = Document()
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
    
    # Add header and footer
    add_header_footer(doc, data['CLIENT_NAME'])
    
    # Parse children data
    children = []
    if data.get('children'):
        children = json.loads(data['children']) if isinstance(data['children'], str) else data['children']
    
    # Build replacements dictionary
    replacements = {
        '{CLIENT_NAME}': data.get('CLIENT_NAME', ''),
        '{COUNTY}': data.get('COUNTY', ''),
        '{SN_BENEFICIARY}': data.get('SN_BENEFICIARY', ''),
        '{PRIMARY_EXECUTOR}': data.get('PRIMARY_EXECUTOR', ''),
        '{ALTERNATE_EXECUTOR}': data.get('ALTERNATE_EXECUTOR', ''),
        '{TRUSTEE_NAME}': data.get('TRUSTEE_NAME', ''),
        '{DISINHERITED_NAME}': data.get('DISINHERITED_NAME', ''),
        '{DISINHERITED_RELATION}': data.get('DISINHERITED_RELATION', ''),
        '{EXECUTION_MONTH}': data.get('EXECUTION_MONTH', ''),
        '{EXECUTION_YEAR}': data.get('EXECUTION_YEAR', ''),
    }
    
    # Add children to replacements
    if children:
        child_list = ', '.join([f"{child.get('name', '')}" for child in children])
        replacements['{CHILDREN_LIST}'] = child_list
        
        # Detailed children with birthdates
        detailed_children = []
        for child in children:
            detailed_children.append(f"{child.get('name', '')}, born {child.get('dob', '')}")
        replacements['{CHILDREN_DETAILED}'] = ', and '.join(detailed_children) if len(detailed_children) > 1 else detailed_children[0]
    
    # Pronouns
    if data.get('CLIENT_GENDER') == 'Male':
        replacements['{he/she}'] = 'he'
        replacements['{his/her}'] = 'his'
        replacements['{him/her}'] = 'him'
    else:
        replacements['{he/she}'] = 'she'
        replacements['{his/her}'] = 'her'
        replacements['{him/her}'] = 'her'
    
    # Step 1: Replace all variables in template
    replace_in_document(doc, replacements)
    
    # Step 2: Insert Article III clauses
    insert_article_iii_clauses(doc, data)
    
    # Step 3: Replace variables again (for variables in inserted clauses)
    replace_in_document(doc, replacements)
    
    # Step 4: Insert trust for minors if needed
    if children:
        insert_trust_for_minors(doc, data, children)
    
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
            doc_io = generate_will_document(data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="Will_{data["CLIENT_NAME"].replace(" ", "_")}.docx"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(doc_io.getvalue())
            
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
