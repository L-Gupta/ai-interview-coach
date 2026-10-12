#!/usr/bin/env python3
"""
Integration Verification Script
Tests frontend-backend integration and environment setup
"""

import os
import sys
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "OK": Colors.GREEN + "✓",
        "FAIL": Colors.RED + "✗",
        "WARN": Colors.YELLOW + "⚠",
        "INFO": Colors.BLUE + "ℹ",
    }
    prefix = colors.get(status, "ℹ") + Colors.END
    print(f"{prefix} {message}")

def check_file_exists(path, description):
    """Check if a file exists"""
    if Path(path).exists():
        print_status(f"{description} exists", "OK")
        return True
    else:
        print_status(f"{description} MISSING: {path}", "FAIL")
        return False

def check_directory_exists(path, description):
    """Check if a directory exists"""
    if Path(path).exists() and Path(path).is_dir():
        print_status(f"{description} exists", "OK")
        return True
    else:
        print_status(f"{description} MISSING: {path}", "FAIL")
        return False

def check_env_variable(key, description, optional=False):
    """Check if an environment variable is set"""
    value = os.getenv(key)
    if value:
        # Hide sensitive values
        if key in ["GEMINI_API_KEY", "PINECONE_API_KEY", "SECRET_KEY"]:
            display = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display = value
        print_status(f"{description}: {display}", "OK")
        return True
    elif optional:
        print_status(f"{description}: Not set (optional)", "WARN")
        return True
    else:
        print_status(f"{description}: NOT SET", "FAIL")
        return False

def check_json_file(path, description):
    """Check if a JSON file is valid"""
    try:
        with open(path, 'r') as f:
            json.load(f)
        print_status(f"{description} is valid JSON", "OK")
        return True
    except Exception as e:
        print_status(f"{description} is INVALID: {e}", "FAIL")
        return False

def verify_backend_setup():
    """Verify backend setup"""
    print(f"\n{Colors.BLUE}{'='*50}")
    print("BACKEND SETUP VERIFICATION")
    print(f"{'='*50}{Colors.END}\n")
    
    results = []
    
    # Check backend directory
    results.append(check_directory_exists("backend", "Backend directory"))
    
    # Check backend main.py
    results.append(check_file_exists("backend/main.py", "Backend main.py"))
    
    # Check backend virtual environment
    venv_paths = ["backend/venv", "backend/.venv"]
    venv_exists = any(Path(p).exists() for p in venv_paths)
    if venv_exists:
        print_status("Virtual environment exists", "OK")
        results.append(True)
    else:
        print_status(f"Virtual environment MISSING: {venv_paths}", "FAIL")
        results.append(False)
    
    # Check backend requirements.txt
    results.append(check_file_exists("backend/requirements.txt", "Backend requirements.txt"))
    
    # Check backend .env
    results.append(check_file_exists(".env", "Root .env configuration"))
    
    # Check backend key directories
    results.append(check_directory_exists("backend/api", "Backend api directory"))
    results.append(check_directory_exists("backend/auth", "Backend auth directory"))
    results.append(check_directory_exists("backend/agents", "Backend agents directory"))
    results.append(check_directory_exists("backend/file", "Backend file directory"))
    
    # Check critical backend files
    backend_files = [
        ("backend/main.py", "Main entry point"),
        ("backend/core/config.py", "Configuration"),
        ("backend/core/security.py", "Security utilities"),
        ("backend/database/db.py", "Database setup"),
        ("backend/auth/router.py", "Auth router"),
        ("backend/api/interview_router.py", "Interview router"),
        ("backend/file/agentic_file_controller.py", "File controller"),
    ]
    
    for file_path, description in backend_files:
        results.append(check_file_exists(file_path, description))
    
    return all(results)

def verify_frontend_setup():
    """Verify frontend setup"""
    print(f"\n{Colors.BLUE}{'='*50}")
    print("FRONTEND SETUP VERIFICATION")
    print(f"{'='*50}{Colors.END}\n")
    
    results = []
    
    # Check frontend directory
    results.append(check_directory_exists("frontend", "Frontend directory"))
    
    # Check package.json
    results.append(check_file_exists("frontend/package.json", "Frontend package.json"))
    if Path("frontend/package.json").exists():
        results.append(check_json_file("frontend/package.json", "package.json"))
    
    # Check node_modules
    if Path("frontend/node_modules").exists():
        print_status("Frontend dependencies (node_modules) installed", "OK")
        results.append(True)
    else:
        print_status("Frontend dependencies (node_modules) NOT INSTALLED", "WARN")
        print_status("Run: cd frontend && npm install", "INFO")
        results.append(False)  # Warning, not critical
    
    # Check environment variables
    results.append(check_file_exists(".env", "Root .env file (frontend REACT_APP_* vars)"))
    
    # Check key frontend files
    frontend_files = [
        ("frontend/src/App.js", "App component"),
        ("frontend/src/index.js", "Index file"),
        ("frontend/src/api.js", "API client"),
    ]
    
    for file_path, description in frontend_files:
        results.append(check_file_exists(file_path, description))
    
    # Check public directory
    results.append(check_directory_exists("frontend/public", "Public directory"))
    results.append(check_file_exists("frontend/public/index.html", "HTML template"))
    
    return all(results)

