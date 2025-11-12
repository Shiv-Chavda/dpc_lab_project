"""
Distributed Chat Server with File Sharing
Handles multiple clients concurrently with chat and file sharing capabilities
"""

import socket
import threading
import os
import json
import time
from datetime import datetime

# Global data structures
clients = {}  # {conn: {"name": str, "addr": tuple}}
files_shared = {}  # {filename: {"uploader": str, "timestamp": str, "size": int}}
files_lock = threading.Lock()
clients_lock = threading.Lock()

# Configuration
BUFFER_SIZE = 4096
FILE_STORAGE_DIR = "shared_files"

# Ensure file storage directory exists
if not os.path.exists(FILE_STORAGE_DIR):
    os.makedirs(FILE_STORAGE_DIR)


def broadcast(msg, exclude=None):
    """Send message to all connected clients except the excluded one"""
    with clients_lock:
        for conn in list(clients.keys()):
            if conn is exclude:
                continue
            try:
                conn.sendall(msg)
            except Exception:
                cleanup_client(conn)


def cleanup_client(conn):
    """Remove client and close connection"""
    try:
        conn.close()
    except Exception:
        pass
    with clients_lock:
        clients.pop(conn, None)


def send_file_list(conn):
    """Send the list of available files to a client"""
    with files_lock:
        if not files_shared:
            conn.sendall(b"[FILES] No files available yet.\n")
        else:
            msg = "[FILES] Available files:\n"
            for idx, (filename, info) in enumerate(files_shared.items(), 1):
                msg += f"  {idx}. {filename} ({info['size']} bytes) - uploaded by {info['uploader']} at {info['timestamp']}\n"
            conn.sendall(msg.encode())


def handle_file_upload(conn, client_info):
    """Handle file upload from client"""
    filepath = None
    try:
        print(f"[FILE] Upload request from {client_info['name']}")
        
        # Receive filename and size
        conn.settimeout(30)  # Set timeout for file operations
        print(f"[FILE] Waiting for metadata from {client_info['name']}...")
        metadata = conn.recv(BUFFER_SIZE).decode('utf-8', 'ignore').strip()
        
        if not metadata:
            print(f"[ERROR] No metadata received from {client_info['name']}")
            conn.sendall(b"[ERROR] No metadata received\n")
            return
        
        print(f"[FILE] Received metadata: {metadata}")
        
        parts = metadata.split('|')
        if len(parts) != 2:
            print(f"[ERROR] Invalid metadata format from {client_info['name']}: {metadata}")
            conn.sendall(b"[ERROR] Invalid file metadata\n")
            return
        
        filename = parts[0]
        try:
            filesize = int(parts[1])
        except ValueError:
            print(f"[ERROR] Invalid file size from {client_info['name']}: {parts[1]}")
            conn.sendall(b"[ERROR] Invalid file size\n")
            return
        
        print(f"[FILE] File: {filename}, Size: {filesize} bytes")
        
        # Send acknowledgment
        conn.sendall(b"READY")
        print(f"[FILE] Sent READY acknowledgment to {client_info['name']}")
        
        # Receive file data
        filepath = os.path.join(FILE_STORAGE_DIR, filename)
        received = 0
        
        print(f"[FILE] Receiving {filename} ({filesize} bytes) from {client_info['name']}...")
        
        with open(filepath, 'wb') as f:
            while received < filesize:
                remaining = filesize - received
                chunk_size = min(BUFFER_SIZE, remaining)
                chunk = conn.recv(chunk_size)
                
                if not chunk:
                    print(f"[ERROR] Connection lost while receiving file (received {received}/{filesize})")
                    break
                
                f.write(chunk)
                received += len(chunk)
                
                # Progress update every 1MB
                if received % (1024 * 1024) < BUFFER_SIZE or received == filesize:
                    progress = (received / filesize) * 100
                    print(f"[FILE] Progress: {received}/{filesize} bytes ({progress:.1f}%)")
        
        conn.settimeout(None)  # Reset timeout
        
        if received == filesize:
            # Store file metadata
            with files_lock:
                files_shared[filename] = {
                    "uploader": client_info["name"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "size": filesize
                }
            
            success_msg = f"[SUCCESS] File '{filename}' uploaded successfully!\n"
            conn.sendall(success_msg.encode())
            
            # Notify all users
            notification = f"[FILE] {client_info['name']} uploaded '{filename}' ({filesize} bytes)\n".encode()
            broadcast(notification, exclude=conn)
            print(f"[FILE] ✓ {filename} uploaded successfully by {client_info['name']}")
        else:
            error_msg = f"[ERROR] File upload incomplete (received {received}/{filesize} bytes)\n"
            conn.sendall(error_msg.encode())
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"[ERROR] Removed incomplete file: {filename}")
                
    except socket.timeout:
        print(f"[ERROR] File upload timeout for {client_info['name']}")
        try:
            conn.sendall(b"[ERROR] Upload timeout\n")
        except:
            pass
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"[ERROR] File upload error from {client_info['name']}: {e}")
        try:
            conn.sendall(f"[ERROR] Upload failed: {e}\n".encode())
        except:
            pass
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    finally:
        try:
            conn.settimeout(None)  # Ensure timeout is reset
        except:
            pass


