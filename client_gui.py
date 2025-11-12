"""
GUI Chat Client with File Sharing
Tkinter-based graphical interface for better user experience
"""

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
import os

BUFFER_SIZE = 4096


class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Distributed Chat Client")
        self.root.geometry("800x600")
        
        self.sock = None
        self.running = False
        self.username = ""
        self.pause_receive = False  # Flag to pause receive thread during file operations
        
        self.create_connection_frame()
        
    def create_connection_frame(self):
        """Create connection setup UI"""
        self.conn_frame = tk.Frame(self.root, padx=20, pady=20)
        self.conn_frame.pack(expand=True, fill='both')
        
        # Title
        title = tk.Label(self.conn_frame, text="Distributed Chat Client", 
                        font=('Arial', 18, 'bold'))
        title.pack(pady=10)
        
        # Connection inputs
        input_frame = tk.Frame(self.conn_frame)
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Server Host:", font=('Arial', 10)).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.host_entry = tk.Entry(input_frame, width=20)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="Port:", font=('Arial', 10)).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.port_entry = tk.Entry(input_frame, width=20)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(input_frame, text="Your Name:", font=('Arial', 10)).grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.name_entry = tk.Entry(input_frame, width=20)
        self.name_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Connect button
        self.connect_btn = tk.Button(self.conn_frame, text="Connect", 
                                     command=self.connect_to_server,
                                     font=('Arial', 12, 'bold'),
                                     bg='#4CAF50', fg='white',
                                     padx=20, pady=10)
        self.connect_btn.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(self.conn_frame, text="", font=('Arial', 10))
        self.status_label.pack()
        
    def create_chat_frame(self):
        """Create main chat UI"""
        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Top bar with username and buttons
        top_frame = tk.Frame(self.chat_frame, bg='#2196F3', padx=10, pady=5)
        top_frame.pack(fill='x')
        
        tk.Label(top_frame, text=f"User: {self.username}", 
                font=('Arial', 12, 'bold'), bg='#2196F3', fg='white').pack(side='left')
        
        tk.Button(top_frame, text="Files", command=self.show_files,
                 bg='#fff', padx=10).pack(side='right', padx=2)
        tk.Button(top_frame, text="Users", command=self.show_users,
                 bg='#fff', padx=10).pack(side='right', padx=2)
        tk.Button(top_frame, text="Upload", command=self.upload_file,
                 bg='#fff', padx=10).pack(side='right', padx=2)
        
        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, 
                                                   wrap=tk.WORD,
                                                   state='disabled',
                                                   font=('Courier', 10),
                                                   bg='#f5f5f5')
        self.chat_area.pack(expand=True, fill='both', pady=5)
        
        # Message input area
        input_frame = tk.Frame(self.chat_frame)
        input_frame.pack(fill='x', pady=5)
        
        self.message_entry = tk.Entry(input_frame, font=('Arial', 11))
        self.message_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        self.send_btn = tk.Button(input_frame, text="Send", 
                                  command=self.send_message,
                                  bg='#4CAF50', fg='white',
                                  font=('Arial', 10, 'bold'),
                                  padx=20)
        self.send_btn.pack(side='right')
        
        self.message_entry.focus()
        
    def connect_to_server(self):
        """Connect to the chat server"""
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        self.username = self.name_entry.get().strip()
        
        if not host or not port:
            messagebox.showerror("Error", "Please enter host and port!")
            return
        
        if not self.username:
            self.username = f"User_{os.getpid()}"
        
        try:
            port = int(port)
            
            self.status_label.config(text="Connecting...", fg="blue")
            self.connect_btn.config(state='disabled')
            
            # Create socket and connect
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            
            self.running = True
            
            # Switch to chat interface FIRST (before starting receive thread)
            self.conn_frame.destroy()
            self.create_chat_frame()
            
            # Wait for server prompt and send username
            import time
            time.sleep(0.2)
            self.sock.sendall(self.username.encode())
            
            # NOW start receive thread (after chat_area exists)
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid port number!")
            self.connect_btn.config(state='normal')
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Could not connect to server. Is it running?")
            self.connect_btn.config(state='normal')
            self.status_label.config(text="Connection failed", fg="red")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {e}")
            self.connect_btn.config(state='normal')
            self.status_label.config(text="Connection failed", fg="red")
    
    def receive_messages(self):
        """Continuously receive messages from server"""
        import time
        while self.running:
            try:
                # Pause receiving if file operation is in progress
                if self.pause_receive:
                    time.sleep(0.1)
                    continue
                
                data = self.sock.recv(BUFFER_SIZE)
                if not data:
                    self.running = False
                    self.display_message("\n[DISCONNECTED] Connection lost.\n", 'red')
                    break
                
                message = data.decode('utf-8', 'ignore')
                self.display_message(message)
                
            except Exception as e:
                if self.running:
                    self.display_message(f"\n[ERROR] {e}\n", 'red')
                self.running = False
                break
    
    def display_message(self, message, color='black'):
        """Display message in chat area"""
        # Safety check: ensure chat_area exists
        if not hasattr(self, 'chat_area') or self.chat_area is None:
            return
        
        self.chat_area.config(state='normal')
        
        # Add color tags for different message types
        if '[ERROR]' in message or 'DISCONNECTED' in message:
            self.chat_area.insert(tk.END, message, 'error')
        elif '[SUCCESS]' in message or 'uploaded' in message:
            self.chat_area.insert(tk.END, message, 'success')
        elif '[FILE]' in message or '[DOWNLOAD]' in message or '[UPLOAD]' in message:
            self.chat_area.insert(tk.END, message, 'file')
        elif '*' in message and 'joined' in message:
            self.chat_area.insert(tk.END, message, 'join')
        elif '*' in message and 'left' in message:
            self.chat_area.insert(tk.END, message, 'leave')
        else:
            self.chat_area.insert(tk.END, message)
        
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
        
        # Configure tags
        self.chat_area.tag_config('error', foreground='red')
        self.chat_area.tag_config('success', foreground='green')
        self.chat_area.tag_config('file', foreground='blue')
        self.chat_area.tag_config('join', foreground='green', font=('Courier', 10, 'bold'))
        self.chat_area.tag_config('leave', foreground='orange', font=('Courier', 10, 'bold'))
    
    def send_message(self):
        """Send message to server"""
        message = self.message_entry.get().strip()
        
        if not message:
            return
        
        try:
            self.sock.sendall(message.encode())
            self.message_entry.delete(0, tk.END)
            
            if message == "/quit":
                self.running = False
                self.sock.close()
                self.root.destroy()
                
        except Exception as e:
            self.display_message(f"\n[ERROR] Send failed: {e}\n", 'red')
    
    def show_users(self):
        """Request and display user list"""
        try:
            self.sock.sendall(b"/users")
        except Exception as e:
            self.display_message(f"\n[ERROR] {e}\n", 'red')
    
    def show_files(self):
        """Show available files and download options"""
        try:
            # Request file list
            self.sock.sendall(b"/files")
            
            # Create file dialog
            file_window = tk.Toplevel(self.root)
            file_window.title("Shared Files")
            file_window.geometry("500x400")
            
            tk.Label(file_window, text="Shared Files", 
                    font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Instructions
            tk.Label(file_window, text="Enter filename below to download:", 
                    font=('Arial', 10)).pack(pady=5)
            
            # Download frame
            dl_frame = tk.Frame(file_window)
            dl_frame.pack(pady=10)
            
            filename_entry = tk.Entry(dl_frame, width=30, font=('Arial', 10))
            filename_entry.pack(side='left', padx=5)
            
            def download():
                filename = filename_entry.get().strip()
                if filename:
                    self.download_file(filename)
                    file_window.destroy()
            
            tk.Button(dl_frame, text="Download", command=download,
                     bg='#2196F3', fg='white', padx=15).pack(side='left')
            
            tk.Button(file_window, text="Close", command=file_window.destroy,
                     padx=20, pady=5).pack(pady=10)
            
        except Exception as e:
            self.display_message(f"\n[ERROR] {e}\n", 'red')
    
    def upload_file(self):
        """Upload a file to server"""
        filepath = filedialog.askopenfilename(title="Select file to upload")
        
        if not filepath:
            return
        
        try:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            # Pause the receive thread temporarily for file upload
            self.pause_receive = True
            
            # Send upload command
            self.sock.sendall(b"/upload")
            
            # Wait for server ready message
            import time
            time.sleep(0.1)
            ready_msg = self.sock.recv(BUFFER_SIZE)
            
            # Check if server is ready
            if b"Ready to receive" not in ready_msg:
                self.display_message(f"[ERROR] Unexpected response: {ready_msg.decode()}\n", 'red')
                self.pause_receive = False
                return
            
            # Send file metadata
            metadata = f"{filename}|{filesize}"
            self.sock.sendall(metadata.encode())
            
            # Wait for acknowledgment
            ack = self.sock.recv(BUFFER_SIZE)
            if ack != b"READY":
                self.display_message("[ERROR] Server not ready for transfer\n", 'red')
                self.pause_receive = False
                return
            
            # Send file data
            self.display_message(f"[UPLOAD] Uploading {filename} ({filesize} bytes)...\n", 'blue')
            
            with open(filepath, 'rb') as f:
                sent = 0
                while sent < filesize:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    self.sock.sendall(chunk)
                    sent += len(chunk)
            
            # Resume receive thread
            self.pause_receive = False
            
            self.display_message(f"[UPLOAD] Upload complete! Waiting for confirmation...\n", 'green')
            
        except Exception as e:
            self.display_message(f"\n[ERROR] Upload failed: {e}\n", 'red')
            self.pause_receive = False
    
    def download_file(self, filename):
        """Download a file from server"""
        save_dir = "downloads"
        
        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Pause the receive thread for file download
            self.pause_receive = True
            
            # Send download command
            self.sock.sendall(b"/download")
            
            # Wait for prompt
            import time
            time.sleep(0.1)
            prompt = self.sock.recv(BUFFER_SIZE)
            
            # Send filename
            self.sock.sendall(filename.encode())
            
            # Receive response
            response = self.sock.recv(BUFFER_SIZE).decode('utf-8', 'ignore')
            
            if response.startswith("ERROR"):
                self.display_message(f"[ERROR] {response.split('|')[1]}\n", 'red')
                self.pause_receive = False
                return
            
            # Parse file size
            parts = response.split('|')
            if parts[0] != "OK":
                self.display_message("[ERROR] Invalid server response\n", 'red')
                self.pause_receive = False
                return
            
            filesize = int(parts[1])
            
            # Send ready acknowledgment
            self.sock.sendall(b"READY")
            
            # Receive file data
            filepath = os.path.join(save_dir, filename)
            received = 0
            
            self.display_message(f"[DOWNLOAD] Downloading {filename} ({filesize} bytes)...\n", 'blue')
            
            with open(filepath, 'wb') as f:
                while received < filesize:
                    chunk = self.sock.recv(min(BUFFER_SIZE, filesize - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            
            # Resume receive thread
            self.pause_receive = False
            
            if received == filesize:
                self.display_message(f"[SUCCESS] File saved to {filepath}\n", 'green')
                messagebox.showinfo("Success", f"File downloaded to {filepath}")
            else:
                self.display_message("[ERROR] Download incomplete\n", 'red')
                
        except Exception as e:
            self.display_message(f"\n[ERROR] Download failed: {e}\n", 'red')
            self.pause_receive = False


def main():
    root = tk.Tk()
    app = ChatClientGUI(root)
    
    def on_closing():
        app.running = False
        if app.sock:
            try:
                app.sock.close()
            except:
                pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
