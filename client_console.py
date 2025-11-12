"""
Console-based Chat Client with File Sharing
Supports concurrent message sending/receiving and file operations
"""

import socket
import threading
import os
import sys

BUFFER_SIZE = 4096
running = True


def receive_messages(sock):
    """Continuously receive and display messages from server"""
    global running
    
    while running:
        try:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                print("\n[DISCONNECTED] Connection lost.")
                running = False
                break
            
            message = data.decode('utf-8', 'ignore')
            print(message, end='')
            
        except Exception as e:
            if running:
                print(f"\n[ERROR] Receive error: {e}")
            running = False
            break


def send_message(sock, message):
    """Send a message to the server"""
    try:
        sock.sendall(message.encode())
        return True
    except Exception as e:
        print(f"[ERROR] Send error: {e}")
        return False


def upload_file(sock, filepath):
    """Upload a file to the server"""
    try:
        if not os.path.exists(filepath):
            print("[ERROR] File not found!")
            return
        
        filename = os.path.basename(filepath)
        filesize = os.path.getsize(filepath)
        
        # Send upload command
        send_message(sock, "/upload")
        
        # Wait for server ready message
        response = sock.recv(BUFFER_SIZE).decode('utf-8', 'ignore')
        if "Ready to receive" not in response:
            print(f"[ERROR] {response}")
            return
        
        # Send file metadata
        metadata = f"{filename}|{filesize}"
        sock.sendall(metadata.encode())
        
        # Wait for server acknowledgment
        ack = sock.recv(BUFFER_SIZE)
        if ack != b"READY":
            print("[ERROR] Server not ready for file transfer")
            return
        
        # Send file data
        print(f"[UPLOAD] Uploading {filename} ({filesize} bytes)...")
        sent = 0
        
        with open(filepath, 'rb') as f:
            while sent < filesize:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                sock.sendall(chunk)
                sent += len(chunk)
                
                # Show progress
                progress = (sent / filesize) * 100
                print(f"\r[UPLOAD] Progress: {progress:.1f}%", end='')
        
        print()  # New line after progress
        
        # Wait for server confirmation
        # (Will be received by the receive_messages thread)
        
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")


def download_file(sock, filename, save_dir="downloads"):
    """Download a file from the server"""
    try:
        # Create downloads directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Send download command
        send_message(sock, "/download")
        
        # Send filename immediately (no prompt from server)
        sock.sendall(filename.encode())
        
        # Receive response
        response = sock.recv(BUFFER_SIZE).decode('utf-8', 'ignore')
        
        if response.startswith("ERROR"):
            print(f"[ERROR] {response.split('|')[1]}")
            return
        
        # Parse file size
        parts = response.split('|')
        if parts[0] != "OK":
            print("[ERROR] Invalid server response")
            return
        
        filesize = int(parts[1])
        
        # Send ready acknowledgment
        sock.sendall(b"READY")
        
        # Receive file data
        filepath = os.path.join(save_dir, filename)
        received = 0
        
        print(f"[DOWNLOAD] Downloading {filename} ({filesize} bytes)...")
        
        with open(filepath, 'wb') as f:
            while received < filesize:
                chunk = sock.recv(min(BUFFER_SIZE, filesize - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                
                # Show progress
                progress = (received / filesize) * 100
                print(f"\r[DOWNLOAD] Progress: {progress:.1f}%", end='')
        
        print()  # New line after progress
        
        if received == filesize:
            print(f"[SUCCESS] File saved to {filepath}")
        else:
            print("[ERROR] Download incomplete")
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")


def main():
    """Main client function"""
    import argparse
    
    ap = argparse.ArgumentParser(description="Chat Client with File Sharing")
    ap.add_argument("--host", default="127.0.0.1", help="Server host address")
    ap.add_argument("--port", type=int, default=5000, help="Server port")
    args = ap.parse_args()
    
    global running
    
    print("=" * 60)
    print("  DISTRIBUTED CHAT CLIENT")
    print("=" * 60)
    print(f"  Connecting to {args.host}:{args.port}...")
    print("=" * 60)
    print()
    
    try:
        # Connect to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((args.host, args.port))
        print("[CONNECTED] Successfully connected to server!\n")
        
        # Start receive thread
        receive_thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
        receive_thread.start()
        
        # Wait a moment for initial server messages
        import time
        time.sleep(0.5)
        
        # Main input loop
        print("\nYou can start typing messages or use commands.")
        print("Type /help to see available commands.\n")
        
        while running:
            try:
                message = input()
                
                if not running:
                    break
                
                if not message.strip():
                    continue
                
                # Handle special file operations
                if message.startswith("/upload "):
                    filepath = message[8:].strip()
                    upload_file(sock, filepath)
                
                elif message.startswith("/download "):
                    filename = message[10:].strip()
                    download_file(sock, filename)
                
                else:
                    # Send regular message or command
                    if not send_message(sock, message):
                        break
                    
                    if message == "/quit":
                        running = False
                        break
                        
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n[QUIT] Disconnecting...")
                send_message(sock, "/quit")
                break
        
        # Cleanup
        running = False
        sock.close()
        print("\n[DISCONNECTED] Connection closed.")
        
    except ConnectionRefusedError:
        print("[ERROR] Could not connect to server. Is it running?")
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
