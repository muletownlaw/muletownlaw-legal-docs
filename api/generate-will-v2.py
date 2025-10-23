from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
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

def load_clause_content(clause_filename):
    """Load clause content as text, skipping markers"""
    clause_path = os.path.join(os.path.dirname(__file__), 'clauses', clause_filename)
    try:
        clause_doc = Document(clause_path)
        lines = []
        for para in clause_doc.paragraphs:
            text = para.text.strip()
            if text and not text.startswith('##'):
                lines.append(text)
        return '\n\n'.join(lines)
    except:
        return ''

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
    """Generate will using marker-based template"""
    template_path = os.path.join(os.path.dirname(__file__), 'Simple_Will.docx')
    doc = Document(template_path)
    
    # Calculate derived values
    client_gender = data.get('CLIENT_GENDER', 'Male')
    is_married = bool(data.get('CLIENT_SPOUSE_NAME', '').strip())
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
    
    # Children
    children = data.get('children', [])
    num_children = len(children)
    children_list = format_children_list(children)
    child_or_children = 'child' if num_children == 1 else 'children'
    
    # Build replacements
    replacements = {
        '{CLIENT_NAME}': data.get('CLIENT_NAME', '').upper(),
        '{CLIENT_COUNTY}': data.get('CLIENT_COUNTY', 'Maury'),
        '{CLIENT_PRONOUN_SUBJECTIVE}': client_pronoun_subj,
        '{CLIENT_PRONOUN_POSSESSIVE}': client_pronoun_poss,
        '{CLIENT_SPOUSE_NAME}': data.get('CLIENT_SPOUSE_NAME', '').upper() if is_married else '',
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
        '{NUMBER_OF_CHILDREN}': number_to_words(num_children) if num_children > 0 else 'no',
        '{CHILDREN_LIST}': children_list,
        '{CHILD_OR_CHILDREN}': child_or_children,
        '{CONTINGENT_BENEFICIARY_NAME}': data.get('CONTINGENT_BENEFICIARY_NAME', '').upper(),
        '{CONTINGENT_BENEFICIARY_RELATION}': data.get('CONTINGENT_BENEFICIARY_RELATION', ''),
        '{DISINHERITED_NAME}': data.get('DISINHERITED_NAME', '').upper() if data.get('INCLUDE_DISINHERITANCE') else '',
        '{DISINHERITED_RELATION}': data.get('DISINHERITED_RELATION', '') if data.get('INCLUDE_DISINHERITANCE') else '',
    }
    
    # Step 1: Replace all variables
    replace_in_document(doc, replacements)
    
    # Step 2: Handle conditional married sections
    paragraphs_to_remove = []
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text
        
        # Handle ##IF_MARRIED## sections
        if '##IF_MARRIED##' in text:
            if is_married:
                # Remove markers, keep content
                for run in para.runs:
                    run.text = run.text.replace('##IF_MARRIED##', '').replace('##END_IF##', '')
            else:
                # Remove entire paragraph
                paragraphs_to_remove.append(i)
        
        # Handle ##Delete first sentence if unmarried##
        elif '##Delete first sentence if unmarried##' in text:
            if is_married:
                # Remove marker only
                for run in para.runs:
                    run.text = run.text.replace('##Delete first sentence if unmarried##', '')
            else:
                # Remove "I am married..." sentence, keep children part
                if 'I have' in text:
                    start_idx = text.find('I have')
                    new_text = text[start_idx:].replace('##Delete first sentence if unmarried##', '')
                    for run in para.runs:
                        run.text = ''
                    if para.runs:
                        para.runs[0].text = new_text
    
    # Remove marked paragraphs (do this backwards so indices don't shift)
    for i in reversed(paragraphs_to_remove):
        p = doc.paragraphs[i]._element
        p.getparent().remove(p)
    
    # Step 3: Handle clause insertions at markers
    clauses_to_insert = []
    
    # Article III clauses
    article_iii_clauses = []
    if data.get('INCLUDE_HANDWRITTEN_LIST'):
        article_iii_clauses.append(load_clause_content('Handwritten_List.docx'))
    if data.get('INCLUDE_DISINHERITANCE'):
        article_iii_clauses.append(load_clause_content('Love_And_Affection.docx'))
    if data.get('INCLUDE_REAL_ESTATE_DEBT'):
        article_iii_clauses.append(load_clause_content('Real_Estate_Debt.docx'))
    
    # New articles
    new_articles = []
    article_counter = 6  # Start at VI
    if data.get('INCLUDE_NO_CONTEST'):
        no_contest_content = load_clause_content('No_Contest.docx')
        new_articles.append(f"Article {article_counter} - No Contest\n\n{no_contest_content}")
        article_counter += 1
    
    # Replace markers with content
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        
        if text == '##INSERT_ARTICLE_III_CLAUSES##':
            # Replace with Article III clauses
            replacement = '\n\n'.join(article_iii_clauses) if article_iii_clauses else ''
            for run in para.runs:
                run.text = ''
            if para.runs and replacement:
                para.runs[0].text = replacement
            elif not replacement:
                # Remove empty marker paragraph
                p = para._element
                p.getparent().remove(p)
        
        elif text == '##INSERT_NEW_ARTICLES##':
            # Replace with new articles
            replacement = '\n\n'.join(new_articles) if new_articles else ''
            for run in para.runs:
                run.text = ''
            if para.runs and replacement:
                para.runs[0].text = replacement
            elif not replacement:
                # Remove empty marker paragraph
                p = para._element
                p.getparent().remove(p)
            
            # Now renumber subsequent articles
            renumber_from = i + 1
            for j in range(renumber_from, len(doc.paragraphs)):
                p_text = doc.paragraphs[j].text.strip()
                if p_text.startswith('Article '):
                    # Extract title
                    match = re.match(r'Article \w+ - (.+)', p_text)
                    if match:
                        title = match.group(1)
                        # Update to new number
                        for run in doc.paragraphs[j].runs:
                            if 'Article' in run.text:
                                run.text = f'Article {article_counter} - {title}'
                                article_counter += 1
                                break
    
    # Step 4: Fix unmarried executor appointment
    if not is_married:
        for para in doc.paragraphs:
            if 'appoint my' in para.text and ', ,' in para.text:
                for run in para.runs:
                    # Replace blank spouse with alternate executor
                    run.text = run.text.replace(
                        f'my {spouse_type}, ,',
                        replacements['{ALTERNATE_EXECUTOR_NAME}'] + ','
                    )
    
    # Step 5: Final cleanup - remove any remaining markers or fix spouse references
    for para in doc.paragraphs:
        text = para.text
        if '##' in text or ', ,' in text:
            for run in para.runs:
                # Remove any remaining markers
                run.text = run.text.replace('##', '')
                # Fix any remaining blank spouse references
                if not is_married:
                    run.text = run.text.replace(f'my {spouse_type}, ,', replacements['{ALTERNATE_EXECUTOR_NAME}'])
                    run.text = run.text.replace(f'my said {spouse_type}, ,', 'my children')
    
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