def verify_environment_variables():
    """Verify environment variables"""
    print(f"\n{Colors.BLUE}{'='*50}")
    print("ENVIRONMENT VARIABLES")
    print(f"{'='*50}{Colors.END}\n")
    
    # Load backend .env
    print(f"{Colors.YELLOW}Backend Configuration:{Colors.END}")
    env_file = Path(".env")
    if env_file.exists():
        env_vars = {}
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        required_backend_vars = [
            ("DATABASE_URL", "Database URL", False),
            ("SECRET_KEY", "JWT Secret Key", False),
            ("GEMINI_API_KEY", "Gemini API Key", False),
            ("PINECONE_API_KEY", "Pinecone API Key", False),
            ("ALLOWED_ORIGINS", "CORS Origins", False),
        ]
        
        results = []
        for var_name, description, optional in required_backend_vars:
            if var_name in env_vars:
                value = env_vars[var_name]
                if var_name in ["GEMINI_API_KEY", "PINECONE_API_KEY", "SECRET_KEY"]:
                    value = value[:15] + "..." if len(value) > 15 else "***"
                print_status(f"{description}: {value}", "OK")
                results.append(True)
            elif optional:
                print_status(f"{description}: (optional)", "WARN")
                results.append(True)
            else:
                print_status(f"{description}: NOT CONFIGURED", "FAIL")
                results.append(False)
        
        # Check CORS includes both dev ports
        if "ALLOWED_ORIGINS" in env_vars:
            origins = env_vars["ALLOWED_ORIGINS"]
            if "3000" in origins or "3000" in str(origins):
                print_status("CORS includes port 3000 (React)", "OK")
            else:
                print_status("CORS missing port 3000 (React)", "WARN")
            if "5173" in origins or "5173" in str(origins):
                print_status("CORS includes port 5173 (Vite)", "OK")
            else:
                print_status("CORS missing port 5173 (Vite)", "WARN")
        
        return all(results)
    else:
        print_status("Backend .env file not found", "FAIL")
        return False

def verify_api_client():
    """Verify frontend API client"""
    print(f"\n{Colors.BLUE}{'='*50}")
    print("API CLIENT VERIFICATION")
    print(f"{'='*50}{Colors.END}\n")
    
    api_file = Path("frontend/src/api.js")
    if not api_file.exists():
        print_status("API client file not found", "FAIL")
        return False
    
    results = []
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Check for required API functions
    required_functions = [
        "register",
        "login",
        "logout",
        "isAuthenticated",
        "startInterview",
        "getNextQuestion",
        "submitAnswer",
        "getInterviewReport",
        "endInterview",
        "uploadResume",
        "healthCheck",
    ]
    
    for func in required_functions:
        if f"export async function {func}" in content or f"export function {func}" in content:
            print_status(f"API function '{func}' implemented", "OK")
            results.append(True)
        else:
            print_status(f"API function '{func}' MISSING", "FAIL")
            results.append(False)
    
    return all(results)

def verify_file_module():
    """Verify backend file processing module"""
    print(f"\n{Colors.BLUE}{'='*50}")
    print("FILE PROCESSING MODULE VERIFICATION")
    print(f"{'='*50}{Colors.END}\n")
    
    results = []
    file_modules = [
        ("backend/file/file_upload.py", "File upload module"),
        ("backend/file/file_pinecone.py", "Pinecone integration"),
        ("backend/file/agentic_file_parse.py", "Resume parser"),
        ("backend/file/agentic_file_chunk.py", "Text chunker"),
        ("backend/file/agentic_file_embed.py", "Embedder"),
        ("backend/file/agentic_file_controller.py", "Pipeline controller"),
        ("backend/file/agentic_file_router.py", "File router"),
    ]
    
    for file_path, description in file_modules:
        results.append(check_file_exists(file_path, description))
    
    return all(results)

def main():
    """Main verification function"""
    print(f"\n{Colors.BLUE}{'='*50}")
    print("AI INTERVIEW COACH - INTEGRATION VERIFICATION")
    print(f"{'='*50}{Colors.END}\n")
    
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working Directory: {os.getcwd()}\n")
    
    results = {
        "Backend Setup": verify_backend_setup(),
        "Frontend Setup": verify_frontend_setup(),
        "Environment Variables": verify_environment_variables(),
        "API Client": verify_api_client(),
        "File Module": verify_file_module(),
    }
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*50}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*50}{Colors.END}\n")
    
    all_passed = True
    for component, passed in results.items():
        status = "OK" if passed else "FAIL"
        print_status(f"{component}: {status}", status)
        if not passed:
            all_passed = False
    
    # Next steps
    print(f"\n{Colors.BLUE}{'='*50}")
    print("NEXT STEPS")
    print(f"{'='*50}{Colors.END}\n")
    
    if all_passed:
        print_status("All checks passed! Ready to start the application.", "OK")
        print("\n1. Terminal 1 - Start Backend:")
        print("   cd backend")
        print("   source venv/bin/activate  # or venv\\Scripts\\Activate on Windows")
        print("   python main.py")
        print("\n2. Terminal 2 - Start Frontend:")
        print("   cd frontend")
        print("   npm install  # Only if node_modules not present")
        print("   npm start")
        print("\n3. Open http://localhost:3000 in your browser")
    else:
        print_status("Some checks failed. Please fix the issues above.", "FAIL")
        print("\nCommon fixes:")
        print("• Backend: source venv/bin/activate && pip install -r requirements.txt")
        print("• Frontend: npm install")
        print("• Environment: Copy .env.example to .env and configure")
    
    print(f"\n{Colors.BLUE}{'='*50}{Colors.END}\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
