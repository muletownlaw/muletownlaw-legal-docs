from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
import os

def replace_in_document(doc, replacements):
    """Replace all placeholders in the document"""
    for paragraph in doc.paragraphs:
        for placeholder, value in replacements.items():
            if placeholder in paragraph.text:
                # Replace inline with proper formatting preservation
                for run in paragraph.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, value)
    
    # Also check tables if any
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for placeholder, value in replacements.items():
                        if placeholder in paragraph.text:
                            for run in paragraph.runs:
                                if placeholder in run.text:
                                    run.text = run.text.replace(placeholder, value)

def generate_acp_document(data):
    """Generate Advanced Care Plan from template"""
    # Load the template from the same directory
    template_path = os.path.join(os.path.dirname(__file__), 'Advance_Care_Plan.docx')
    
    doc = Document(template_path)
    
    # Determine pronoun based on gender (if provided, default to he/she)
    pronoun = "he/she"  # Default if no gender provided
    if 'CLIENT_GENDER' in data:
        pronoun = "he" if data['CLIENT_GENDER'] == 'Male' else "she"
    
    # Define all replacements matching the correct template's placeholders
    replacements = {
        '{CLIENT NAME}': data['CLIENT_NAME'].upper(),
        '{CLIENT PRONOUN- he/she}': pronoun,
        '{NAME OF PERSON 1}': data['AGENT1_NAME'].upper(),
        '{RELATION 1 TO CLIENT}': data['AGENT1_RELATION'],
        '{NAME OF PERSON 2}': data['AGENT2_NAME'].upper(),
        '{RELATION 2 TO CLIENT}': data['AGENT2_RELATION'],
        '{MONTH}': data['EXEC_MONTH'],
        '{CURRENT YEAR}': data['EXEC_YEAR'],
    }
    
    # Replace in all paragraphs
    replace_in_document(doc, replacements)
    
    return doc

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Generate document
            doc = generate_acp_document(data)
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="ACP_{data["CLIENT_NAME"].replace(" ", "_")}.docx"')
            self.end_headers()
            self.wfile.write(buffer.getvalue())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_msg = {'error': str(e), 'type': type(e).__name__}
            self.wfile.write(json.dumps(error_msg).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
