from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
import re

def replace_placeholders(doc, data):
    """Replace placeholders in document with actual data"""
    
    # Mapping of template placeholders to data keys
    replacements = {
        '{CLIENT NAME}': data['CLIENT_NAME'].upper(),
        '{COUNTY}': data['COUNTY'],
        '{AIF NAME (usually the client\'s spouse)}': data['AIF_NAME'].upper() + ' as my attorney-in-fact. If my said ' + data['AIF_RELATIONSHIP'] + ' is unwilling or unable to serve in said capacity, then I appoint my ' + data['ALTERNATE_AIF_RELATIONSHIP'] + ', ' + data['ALTERNATE_AIF_NAME'].upper(),
        '{AIF RELATIONSHIP}': data['AIF_RELATIONSHIP'],
        '{ALTERNATE AIF NAME}': data['ALTERNATE_AIF_NAME'].upper(),
        '{ALTERNATE AIF RELATIONSHIP}': data['ALTERNATE_AIF_RELATIONSHIP'],
        '{CURRENT MONTH}': data['EXEC_MONTH'].upper(),
        '{YEAR}': data['EXEC_YEAR']
    }
    
    # Replace in paragraphs
    for para in doc.paragraphs:
        for key, value in replacements.items():
            if key in para.text:
                # Need to preserve formatting, so we replace in runs
                for run in para.runs:
                    if key in run.text:
                        run.text = run.text.replace(key, value)
    
    # Replace in tables (if any)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for key, value in replacements.items():
                        if key in para.text:
                            for run in para.runs:
                                if key in run.text:
                                    run.text = run.text.replace(key, value)
    
    # Replace in headers
    for section in doc.sections:
        header = section.header
        for para in header.paragraphs:
            for key, value in replacements.items():
                if key in para.text:
                    for run in para.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, value)
        
        # Replace in footers
        footer = section.footer
        for para in footer.paragraphs:
            for key, value in replacements.items():
                if key in para.text:
                    for run in para.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, value)
    
    return doc

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Load the template
            # Note: In production, you'd upload the template to your repo
            # For now, we'll create the document from scratch as fallback
            doc = self.create_document_from_scratch(data)
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Content-Disposition', f'attachment; filename="POA_{data["CLIENT_NAME"].replace(" ", "_")}.docx"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(buffer.getvalue())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def create_document_from_scratch(self, data):
        """Create POA document from scratch (fallback method)"""
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        doc = Document()
        
        # Set up document margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
        
        # Add header
        section = doc.sections[0]
        header = section.header
        header_para = header.paragraphs[0]
        header_para.text = "Prepared by:\nMuletown Law, P.C.\n1109 S Garden Street\nColumbia, TN 38401"
        header_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Add footer with page number
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
        
        # Title
        title = doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title.add_run("DURABLE GENERAL POWER OF ATTORNEY")
        run.bold = True
        run.font.size = Pt(14)
        doc.add_paragraph()
        
        # Determine pronouns
        pronouns = {
            'subjective': 'he' if data['CLIENT_GENDER'] == 'Male' else 'she',
            'possessive': 'his' if data['CLIENT_GENDER'] == 'Male' else 'her',
            'objective': 'him' if data['CLIENT_GENDER'] == 'Male' else 'her'
        }
        
        # Opening paragraph
        p = doc.add_paragraph()
        p.add_run(f"I, ").bold = False
        p.add_run(data['CLIENT_NAME'].upper()).bold = True
        p.add_run(f", a resident of ").bold = False
        p.add_run(f"{data['COUNTY']} County").bold = True
        p.add_run(f", Tennessee do hereby make, constitute and appoint my {data['AIF_RELATIONSHIP']}, ").bold = False
        p.add_run(data['AIF_NAME'].upper()).bold = True
        p.add_run(f" as my attorney-in-fact. If my said {data['AIF_RELATIONSHIP']} is unwilling or unable to serve in said capacity, then I appoint my {data['ALTERNATE_AIF_RELATIONSHIP']}, ").bold = False
        p.add_run(data['ALTERNATE_AIF_NAME'].upper()).bold = True
        p.add_run(", as my alternate attorney-in-fact under the Uniform Durable Power of Attorney Act (T.C.A. § 34-6-101, et seq.) and in my name and stead to:").bold = False
        doc.add_paragraph()
        
        # Add all the articles (abbreviated for space)
        self.add_article(doc, "I", "GENERAL AUTHORITY")
        doc.add_paragraph("1.\tGenerally, do, sign or perform in the principal's name, place and stead any act, deed, matter or thing whatsoever...")
        doc.add_paragraph()
        
        # Signature section
        p = doc.add_paragraph()
        p.add_run(f"WITNESS MY SIGNATURE THIS _________ DAY OF ").bold = False
        p.add_run(data['EXEC_MONTH'].upper()).bold = True
        p.add_run(", ").bold = False
        p.add_run(data['EXEC_YEAR']).bold = True
        p.add_run(".").bold = False
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Signature line
        p = doc.add_paragraph()
        p.add_run("_" * 50)
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.add_run(data['CLIENT_NAME'].upper()).bold = True
        
        return doc
    
    def add_article(self, doc, number, title):
        """Add article header"""
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Pt
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"{number}. {title.upper()}")
        run.bold = True
        run.font.size = Pt(12)
        run.font.small_caps = True
        doc.add_paragraph()
