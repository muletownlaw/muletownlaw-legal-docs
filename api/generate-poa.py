from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
import os
import re

def merge_runs_in_paragraph(paragraph):
    """Merge all runs in a paragraph to handle split placeholders"""
    if not paragraph.runs:
        return
    
    # Get full text
    full_text = paragraph.text
    
    # Clear all runs
    for run in paragraph.runs:
        run.text = ''
    
    # Put all text in first run, preserving its formatting
    if paragraph.runs:
        paragraph.runs[0].text = full_text

def replace_in_document(doc, replacements):
    """Replace all placeholders - handles split runs"""
    
    # First, merge runs in all paragraphs to consolidate text
    for paragraph in doc.paragraphs:
        merge_runs_in_paragraph(paragraph)
    
    # Also merge runs in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    merge_runs_in_paragraph(paragraph)
    
    # Now do replacements (runs are merged, so text is in single runs)
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

def generate_poa_document(data):
    """Generate POA from template"""
    template_path = os.path.join(os.path.dirname(__file__), 'POA.docx')
    doc = Document(template_path)
    
    replacements = {
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
        '{ATTORNEY_NAME}': data.get('ATTORNEY_NAME', 'Thomas M. Hutto'),
        '{AttorneyName}': data.get('ATTORNEY_NAME', 'Thomas M. Hutto'),
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