def handle_file_download(conn, client_info):
    """Handle file download request from client"""
    try:
        print(f"[FILE] Download request from {client_info['name']}")
        
        # Receive filename
        conn.settimeout(30)  # Set timeout for file operations
        print(f"[FILE] Waiting for filename from {client_info['name']}...")
        filename = conn.recv(BUFFER_SIZE).decode('utf-8', 'ignore').strip()
        
        if not filename:
            print(f"[ERROR] No filename received from {client_info['name']}")
            return
        
        print(f"[FILE] Requested file: {filename}")
        
        filepath = os.path.join(FILE_STORAGE_DIR, filename)
        
        with files_lock:
            if filename not in files_shared:
                print(f"[ERROR] File '{filename}' not in shared files list")
                conn.sendall(b"ERROR|File not found")
                conn.settimeout(None)
                return
        
        if not os.path.exists(filepath):
            print(f"[ERROR] File '{filename}' not found on disk")
            conn.sendall(b"ERROR|File not found on server")
            conn.settimeout(None)
            return
        
        # Send file size
        filesize = os.path.getsize(filepath)
        response = f"OK|{filesize}"
        conn.sendall(response.encode())
        print(f"[FILE] Sent file info: {response}")
        
        # Wait for client acknowledgment
        print(f"[FILE] Waiting for READY acknowledgment from {client_info['name']}...")
        ack = conn.recv(BUFFER_SIZE)
        
        if ack != b"READY":
            print(f"[ERROR] Invalid acknowledgment from {client_info['name']}: {ack}")
            conn.settimeout(None)
            return
        
        print(f"[FILE] Sending {filename} ({filesize} bytes) to {client_info['name']}...")
        
        # Set to blocking mode for file transfer
        conn.settimeout(None)
        
        # Send file data
        sent = 0
        with open(filepath, 'rb') as f:
            while sent < filesize:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                conn.sendall(chunk)
                sent += len(chunk)
                
                # Progress update every 1MB
                if sent % (1024 * 1024) < BUFFER_SIZE or sent == filesize:
                    progress = (sent / filesize) * 100
                    print(f"[FILE] Download progress: {sent}/{filesize} bytes ({progress:.1f}%)")
        
        print(f"[FILE] ✓ {filename} sent successfully to {client_info['name']}")
        
    except socket.timeout:
        print(f"[ERROR] File download timeout for {client_info['name']}")
    except Exception as e:
        print(f"[ERROR] File download error for {client_info['name']}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Always reset timeout to None after file operations
        try:
            conn.settimeout(None)
        except:
            pass


def handle_client(conn, addr):
    """Handle individual client connection"""
    client_info = {"name": None, "addr": addr}
    
    try:
        # Get client name
        conn.sendall(b"Enter your name: ")
        name = conn.recv(1024).decode('utf-8', 'ignore').strip()
        
        if not name:
            name = f"User_{addr[0]}:{addr[1]}"
        
        client_info["name"] = name
        
        with clients_lock:
            clients[conn] = client_info
        
        # Notify all users about new join
        join_msg = f"* {name} joined the chat *\n".encode()
        print(f"[JOIN] {name} connected from {addr}")
        broadcast(join_msg)
        
        # Send welcome message and instructions
        welcome = f"""
Welcome to the Distributed Chat, {name}!
Commands:
  /quit          - Exit the chat
  /users         - List online users
  /files         - List shared files
  /upload        - Upload a file
  /download      - Download a file
  /help          - Show this help message

Type your message to chat with everyone!
----------------------------------------
"""
        conn.sendall(welcome.encode())
        
        # Main message loop
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break
            
            text = data.decode('utf-8', 'ignore').strip()
            
            if not text:
                continue
            
            # Handle commands
            if text == "/quit":
                conn.sendall(b"[BYE] Goodbye!\n")
                break
            
            elif text == "/users":
                with clients_lock:
                    users_list = "[USERS] Online users:\n"
                    for idx, info in enumerate(clients.values(), 1):
                        users_list += f"  {idx}. {info['name']}\n"
                    conn.sendall(users_list.encode())
            
            elif text == "/files":
                send_file_list(conn)
            
            elif text == "/upload":
                conn.sendall(b"[UPLOAD] Ready to receive file. Send metadata.\n")
                handle_file_upload(conn, client_info)
            
            elif text == "/download":
                # Don't send prompt - client already knows what file to request
                handle_file_download(conn, client_info)
            
            elif text == "/help":
                conn.sendall(welcome.encode())
            
            else:
                # Regular chat message
                timestamp = datetime.now().strftime("%H:%M:%S")
                msg = f"[{timestamp}] {name}: {text}\n".encode()
                print(f"[CHAT] {name}: {text}")
                broadcast(msg)  # Broadcast to all clients including sender
                
    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    
    finally:
        # Client disconnected
        with clients_lock:
            client_data = clients.pop(conn, None)
        
        try:
            conn.close()
        except Exception:
            pass
        
        if client_data:
            leave_msg = f"* {client_data['name']} left the chat *\n".encode()
            print(f"[LEAVE] {client_data['name']} disconnected")
            broadcast(leave_msg)


def main():
    """Main server function"""
    import argparse
    
    ap = argparse.ArgumentParser(description="Distributed Chat Server with File Sharing")
    ap.add_argument("--host", default="0.0.0.0", help="Server host address")
    ap.add_argument("--port", type=int, default=5000, help="Server port")
    args = ap.parse_args()
    
    print("=" * 60)
    print("  DISTRIBUTED CHAT SERVER WITH FILE SHARING")
    print("=" * 60)
    print(f"  Host: {args.host}")
    print(f"  Port: {args.port}")
    print(f"  File Storage: {os.path.abspath(FILE_STORAGE_DIR)}")
    print("=" * 60)
    print()
    
    try:
        with socket.create_server((args.host, args.port), reuse_port=False) as server_socket:
            server_socket.listen()
            print(f"[SERVER] Listening on {args.host}:{args.port}")
            print("[SERVER] Waiting for connections...\n")
            
            while True:
                conn, addr = server_socket.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                thread.start()
                
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    except Exception as e:
        print(f"[ERROR] Server error: {e}")


if __name__ == "__main__":
    main()
