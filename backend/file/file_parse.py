import os
from typing import Optional
import fitz  # PyMuPDF
from docx import Document

UPLOAD_DIR = os.path.join("file","uploads")

def parse_pdf(filepath: str) -> str:
    try:
        doc = fitz.open(filepath)
        text = "\n".join([page.get_text() for page in doc])
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")
        return ""

def parse_docx(filepath: str) -> str:
    try:
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception as e:
        print(f"❌ Error parsing DOCX: {e}")
        return ""

def parse_resume(filename: str) -> Optional[str]:
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    if filename.lower().endswith(".pdf"):
        return parse_pdf(file_path)
    elif filename.lower().endswith(".docx"):
        return parse_docx(file_path)
    else:
        print("❌ Unsupported file type.")
        return None
    
def save_parsed_text_to_file(text: str, original_filename: str):
    base_name = os.path.splitext(original_filename)[0]
    output_path = os.path.join(UPLOAD_DIR, f"{base_name}_parsed.txt")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"📄 Parsed text saved to: {output_path}")

