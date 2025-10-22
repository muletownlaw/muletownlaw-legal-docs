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

def generate_hcpoa_document(data):
    """Generate Healthcare POA from template"""
    # Load the template from the same directory
    template_path = os.path.join(os.path.dirname(__file__), 'HCPOA.docx')
    
    doc = Document(template_path)
    
    # Define all replacements matching YOUR template's placeholders
    replacements = {
        '{CLIENT NAME}': data['CLIENT_NAME'].upper(),
        '{CLIENT COUNTY}': data['COUNTY'],
        '{AIF NAME}': data['AGENT1_NAME'].upper(),
        '{AIF RELATION TO CLIENT}': data['AGENT1_RELATION'],
        '{AIF COUNTY}': data['AGENT1_COUNTY'],
        '{ALTERNATE AIF NAME}': data['AGENT2_NAME'].upper(),
        '{ALTERNATE AIF RELATION TO CLIENT}': data['AGENT2_RELATION'],
        '{ALTERNATE AIF COUNTY}': data['AGENT2_COUNTY'],
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
            doc = generate_hcpoa_document(data)
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="HCPOA_{data["CLIENT_NAME"].replace(" ", "_")}.docx"')
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
