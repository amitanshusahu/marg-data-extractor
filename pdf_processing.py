import fitz

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text("text") for page in doc)
        return text.strip() or "⚠ No readable text found in PDF."
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return ""
