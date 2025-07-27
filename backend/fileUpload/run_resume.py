#imports
import os
from fileUpload.file_parse import parse_resume, save_parsed_text_to_file
from fileUpload.file_chunk import chunk_text_by_paragraph, save_chunks_to_file
from fileUpload.file_embed import load_chunks_from_file, embed_chunks
from fileUpload.file_pinecone import upsert_embeddings

# setting variables
UPLOAD_DIR = "uploads"
FILENAME = "sample_resume.pdf" 

def run_pipeline(filename: str):
    print(f"📂 Running pipeline for: {filename}")

    # Step 1: Parse
    parsed_text = parse_resume(filename)
    if not parsed_text:
        raise RuntimeError("Parsing failed.")

    save_parsed_text_to_file(parsed_text, filename)
    parsed_filename = filename.replace(".pdf", "_parsed.txt").replace(".docx", "_parsed.txt")

    # Step 2: Chunk
    chunks = chunk_text_by_paragraph(parsed_text, max_chars=1250)
    save_chunks_to_file(chunks, parsed_filename)

    # Step 3: Embed
    chunk_file = parsed_filename.replace("_parsed.txt", "_chunks.txt")
    chunks = load_chunks_from_file(chunk_file)
    embeddings = embed_chunks(chunks)
    if not embeddings:
        raise RuntimeError("Embedding failed.")

    # Step 4: Pinecone Upsert
    upsert_embeddings(embeddings, original_filename=filename)

    return {
        "chunks": len(chunks),
        "resume_id": filename.replace(".pdf", "").replace(".docx", "")
    }

if __name__ == "__main__":
    from file_upload import upload_resume_from_local
    result = upload_resume_from_local("C:/Users/lakshya3012/Downloads/sample_resume.pdf")
    print(result)