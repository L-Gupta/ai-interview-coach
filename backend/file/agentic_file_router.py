"""
Updated File Router - Uses Agentic Pipeline
This is a drop-in replacement for your existing file_router.py
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from file.file_upload import save_resume_and_init_reports
from auth.dependencies import get_current_active_user

# OPTION 1: Use the full agentic pipeline
from file.agentic_file_controller import run_pipeline

# OPTION 2: Use individual agentic components (commented out)
# from file.agentic_file_parse import parse_resume, save_parsed_text_to_file
# from file.agentic_file_chunk import chunk_text_by_paragraph, save_chunks_to_file
# from file.agentic_file_embed import embed_chunks, load_chunks_from_file
# from file.file_pinecone import upsert_embeddings

router = APIRouter(tags=["Resume upload"])


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), resume_id: str = Form(None)):
    """
    Upload and process resume using agentic AI pipeline.
    
    The agent will:
    1. Intelligently detect and parse the file format
    2. Chunk the content based on semantic structure
    3. Embed chunks with automatic retry on failures
    4. Upload to Pinecone with validation
    
    All steps are monitored and errors are handled automatically.
    """
    
    # Validate file type
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed."
        )
    
    try:
        # Step 1: Save file and initialize report directories
        save_filename, safe_resume_id = save_resume_and_init_reports(file, resume_id or None)
        
        print(f"\n{'='*60}")
        print(f"📤 Resume Upload Started")
        print(f"{'='*60}")
        print(f"Original filename: {file.filename}")
        print(f"Saved as: {save_filename}")
        print(f"Resume ID: {safe_resume_id}")
        print(f"{'='*60}\n")
        
        # Step 2: Run agentic pipeline
        # This single function call orchestrates everything with AI agents
        result = run_pipeline(save_filename, resume_id=safe_resume_id)
        
        # Step 3: Return detailed results
        return {
            "message": result.get("message", "Resume processed"),
            "status": result.get("status", "unknown"),
            "filename": save_filename,
            "resume_id": safe_resume_id,
            "chunks_created": result.get("chunks", 0),
            "agent_summary": result.get("agent_summary", ""),
            **result  # Include any additional fields from the agent
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print("\n❌ UPLOAD FAILED:")
        traceback.print_exc()
        
        # Return user-friendly error
        raise HTTPException(
            status_code=500,
            detail=f"Resume processing failed: {str(e)}"
        )


# Optional: Endpoint to check pipeline status
@router.get("/resume-status/{resume_id}")
async def check_resume_status(resume_id: str):
    """
    Check if a resume has been fully processed.
    
    Returns status of each pipeline step.
    """
    from pathlib import Path
    
    upload_dir = Path("file/uploads")
    reports_dir = Path("end/reports")
    
    status = {
        "resume_id": resume_id,
        "uploaded": False,
        "parsed": False,
        "chunked": False,
        "embedded": False,
        "reports_initialized": False
    }
    
    # Check if files exist
    status["uploaded"] = any([
        (upload_dir / f"{resume_id}.pdf").exists(),
        (upload_dir / f"{resume_id}.docx").exists()
    ])
    
    status["parsed"] = (upload_dir / f"{resume_id}_parsed.txt").exists()
    status["chunked"] = (upload_dir / f"{resume_id}_chunks.txt").exists()
    status["reports_initialized"] = (reports_dir / resume_id).exists()
    
    # Embeddings are in Pinecone, so we assume if chunks exist, embeddings do too
    status["embedded"] = status["chunked"]
    
    # Overall status
    all_complete = all([
        status["parsed"],
        status["chunked"],
        status["embedded"]
    ])
    
    status["overall_status"] = "complete" if all_complete else "incomplete"
    
    return status


# Optional: Manual pipeline trigger (for re-processing)
@router.post("/reprocess-resume/{resume_id}")
async def reprocess_resume(resume_id: str):
    """
    Re-run the pipeline on an already uploaded resume.
    
    Useful if initial processing failed or you want to use new chunking strategy.
    """
    from pathlib import Path
    
    upload_dir = Path("file/uploads")
    
    # Find the uploaded file
    pdf_path = upload_dir / f"{resume_id}.pdf"
    docx_path = upload_dir / f"{resume_id}.docx"
    
    if pdf_path.exists():
        filename = f"{resume_id}.pdf"
    elif docx_path.exists():
        filename = f"{resume_id}.docx"
    else:
        raise HTTPException(
            status_code=404,
            detail=f"No resume file found for {resume_id}"
        )
    
    try:
        # Re-run the agentic pipeline
        result = run_pipeline(filename, resume_id=resume_id)
        
        return {
            "message": "Resume reprocessed",
            "resume_id": resume_id,
            **result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Reprocessing failed: {str(e)}"
        )


# Optional: Get pipeline logs/reasoning
@router.get("/pipeline-logs/{resume_id}")
async def get_pipeline_logs(resume_id: str):
    """
    Get detailed logs of how the agent processed this resume.
    
    (This would require storing agent reasoning, which isn't implemented yet)
    """
    return {
        "message": "Pipeline logging not yet implemented",
        "resume_id": resume_id,
        "suggestion": "Check server console for verbose agent output"
    }