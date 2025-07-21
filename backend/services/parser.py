# backend/services/parser.py

import fitz  # PyMuPDF
import docx

def parse_resume(file_bytes: bytes, filetype: str) -> str:
    if filetype == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    elif filetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file type")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    with open("temp_resume.docx", "wb") as f:
        f.write(file_bytes)
    doc = docx.Document("temp_resume.docx")
    return "\n".join([para.text for para in doc.paragraphs])
