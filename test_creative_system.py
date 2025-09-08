#!/usr/bin/env python3
"""
Creative Projects System test script for MindForge
"""

import requests
import json
import os
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check: PASS")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Health check: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
        return False

def test_api_status():
    """Test API status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ API status: PASS")
            print(f"   Version: {data.get('api_version', 'N/A')}")
            return True
        else:
            print(f"❌ API status: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API status: ERROR - {e}")
        return False

def test_creative_projects_endpoint():
    """Test creative projects endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/creative/projects")
        if response.status_code == 200:
            print("✅ Creative projects endpoint: PASS")
            return True
        else:
            print(f"❌ Creative projects endpoint: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Creative projects endpoint: ERROR - {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("🧪 Running MindForge Creative Projects System Tests\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("API Status", test_api_status),
        ("Creative Projects Endpoint", test_creative_projects_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Creative projects system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python test_creative_system.py [test_name]")
        print("Available tests: health, status, projects, all")
        sys.exit(0)
    
    test_name = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if test_name == "health":
        test_health_check()
    elif test_name == "status":
        test_api_status()
    elif test_name == "projects":
        test_creative_projects_endpoint()
    else:
        run_all_tests()
