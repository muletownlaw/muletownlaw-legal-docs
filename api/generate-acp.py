from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_header_footer(doc, client_name):
    """Add header and footer to document"""
    section = doc.sections[0]
    
    # Header
    header = section.header
    header_para = header.paragraphs[0]
    header_para.text = "MULETOWN LAW, P.C.\n1109 S Garden Street\nColumbia, TN 38401\n(931) 548-7051"
    header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in header_para.runs:
        run.font.size = Pt(10)
    
    # Footer
    footer = section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = f"Advance Care Plan - {client_name}"
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in footer_para.runs:
        run.font.size = Pt(10)

def generate_acp_document(data):
    """Generate Advanced Care Plan document"""
    doc = Document()
    
    # Set up margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # Add header and footer
    add_header_footer(doc, data['CLIENT_NAME'])
    
    # TITLE
    p = doc.add_paragraph()
    run = p.add_run("ADVANCE CARE PLAN")
    run.bold = True
    run.font.size = Pt(14)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    
    # Opening
    p = doc.add_paragraph()
    p.add_run("\tI, ")
    run = p.add_run(data['CLIENT_NAME'].upper())
    run.bold = True
    p.add_run(", hereby give these advance instructions on how I want to be treated by my doctors and other health care providers when I can no longer make those treatment decisions myself.")
    doc.add_paragraph()
    
    # AGENTS SECTION
    p = doc.add_paragraph()
    run = p.add_run("AGENTS:")
    run.bold = True
    p.add_run("  I want the following persons to make health care decisions for me:")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run("Name:  ")
    run = p.add_run(data['AGENT1_NAME'].upper())
    run.bold = True
    p.add_run("\t\t\tRelation:  " + data['AGENT1_RELATION'])
    
    p = doc.add_paragraph()
    p.add_run("Name:  ")
    run = p.add_run(data['AGENT2_NAME'].upper())
    run.bold = True
    p.add_run("\t\t\tRelation:  " + data['AGENT2_RELATION'])
    doc.add_paragraph()
    
    # QUALITY OF LIFE
    p = doc.add_paragraph()
    run = p.add_run("QUALITY OF LIFE:")
    run.bold = True
    doc.add_paragraph()
    
    doc.add_paragraph("I want my doctors to help me maintain an acceptable quality of life including adequate pain management. A quality of life that is unacceptable to me means when I have any of the following conditions:")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    run = p.add_run("PERMANENT UNCONSCIOUS CONDITION:")
    run.bold = True
    p.add_run("  I become totally unaware of people or surroundings with little chance of ever waking up from the coma.")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    run = p.add_run("PERMANENT CONFUSION:")
    run.bold = True
    p.add_run("   I become unable to remember, understand or make decisions. I do not recognize loved ones or cannot have a clear conversation with them.")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    run = p.add_run("DEPENDENT IN ALL ACTIVITIES OF DAILY LIVING:")
    run.bold = True
    p.add_run("  I am no longer able to talk clearly or move by myself. I depend on others for feeding, bathing, dressing and walking. Rehabilitation or any other restorative treatment will not help.")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    run = p.add_run("END-STAGE ILLNESSES:")
    run.bold = True
    p.add_run("  I have an illness that has reached its final stages in spite of full treatment. Examples: Widespread cancer that does not respond anymore to treatment; chronic and/or damaged heart and lungs, where oxygen is needed most of the time and activities are limited due to the feeling of suffocation.")
    doc.add_paragraph()
    
    # TREATMENT SECTION
    p = doc.add_paragraph()
    run = p.add_run("TREATMENT:")
    run.bold = True
    doc.add_paragraph()
    
    doc.add_paragraph("If my quality of life becomes unacceptable to me and my condition is irreversible (that is, it will not improve), I do not want the following treatment:")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    run = p.add_run("CPR (Cardiopulmonary Resuscitation):")
    run.bold = True
    p.add_run("  To make the heart beat again and restore breathing after it has stopped. Usually this involves electric shock, chest compressions, and breathing assistance.")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    run = p.add_run("Life Support / Other Artificial Support:")
    run.bold = True
    p.add_run("  Continuous use of breathing machine, IV fluids, medications, and other equipment that helps the lungs, heart, kidneys and other organs to continue to work.")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    run = p.add_run("Treatment Of New Conditions:")
    run.bold = True
    p.add_run("  Use of surgery, blood transfusions, or antibiotics that will deal with a new condition but will not help the main illness.")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    run = p.add_run("Tube Feeding/IV Fluids:")
    run.bold = True
    p.add_run(" Use of tubes to deliver food and water to patient's stomach or use of IV fluids into a vein which would include artificially delivered nutrition and hydration.")
    doc.add_paragraph()
    
    doc.add_paragraph("Other instructions, such as burial arrangements, hospice care, etc.:_________________")
    doc.add_paragraph("________________________________________________________________________________________________________________________________________________________________")
    doc.add_paragraph()
    
    # ORGAN DONATION
    p = doc.add_paragraph()
    run = p.add_run("Organ donation (optional):")
    run.bold = True
    p.add_run(" Upon my death, I wish to make the following anatomical gifts (please mark one):")
    
    doc.add_paragraph("    Any organ/tissue             My entire body          Only the following organs/tissues: ________________________________________________________________________________________________________________________________________________________________")
    doc.add_paragraph()
    
    # SIGNATURE SECTION
    p = doc.add_paragraph(f"This the _________ day of {data['EXEC_MONTH']}, {data['EXEC_YEAR']}.")
    doc.add_paragraph()
    
    doc.add_paragraph("       Signature: _____________________________________")
    doc.add_paragraph("Witnesses:")
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Witness declarations
    doc.add_paragraph("I am a competent adult who is not named as the agent. I am a competent adult who is not named as the agent. I am not related to the patient by blood, marriage, or adoption and I would not be entitled to any portion of the patient's estate upon his or her death under any existing will or codicil or by operation of law. I witnessed the patient's signature on this form.")
    doc.add_paragraph()
    
    doc.add_paragraph("I am a competent adult who is not named as the agent. I am not related to the patient by blood, marriage, or adoption and I would not be entitled to any portion of the patient's estate upon his or her death under any existing will or codicil or by operation of law.  I witnessed the patient's signature on this form.")
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    
    doc.add_paragraph("_____________________________________")
    doc.add_paragraph("WITNESS 1")
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    
    doc.add_paragraph("_____________________________________")
    doc.add_paragraph("WITNESS 2")
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    
    # NOTARY SECTION
    doc.add_paragraph("STATE OF TENNESSEE")
    doc.add_paragraph("COUNTY OF MAURY")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run("Personally appeared before me, the undersigned Notary Public of said state and county, ")
    run = p.add_run(data['CLIENT_NAME'].upper())
    run.bold = True
    p.add_run(", the within named bargainor, with whom I am personally acquainted (or proved to me on the basis of satisfactory evidence), and who acknowledged that she executed the within instrument for the purposes therein contained and expressed.")
    
    p = doc.add_paragraph(f"WITNESS my hand and seal at office in Columbia, Tennessee, this the _________ day of {data['EXEC_MONTH']}, {data['EXEC_YEAR']}.")
    doc.add_paragraph()
    
    doc.add_paragraph("My commission expires:\t________________________________")
    doc.add_paragraph()
    doc.add_paragraph("___________________\tNotary Public")
    
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
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
