from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
import os

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

def generate_acp_document(data):
    """Generate ACP from standardized template"""
    template_path = os.path.join(os.path.dirname(__file__), 'Advance_Care_Plan.docx')
    doc = Document(template_path)
    
    pronoun = data.get('CLIENT_PRONOUN', 'he' if data.get('CLIENT_GENDER') == 'Male' else 'she')
    
    # All possible placeholder variations including date fields
    replacements = {
        # Client info
        '{CLIENT_NAME}': data['CLIENT_NAME'].upper(),
        '{CLIENT_PRONOUN}': pronoun,
        '{CLIENT PRONOUN}': pronoun,  # Space variation
        '{CLIENT_GENDER}': data.get('CLIENT_GENDER', 'Male'),
        
        # Agent info with all variations
        '{PRIMARY_AGENT_NAME}': data['PRIMARY_AGENT_NAME'].upper(),
        '{PRIMARY AGENT NAME}': data['PRIMARY_AGENT_NAME'].upper(),
        '{PRIMARY_AGENT_RELATION}': data['PRIMARY_AGENT_RELATION'],
        '{PRIMARY AGENT RELATION}': data['PRIMARY_AGENT_RELATION'],
        '{PRIMARYAGENTRELATION}': data['PRIMARY_AGENT_RELATION'],
        
        '{ALTERNATE_AGENT_NAME}': data['ALTERNATE_AGENT_NAME'].upper(),
        '{ALTERNATE AGENT NAME}': data['ALTERNATE_AGENT_NAME'].upper(),
        '{ALTERNATE_AGENT_RELATION}': data['ALTERNATE_AGENT_RELATION'],
        '{ALTERNATE AGENT RELATION}': data['ALTERNATE_AGENT_RELATION'],
        '{ALTERNATEAGENTRELATION}': data['ALTERNATE_AGENT_RELATION'],
        
        # Date fields - multiple variations for both locations
        '{EXEC_MONTH}': data.get('EXEC_MONTH', 'October'),
        '{EXEC MONTH}': data.get('EXEC_MONTH', 'October'),
        '{MONTH}': data.get('EXEC_MONTH', 'October'),
        '{Month}': data.get('EXEC_MONTH', 'October'),
        '{month}': data.get('EXEC_MONTH', 'October'),
        
        '{EXEC_YEAR}': data.get('EXEC_YEAR', '2025'),
        '{EXEC YEAR}': data.get('EXEC_YEAR', '2025'),
        '{YEAR}': data.get('EXEC_YEAR', '2025'),
        '{Year}': data.get('EXEC_YEAR', '2025'),
        '{year}': data.get('EXEC_YEAR', '2025'),
        '{CURRENT_YEAR}': data.get('EXEC_YEAR', '2025'),
        '{CURRENT YEAR}': data.get('EXEC_YEAR', '2025'),
    }
    
    replace_in_document(doc, replacements)
    return doc

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            doc = generate_acp_document(data)
            
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="ACP_{data["CLIENT_NAME"].replace(" ", "_")}.docx"')
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
