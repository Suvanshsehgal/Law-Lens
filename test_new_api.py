#!/usr/bin/env python3
"""
Test script for the new Routes/Services FastAPI structure
"""

import requests
import json
import time
import os

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_upload(pdf_path):
    """Test document upload with new structure"""
    print(f"📄 Testing document upload: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return None
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{API_BASE}/pdf/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data['session_id']
            print(f"✅ Upload successful! Session ID: {session_id}")
            print(f"📊 Metrics: {data['metrics']}")
            print(f"🔑 Keywords: {data['keywords'][:5]}...")  # Show first 5
            return session_id
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_chat(session_id, query):
    """Test chat functionality with new structure"""
    print(f"💬 Testing chat: '{query}'")
    
    try:
        response = requests.post(f"{API_BASE}/chat/", json={
            'session_id': session_id,
            'query': query
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response: {data['answer']}")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

def test_downloads(session_id):
    """Test download endpoints with new structure"""
    print("📥 Testing download endpoints...")
    
    endpoints = [
        ('highlighted', 'highlighted.pdf'),
        ('keywords', 'keywords.txt'),
        ('text', 'extracted_text.txt')
    ]
    
    for endpoint, filename in endpoints:
        try:
            response = requests.get(f"{API_BASE}/pdf/download/{endpoint}/{session_id}")
            
            if response.status_code == 200:
                # Save file
                with open(f"test_{filename}", 'wb') as f:
                    f.write(response.content)
                print(f"✅ Downloaded: test_{filename}")
            else:
                print(f"❌ Download {endpoint} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Download {endpoint} error: {e}")

def test_session_management(session_id):
    """Test session endpoints with new structure"""
    print("🗂️ Testing session management...")
    
    # Get session data
    try:
        response = requests.get(f"{API_BASE}/pdf/session/{session_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session data retrieved: {data['filename']}")
        else:
            print(f"❌ Get session failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get session error: {e}")
    
    # Delete session
    try:
        response = requests.delete(f"{API_BASE}/pdf/session/{session_id}")
        if response.status_code == 200:
            print("✅ Session deleted successfully")
        else:
            print(f"❌ Delete session failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Delete session error: {e}")

def main():
    """Run all tests for new API structure"""
    print("🧪 Law-Lens API Test Suite (Routes/Services)")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("❌ Server not running or unhealthy. Start with: python run_api.py")
        return
    
    print()
    
    # Test 2: Upload document
    test_pdf = "test_document.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"⚠️  Test PDF not found: {test_pdf}")
        print("Please place a PDF file named 'test_document.pdf' in the current directory")
        print("Or modify the test_pdf variable in this script")
        return
    
    session_id = test_upload(test_pdf)
    if not session_id:
        return
    
    print()
    
    # Test 3: Chat
    test_queries = [
        "What is this document about?",
        "What are the main legal terms?",
        "Are there any important obligations?"
    ]
    
    for query in test_queries:
        test_chat(session_id, query)
        time.sleep(1)  # Small delay between requests
    
    print()
    
    # Test 4: Downloads
    test_downloads(session_id)
    
    print()
    
    # Test 5: Session management
    test_session_management(session_id)
    
    print()
    print("🎉 Test suite completed!")
    print("Check the generated test files:")
    print("- test_highlighted.pdf")
    print("- test_keywords.txt") 
    print("- test_extracted_text.txt")

if __name__ == "__main__":
    main()