from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
import os
import sys

def find_template():
    """Find the POA template file in various possible locations"""
    # Possible locations
    possible_paths = [
        # Same directory as this file
        os.path.join(os.path.dirname(__file__), 'POA_TEMPLATE.docx'),
        # Relative to current working directory
        'POA_TEMPLATE.docx',
        'api/POA_TEMPLATE.docx',
        # Absolute paths that Vercel might use
        '/var/task/api/POA_TEMPLATE.docx',
        './api/POA_TEMPLATE.docx',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def replace_in_paragraph(paragraph, replacements):
    """Replace placeholders in a paragraph"""
    full_text = paragraph.text
    
    # Check if any placeholder exists
    has_placeholder = False
    for placeholder in replacements.keys():
        if placeholder in full_text:
            has_placeholder = True
            full_text = full_text.replace(placeholder, replacements[placeholder])
    
    if has_placeholder:
        # Clear all runs and set new text
        for run in paragraph.runs:
            run.text = ''
        if paragraph.runs:
            paragraph.runs[0].text = full_text
        else:
            paragraph.add_run(full_text)

def generate_poa_document(data):
    """Generate POA document from template"""
    
    # Find template
    template_path = find_template()
    
    if not template_path:
        # Create error document
        doc = Document()
        doc.add_paragraph("ERROR: Template file not found")
        doc.add_paragraph("Please upload POA_TEMPLATE.docx to the api/ folder")
        doc.add_paragraph("")
        doc.add_paragraph("Searched in:")
        doc.add_paragraph(f"- {os.path.dirname(__file__)}")
        doc.add_paragraph(f"- Current directory: {os.getcwd()}")
        doc.add_paragraph(f"- Files in current dir: {os.listdir('.')}")
        try:
            doc.add_paragraph(f"- Files in api/: {os.listdir('api')}")
        except:
            doc.add_paragraph("- Could not list api/ directory")
        return doc
    
    # Load template
    try:
        doc = Document(template_path)
    except Exception as e:
        # Create error document
        doc = Document()
        doc.add_paragraph(f"ERROR loading template: {str(e)}")
        return doc
    
    # Determine pronouns based on gender
    gender = data.get('CLIENT_GENDER', 'Male')
    if gender == 'Male':
        pronouns = {
            'subjective': 'he',
            'possessive': 'his', 
            'objective': 'him'
        }
    else:
        pronouns = {
            'subjective': 'she',
            'possessive': 'her',
            'objective': 'her'
        }
    
    # Define all replacements
    replacements = {
        '{CLIENT NAME}': data.get('CLIENT_NAME', ''),
        '{COUNTY}': data.get('COUNTY', ''),
        '{AIF RELATIONSHIP}': data.get('AIF_RELATIONSHIP', ''),
        '{AIF NAME}': data.get('AIF_NAME', ''),
        '{ALTERNATE AIF RELATIONSHIP}': data.get('ALTERNATE_AIF_RELATIONSHIP', ''),
        '{ALTERNATE AIF NAME}': data.get('ALTERNATE_AIF_NAME', ''),
        '{EXEC MONTH}': data.get('EXEC_MONTH', ''),
        '{EXEC YEAR}': data.get('EXEC_YEAR', ''),
        '{SUBJECTIVE PRONOUN}': pronouns['subjective'],
        '{POSSESSIVE PRONOUN}': pronouns['possessive'],
        '{OBJECTIVE PRONOUN}': pronouns['objective'],
        '{HE/SHE}': pronouns['subjective'],
        '{HIS/HER}': pronouns['possessive'],
        '{HIM/HER}': pronouns['objective'],
    }
    
    # Replace in all paragraphs
    for paragraph in doc.paragraphs:
        replace_in_paragraph(paragraph, replacements)
    
    # Replace in headers and footers
    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            replace_in_paragraph(paragraph, replacements)
        for paragraph in section.footer.paragraphs:
            replace_in_paragraph(paragraph, replacements)
    
    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_in_paragraph(paragraph, replacements)
    
    return doc

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Generate document
            doc = generate_poa_document(data)
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            # Get file content
            file_content = buffer.getvalue()
            
            # Get client name for filename
            client_name = data.get('CLIENT_NAME', 'Client').replace(' ', '_')
            filename = f'POA_{client_name}.docx'
            
            # Send response with proper headers - CRITICAL for .docx
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(file_content)))
            self.end_headers()
            
            # Write document
            self.wfile.write(file_content)
            
        except Exception as e:
            # Log error details
            import traceback
            error_detail = traceback.format_exc()
            
            # Return error
            error_response = json.dumps({
                'error': str(e),
                'type': type(e).__name__,
                'detail': error_detail,
                'cwd': os.getcwd(),
                'files': os.listdir('.') if os.path.exists('.') else []
            })
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(error_response.encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
