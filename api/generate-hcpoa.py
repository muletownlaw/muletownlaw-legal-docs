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
    footer_para.text = f"Healthcare Power of Attorney - {client_name}"
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in footer_para.runs:
        run.font.size = Pt(10)

def generate_hcpoa_document(data):
    """Generate Healthcare POA document"""
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
    
    # WARNING SECTION
    p = doc.add_paragraph()
    run = p.add_run("WARNING TO PERSON EXECUTING THIS DOCUMENT")
    run.bold = True
    run.font.size = Pt(12)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    
    doc.add_paragraph("This is an important legal document, and this warning is required by law. Before executing this document you should know these important facts.")
    doc.add_paragraph()
    
    doc.add_paragraph("This document gives the person you designate as your agent (the attorney in fact), the power to make health care decisions for you. Your agent must act consistently with your desires as stated in this document.")
    doc.add_paragraph()
    
    doc.add_paragraph("Except as you otherwise specify in this document, this document gives your agent the power to consent to your doctor not giving treatment or stopping treatment necessary to keep you alive.")
    doc.add_paragraph()
    
    doc.add_paragraph("Notwithstanding this document, you have the right to make medical and other health care decisions for yourself so long as you can give informed consent with respect to the particular decision. In addition, no treatment may be given to you over your objection, and health care necessary to keep you alive may not be stopped or withheld if you object at the time.")
    doc.add_paragraph()
    
    doc.add_paragraph("This document gives your agent authority to consent, to refuse to consent, or to withdraw consent to any care, treatment, service, or procedure to maintain, diagnose or treat a physical or mental condition. This power is subject to any limitations that you include in this document. You may state in this document any types of treatment that you do not desire. In addition, a court can take away the power of your agent to make health care decisions for you if your agent (1) authorizes anything that is illegal or (2) acts contrary to your desires as stated in this document.")
    doc.add_paragraph()
    
    doc.add_paragraph("You have the right to revoke the authority of your agent by notifying your agent or your treating physician, hospital or other health care provider orally or in writing of the revocation.")
    doc.add_paragraph()
    
    doc.add_paragraph("Your agent has the right to examine your medical records and to consent to their disclosure unless you limit this right in this document.")
    doc.add_paragraph()
    
    doc.add_paragraph("Unless you otherwise specify in this document, this document gives your agent the power after you die to (1) authorize an autopsy, (2) donate your body or parts thereof for transplant or therapeutic or educational or scientific purposes, and (3) direct the disposition of your remains.")
    doc.add_paragraph()
    
    doc.add_paragraph("If there is anything in this document that you do not understand, you should ask a lawyer to explain it to you.")
    doc.add_paragraph()
    
    # Acknowledgment section
    p = doc.add_paragraph()
    p.add_run("\tAcknowledgment of Receipt & Warning:").bold = False
    doc.add_paragraph()
    
    p = doc.add_paragraph(f"Date: ______________________\t_______________________________________")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    run = p.add_run(data['CLIENT_NAME'].upper())
    run.bold = True
    p.add_run(", Principal")
    doc.add_paragraph()
    doc.add_paragraph()
    
    # TITLE
    p = doc.add_paragraph()
    run = p.add_run("\tDURABLE POWER OF ATTORNEY FOR HEALTH CARE")
    run.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Main body
    p = doc.add_paragraph()
    p.add_run("I, ")
    run = p.add_run(data['CLIENT_NAME'].upper())
    run.bold = True
    p.add_run(f", a resident of {data['COUNTY']} County, Tennessee, having read and fully understood the importance of the attached warning statement, hereby designate and appoint my {data['AGENT1_RELATION']}, ")
    run = p.add_run(data['AGENT1_NAME'].upper())
    run.bold = True
    p.add_run(f", of {data['AGENT1_COUNTY']} County, Tennessee, or my {data['AGENT2_RELATION']}, ")
    run = p.add_run(data['AGENT2_NAME'].upper())
    run.bold = True
    p.add_run(f", of {data['AGENT2_COUNTY']} County, Tennessee, either of whom may act alone, as my attorney-in-fact to make health care decisions for me as herein provided if I am incapacitated or otherwise unable to make such decisions for myself.")
    doc.add_paragraph()
    
    doc.add_paragraph("I intend by this instrument to create a Durable Power of Attorney for Health Care, pursuant to Tennessee Code Annotated, Sections 34-6-201 et seq. Accordingly, I specifically authorize my attorney-in-fact to make any and all health care decisions on my behalf to the same extent that I could make such decisions for myself if I had the capacity to do so. The term \"health care decisions\" shall mean the consent, refusal of consent, or withdrawal of consent with respect to any care, treatment, service or procedure deemed necessary or advisable by my attending physician or other health care provider to maintain, diagnose or treat my physical or mental condition. The terms \"medical care\" and \"terminal condition\" shall have the meanings set forth in Tennessee Code Annotated, Section 32-11-103. Except to the extent specific action is mandated in the following paragraph, my attorney-in-fact shall have full discretion in making health care decisions on my behalf.")
    doc.add_paragraph()
    
    doc.add_paragraph("If at any time I should have a terminal condition and my attending physician has determined there is no reasonable medical expectation of recovery and which, as a medical probability, will result in my death regardless of the use or discontinuance of medical treatment implemented for the purpose of sustaining life, or the life process, my attorney-in-fact shall direct that medical care (specifically including artificially provided food, water or other nourishment or fluids) be withheld or withdrawn, and that I be permitted to die naturally, with only the administration of medications or the performance of any medical procedure deemed necessary to provide me with comfortable care or to alleviate pain. Notwithstanding the foregoing, if I have indicated a desire to donate any of my organs and/or tissues for transplantation, either pursuant to the terms of a Living Will executed by me or by other written or verbal directions to my attorney-in-fact, my attorney-in-fact shall direct my attending physician to maintain me on artificial support systems only for the period of time required to maintain the viability of and to remove such organs and/or tissues.")
    
    doc.add_paragraph("My attorney-in-fact is my personal representative as defined for HIPAA purposed and shall have the same right as I to request, receive and review any information, verbal or written, regarding my physical or mental health, including, but not limited to, medical and hospital records; to execute on my behalf any releases or other documents that may be required in order to obtain such information; and to consent to the disclosure of such information. I grant my attorney-in-fact the power and authority to execute on my behalf any waiver, release, or other document which may be necessary in order to implement the health care decisions that this instrument authorizes my attorney-in-fact to make on my behalf.")
    doc.add_paragraph()
    
    doc.add_paragraph("Unless a court with appropriate jurisdiction finds by clear and convincing evidence that my attorney-in-fact should be acting on my behalf in bad faith, my attorney-in-fact shall have priority over any other person to act for me in all matters of health care decisions. If, following the execution of this instrument, a court appoints a conservator, guardian or other fiduciary to act on my behalf (collectively, the \"fiduciary\"), the fiduciary shall not have the power to revoke or amend this Durable Power of Attorney for Health Care, or to replace my attorney-in-fact acting hereunder.")
    doc.add_paragraph()
    
    doc.add_paragraph("It is my specific desire that any health care provider who, as a matter of conscience, cannot or will not implement the health care decisions made by my attorney-in-fact for my benefit pursuant to this Durable Power of Attorney for Health Care, arrange for my prompt and orderly transfer to the care of others who can and will implement such decisions.")
    doc.add_paragraph()
    
    doc.add_paragraph("I may revoke the appointment of my attorney-in-fact by notifying my attorney-in-fact, or my treating physician or other health care provider, either orally or in writing. The authority of my attorney-in-fact acting hereunder may be terminated or revoked only as herein provided and shall in no way be affected by the existence of a living will executed by me.")
    doc.add_paragraph()
    
    doc.add_paragraph("This instrument is to be construed and interpreted as a Durable Power of Attorney for Health Care and is intended to comply in all respects with the provisions of Tennessee Code Annotated, Sections 34-6-201 et seq.; and all terms used in this instrument shall have the meanings set forth for such terms in the statute, unless otherwise specifically defined herein. This instrument revokes any prior durable powers of attorney for health care executed by me. Nothing in this instrument shall affect any rights my attorney-in-fact may have, apart from this Durable Power of Attorney for Health Care, to make, or participate in the making of, health care decisions on my behalf.")
    doc.add_paragraph()
    
    p = doc.add_paragraph(f"Dated this _____ day of {data['EXEC_MONTH']}, {data['EXEC_YEAR']}.")
    doc.add_paragraph()
    doc.add_paragraph()
    
    doc.add_paragraph("____________________________________")
    doc.add_paragraph()
    p = doc.add_paragraph()
    run = p.add_run(data['CLIENT_NAME'].upper())
    run.bold = True
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()
    
    # Witness section
    doc.add_paragraph("We, the subscribing witnesses hereto, declare under penalty of perjury under the laws of Tennessee that the person who signed this document is personally known to us to be the principal; that the principal signed this durable power of attorney in our presence; that the principal appears to be of sound mind and under no duress, fraud or undue influence; and that neither of us is the person appointed as attorney-in-fact by this document. Each witness further individually declares that he or she is not a health care provider, an employee of a health care provider, the operator of a health care institution, nor an employee of an operator of a health care institution; that he or she is not related to the principal by blood, marriage, or adoption; and that, to the best of his or her knowledge, he or she does not at the present time have a claim against any portion of the estate of the principal or is entitled to any part of the estate of the principal upon the principal's death under any will or codicil now existing, or by operation of law.")
    doc.add_paragraph()
    doc.add_paragraph()
    
    doc.add_paragraph("____________________________________")
    doc.add_paragraph("WITNESS")
    doc.add_paragraph()
    doc.add_paragraph("____________________________________")
    doc.add_paragraph("WITNESS")
    doc.add_paragraph()
    
    doc.add_paragraph("Sworn to and subscribed before me,")
    doc.add_paragraph()
    doc.add_paragraph(f"this _____ day of {data['EXEC_MONTH']}, {data['EXEC_YEAR']}.")
    doc.add_paragraph()
    doc.add_paragraph()
    
    doc.add_paragraph("________________________________")
    doc.add_paragraph("Notary Public")
    doc.add_paragraph()
    doc.add_paragraph("My Commission Expires:")
    doc.add_paragraph()
    doc.add_paragraph("____________________")
    
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
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
