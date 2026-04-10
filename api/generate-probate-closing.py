"""Generate probate closing documents as a ZIP file."""
from http.server import BaseHTTPRequestHandler
import json
from io import BytesIO
from probate_utils import (
    load_template, replace_in_document, build_common_replacements,
    select_closing_documents, select_receipt_waiver_template,
    derive_pronouns, derive_pr_title, build_zip
)


def generate_receipt_waiver(heir, data):
    """Generate receipt & waiver for one heir.

    Builds per-heir replacements (beneficiary name, address, pronoun,
    beneficiary type statement) merged with common replacements
    (decedent name, executor name, county, fees, docket number, firm name).
    """
    template_name, output_title = select_receipt_waiver_template(heir, data)
    doc = load_template(template_name)
    heir_pronouns = derive_pronouns(heir.get('heir_gender', 'Female'))
    pr_title = derive_pr_title(data.get('estate_type', 'Testate'),
                                data.get('pr_gender', 'Male'))

    replacements = {
        # Per-heir fields
        '{Beneficiary Name}': heir['heir_full_name'],
        '{BENEFICIARY NAME}': heir['heir_full_name'],
        '{Beneficiary}': heir['heir_full_name'],
        '{Beneficiary Address}': heir.get('heir_address', ''),
        '{Beneficiary City, State Zip}': heir.get('heir_city', ''),
        '{Beneficiary Pronoun}': heir_pronouns['subject'],
        '{Beneficiary Pronoun HIS/HER}': heir_pronouns['possessive'],
        '{Beneficiary Relationship}': heir.get('heir_relationship', ''),

        # Common fields
        '{Decedent Name}': data.get('decedent_full_name', ''),
        '{DECEDENT}': data.get('decedent_full_name', ''),
        '{DECEDENT NAME}': data.get('decedent_full_name', ''),
        '{Decedent}': data.get('decedent_full_name', ''),
        '{Executor Name}': data.get('pr_full_name', ''),
        '{EXECUTOR NAME}': data.get('pr_full_name', ''),
        '{Executor}': data.get('pr_full_name', ''),
        '{PETITIONER NAME}': data.get('pr_full_name', ''),
        '{Petitioner Name}': data.get('pr_full_name', ''),
        '{Executor/trix}': pr_title,
        '{Executor/Executrix}': pr_title,
        '{Title}': pr_title,
        '{TITLE}': pr_title,
        '{Administrator/trix}': pr_title,
        '{AttorneyFeeAmount}': data.get('attorney_fee_amount', ''),
        '{ExecutorFeeTotal}': data.get('executor_fee_amount', ''),
        '{Docket Number}': data.get('case_number', ''),
        '{docket number}': data.get('case_number', ''),
        '{COUNTY}': data.get('decedent_county', ''),
        '{County}': data.get('decedent_county', ''),
        '{ATTORNEY}': data.get('attorney_full_name', ''),
        '{ATTORNEY NAME}': data.get('attorney_full_name', ''),
        '{BPR #}': data.get('attorney_bpr', ''),
        '{BPR}': data.get('attorney_bpr', ''),
        'Dale, Hutto & Lyle, PLLC': data.get('firm_name', 'Muletown Law, P.C.'),
    }
    replace_in_document(doc, replacements)
    return output_title, doc


def generate_closing_package(data):
    """Generate all closing documents and return as ZIP BytesIO."""
    replacements = build_common_replacements(data)
    documents = []

    # 1. Closing petition and order
    selected = select_closing_documents(data)
    for template_name, output_title in selected:
        doc = load_template(template_name)
        replace_in_document(doc, replacements)
        documents.append((output_title, doc))

    # 2. Receipt & waiver per heir
    for heir in data.get('heirs', []):
        title, doc = generate_receipt_waiver(heir, data)
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

            zip_buffer = generate_closing_package(data)

            decedent_name = data.get('decedent_full_name', 'Unknown').replace(' ', '_')
            filename = f"Probate_Closing_{decedent_name}.zip"

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
