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
        self.root.geometry("960x620")
        self.root.minsize(820, 540)

        # Base colors / theme
        self.bg_main = "#0f172a"  # slate-900
        self.bg_panel = "#020617"  # slate-950
        self.bg_accent = "#1d4ed8"  # blue-700
        self.bg_accent_soft = "#1e293b"  # slate-800
        self.fg_primary = "#e5e7eb"  # gray-200
        self.fg_muted = "#9ca3af"  # gray-400
        self.success_color = "#22c55e"  # green-500
        self.error_color = "#ef4444"  # red-500
        self.file_color = "#38bdf8"  # sky-400
        self.join_color = "#22c55e"  # green-500
        self.leave_color = "#f97316"  # orange-400

        self.root.configure(bg=self.bg_main)

        self.sock = None
        self.running = False
        self.username = ""
        self.receive_lock = threading.Lock()  # Lock for coordinating file operations

        self.create_connection_frame()
        
    def create_connection_frame(self):
        """Create connection setup UI"""
        self.conn_frame = tk.Frame(self.root, padx=32, pady=32, bg=self.bg_main)
        self.conn_frame.pack(expand=True, fill="both")

        card = tk.Frame(self.conn_frame, bg=self.bg_panel, bd=0, relief="flat")
        card.pack(expand=True, ipadx=24, ipady=24)

        # Title
        title = tk.Label(
            card,
            text="Distributed Chat Client",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_panel,
            fg=self.fg_primary,
        )
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            card,
            text="Connect, chat and share files with the lab server",
            font=("Segoe UI", 10),
            bg=self.bg_panel,
            fg=self.fg_muted,
        )
        subtitle.pack(pady=(0, 18))

        # Connection inputs
        input_frame = tk.Frame(card, bg=self.bg_panel)
        input_frame.pack(pady=10)

        label_kwargs = {"font": ("Segoe UI", 10), "bg": self.bg_panel, "fg": self.fg_muted}
        entry_kwargs = {"width": 24, "font": ("Segoe UI", 10), "bg": self.bg_accent_soft, "fg": self.fg_primary,
                        "insertbackground": self.fg_primary, "borderwidth": 0, "relief": "flat"}

        tk.Label(input_frame, text="Server Host", **label_kwargs).grid(row=0, column=0, sticky="w", padx=5, pady=6)
        self.host_entry = tk.Entry(input_frame, **entry_kwargs)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=0, column=1, padx=5, pady=6)

        tk.Label(input_frame, text="Port", **label_kwargs).grid(row=1, column=0, sticky="w", padx=5, pady=6)
        self.port_entry = tk.Entry(input_frame, **entry_kwargs)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=1, column=1, padx=5, pady=6)

        tk.Label(input_frame, text="Your Name", **label_kwargs).grid(row=2, column=0, sticky="w", padx=5, pady=6)
        self.name_entry = tk.Entry(input_frame, **entry_kwargs)
        self.name_entry.grid(row=2, column=1, padx=5, pady=6)

        # Connect button
        self.connect_btn = tk.Button(
            card,
            text="Connect to Server",
            command=self.connect_to_server,
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_accent,
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            padx=26,
            pady=10,
            borderwidth=0,
            relief="flat",
            cursor="hand2",
        )
        self.connect_btn.pack(pady=(18, 8))

        # Status label
        self.status_label = tk.Label(
            card,
            text="",
            font=("Segoe UI", 9),
            bg=self.bg_panel,
            fg=self.fg_muted,
        )
        self.status_label.pack(pady=(4, 0))
        
    def create_chat_frame(self):
        """Create main chat UI"""
        self.chat_frame = tk.Frame(self.root, bg=self.bg_main)
        self.chat_frame.pack(expand=True, fill="both", padx=16, pady=16)

        # Main layout: left = chat, right = side panel
        main_pane = tk.Frame(self.chat_frame, bg=self.bg_main)
        main_pane.pack(expand=True, fill="both")

        # Top bar with username and controls
        top_frame = tk.Frame(main_pane, bg=self.bg_panel, padx=14, pady=8)
        top_frame.pack(fill="x", side="top")

        tk.Label(
            top_frame,
            text=f"{self.username}",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_panel,
            fg=self.fg_primary,
        ).pack(side="left")

        tk.Label(
            top_frame,
            text="Connected to chat server",
            font=("Segoe UI", 9),
            bg=self.bg_panel,
            fg=self.fg_muted,
        ).pack(side="left", padx=(8, 0))

        def make_top_button(text, command):
            return tk.Button(
                top_frame,
                text=text,
                command=command,
                font=("Segoe UI", 9, "bold"),
                bg=self.bg_accent_soft,
                fg=self.fg_primary,
                activebackground="#1f2937",
                activeforeground=self.fg_primary,
                padx=14,
                pady=5,
                borderwidth=0,
                relief="flat",
                cursor="hand2",
            )

        make_top_button("Upload", self.upload_file).pack(side="right", padx=(4, 0))
        make_top_button("Files", self.show_files).pack(side="right", padx=(4, 0))
        make_top_button("Users", self.show_users).pack(side="right", padx=(4, 0))

        # Content area
        content_frame = tk.Frame(main_pane, bg=self.bg_main)
        content_frame.pack(expand=True, fill="both", pady=(8, 0))

        # Left: chat area
        chat_container = tk.Frame(content_frame, bg=self.bg_main)
        chat_container.pack(side="left", expand=True, fill="both")

        self.chat_area = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            state="disabled",
            font=("Consolas", 10),
            bg=self.bg_accent_soft,
            fg=self.fg_primary,
            insertbackground=self.fg_primary,
            borderwidth=0,
            relief="flat",
        )
        self.chat_area.pack(expand=True, fill="both")

        # Right: quick help / legend
        side_panel = tk.Frame(
            content_frame,
            bg=self.bg_panel,
            width=220,
            padx=10,
            pady=10,
        )
        side_panel.pack(side="right", fill="y", padx=(8, 0))

        tk.Label(
            side_panel,
            text="Commands",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_panel,
            fg=self.fg_primary,
        ).pack(anchor="w", pady=(0, 4))

        commands_text = (
            "/users  - list online users\n"
            "/files  - list shared files\n"
            "/upload - upload a file\n"
            "/download - download a file\n"
            "/quit   - leave chat"
        )

        tk.Label(
            side_panel,
            text=commands_text,
            font=("Segoe UI", 9),
            justify="left",
            bg=self.bg_panel,
            fg=self.fg_muted,
        ).pack(anchor="w")

        tk.Label(
            side_panel,
            text="Legend",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_panel,
            fg=self.fg_primary,
        ).pack(anchor="w", pady=(12, 4))

        legend_items = [
            ("System / errors", self.error_color),
            ("Uploads / downloads", self.file_color),
            ("Join / leave", self.join_color),
        ]

        for text, color in legend_items:
            row = tk.Frame(side_panel, bg=self.bg_panel)
            row.pack(anchor="w", pady=1)
            tk.Label(row, width=2, bg=color).pack(side="left", padx=(0, 6))
            tk.Label(
                row,
                text=text,
                font=("Segoe UI", 9),
                bg=self.bg_panel,
                fg=self.fg_muted,
            ).pack(side="left")

        # Message input area
        input_frame = tk.Frame(self.chat_frame, bg=self.bg_main, pady=6)
        input_frame.pack(fill="x")

        self.message_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 10),
            bg=self.bg_accent_soft,
            fg=self.fg_primary,
            insertbackground=self.fg_primary,
            borderwidth=0,
            relief="flat",
        )
        self.message_entry.pack(side="left", expand=True, fill="x", padx=(0, 6), ipady=6)
        self.message_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg=self.bg_accent,
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=24,
            pady=6,
            borderwidth=0,
            relief="flat",
            cursor="hand2",
        )
        self.send_btn.pack(side="right")

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
        while self.running:
            try:
                # Try to acquire lock with timeout - if file operation is in progress, skip
                if self.receive_lock.acquire(blocking=False):
                    try:
                        self.sock.settimeout(1.0)  # Use timeout to allow clean shutdown
                        data = self.sock.recv(BUFFER_SIZE)
                        
                        if not data:
                            self.running = False
                            self.display_message("\n[DISCONNECTED] Connection lost.\n", 'red')
                            break
                        
                        message = data.decode('utf-8', 'ignore')
                        self.display_message(message)
                    finally:
                        self.receive_lock.release()
                else:
                    # Lock is held by file operation, wait a bit
                    import time
                    time.sleep(0.1)
                
            except socket.timeout:
                # Timeout is normal, just continue
                continue
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
        self.chat_area.tag_config('error', foreground=self.error_color)
        self.chat_area.tag_config('success', foreground=self.success_color)
        self.chat_area.tag_config('file', foreground=self.file_color)
        self.chat_area.tag_config('join', foreground=self.join_color, font=('Consolas', 10, 'bold'))
        self.chat_area.tag_config('leave', foreground=self.leave_color, font=('Consolas', 10, 'bold'))
    
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
        
        # Run upload in a separate thread to avoid blocking GUI
        upload_thread = threading.Thread(target=self._upload_file_thread, args=(filepath,), daemon=True)
        upload_thread.start()
    
    def _upload_file_thread(self, filepath):
        """Thread function to handle file upload"""
        import time
        try:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            # Use lock to serialize socket access
            with self.receive_lock:
                # Temporarily set socket to blocking mode with longer timeout
                self.sock.settimeout(30.0)
                
                # Send upload command
                self.sock.sendall(b"/upload")
                
                # Wait for server ready message
                ready_msg = self.sock.recv(BUFFER_SIZE)
                
                # Check if server is ready
                if b"Ready to receive" not in ready_msg:
                    self.display_message(f"[ERROR] Unexpected response: {ready_msg.decode()}\n", 'red')
                    self.sock.settimeout(1.0)
                    return
                
                # Send file metadata
                metadata = f"{filename}|{filesize}"
                self.sock.sendall(metadata.encode())
                
                # Wait for acknowledgment
                ack = self.sock.recv(BUFFER_SIZE)
                if ack != b"READY":
                    self.display_message("[ERROR] Server not ready for transfer\n", 'red')
                    self.sock.settimeout(1.0)
                    return
                
                # Send file data
                self.display_message(f"[UPLOAD] Uploading {filename} ({filesize} bytes)...\n", 'blue')
                
                sent = 0
                with open(filepath, 'rb') as f:
                    while sent < filesize:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        self.sock.sendall(chunk)
                        sent += len(chunk)
                
                # Wait for confirmation
                try:
                    confirmation = self.sock.recv(BUFFER_SIZE).decode('utf-8', 'ignore')
                    self.display_message(confirmation)
                except socket.timeout:
                    self.display_message("[INFO] Upload sent, waiting for server confirmation...\n", 'blue')
                
                # Restore timeout for receive loop
                self.sock.settimeout(1.0)
            
        except socket.timeout as e:
            self.display_message(f"\n[ERROR] Upload failed: Connection timeout. Server may be busy.\n", 'red')
            try:
                self.sock.settimeout(1.0)
            except:
                pass
        except Exception as e:
            self.display_message(f"\n[ERROR] Upload failed: {e}\n", 'red')
            try:
                self.sock.settimeout(1.0)
            except:
                pass
    
    def download_file(self, filename):
        """Download a file from server"""
        # Run download in a separate thread to avoid blocking GUI
        download_thread = threading.Thread(target=self._download_file_thread, args=(filename,), daemon=True)
        download_thread.start()
    
    def _download_file_thread(self, filename):
        """Thread function to handle file download"""
        import time
        save_dir = "downloads"
        
        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            self.display_message(f"[DOWNLOAD] Requesting {filename}...\n", 'blue')
            
            # Use lock to serialize socket access - keep locked for entire operation
            with self.receive_lock:
                # Temporarily set socket to blocking mode with longer timeout
                self.sock.settimeout(30.0)
                
                # Send download command
                self.sock.sendall(b"/download")
                
                # Small delay to ensure server processes command first
                time.sleep(0.1)
                
                # Send filename
                self.sock.sendall(filename.encode())
                
                # Receive response
                response = self.sock.recv(BUFFER_SIZE).decode('utf-8', 'ignore')
                
                if response.startswith("ERROR"):
                    self.display_message(f"[ERROR] {response.split('|')[1]}\n", 'red')
                    self.sock.settimeout(1.0)
                    return
                
                # Parse file size
                parts = response.split('|')
                if parts[0] != "OK":
                    self.display_message(f"[ERROR] Invalid server response: {response}\n", 'red')
                    self.sock.settimeout(1.0)
                    return
                
                filesize = int(parts[1])
                
                # Send ready acknowledgment
                self.sock.sendall(b"READY")
                
                # Receive file data
                filepath = os.path.join(save_dir, filename)
                received = 0
                
                self.display_message(f"[DOWNLOAD] Downloading {filename} ({filesize} bytes)...\n", 'blue')
                
                # Set socket to blocking mode (no timeout) for large file transfers
                self.sock.settimeout(None)
                
                try:
                    with open(filepath, 'wb') as f:
                        while received < filesize:
                            remaining = filesize - received
                            chunk_size = min(BUFFER_SIZE, remaining)
                            chunk = self.sock.recv(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            received += len(chunk)
                    
                    # DEBUG: Log after file write completes
                    print(f"DEBUG: File write complete. Received: {received}, Filesize: {filesize}")
                    
                except Exception as e:
                    self.display_message(f"[ERROR] File write error: {e}\n", 'red')
                    self.sock.settimeout(1.0)
                    return
                finally:
                    # Always restore timeout after file transfer
                    self.sock.settimeout(1.0)
                
                # DEBUG: Log before checking completion
                print(f"DEBUG: Checking completion. received={received}, filesize={filesize}, equal={received == filesize}")
                
                # Check download completion
                if received == filesize:
                    print(f"DEBUG: About to display success message")
                    self.display_message(f"[SUCCESS] Downloaded {filename} to {filepath}\n", 'green')
                    print(f"DEBUG: Success message displayed, showing messagebox")
                    # Schedule messagebox on main thread
                    self.root.after(0, lambda f=filepath: messagebox.showinfo("Success", f"File downloaded to:\n{f}"))
                else:
                    print(f"DEBUG: Download incomplete")
                    self.display_message(f"[ERROR] Download incomplete ({received}/{filesize} bytes)\n", 'red')
                    
        except socket.timeout as e:
            self.display_message(f"\n[ERROR] Download failed: Connection timeout. Server may be busy.\n", 'red')
            try:
                self.sock.settimeout(1.0)
            except:
                pass
        except Exception as e:
            self.display_message(f"\n[ERROR] Download failed: {e}\n", 'red')
            try:
                self.sock.settimeout(1.0)
            except:
                pass


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
