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
    # Header
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

def add_article_header(doc, article_num, title):
    """Add centered, bold, small caps article header"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"{article_num}. {title.upper()}")
    run.bold = True
    run.font.size = Pt(12)
    # Small caps effect
    run.font.small_caps = True
    doc.add_paragraph()  # Spacing after

def generate_poa_document(data):
    """Generate POA document with proper formatting"""
    doc = Document()
    
    # Set up document margins (1 inch = 914400 EMUs)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # Add header and footer
    add_header_footer(doc, data['CLIENT_NAME'])
    
    # Title - centered, bold
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("DURABLE GENERAL POWER OF ATTORNEY")
    run.bold = True
    run.font.size = Pt(14)
    doc.add_paragraph()  # Spacing
    
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
    p.add_run(", as my alternate attorney-in-fact under the Uniform Durable Power of Attorney Act (T.C.A. Â§ 34-6-101, et seq.) and in my name and stead to:").bold = False
    doc.add_paragraph()
    
    # ARTICLE I - GENERAL AUTHORITY
    add_article_header(doc, "I", "GENERAL AUTHORITY")
    
    p = doc.add_paragraph("1.\t")
    p.add_run(f"Generally, do, sign or perform in the principal's name, place and stead any act, deed, matter or thing whatsoever, that ought to be done, signed or performed, or that, in the opinion of the attorney-in-fact, ought to be done, signed or performed in and about the premises, of every nature and kind whatsoever, to all intents and purposes whatsoever, as fully and effectually as the principal could do if personally present and acting. The enumeration of specific powers hereunder shall not in any way limit the general powers conferred herein;")
    doc.add_paragraph()
    
    # ARTICLE II - PROPERTY YOU OWN
    add_article_header(doc, "II", "PROPERTY YOU OWN (Real Estate and Personal Tangible Property)")
    
    p = doc.add_paragraph("2.\t")
    p.add_run("Buy, sell, lease, alter, maintain, pledge or in any way deal with real and personal property and sign each instrument necessary or advisable to complete any real or personal property transaction, including, but not limited to, deeds, deeds of trust, closing statements, options, notes and bills of sale;")
    doc.add_paragraph()
    
    p = doc.add_paragraph("3.\t")
    p.add_run("Have free and private access to any safe deposit box in the principal's individual name, alone or with others, in any bank, including authority to have it drilled, with full right to deposit and withdraw from the safe deposit box or to give full discharge for the safe deposit box;")
    doc.add_paragraph()
    
    # ARTICLE III - PROPERTY YOU CONTROL
    add_article_header(doc, "III", "PROPERTY YOU CONTROL (Business Interests and Trusts)")
    
    p = doc.add_paragraph("4.\t")
    p.add_run("Engage in and transact any and all lawful business of whatever nature or kind for the principal and in the principal's name, whether as partner, joint adventurer, stockholder, or in any other manner or form, and vote any stock or enter voting trusts;")
    doc.add_paragraph()
    
    p = doc.add_paragraph("5.\t")
    p.add_run("Transfer any property owned by the principal to any revocable trust created by the principal with provisions for the principal's care and support;")
    doc.add_paragraph()
    
    # ARTICLE IV - PROPERTY IN ACCOUNTS
    add_article_header(doc, "IV", "PROPERTY IN ACCOUNTS (Checking, Savings, Retirement, Investment)")
    
    sections_iv = [
        "Receive from or disburse to any source whatever moneys through checking or savings or other accounts or otherwise, endorse, sign and issue checks, withdrawal receipts or any other instrument, and open or close any accounts in the principal's name alone or jointly with any other person;",
        "Establish, utilize and terminate checking and savings accounts, money market accounts and agency accounts with financial institutions of all kinds, including securities brokers and corporate fiduciaries;",
        "Invest or reinvest each item of money or other property and lend money or property upon such terms and conditions and with such security as the principal's attorney-in-fact may deem appropriate, or renew, extend, or modify loans, all in accordance with the fiduciary standard of T.C.A. Â§ 35-3-117;",
        "Buy United States government bonds redeemable at par in payment of any United States estate taxes imposed at principal's death;",
        "Create, contribute to, borrow from and otherwise deal with an employee benefit plan or individual retirement account for the principal's benefit, select any payment option under any employee benefit plan or individual retirement account in which the principal is a participant or change options the principal has selected, make \"roll-overs\" of plan benefits into other retirement plans, and apply for and receive payments and benefits;"
    ]
    
    for i, text in enumerate(sections_iv, start=6):
        p = doc.add_paragraph(f"{i}.\t")
        p.add_run(text)
        doc.add_paragraph()
    
    # ARTICLE V - BORROWING AND CREDIT
    add_article_header(doc, "V", "BORROWING AND CREDIT")
    
    p = doc.add_paragraph("11.\t")
    p.add_run("Borrow money for any of the purposes described herein, and secure such borrowings in such manner as the principal's attorney-in-fact shall deem appropriate, and use any credit card held in the principal's name for any of the purposes described therein;")
    doc.add_paragraph()
    
    # ARTICLE VI - INSURANCE
    add_article_header(doc, "VI", "INSURANCE")
    
    p = doc.add_paragraph("12.\t")
    p.add_run("Acquire, maintain, cancel or in any manner deal with any policy of life, accident, disability, hospitalization, medical or casualty insurance, and prosecute each claim for benefits due under any policy;")
    doc.add_paragraph()
    
    # ARTICLE VII - TAX AND GOVERNMENT BENEFITS
    add_article_header(doc, "VII", "TAX AND GOVERNMENT BENEFITS")
    
    sections_vii = [
        "Make, sign and file each income, gift, property or any other tax return or declaration required by the United States or any state, county, municipality or other legally constituted authority;",
        "Receive and give receipt for any money or other obligation due or to become due to the principal from the United States, or any agency or subdivision of the United States, and to act as representative payee for any payment to which the principal may be entitled, and effect redemption of any bond or other security in which the United States, or any agency or subdivision of the United States, is the obligor or payor, and give full discharge therefor;"
    ]
    
    for i, text in enumerate(sections_vii, start=13):
        p = doc.add_paragraph(f"{i}.\t")
        p.add_run(text)
        doc.add_paragraph()
    
    # ARTICLE VIII - PERSONAL MATTERS
    add_article_header(doc, "VIII", "PERSONAL MATTERS")
    
    sections_viii = [
        "Provide for the support and protection of the principal, or of the principal's spouse, or of any minor child of the principal or of the principal's spouse dependent upon the principal, including, without limitation, provision for food, lodging, housing, medical services, recreation and travel;",
        "Pay dues to any club or organization to which the principal belongs, and make charitable contributions in fulfillment of any charitable pledge made by the principal;",
        "Make advance arrangements for the principal's funeral and burial, including the purchase of a burial plot and marker, if the principal has not already done so.",
        "To access, handle, distribute and dispose of my digital assets. For purposes of this provision, digital assets include files stored on my digital devices, including but not limited to, desktops, tablets, peripherals, storage devices, mobile telephones, smart phones and any similar digital device which currently exists or may exist as technology develops or such comparable items as technology develops. The term \"digital assets\" also includes but is not limited to emails received, email accounts, digital music, digital photographs, digital videos, software licenses, social network accounts, file sharing accounts, financial accounts, domain registrations, DNS service accounts, web hosting accounts, tax preparation service accounts, online stores, affiliate programs, other online accounts and similar digital items which currently exist or may exist as technology develops or such comparable items as technology develops, regardless of the ownership of the physical device upon which the digital item is stored."
    ]
    
    for i, text in enumerate(sections_viii, start=15):
        p = doc.add_paragraph(f"{i}.\t")
        p.add_run(text)
        doc.add_paragraph()
    
    # ARTICLE IX - LEGAL AND ADMINISTRATIVE MATTERS
    add_article_header(doc, "IX", "LEGAL AND ADMINISTRATIVE MATTERS")
    
    sections_ix = [
        "Sue, defend or compromise suits and legal actions, and employ counsel in connection with the suits and legal actions, including the power to seek a declaratory judgment interpreting this power of attorney, or a mandatory injunction requiring compliance with the instructions of the principal's attorney-in-fact, or actual and punitive damages against any person failing or refusing to follow the instructions of the principal's attorney-in-fact;",
        "Contract for or employ agents, accountants, advisors, attorneys and others for services in connection with the performance by the principal's attorney-in-fact of any powers herein;",
        "Reimburse the attorney-in-fact or others for all reasonable costs and expenses actually incurred and paid by such persons on behalf of the principal;",
        "Execute other Power of Attorney forms on behalf of the principal that may be required by the internal revenue service, financial or brokerage institutions, or others, naming the attorney-in-fact hereunder as attorney-in-fact for the principal on such additional forms;",
        "Request, receive and review any information, verbal or written, regarding the principal's affairs or the principal's physical or mental health, including legal, medical and hospital records, execute any releases or other documents that may be required in order to obtain such information, and disclose such information to such persons, organizations, firms or corporations as the principal's attorney-in-fact shall deem appropriate; and"
    ]
    
    for i, text in enumerate(sections_ix, start=19):
        p = doc.add_paragraph(f"{i}.\t")
        p.add_run(text)
        doc.add_paragraph()
    
    # Closing paragraphs
    p = doc.add_paragraph()
    p.add_run("The above powers include those specified in T.C.A. Â§ 34-6-109; and without the necessity of obtaining any judicial authorization or approval, those powers shall be vested by me into my attorney-in-fact, who shall use their best judgment and discretion on my behalf to exercise them.")
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run(f"My attorney-in-fact may do, execute, and perform all and every other act or acts which may be necessary or incidental to any of the matters mentioned above or deemed desirable in connection with any such matters by my said attorney-in-fact, as fully and completely as I might do myself and I do hereby ratify and confirm any acts done by my said attorney-in-fact within the premises. This Power of Attorney shall not be affected by subsequent disability or incapacity of the principal as provided by T.C.A. Â§ 34-6-101 et seq., and shall remain in full force and effect in spite of such disability or incapacity, and in the event a proceeding be brought for the appointment of a Conservator or Guardian for my Estate, I request the Court to appoint my {data['AIF_RELATIONSHIP']}, ").bold = False
    p.add_run(data['AIF_NAME'].upper()).bold = True
    p.add_run(f", as my Conservator or Guardian. If my said {data['AIF_RELATIONSHIP']} is unwilling or unable to serve in said capacity, then I request the Court to appoint {data['ALTERNATE_AIF_RELATIONSHIP']}, ").bold = False
    p.add_run(data['ALTERNATE_AIF_NAME'].upper()).bold = True
    p.add_run(", as my Conservator or Guardian. This Power of Attorney shall remain in full force and effect unless revoked by me by written instrument which shall be recorded in the Register's Office of Maury County, Tennessee.").bold = False
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
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Notary section
    p = doc.add_paragraph()
    p.add_run("STATE OF TENNESSEE").bold = True
    p = doc.add_paragraph()
    p.add_run(f"COUNTY OF {data['COUNTY'].upper()}").bold = True
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run(f"Personally, appeared before me, the undersigned a Notary Public in and for the state and county aforesaid, the within named ").bold = False
    p.add_run(data['CLIENT_NAME'].upper()).bold = True
    p.add_run(f" with whom I am personally acquainted, and who acknowledged that {pronouns['subjective']} executed the foregoing instrument for the purposes therein contained.").bold = False
    doc.add_paragraph()
    
    p = doc.add_paragraph()
    p.add_run(f"WITNESS my hand and official seal at office in Maury County, Tennessee, this _________ day of ").bold = False
    p.add_run(data['EXEC_MONTH'].upper()).bold = True
    p.add_run(", ").bold = False
    p.add_run(data['EXEC_YEAR']).bold = True
    p.add_run(".").bold = False
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Notary signature line
    p = doc.add_paragraph()
    p.add_run("_" * 50)
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run("NOTARY PUBLIC").bold = True
    doc.add_paragraph()
    doc.add_paragraph()
    
    p = doc.add_paragraph("My Commission Expires: _____________________")
    
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
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
