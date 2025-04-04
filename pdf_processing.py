import fitz
import re
import json

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text("text") for page in doc)
        return to_json(text.strip()) or "⚠ No readable text found in PDF."
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return ""


def parse_invoice(text):
    invoice_details = {}
    product_details = []

    # Extract invoice number and date
    invoice_match = re.search(r'Invoice No.\s*:\s*(\S+)\s*Date:\s*(\d{2}-\d{2}-\d{4})', text)
    if invoice_match:
        invoice_details['Invoice No.'] = invoice_match.group(1)
        invoice_details['Date'] = invoice_match.group(2)

    # Extract seller details
    seller_match = re.search(r'GST INVOICE\n(.+)\n(.+)\n', text)
    if seller_match:
        invoice_details['Seller'] = seller_match.group(1).strip()
        invoice_details['Location'] = seller_match.group(2).strip()

    # Extract phone number
    phone_match = re.search(r'Phone\s*:\s*([\d+]+)', text)
    if phone_match:
        invoice_details['Phone'] = phone_match.group(1)

    # Extract subtotal and grand total
    subtotal_match = re.search(r'SUB TOTAL\s*(\d+\.\d+)', text)
    grand_total_match = re.search(r'GRAND TOTAL\s*(\d+\.\d+)', text)

    if subtotal_match:
        invoice_details['Subtotal'] = subtotal_match.group(1)
    if grand_total_match:
        invoice_details['Grand Total'] = grand_total_match.group(1)

    # Extract product details
    product_pattern = re.compile(r'(?P<SN>\d+)\.\n(?P<Product_Name>.+?)\n(?P<Pack>\d+)\n(?P<Batch>\S+)\n(?P<Exp>\d+/\d+)\n(?P<QTY>[\d.]+)\n(?P<MRP>[\d.]+)\n(?P<Rate>[\d.]+)\n(?P<SGST>[\d.]+)?\n(?P<CGST>[\d.]+)?\n(?P<Amount>[\d.]+)?', re.DOTALL)

    for match in product_pattern.finditer(text):
        product_details.append({
            'SN': match.group('SN'),
            'Product Name': match.group('Product_Name').strip(),
            'Pack': match.group('Pack'),
            'Batch': match.group('Batch'),
            'Exp': match.group('Exp'),
            'QTY': match.group('QTY'),
            'MRP': match.group('MRP'),
            'Rate': match.group('Rate'),
            'SGST': match.group('SGST') if match.group('SGST') else '0.00',
            'CGST': match.group('CGST') if match.group('CGST') else '0.00',
            'Amount': match.group('Amount') if match.group('Amount') else '0.00',
        })

    return {
        'Invoice Details': invoice_details,
        'Product Details': product_details
    }

def to_json(invoice_text):
    parsed_data = parse_invoice(invoice_text)
    json_data = json.dumps(parsed_data, indent=4)

    return json_data
