"""Generate probate opening documents as a ZIP file."""
from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from probate_utils import (
    load_template, replace_in_document, build_common_replacements,
    select_opening_documents, determine_declinations, derive_pronouns,
    derive_pr_title, build_zip, generate_flags
)


def generate_declination_doc(decliner, data):
    """Generate a single declination document for one person."""
    doc = load_template('Declination to Serve CURLY.docx')
    pr_title = derive_pr_title(data.get('estate_type', 'Testate'),
                                data.get('pr_gender', 'Male'))
    dec_pronouns = derive_pronouns(decliner.get('gender', 'Male'))

    replacements = {
        '{DECLINER NAME}': decliner['name'],
        '{DECEDENT}': data.get('decedent_full_name', ''),
        '{Decedent Name}': data.get('decedent_full_name', ''),
        '{PETITIONER}': data.get('pr_full_name', ''),
        '{RELATION TO DECEDENT}': decliner.get('relationship', ''),
        '{HIS/HER}': dec_pronouns['possessive'],
        '{his/her}': dec_pronouns['possessive'],
        '{Administrator/trix CHOOSE ONE}': pr_title,
        '{Title Executor/Executrix CHOOSE ONE}': pr_title,
        '{COUNTY}': data.get('decedent_county', ''),
        '{COUNTY NAME}': data.get('decedent_county', ''),
        'Dale, Hutto & Lyle, PLLC': data.get('firm_name', 'Muletown Law, P.C.'),
    }
    replace_in_document(doc, replacements)
    return doc


def generate_opening_package(data):
    """Generate all opening documents and return as ZIP BytesIO."""
    replacements = build_common_replacements(data)
    documents = []

    # 1. Generate petition, order, oath per selection logic
    selected = select_opening_documents(data)
    for template_name, output_title in selected:
        doc = load_template(template_name)
        replace_in_document(doc, replacements)
        documents.append((output_title, doc))

    # 2. Generate declinations
    declinations = determine_declinations(data)
    for decliner in declinations:
        doc = generate_declination_doc(decliner, data)
        title = f"Declination to Serve - {decliner['name']}"
        documents.append((title, doc))

    # 3. Build ZIP
    date_str = data.get('generation_date') or None
    return build_zip(documents, date_str)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            zip_buffer = generate_opening_package(data)

            decedent_name = data.get('decedent_full_name', 'Unknown').replace(' ', '_')
            filename = f"Probate_Opening_{decedent_name}.zip"

            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition',
                             f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(zip_buffer.getvalue())

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
