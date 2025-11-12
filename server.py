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
    try:
        # Receive filename and size
        metadata = conn.recv(BUFFER_SIZE).decode('utf-8', 'ignore').strip()
        if not metadata:
            return
        
        parts = metadata.split('|')
        if len(parts) != 2:
            conn.sendall(b"[ERROR] Invalid file metadata\n")
            return
        
        filename = parts[0]
        filesize = int(parts[1])
        
        # Send acknowledgment
        conn.sendall(b"READY")
        
        # Receive file data
        filepath = os.path.join(FILE_STORAGE_DIR, filename)
        received = 0
        
        with open(filepath, 'wb') as f:
            while received < filesize:
                chunk = conn.recv(min(BUFFER_SIZE, filesize - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
        
        if received == filesize:
            # Store file metadata
            with files_lock:
                files_shared[filename] = {
                    "uploader": client_info["name"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "size": filesize
                }
            
            conn.sendall(b"[SUCCESS] File uploaded successfully!\n")
            
            # Notify all users
            notification = f"[FILE] {client_info['name']} uploaded '{filename}' ({filesize} bytes)\n".encode()
            broadcast(notification)
            print(f"[FILE] {filename} uploaded by {client_info['name']}")
        else:
            conn.sendall(b"[ERROR] File upload incomplete\n")
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        print(f"[ERROR] File upload error: {e}")
        conn.sendall(f"[ERROR] Upload failed: {e}\n".encode())


def handle_file_download(conn, client_info):
    """Handle file download request from client"""
    try:
        # Receive filename
        filename = conn.recv(BUFFER_SIZE).decode('utf-8', 'ignore').strip()
        if not filename:
            return
        
        filepath = os.path.join(FILE_STORAGE_DIR, filename)
        
        with files_lock:
            if filename not in files_shared:
                conn.sendall(b"ERROR|File not found")
                return
        
        if not os.path.exists(filepath):
            conn.sendall(b"ERROR|File not found on server")
            return
        
        # Send file size
        filesize = os.path.getsize(filepath)
        conn.sendall(f"OK|{filesize}".encode())
        
        # Wait for client acknowledgment
        ack = conn.recv(BUFFER_SIZE)
        if ack != b"READY":
            return
        
        # Send file data
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                conn.sendall(chunk)
        
        print(f"[FILE] {filename} downloaded by {client_info['name']}")
        
    except Exception as e:
        print(f"[ERROR] File download error: {e}")


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
                conn.sendall(b"[DOWNLOAD] Enter filename: ")
                handle_file_download(conn, client_info)
            
            elif text == "/help":
                conn.sendall(welcome.encode())
            
            else:
                # Regular chat message
                timestamp = datetime.now().strftime("%H:%M:%S")
                msg = f"[{timestamp}] {name}: {text}\n".encode()
                print(f"[CHAT] {name}: {text}")
                broadcast(msg, exclude=conn)
                
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
