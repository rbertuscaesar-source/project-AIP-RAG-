import fitz

def load_pdf(file_path):
    documents = []

    pdf = fitz.open(file_path)

    for page_number, page in enumerate(pdf, start=1):
        text = page.get_text()

        documents.append({
            "text": text,
            "page": page_number
        })

    pdf.close()

    return documents

from docx import Document

def load_docx(file_path):
    doc = Document(file_path)

    text = "\n".join(
        paragraph.text
        for paragraph in doc.paragraphs
    )

    return [{
        "text": text,
        "page": 1
    }]

def load_txt(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return [{
        "text": text,
        "page": 1
    }]