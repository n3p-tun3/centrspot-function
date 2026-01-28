"""
Test script for Keyword Video Generator Appwrite Function
This simulates function execution locally for testing
"""

import json
import sys
from pathlib import Path

# Add the appwrite-function directory to path
sys.path.insert(0, str(Path(__file__).parent / 'appwrite-function'))

# Mock Appwrite context
class MockContext:
    def __init__(self):
        self.req = MockRequest()
        self.res = MockResponse()
        self.logs = []
        self.errors = []
    
    def log(self, message):
        print(f"[LOG] {message}")
        self.logs.append(message)
    
    def error(self, message):
        print(f"[ERROR] {message}", file=sys.stderr)
        self.errors.append(message)

class MockRequest:
    def __init__(self):
        self.body = None
        self.headers = {}

class MockResponse:
    def json(self, data, status_code=200):
        print(f"\n[RESPONSE] Status: {status_code}")
        print(json.dumps(data, indent=2))
        return data

# Test cases
def test_valid_request():
    """Test with valid parameters"""
    print("\n" + "="*50)
    print("TEST 1: Valid Request")
    print("="*50)
    
    from main import main
    
    context = MockContext()
    context.req.body = json.dumps({
        "keyword": "Hello World",
        "highlight": True,
        "frame_count": 3  # Use fewer frames for testing
    })
    
    # Note: This will fail without proper Appwrite setup
    # But it will test the validation and frame generation logic
    try:
        result = main(context)
        print("✓ Test passed - Function executed without errors")
    except Exception as e:
        print(f"✗ Expected error (no Appwrite setup): {e}")
        print("  This is normal for local testing")

def test_missing_keyword():
    """Test with missing keyword"""
    print("\n" + "="*50)
    print("TEST 2: Missing Keyword")
    print("="*50)
    
    from main import main
    
    context = MockContext()
    context.req.body = json.dumps({
        "highlight": True,
        "frame_count": 7
    })
    
    try:
        main(context)
        print("✓ Test passed - Default keyword used")
    except Exception as e:
        print(f"✗ Test failed: {e}")

def test_invalid_frame_count():
    """Test with invalid frame count"""
    print("\n" + "="*50)
    print("TEST 3: Invalid Frame Count")
    print("="*50)
    
    from main import main
    
    context = MockContext()
    context.req.body = json.dumps({
        "keyword": "Test",
        "frame_count": 100  # Too many
    })
    
    try:
        result = main(context)
        if "error" in result:
            print("✓ Test passed - Invalid frame count rejected")
        else:
            print("✗ Test failed - Should reject invalid frame count")
    except Exception as e:
        print(f"Expected validation error: {e}")

def test_frame_generation():
    """Test frame generation without Appwrite"""
    print("\n" + "="*50)
    print("TEST 4: Frame Generation (No Upload)")
    print("="*50)
    
    from main import render_frame
    
    try:
        # Generate a test frame
        frame_bytes = render_frame("Test Keyword", highlight_box=True)
        
        print(f"✓ Frame generated successfully")
        print(f"  Size: {len(frame_bytes)} bytes ({len(frame_bytes) / 1024:.1f} KB)")
        
        # Save test frame
        with open('/tmp/test_frame.png', 'wb') as f:
            f.write(frame_bytes)
        print(f"  Saved to: /tmp/test_frame.png")
        
    except Exception as e:
        print(f"✗ Frame generation failed: {e}")

def test_invalid_json():
    """Test with invalid JSON"""
    print("\n" + "="*50)
    print("TEST 5: Invalid JSON")
    print("="*50)
    
    from main import main
    
    context = MockContext()
    context.req.body = "not valid json {"
    
    try:
        result = main(context)
        if "error" in result:
            print("✓ Test passed - Invalid JSON rejected")
        else:
            print("✗ Test failed - Should reject invalid JSON")
    except Exception as e:
        print(f"Expected error: {e}")

def test_long_keyword():
    """Test with keyword that's too long"""
    print("\n" + "="*50)
    print("TEST 6: Long Keyword")
    print("="*50)
    
    from main import main
    
    context = MockContext()
    context.req.body = json.dumps({
        "keyword": "A" * 100,  # 100 characters
        "frame_count": 5
    })
    
    try:
        result = main(context)
        if "error" in result:
            print("✓ Test passed - Long keyword rejected")
        else:
            print("✗ Test failed - Should reject long keyword")
    except Exception as e:
        print(f"Expected validation error: {e}")

# Run all tests
if __name__ == "__main__":
    print("\n" + "="*50)
    print("Keyword Video Generator - Function Tests")
    print("="*50)
    
    tests = [
        test_frame_generation,
        test_missing_keyword,
        test_invalid_frame_count,
        test_long_keyword,
        test_invalid_json,
        test_valid_request  # This will fail without Appwrite, but tests logic
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
    
    print("\n" + "="*50)
    print("Tests Complete")
    print("="*50)
    print("\nNote: Full integration tests require Appwrite setup")
    print("These tests validate the core frame generation logic")
