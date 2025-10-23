from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
import os
import re

def replace_in_document(doc, replacements):
    """Replace all placeholders in the document - handles variations"""
    # Replace in paragraphs
    for paragraph in doc.paragraphs:
        for placeholder, value in replacements.items():
            # Try exact match first
            if placeholder in paragraph.text:
                for run in paragraph.runs:
                    if placeholder in run.text:
                        run.text = run.text.replace(placeholder, value)
            # Also try with spaces (common issue)
            placeholder_with_spaces = placeholder.replace('_', ' ')
            if placeholder_with_spaces in paragraph.text:
                for run in paragraph.runs:
                    if placeholder_with_spaces in run.text:
                        run.text = run.text.replace(placeholder_with_spaces, value)
    
    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for placeholder, value in replacements.items():
                        if placeholder in paragraph.text:
                            for run in paragraph.runs:
                                if placeholder in run.text:
                                    run.text = run.text.replace(placeholder, value)
                        placeholder_with_spaces = placeholder.replace('_', ' ')
                        if placeholder_with_spaces in paragraph.text:
                            for run in paragraph.runs:
                                if placeholder_with_spaces in run.text:
                                    run.text = run.text.replace(placeholder_with_spaces, value)

def generate_poa_document(data):
    """Generate POA from standardized template"""
    template_path = os.path.join(os.path.dirname(__file__), 'POA.docx')
    doc = Document(template_path)
    
    # All possible placeholder variations
    replacements = {
        # Standard format
        '{CLIENT_NAME}': data['CLIENT_NAME'].upper(),
        '{CLIENT_GENDER}': data.get('CLIENT_GENDER', 'Male'),
        '{CLIENT_COUNTY}': data['CLIENT_COUNTY'],
        '{PRIMARY_AGENT_NAME}': data['PRIMARY_AGENT_NAME'].upper(),
        '{PRIMARY_AGENT_RELATION}': data['PRIMARY_AGENT_RELATION'],
        '{PRIMARY_AGENT_COUNTY}': data.get('PRIMARY_AGENT_COUNTY', data['CLIENT_COUNTY']),
        '{ALTERNATE_AGENT_NAME}': data['ALTERNATE_AGENT_NAME'].upper(),
        '{ALTERNATE_AGENT_RELATION}': data['ALTERNATE_AGENT_RELATION'],
        '{ALTERNATE_AGENT_COUNTY}': data.get('ALTERNATE_AGENT_COUNTY', data['CLIENT_COUNTY']),
        '{EXEC_MONTH}': data.get('EXEC_MONTH', 'October'),
        '{EXEC_YEAR}': data.get('EXEC_YEAR', '2025'),
        # Attorney name variations
        '{ATTORNEY_NAME}': data.get('ATTORNEY_NAME', 'Thomas M. Hutto'),
        '{AttorneyName}': data.get('ATTORNEY_NAME', 'Thomas M. Hutto'),
        '{Attorney Name}': data.get('ATTORNEY_NAME', 'Thomas M. Hutto'),
        '{ATTY_NAME}': data.get('ATTORNEY_NAME', 'Thomas M. Hutto'),
    }
    
    replace_in_document(doc, replacements)
    return doc

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            doc = generate_poa_document(data)
            
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="POA_{data["CLIENT_NAME"].replace(" ", "_")}.docx"')
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
