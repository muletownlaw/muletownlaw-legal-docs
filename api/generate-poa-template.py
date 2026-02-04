from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
import urllib.request
import sys
import os

# Add the api directory to path so we can import template_config
sys.path.insert(0, os.path.dirname(__file__))
from template_config import TEMPLATE_URLS

def download_template(url):
    """Download template from Google Drive"""
    try:
        print(f"[POA] Downloading template from: {url}")
        with urllib.request.urlopen(url) as response:
            template_bytes = response.read()
            print(f"[POA] Template downloaded: {len(template_bytes)} bytes")
            return BytesIO(template_bytes)
    except Exception as e:
        print(f"[POA] Template download failed: {e}")
        raise Exception(f"Failed to download template: {str(e)}")

def replace_placeholders(doc, data):
    """Replace placeholders in the document with actual data"""
    
    # Derive pronouns based on gender
    pronouns = {
        'he': 'he' if data['CLIENT_GENDER'] == 'Male' else 'she',
        'his': 'his' if data['CLIENT_GENDER'] == 'Male' else 'her',
        'him': 'him' if data['CLIENT_GENDER'] == 'Male' else 'her'
    }
    
    # Create replacement map
    replacements = {
        '{CLIENT_NAME}': data['CLIENT_NAME'].upper(),
        '{COUNTY}': data['COUNTY'],
        '{AIF_NAME}': data['AIF_NAME'].upper(),
        '{AIF_RELATIONSHIP}': data.get('AIF_RELATIONSHIP', ''),
        '{ALTERNATE_AIF_NAME}': data['ALTERNATE_AIF_NAME'].upper(),
        '{ALTERNATE_AIF_RELATIONSHIP}': data.get('ALTERNATE_AIF_RELATIONSHIP', ''),
        '{EXEC_MONTH}': data['EXEC_MONTH'].upper(),
        '{EXEC_YEAR}': data['EXEC_YEAR'],
        '{PRONOUN_SUBJECTIVE}': pronouns['he'],
        '{PRONOUN_POSSESSIVE}': pronouns['his'],
        '{PRONOUN_OBJECTIVE}': pronouns['him']
    }
    
    print(f"[POA] Replacing {len(replacements)} placeholders")
    
    # Replace in paragraphs
    for paragraph in doc.paragraphs:
        for key, value in replacements.items():
            if key in paragraph.text:
                # Replace inline while preserving formatting
                for run in paragraph.runs:
                    if key in run.text:
                        run.text = run.text.replace(key, value)
    
    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for key, value in replacements.items():
                        if key in paragraph.text:
                            for run in paragraph.runs:
                                if key in run.text:
                                    run.text = run.text.replace(key, value)
    
    # Replace in headers/footers
    for section in doc.sections:
        # Header
        for paragraph in section.header.paragraphs:
            for key, value in replacements.items():
                if key in paragraph.text:
                    for run in paragraph.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, value)
        
        # Footer
        for paragraph in section.footer.paragraphs:
            for key, value in replacements.items():
                if key in paragraph.text:
                    for run in paragraph.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, value)
    
    print("[POA] Placeholder replacement complete")
    return doc

def generate_poa_document(data):
    """Generate POA document from Google Drive template"""
    
    # Get template URL from config
    template_url = TEMPLATE_URLS['poa']
    
    # Download template from Google Drive
    template_buffer = download_template(template_url)
    
    # Open the template
    doc = Document(template_buffer)
    
    # Replace all placeholders with actual data
    doc = replace_placeholders(doc, data)
    
    return doc

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"[POA] Received request with keys: {list(data.keys())}")
            
            # Generate document
            doc = generate_poa_document(data)
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            print(f"[POA] Document generated: {len(buffer.getvalue())} bytes")
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="POA_{data["CLIENT_NAME"].replace(" ", "_")}.docx"')
            self.end_headers()
            self.wfile.write(buffer.getvalue())
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[POA ERROR] {error_trace}")
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e),
                'type': type(e).__name__,
                'traceback': error_trace
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
