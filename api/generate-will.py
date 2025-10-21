from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_UNDERLINE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_header_footer(doc, client_name):
    """Add header and footer to document"""
    section = doc.sections[0]
    header = section.header
    header_para = header.paragraphs[0]
    header_para.text = "Prepared by:\nMuletown Law, P.C.\n1109 S Garden Street\nColumbia, TN 38401"
    header_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Footer with page number
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

def generate_will_document(data):
    """Generate Last Will and Testament document"""
    doc = Document()
    
    # Set up document margins
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    
    # Add header/footer
    add_header_footer(doc, data.get('clientName', ''))
    
    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("LAST WILL AND TESTAMENT")
    title_run.bold = True
    title_run.font.size = Pt(14)
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_run = subtitle.add_run(f"OF {data.get('clientName', '').upper()}")
    subtitle_run.bold = True
    subtitle_run.font.size = Pt(12)
    
    doc.add_paragraph()  # Spacing
    
    # Article I - Introduction
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ARTICLE I")
    run.bold = True
    doc.add_paragraph()
    
    intro_text = f"I, {data.get('clientName', '')}, a resident of {data.get('county', '')} County, Tennessee, being of sound mind and disposing memory, do hereby make, publish and declare this to be my Last Will and Testament, hereby revoking all former Wills and Codicils made by me."
    doc.add_paragraph(intro_text)
    doc.add_paragraph()
    
    # Article II - Executor
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ARTICLE II - EXECUTOR")
    run.bold = True
    doc.add_paragraph()
    
    executor_text = f"I hereby nominate and appoint {data.get('executor', '')} as Executor of this my Last Will and Testament."
    doc.add_paragraph(executor_text)
    
    if data.get('alternateExecutor'):
        alt_text = f"If {data.get('executor', '')} is unable or unwilling to serve, I nominate and appoint {data.get('alternateExecutor', '')} as alternate Executor."
        doc.add_paragraph(alt_text)
    
    doc.add_paragraph()
    
    # Article III - Debts and Expenses
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ARTICLE III - DEBTS AND EXPENSES")
    run.bold = True
    doc.add_paragraph()
    
    debts_text = "I direct my Executor to pay all of my just debts, funeral expenses, and costs of administration as soon as practicable after my death."
    doc.add_paragraph(debts_text)
    doc.add_paragraph()
    
    # Article IV - Disposition of Property
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("ARTICLE IV - DISPOSITION OF PROPERTY")
    run.bold = True
    doc.add_paragraph()
    
    # Specific bequests
    if data.get('specificBequests'):
        doc.add_paragraph("A. Specific Bequests").bold = True
        for bequest in data.get('specificBequests', []):
            bequest_text = f"I give and bequeath {bequest.get('item', '')} to {bequest.get('beneficiary', '')}."
            doc.add_paragraph(bequest_text)
        doc.add_paragraph()
    
    # Residuary estate
    doc.add_paragraph("B. Residuary Estate").bold = True
    residuary_text = f"I give, devise and bequeath all the rest, residue and remainder of my estate, both real and personal, of whatsoever kind and wheresoever situated, to {data.get('residuaryBeneficiary', '')}."
    doc.add_paragraph(residuary_text)
    
    doc.add_paragraph()
    
    # Signature section
    doc.add_paragraph()
    doc.add_paragraph()
    sig_line = doc.add_paragraph("_" * 40)
    sig_line.alignment = WD_ALIGN_PARAGRAPH.LEFT
    sig_name = doc.add_paragraph(data.get('clientName', ''))
    sig_name.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Witness section
    witness_intro = doc.add_paragraph("The foregoing instrument was signed, sealed, published and declared by the above-named Testator as and for their Last Will and Testament in our presence, and we, at their request and in their presence, and in the presence of each other, have hereunto subscribed our names as witnesses this _____ day of _____________, 20___.")
    doc.add_paragraph()
    
    # Two witness signature blocks
    for i in range(1, 3):
        doc.add_paragraph(f"Witness {i}:")
        doc.add_paragraph("_" * 40)
        doc.add_paragraph("Printed Name: _" * 20)
        doc.add_paragraph("Address: _" * 25)
        doc.add_paragraph()
    
    return doc

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST request to generate Will document"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Generate document
            doc = generate_will_document(data)
            
            # Save to BytesIO
            doc_bytes = BytesIO()
            doc.save(doc_bytes)
            doc_bytes.seek(0)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Disposition', f'attachment; filename="Will_{data.get("clientName", "Document").replace(" ", "_")}.docx"')
            self.end_headers()
            self.wfile.write(doc_bytes.read())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = json.dumps({'error': str(e)})
            self.wfile.write(error_response.encode())
