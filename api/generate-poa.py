from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
import urllib.request
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Template URLs from Google Drive (update these with your actual URLs)
TEMPLATE_URLS = {
    'poa': 'https://drive.google.com/uc?export=download&id=YOUR_POA_TEMPLATE_FILE_ID',
    'will': 'https://drive.google.com/uc?export=download&id=YOUR_WILL_TEMPLATE_FILE_ID',
    'hcpoa': 'https://drive.google.com/uc?export=download&id=YOUR_HCPOA_TEMPLATE_FILE_ID',
    'acp': 'https://drive.google.com/uc?export=download&id=YOUR_ACP_TEMPLATE_FILE_ID'
}

def download_template(template_type):
    """Download template from Google Drive"""
    url = TEMPLATE_URLS.get(template_type)
    if not url:
        raise ValueError(f"Unknown template type: {template_type}")
    
    # Download template
    response = urllib.request.urlopen(url)
    template_bytes = response.read()
    
    # Load as Document
    return Document(BytesIO(template_bytes))

def replace_placeholders(doc, replacements):
    """Replace placeholders in document with actual values"""
    # Replace in paragraphs
    for paragraph in doc.paragraphs:
        for key, value in replacements.items():
            if key in paragraph.text:
                # Replace in runs to preserve formatting
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
    
    return doc

def generate_poa_document(data):
    """Generate POA document from Google Drive template"""
    # Download template
    doc = download_template('poa')
    
    # Prepare replacements
    replacements = {
        '{CLIENT_NAME}': data['CLIENT_NAME'].upper(),
        '{COUNTY}': data['COUNTY'],
        '{AIF_RELATIONSHIP}': data['AIF_RELATIONSHIP'],
        '{AIF_NAME}': data['AIF_NAME'].upper(),
        '{ALTERNATE_AIF_RELATIONSHIP}': data['ALTERNATE_AIF_RELATIONSHIP'],
        '{ALTERNATE_AIF_NAME}': data['ALTERNATE_AIF_NAME'].upper(),
        '{EXEC_MONTH}': data['EXEC_MONTH'].upper(),
        '{EXEC_YEAR}': data['EXEC_YEAR']
    }
    
    # Add pronouns based on gender
    if data['CLIENT_GENDER'] == 'Male':
        replacements['{PRONOUN_SUBJECTIVE}'] = 'he'
        replacements['{PRONOUN_POSSESSIVE}'] = 'his'
        replacements['{PRONOUN_OBJECTIVE}'] = 'him'
    else:
        replacements['{PRONOUN_SUBJECTIVE}'] = 'she'
        replacements['{PRONOUN_POSSESSIVE}'] = 'her'
        replacements['{PRONOUN_OBJECTIVE}'] = 'her'
    
    # Replace all placeholders
    doc = replace_placeholders(doc, replacements)
    
    return doc

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Generate document
            doc = generate_poa_document(data)
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="POA_{data["CLIENT_NAME"].replace(" ", "_")}.docx"')
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
