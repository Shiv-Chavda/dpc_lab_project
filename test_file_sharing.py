"""
Quick Test Script for File Sharing Fix
Run this after starting the server to verify file operations work correctly
"""

import os
import sys

def create_test_files():
    """Create sample files for testing"""
    print("Creating test files...")
    
    # Create small text file
    with open("test_small.txt", "w") as f:
        f.write("This is a small test file.\n" * 10)
    print("✓ Created test_small.txt (260 bytes)")
    
    # Create medium text file
    with open("test_medium.txt", "w") as f:
        f.write("This is a medium test file with more content.\n" * 100)
    print("✓ Created test_medium.txt (~4.6 KB)")
    
    # Create a binary file
    with open("test_binary.dat", "wb") as f:
        f.write(bytes(range(256)) * 100)
    print("✓ Created test_binary.dat (25.6 KB)")
    
    print("\n✅ Test files created successfully!")
    print("\nNext steps:")
    print("1. Start the server: python server.py")
    print("2. Start client(s): python client_gui.py")
    print("3. Upload these test files using the Upload button")
    print("4. Download them on another client")
    print("5. Verify files in downloads/ folder match originals")

def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    
    dirs = ["shared_files", "downloads"]
    for d in dirs:
        if os.path.exists(d):
            files = os.listdir(d)
            print(f"✓ {d}/ exists ({len(files)} files)")
            if files:
                print(f"  Files: {', '.join(files)}")
        else:
            print(f"✗ {d}/ does not exist (will be created automatically)")

def verify_files():
    """Verify test files exist"""
    print("\nVerifying test files...")
    
    test_files = ["test_small.txt", "test_medium.txt", "test_binary.dat"]
    for f in test_files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            print(f"✓ {f} exists ({size} bytes)")
        else:
            print(f"✗ {f} not found")

def compare_files(file1, file2):
    """Compare two files to verify they match"""
    if not os.path.exists(file1):
        print(f"✗ {file1} not found")
        return False
    
    if not os.path.exists(file2):
        print(f"✗ {file2} not found")
        return False
    
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        content1 = f1.read()
        content2 = f2.read()
        
        if content1 == content2:
            print(f"✓ {file1} and {file2} match perfectly!")
            return True
        else:
            print(f"✗ {file1} and {file2} do NOT match")
            return False

def test_upload_download():
    """Test file integrity after upload/download cycle"""
    print("\n=== File Integrity Test ===")
    print("This test compares original files with downloaded versions")
    print()
    
    test_files = ["test_small.txt", "test_medium.txt", "test_binary.dat"]
    
    for filename in test_files:
        original = filename
        downloaded = os.path.join("downloads", filename)
        
        if os.path.exists(original) and os.path.exists(downloaded):
            compare_files(original, downloaded)
        elif not os.path.exists(downloaded):
            print(f"⚠ {downloaded} not found - upload/download {filename} first")
        else:
            print(f"⚠ {original} not found - run create_test_files() first")

def main():
    """Main test menu"""
    print("=" * 70)
    print("  FILE SHARING FIX - TEST UTILITY")
    print("=" * 70)
    print()
    print("Choose an option:")
    print("  1. Create test files")
    print("  2. Check directories")
    print("  3. Verify test files exist")
    print("  4. Test file integrity (after upload/download)")
    print("  5. Run all checks")
    print("  q. Quit")
    print()
    
    choice = input("Enter choice: ").strip()
    
    if choice == "1":
        create_test_files()
    elif choice == "2":
        check_directories()
    elif choice == "3":
        verify_files()
    elif choice == "4":
        test_upload_download()
    elif choice == "5":
        create_test_files()
        print()
        check_directories()
        print()
        verify_files()
        print()
        test_upload_download()
    elif choice.lower() == "q":
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice")
    
    print()
    input("Press Enter to continue...")
    main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
