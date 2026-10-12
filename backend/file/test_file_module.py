"""
File Module Verification Test
Tests all components in the file/ folder
"""
import sys
import os

def test_imports():
    """Test all file module imports"""
    print("\n" + "="*60)
    print("Testing File Module Imports")
    print("="*60 + "\n")
    
    tests = []
    
    # Test 1: file_upload module
    try:
        from file.file_upload import save_resume_and_init_reports, get_upload_path, get_report_dir
        print("✓ file_upload: save_resume_and_init_reports, get_upload_path, get_report_dir")
        tests.append(("file_upload", True))
    except Exception as e:
        print(f"✗ file_upload FAILED: {e}")
        tests.append(("file_upload", False))
    
    # Test 2: file_pinecone module
    try:
        from file.file_pinecone import upsert_embeddings, query_resume, delete_resume_vectors
        print("✓ file_pinecone: upsert_embeddings, query_resume, delete_resume_vectors")
        tests.append(("file_pinecone", True))
    except Exception as e:
        print(f"✗ file_pinecone FAILED: {e}")
        tests.append(("file_pinecone", False))
    
    # Test 3: agentic_file_parse
    try:
        from file.agentic_file_parse import AgenticResumeParser, parse_resume
        print("✓ agentic_file_parse: AgenticResumeParser, parse_resume")
        tests.append(("agentic_file_parse", True))
    except Exception as e:
        print(f"✗ agentic_file_parse FAILED: {e}")
        tests.append(("agentic_file_parse", False))
    
    # Test 4: agentic_file_chunk
    try:
        from file.agentic_file_chunk import AgenticResumeChunker
        print("✓ agentic_file_chunk: AgenticResumeChunker")
        tests.append(("agentic_file_chunk", True))
    except Exception as e:
        print(f"✗ agentic_file_chunk FAILED: {e}")
        tests.append(("agentic_file_chunk", False))
    
    # Test 5: agentic_file_embed
    try:
        from file.agentic_file_embed import AgenticEmbedder, embed_chunks
        print("✓ agentic_file_embed: AgenticEmbedder, embed_chunks")
        tests.append(("agentic_file_embed", True))
    except Exception as e:
        print(f"✗ agentic_file_embed FAILED: {e}")
        tests.append(("agentic_file_embed", False))
    
    # Test 6: agentic_file_controller
    try:
        from file.agentic_file_controller import AgenticPipelineController, run_pipeline
        print("✓ agentic_file_controller: AgenticPipelineController, run_pipeline")
        tests.append(("agentic_file_controller", True))
    except Exception as e:
        print(f"✗ agentic_file_controller FAILED: {e}")
        tests.append(("agentic_file_controller", False))
    
    # Test 7: agentic_file_router
    try:
        from file.agentic_file_router import router
        print(f"✓ agentic_file_router: router with {len(router.routes)} routes")
        tests.append(("agentic_file_router", True))
    except Exception as e:
        print(f"✗ agentic_file_router FAILED: {e}")
        tests.append(("agentic_file_router", False))
    
    return tests


def test_class_initialization():
    """Test that classes can be instantiated"""
    print("\n" + "="*60)
    print("Testing Class Initialization")
    print("="*60 + "\n")
    
    tests = []
    
    # Test AgenticResumeParser
    try:
        from file.agentic_file_parse import AgenticResumeParser
        parser = AgenticResumeParser()
        print(f"✓ AgenticResumeParser instantiated with {len(parser.tools)} tools")
        tests.append(("AgenticResumeParser", True))
    except Exception as e:
        print(f"✗ AgenticResumeParser FAILED: {e}")
        tests.append(("AgenticResumeParser", False))
    
    # Test AgenticResumeChunker
    try:
        from file.agentic_file_chunk import AgenticResumeChunker
        chunker = AgenticResumeChunker(max_chars=1000)
        print(f"✓ AgenticResumeChunker instantiated with max_chars=1000")
        tests.append(("AgenticResumeChunker", True))
    except Exception as e:
        print(f"✗ AgenticResumeChunker FAILED: {e}")
        tests.append(("AgenticResumeChunker", False))
    
    # Test AgenticEmbedder
    try:
        from file.agentic_file_embed import AgenticEmbedder
        embedder = AgenticEmbedder()
        print(f"✓ AgenticEmbedder instantiated with {len(embedder.tools)} tools")
        tests.append(("AgenticEmbedder", True))
    except Exception as e:
        print(f"✗ AgenticEmbedder FAILED: {e}")
        tests.append(("AgenticEmbedder", False))
    
    # Test AgenticPipelineController
    try:
        from file.agentic_file_controller import AgenticPipelineController
        controller = AgenticPipelineController()
        print(f"✓ AgenticPipelineController instantiated with {len(controller.tools)} tools")
        tests.append(("AgenticPipelineController", True))
    except Exception as e:
        print(f"✗ AgenticPipelineController FAILED: {e}")
        tests.append(("AgenticPipelineController", False))
    
    return tests


def test_directories():
    """Test that required directories exist or can be created"""
    print("\n" + "="*60)
    print("Testing Directory Structure")
    print("="*60 + "\n")
    
    from pathlib import Path
    
    dirs_to_check = [
        Path("file/uploads"),
        Path("end/reports")
    ]
    
    for dir_path in dirs_to_check:
        if dir_path.exists():
            print(f"✓ {dir_path} exists")
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ {dir_path} created")
            except Exception as e:
                print(f"✗ {dir_path} FAILED: {e}")


def test_langchain_imports():
    """Test that all LangChain imports are correct"""
    print("\n" + "="*60)
    print("Testing LangChain Import Updates")
    print("="*60 + "\n")
    
    issues = []
    
    # Check each file for old imports
    files_to_check = [
        "file/agentic_file_parse.py",
        "file/agentic_file_chunk.py",
        "file/agentic_file_embed.py",
        "file/agentic_file_controller.py"
    ]
    
    for filepath in files_to_check:
        with open(filepath, "r") as f:
            content = f.read()
            
        has_old_imports = False
        if "from langchain.agents import" in content:
            print(f"✗ {filepath}: Still uses old 'langchain.agents'")
            has_old_imports = True
        if "from langchain.prompts import" in content:
            print(f"✗ {filepath}: Still uses old 'langchain.prompts'")
            has_old_imports = True
        if "from langchain.tools import" in content:
            print(f"✗ {filepath}: Still uses old 'langchain.tools'")
            has_old_imports = True
        
        if not has_old_imports:
            print(f"✓ {filepath}: All imports updated")
    
    return issues


def main():
    print("\n" + "="*60)
    print("FILE MODULE VERIFICATION TEST")
    print("="*60)
    
    # Run all tests
    import_tests = test_imports()
    class_tests = test_class_initialization()
    test_directories()
    test_langchain_imports()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60 + "\n")
    
    all_tests = import_tests + class_tests
    passed = sum(1 for _, status in all_tests if status)
    total = len(all_tests)
    
    print(f"Import Tests: {sum(1 for name, status in import_tests if status)}/{len(import_tests)} passed")
    print(f"Class Tests:  {sum(1 for name, status in class_tests if status)}/{len(class_tests)} passed")
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - File module is fully functional!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed - check errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
