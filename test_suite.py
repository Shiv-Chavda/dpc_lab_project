"""
Test script for the Distributed Chat Application
Run various test scenarios to verify functionality
"""

import subprocess
import time
import sys
import os

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_server_start():
    """Test if server can start"""
    print_section("TEST 1: Server Startup")
    
    print("Starting server in background...")
    try:
        # Start server process
        server_process = subprocess.Popen(
            [sys.executable, "server.py", "--port", "5001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Check if still running
        if server_process.poll() is None:
            print("✓ Server started successfully!")
            print("✓ Server is running on port 5001")
            
            # Terminate server
            server_process.terminate()
            server_process.wait(timeout=5)
            print("✓ Server stopped cleanly")
            return True
        else:
            stdout, stderr = server_process.communicate()
            print("✗ Server failed to start")
            print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print_section("TEST 2: Module Imports")
    
    modules = [
        ("socket", "server.py, client_console.py, client_gui.py"),
        ("threading", "server.py, client_console.py, client_gui.py"),
        ("tkinter", "client_gui.py"),
        ("argparse", "server.py, client_console.py"),
        ("os", "all modules"),
    ]
    
    all_passed = True
    
    for module_name, used_in in modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name:15} - OK (used in {used_in})")
        except ImportError as e:
            print(f"✗ {module_name:15} - FAILED: {e}")
            if module_name == "tkinter":
                print("  Note: tkinter is optional. Console client will still work.")
            else:
                all_passed = False
    
    return all_passed

def test_file_structure():
    """Test if all required files exist"""
    print_section("TEST 3: File Structure")
    
    required_files = [
        "server.py",
        "client_console.py",
        "client_gui.py",
        "README.md",
        "QUICKSTART.md",
        "requirements.txt",
        "config.ini",
    ]
    
    all_exist = True
    
    for filename in required_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename:25} - {size:6} bytes")
        else:
            print(f"✗ {filename:25} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_code_syntax():
    """Test if Python files have valid syntax"""
    print_section("TEST 4: Code Syntax Check")
    
    py_files = ["server.py", "client_console.py", "client_gui.py"]
    all_valid = True
    
    for filename in py_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                compile(f.read(), filename, 'exec')
            print(f"✓ {filename:25} - Valid syntax")
        except SyntaxError as e:
            print(f"✗ {filename:25} - Syntax error: {e}")
            all_valid = False
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filename, 'r', encoding='latin-1') as f:
                    compile(f.read(), filename, 'exec')
                print(f"✓ {filename:25} - Valid syntax")
            except Exception as e:
                print(f"✗ {filename:25} - Error: {e}")
                all_valid = False
    
    return all_valid

def create_test_file():
    """Create a sample test file for file sharing tests"""
    print_section("TEST 5: Creating Test File")
    
    test_content = """Hello from Distributed Chat Application!

This is a test file for file sharing functionality.

Features tested:
- File upload
- File download
- File listing
- Metadata tracking

Created by test_suite.py
"""
    
    try:
        with open("sample_test_file.txt", "w") as f:
            f.write(test_content)
        
        size = os.path.getsize("sample_test_file.txt")
        print(f"✓ Created sample_test_file.txt ({size} bytes)")
        print("✓ You can use this file to test uploads:")
        print("  /upload sample_test_file.txt")
        return True
    except Exception as e:
        print(f"✗ Failed to create test file: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "█"*60)
    print("  DISTRIBUTED CHAT APPLICATION - TEST SUITE")
    print("█"*60)
    
    results = {}
    
    # Run all tests
    results["File Structure"] = test_file_structure()
    results["Module Imports"] = test_imports()
    results["Code Syntax"] = test_code_syntax()
    results["Test File Creation"] = create_test_file()
    results["Server Startup"] = test_server_start()
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:25} - {status}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 All tests passed! Your application is ready to use.")
        print("\nNext steps:")
        print("1. Start the server:    python server.py")
        print("2. Start a client:      python client_console.py")
        print("3. Or start GUI client: python client_gui.py")
        print("\nSee QUICKSTART.md for detailed instructions.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        if not results["Module Imports"] and "tkinter" in str(results):
            print("\nNote: If only tkinter import failed, you can still use")
            print("the console client (client_console.py).")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
