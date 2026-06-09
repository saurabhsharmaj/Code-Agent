#!/usr/bin/env python3
"""
Setup Validation Script
Verifies all components are properly installed and configured
"""

import os
import sys
import subprocess

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_python_version():
    print_section("Python Version Check")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ required")
        return False
    print("✅ Python version OK")
    return True

def check_imports():
    print_section("Required Packages Check")
    
    required_packages = {
        "langchain": "langchain",
        "langchain_groq": "langchain-groq",
        "langgraph": "langgraph",
        "dotenv": "python-dotenv",
        "yaml": "pyyaml",
        "pydantic": "pydantic",
    }
    
    all_ok = True
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_groq_api_key():
    print_section("Groq API Key Configuration")
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if api_key:
        masked_key = f"{api_key[:10]}...{api_key[-5:]}"
        print(f"✅ GROQ_API_KEY found: {masked_key}")
        return True
    else:
        print("❌ GROQ_API_KEY not found")
        print("\nTo set it:")
        print("  export GROQ_API_KEY='your_actual_key_here'")
        print("  OR create .env file with: GROQ_API_KEY=your_key")
        return False

def check_project_structure():
    print_section("Project Structure Check")
    
    required_dirs = [
        "common",
        "planner-agent",
        "implement-agent",
        "review-agent",
        "decision-agent",
        "report-agent"
    ]
    
    required_files = [
        "main.py",
        "routes.py",
        "requirements.txt",
        ".env",
        "README.md",
        "ARCHITECTURE.md"
    ]
    
    all_ok = True
    
    print("Directories:")
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ - MISSING")
            all_ok = False
    
    print("\nFiles:")
    for file_name in required_files:
        if os.path.isfile(file_name):
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - MISSING")
            all_ok = False
    
    return all_ok

def check_groq_connectivity():
    print_section("Groq API Connectivity Check")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️  Skipping - GROQ_API_KEY not set")
        return None
    
    try:
        from langchain_groq import ChatGroq
        
        print("Testing connection to Groq API...")
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=api_key
        )
        
        # Try a simple inference
        response = llm.invoke("Say 'Connected' briefly")
        print("✅ Connection successful")
        print(f"Response: {response.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("  K8s Deployment Agent Flow - Setup Validation")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_imports),
        ("Groq API Key", check_groq_api_key),
        ("Project Structure", check_project_structure),
        ("Groq Connectivity", check_groq_connectivity),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"Error during {check_name}: {str(e)}")
            results.append((check_name, False))
    
    # Summary
    print_section("Validation Summary")
    
    passed = sum(1 for _, result in results if result is True)
    total = len(results)
    
    for check_name, result in results:
        status = "✅" if result is True else ("❌" if result is False else "⚠️")
        print(f"{status} {check_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All checks passed! You're ready to run:")
        print("   python main.py")
        return 0
    elif passed >= 4:  # At least 4 out of 5
        print("\n⚠️  Most checks passed. Run 'python main.py' to try.")
        return 1
    else:
        print("\n❌ Please fix the issues above before running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
