import os
import re

UPLOAD_DIR = os.path.join("file", "uploads")

def chunk_text_by_paragraph(text: str, max_chars: int = 1250) -> list[str]:
    # Normalize and split into blocks
    lines = text.splitlines()
    chunks = []
    current_chunk = ""
    
    def flush_chunk():
        nonlocal current_chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        current_chunk = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect section headers (e.g. ALL CAPS or keyword-based)
        is_section_header = (
            re.match(r"^[A-Z][A-Z\s]+$", line) or
            line.lower() in {
                "summary", "objective", "experience", "work experience", "projects",
                "education", "skills", "certifications", "awards", "achievements",
                "publications", "volunteer", "activities", "leadership positions",
                "languages", "interests"
            }
        )

        # If current chunk is too long, flush it
        if len(current_chunk) + len(line) > max_chars:
            flush_chunk()

        # If new section detected, flush and start a new chunk
        if is_section_header:
            flush_chunk()

        # Append to current chunk
        current_chunk += line + "\n"

    flush_chunk()  # Add the final chunk

    return chunks


def chunk_parsed_resume(parsed_filename: str) -> list[str]:
    file_path = os.path.join(UPLOAD_DIR, parsed_filename)

    if not os.path.exists(file_path):
        print(f"❌ Parsed file not found: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text_by_paragraph(text)
    print(f"🧩 Chunked into {len(chunks)} pieces.")
    return chunks


def save_chunks_to_file(chunks: list[str], original_filename: str):
    base_name = os.path.splitext(original_filename)[0].replace("_parsed", "")
    output_path = os.path.join(UPLOAD_DIR, f"{base_name}_chunks.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"--- Chunk {i+1} ---\n{chunk}\n\n")

    print(f"📂 Chunks saved to: {output_path}")