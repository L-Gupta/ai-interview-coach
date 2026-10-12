"""
Verification script to test all components
Run this to verify your setup is working correctly
"""

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        # Test FER
        from fer.fer import FER
        detector = FER(mtcnn=False)
        print("✅ FER imported successfully")
    except Exception as e:
        print(f"❌ FER import failed: {e}")
        return False
    
    try:
        # Test agents
        from agents.interviewer_agent import InterviewerAgent
        from agents.integrity_agent import IntegrityAgent
        from agents.video_analysis_agent import VideoAnalysisAgent
        from agents.audio_analysis_agent import AudioAnalysisAgent
        print("✅ All agents imported successfully")
    except Exception as e:
        print(f"❌ Agent imports failed: {e}")
        return False
    
    try:
        # Test LangChain
        from langchain_classic.agents import create_react_agent, AgentExecutor
        from langchain_core.prompts import PromptTemplate
        print("✅ LangChain components imported successfully")
    except Exception as e:
        print(f"❌ LangChain imports failed: {e}")
        return False
    
    try:
        # Test Pinecone
        from pinecone import Pinecone
        print("✅ Pinecone imported successfully")
    except Exception as e:
        print(f"❌ Pinecone import failed: {e}")
        return False
    
    try:
        # Test FastAPI
        from fastapi import FastAPI
        import api.v1.auth
        import api.v1.interview
        print("✅ FastAPI components imported successfully")
    except Exception as e:
        print(f"❌ FastAPI imports failed: {e}")
        return False
    
    try:
        # Test database
        from models.database import User, InterviewSession
        from database.session import get_db
        print("✅ Database models imported successfully")
    except Exception as e:
        print(f"❌ Database imports failed: {e}")
        return False
    
    return True

def test_packages():
    """Test critical package versions"""
    print("\nChecking package versions...")
    
    packages = {
        'fer': '25.10.3',
        'tensorflow': '2.20.0',
        'langchain': '1.2.8',
        'pinecone': '8.0.0',
        'fastapi': '0.128.2',
        'opencv-python': '4.13.0',
        'mediapipe': '0.10.32'
    }
    
    import importlib.metadata
    
    for package, expected_version in packages.items():
        try:
            installed_version = importlib.metadata.version(package)
            if installed_version.startswith(expected_version.split('.')[0]):
                print(f"✅ {package}: {installed_version}")
            else:
                print(f"⚠️  {package}: {installed_version} (expected {expected_version})")
        except Exception as e:
            print(f"❌ {package}: Not installed or error - {e}")

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from core.config import settings
        print(f"✅ Config loaded")
        print(f"   - Database: {settings.DATABASE_URL}")
        print(f"   - Debug: {settings.DEBUG}")
        print(f"   - Port: {settings.PORT}")
        
        # Check if API keys are set (but don't print them)
        if "your-" in settings.GEMINI_API_KEY:
            print("⚠️  GEMINI_API_KEY needs to be set in .env")
        else:
            print("✅ GEMINI_API_KEY is configured")
            
        if "your-" in settings.PINECONE_API_KEY:
            print("⚠️  PINECONE_API_KEY needs to be set in .env")
        else:
            print("✅ PINECONE_API_KEY is configured")
            
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("AI Interview Coach - Setup Verification")
    print("=" * 60)
    print()
    
    # Run tests
    imports_ok = test_imports()
    test_packages()
    config_ok = test_config()
    
    print()
    print("=" * 60)
    if imports_ok and config_ok:
        print("✅ ALL TESTS PASSED - Setup is complete!")
        print()
        print("Next steps:")
        print("1. Update .env file with your API keys")
        print("2. Run: python main.py")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    print("=" * 60)

if __name__ == "__main__":
    main()
