#!/usr/bin/env python3
"""
Import Checker for NovaTech AI Chatbot
Checks which required packages are available and which are missing
"""

import importlib
import sys

def check_import(package_name, import_name=None):
    """Check if a package can be imported"""
    try:
        if import_name:
            importlib.import_module(import_name)
        else:
            importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def main():
    """Check all required packages"""
    print("🔍 NovaTech AI Chatbot - Package Availability Check")
    print("=" * 60)
    
    # Core packages
    core_packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("python-dotenv", "dotenv", "Environment variables"),
    ]
    
    print("\n📦 Core Backend Packages:")
    for package, description in core_packages:
        if len(package.split('.')) > 1:
            pkg_name, import_name = package.split('.', 1)
            available = check_import(pkg_name, import_name)
        else:
            available = check_import(package)
        
        status = "✅" if available else "❌"
        print(f"  {status} {package:<20} - {description}")
    
    # AI/ML packages
    ai_packages = [
        ("google-generativeai", "google.generativeai", "Google Gemini AI"),
        ("langchain", "langchain", "LangChain framework"),
        ("langchain-google-genai", "langchain_google_genai", "LangChain Gemini integration"),
        ("sentence-transformers", "sentence_transformers", "Text embeddings"),
        ("faiss-cpu", "faiss", "Vector database"),
        ("torch", "torch", "PyTorch"),
    ]
    
    print("\n🤖 AI/ML Packages:")
    for package, import_name, description in ai_packages:
        available = check_import(package, import_name)
        status = "✅" if available else "❌"
        print(f"  {status} {package:<25} - {description}")
    
    # Data processing packages
    data_packages = [
        ("pandas", "pandas", "Data manipulation"),
        ("numpy", "numpy", "Numerical computing"),
        ("requests", "requests", "HTTP requests"),
        ("httpx", "httpx", "Async HTTP client"),
    ]
    
    print("\n📊 Data Processing Packages:")
    for package, import_name, description in data_packages:
        available = check_import(package, import_name)
        status = "✅" if available else "❌"
        print(f"  {status} {package:<25} - {description}")
    
    # Check Python version
    print(f"\n🐍 Python Version: {sys.version.split()[0]}")
    
    # Summary
    print("\n" + "=" * 60)
    print("💡 Note: Missing packages will be installed during deployment")
    print("   Your code has fallback handling for missing packages")
    print("   This is normal during development and won't affect deployment")

if __name__ == "__main__":
    main() 