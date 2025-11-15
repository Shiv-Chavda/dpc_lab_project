"""
Modern GUI Chat Client with File Sharing
Refined Tkinter interface while preserving existing network behavior.

This file is a drop-in alternative to `client_gui.py`.
All protocol- and thread-related logic is kept identical; only the UI
layout and styling are improved.
"""

import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os

BUFFER_SIZE = 4096


class ChatClientGUI:
    """Modernized chat client UI using the same API and behavior.

    Usage:
        from client_gui_modern import main
        main()
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self._configure_root()

        self.sock = None
        self.running = False
        self.username = ""
        self.receive_lock = threading.Lock()

        # Track auto refresh callback for users sidebar
        self._users_refresh_job = None

        self.create_connection_frame()

    # ------------------------------------------------------------------
    # Window & theming helpers
    # ------------------------------------------------------------------
    def _configure_root(self) -> None:
        self.root.title("Distributed Chat Client · Modern UI")
        self.root.geometry("960x640")
        self.root.minsize(800, 550)

        # Use a neutral dark-on-light palette
        self.bg_main = "#0f172a"  # Slate-900
        self.bg_panel = "#020617"  # Slate-950
        self.bg_input = "#020617"
        self.bg_button = "#2563eb"  # Blue-600
        self.bg_button_secondary = "#1e293b"  # Slate-800
        self.fg_text = "#e5e7eb"  # Gray-200
        self.accent = "#22c55e"  # Green-500

        self.root.configure(bg=self.bg_main)

    # ------------------------------------------------------------------
    # Connection screen
    # ------------------------------------------------------------------
    def create_connection_frame(self) -> None:
        """Create the initial connection setup UI."""
        self.conn_frame = tk.Frame(self.root, bg=self.bg_main)
        self.conn_frame.pack(expand=True, fill="both")

        card = tk.Frame(
            self.conn_frame,
            bg=self.bg_panel,
            bd=0,
            highlightthickness=1,
            highlightbackground="#1f2937",
            padx=32,
            pady=32,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(
            card,
            text="Distributed Chat Client",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_panel,
            fg=self.fg_text,
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 4), sticky="w")

        subtitle = tk.Label(
            card,
            text="Connect to your chat server and start sharing files.",
            font=("Segoe UI", 10),
            bg=self.bg_panel,
            fg="#9ca3af",
        )
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # Host
        tk.Label(
            card,
            text="Server Host",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_panel,
            fg="#d1d5db",
        ).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.host_entry = self._entry(card)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Port
        tk.Label(
            card,
            text="Port",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_panel,
            fg="#d1d5db",
        ).grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.port_entry = self._entry(card)
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Name
        tk.Label(
            card,
            text="Display Name",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_panel,
            fg="#d1d5db",
        ).grid(row=6, column=0, sticky="w", pady=(0, 4))
        self.name_entry = self._entry(card)
        self.name_entry.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 18))

        # Connect button
        self.connect_btn = tk.Button(
            card,
            text="Connect",
            command=self.connect_to_server,
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_button,
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
        )
        self.connect_btn.grid(row=8, column=0, columnspan=2, pady=(0, 10), sticky="ew")

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        # Status label
        self.status_label = tk.Label(
            card,
            text="",
            font=("Segoe UI", 9),
            bg=self.bg_panel,
            fg="#9ca3af",
            anchor="w",
        )
        self.status_label.grid(row=9, column=0, columnspan=2, sticky="w", pady=(8, 0))

        self.name_entry.focus()

    def _entry(self, parent: tk.Widget) -> tk.Entry:
        return tk.Entry(
            parent,
            font=("Segoe UI", 10),
            bg=self.bg_input,
            fg=self.fg_text,
            insertbackground=self.fg_text,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#374151",
            highlightcolor=self.accent,
            bd=6,
        )

    # ------------------------------------------------------------------
    # Main chat UI
    # ------------------------------------------------------------------
    def create_chat_frame(self) -> None:
        """Create main chat UI (same features, modern layout)."""
        self.chat_frame = tk.Frame(self.root, bg=self.bg_main)
        self.chat_frame.pack(expand=True, fill="both")

        # Top bar
        top_bar = tk.Frame(self.chat_frame, bg="#020617", height=52)
        top_bar.pack(fill="x", side="top")

        title = tk.Label(
            top_bar,
            text=f"{self.username}",
            font=("Segoe UI", 11, "bold"),
            bg="#020617",
            fg=self.fg_text,
        )
        title.pack(side="left", padx=16)

        subtitle = tk.Label(
            top_bar,
            text="Connected to Distributed Chat Server",
            font=("Segoe UI", 9),
            bg="#020617",
            fg="#6b7280",
        )
        subtitle.pack(side="left")

        # Connection status pill (left side)
        self.status_pill = tk.Label(
            top_bar,
            text="● Disconnected",
            font=("Segoe UI", 9, "bold"),
            bg="#020617",
            fg="#6b7280",
            padx=10,
        )
        self.status_pill.pack(side="right", padx=(0, 12))

        # Right-side action buttons
        btn_container = tk.Frame(top_bar, bg="#020617")
        btn_container.pack(side="right", padx=12)

        self._top_button(btn_container, "Users", self.show_users).pack(side="right", padx=4)
        self._top_button(btn_container, "Files", self.show_files).pack(side="right", padx=4)
        self._top_button(btn_container, "Upload", self.upload_file, primary=True).pack(
            side="right", padx=4
        )

        # Main content: chat area + live users sidebar
        main = tk.Frame(self.chat_frame, bg=self.bg_main)
        main.pack(expand=True, fill="both")

        # Chat area card (left)
        chat_card = tk.Frame(
            main,
            bg=self.bg_panel,
            highlightthickness=1,
            highlightbackground="#1f2937",
        )
        chat_card.pack(side="left", expand=True, fill="both", padx=(12, 6), pady=(8, 4))

        self.chat_area = scrolledtext.ScrolledText(
            chat_card,
            wrap=tk.WORD,
            state="disabled",
            font=("Consolas", 10),
            bg="#020617",
            fg=self.fg_text,
            insertbackground=self.fg_text,
            relief="flat",
            padx=10,
            pady=10,
        )
        self.chat_area.pack(expand=True, fill="both")

        # Users sidebar (right)
        sidebar = tk.Frame(
            main,
            bg=self.bg_panel,
            width=210,
            highlightthickness=1,
            highlightbackground="#1f2937",
        )
        sidebar.pack(side="right", fill="y", padx=(6, 12), pady=(8, 4))
        sidebar.pack_propagate(False)

        self.users_label = tk.Label(
            sidebar,
            text="Online users",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_panel,
            fg="#e5e7eb",
        )
        self.users_label.pack(anchor="w", padx=10, pady=(10, 4))

        self.users_listbox = tk.Listbox(
            sidebar,
            bg="#020617",
            fg=self.fg_text,
            activestyle="none",
            highlightthickness=0,
            relief="flat",
            selectbackground="#1d4ed8",
            selectforeground="#e5e7eb",
            font=("Segoe UI", 9),
        )
        self.users_listbox.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        # Message input area
        input_bar = tk.Frame(
            self.chat_frame,
            bg="#020617",
            pady=10,
            padx=12,
        )
        input_bar.pack(fill="x", side="bottom")

        self.message_entry = tk.Entry(
            input_bar,
            font=("Segoe UI", 10),
            bg=self.bg_input,
            fg=self.fg_text,
            insertbackground=self.fg_text,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#374151",
            highlightcolor=self.accent,
            bd=6,
        )
        self.message_entry.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.message_entry.bind("<Return>", lambda _e: self.send_message())

        self.send_btn = tk.Button(
            input_bar,
            text="Send",
            command=self.send_message,
            font=("Segoe UI", 10, "bold"),
            bg=self.accent,
            fg="#022c22",
            activebackground="#16a34a",
            activeforeground="#022c22",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        self.send_btn.pack(side="right")

        self.message_entry.focus()

        # Configure tags for colored/system messages
        self.chat_area.tag_config("error", foreground="#f87171")
        self.chat_area.tag_config("success", foreground="#4ade80")
        self.chat_area.tag_config("file", foreground="#60a5fa")
        self.chat_area.tag_config(
            "join", foreground="#22c55e", font=("Consolas", 10, "bold")
        )
        self.chat_area.tag_config(
            "leave", foreground="#fb923c", font=("Consolas", 10, "bold")
        )
        # New styling tags for regular chat lines
        self.chat_area.tag_config("timestamp", foreground="#9ca3af")
        self.chat_area.tag_config("user", foreground="#e5e7eb", font=("Consolas", 10, "bold"))
        self.chat_area.tag_config("self_user", foreground="#38bdf8", font=("Consolas", 10, "bold"))

    def _top_button(self, parent, text, cmd, primary=False) -> tk.Button:
        bg = self.bg_button if primary else self.bg_button_secondary
        hover = "#1d4ed8" if primary else "#111827"

        btn = tk.Button(
            parent,
            text=text,
            command=cmd,
            font=("Segoe UI", 9, "bold"),
            bg=bg,
            fg="#e5e7eb",
            activebackground=hover,
            activeforeground="#f9fafb",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
        )

        # Simple hover effect
        def on_enter(_e):
            btn.configure(bg=hover)

        def on_leave(_e):
            btn.configure(bg=bg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ------------------------------------------------------------------
    # Networking & behavior (copied from original client_gui.py)
    # ------------------------------------------------------------------
    def connect_to_server(self) -> None:
        """Connect to the chat server (behavior identical to original)."""
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

            self.status_label.config(text="Connecting...", fg="#60a5fa")
            self.connect_btn.config(state="disabled")

            # Create socket and connect
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))

            self.running = True

            # Switch to chat interface BEFORE starting receive thread
            self.conn_frame.destroy()
            self.create_chat_frame()

            # Start connection status and user auto-refresh
            self._set_status("Connected", "#22c55e")
            self._schedule_users_refresh(initial=True)

            # Wait for server prompt and send username
            import time

            time.sleep(0.2)
            self.sock.sendall(self.username.encode())

            # Start receive thread
            receive_thread = threading.Thread(
                target=self.receive_messages, daemon=True
            )
            receive_thread.start()

        except ValueError:
            messagebox.showerror("Error", "Invalid port number!")
            self.connect_btn.config(state="normal")
        except ConnectionRefusedError:
            messagebox.showerror(
                "Error", "Could not connect to server. Is it running?"
            )
            self.connect_btn.config(state="normal")
            self.status_label.config(text="Connection failed", fg="#f87171")
            self._set_status("Disconnected", "#f97316")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {e}")
            self.connect_btn.config(state="normal")
            self.status_label.config(text="Connection failed", fg="#f87171")
            self._set_status("Disconnected", "#f97316")

    def receive_messages(self) -> None:
        """Continuously receive messages from server."""
        while self.running:
            try:
                if self.receive_lock.acquire(blocking=False):
                    try:
                        self.sock.settimeout(1.0)
                        data = self.sock.recv(BUFFER_SIZE)

                        if not data:
                            self.running = False
                            self.display_message(
                                "\n[DISCONNECTED] Connection lost.\n", "red"
                            )
                            self._set_status("Disconnected", "#f97316")
                            break

                        message = data.decode("utf-8", "ignore")
                        self.display_message(message)
                    finally:
                        self.receive_lock.release()
                else:
                    import time

                    time.sleep(0.1)

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.display_message(f"\n[ERROR] {e}\n", "red")
                    self._set_status("Error", "#f97316")
                self.running = False
                break

    def display_message(self, message: str, color: str = "black") -> None:
        """Display message in chat area with nicer styling.

        - Hides [USERS] lists from the chat while still updating the
          sidebar.
        - Highlights timestamps and usernames for normal chat lines.
        - Distinguishes system messages (join/leave, errors, files).
        """
        if not hasattr(self, "chat_area") or self.chat_area is None:
            return

        self.chat_area.config(state="normal")

        # If this is a users list message, refresh the sidebar only
        # to avoid flooding the chat during auto-refresh.
        if message.startswith("[USERS]"):
            self._update_users_sidebar_from_message(message)
        else:
            # Try to detect standard chat lines: [HH:MM:SS] Name: text
            if message.startswith("[") and "]" in message and ":" in message:
                end_bracket = message.find("]")
                timestamp = message[: end_bracket + 1]
                rest = message[end_bracket + 1 :].lstrip()

                if ":" in rest:
                    name_part, body = rest.split(":", 1)
                    username = name_part.strip()
                    body = body.lstrip()

                    # Choose tag for username: self vs others
                    user_tag = "self_user" if username == self.username else "user"

                    # Extra spacing between messages
                    self.chat_area.insert(tk.END, "\n")
                    self.chat_area.insert(tk.END, timestamp + " ", "timestamp")
                    self.chat_area.insert(tk.END, username, user_tag)
                    if body:
                        self.chat_area.insert(tk.END, ": " + body + "\n")
                else:
                    # Fallback if format is unexpected
                    self.chat_area.insert(tk.END, message)
            else:
                # System / informational messages
                if "[ERROR]" in message or "DISCONNECTED" in message:
                    self.chat_area.insert(tk.END, "\n" + message, "error")
                elif "[SUCCESS]" in message or "uploaded" in message:
                    self.chat_area.insert(tk.END, "\n" + message, "success")
                elif "[FILE]" in message or "[DOWNLOAD]" in message or "[UPLOAD]" in message:
                    self.chat_area.insert(tk.END, "\n" + message, "file")
                elif "*" in message and "joined" in message:
                    self.chat_area.insert(tk.END, "\n" + message, "join")
                elif "*" in message and "left" in message:
                    self.chat_area.insert(tk.END, "\n" + message, "leave")
                else:
                    self.chat_area.insert(tk.END, message)

        self.chat_area.config(state="disabled")
        self.chat_area.see(tk.END)

    # ------------------------------------------------------------------
    # Status & users auto-refresh helpers
    # ------------------------------------------------------------------
    def _set_status(self, text: str, color: str) -> None:
        """Update the status pill text/color if it exists."""
        if hasattr(self, "status_pill") and self.status_pill is not None:
            self.status_pill.config(text=f"● {text}", fg=color)

    def _schedule_users_refresh(self, initial: bool = False) -> None:
        """Schedule periodic /users requests while connected.

        Uses Tk's after() so it stays on the main thread. This does *not*
        wait for or parse responses here; responses are handled normally
        in receive_messages/display_message.
        """
        # Cancel any existing job first
        if self._users_refresh_job is not None:
            try:
                self.root.after_cancel(self._users_refresh_job)
            except Exception:
                pass
            self._users_refresh_job = None

        if not self.running or self.sock is None:
            return

        def refresh() -> None:
            if not self.running or self.sock is None:
                return
            try:
                # This uses the same command as the Users button
                self.sock.sendall(b"/users")
            except Exception:
                # If this fails, just stop refreshing; receive loop will handle errors
                return

            # Reschedule next refresh
            if self.running:
                self._users_refresh_job = self.root.after(5000, refresh)

        # Kick off the loop
        if initial:
            self._users_refresh_job = self.root.after(1000, refresh)
        else:
            self._users_refresh_job = self.root.after(5000, refresh)

    def _update_users_sidebar_from_message(self, message: str) -> None:
        """Parse `[USERS]` server message and update sidebar listbox.

        Expected format from server.py:

            [USERS] Online users:\n
              1. Alice\n
              2. Bob\n
        """
        if not hasattr(self, "users_listbox"):
            return

        # Extract lines after the header
        lines = message.splitlines()
        user_lines = [ln.strip() for ln in lines[1:] if ln.strip()]

        users = []
        for ln in user_lines:
            # each line is like "1. username" — split on first '. '
            parts = ln.split(". ", 1)
            if len(parts) == 2:
                users.append(parts[1].strip())

        self.users_listbox.delete(0, tk.END)
        for u in users:
            # Use a simple bullet prefix for visual clarity
            self.users_listbox.insert(tk.END, f"• {u}")

        # Update online count in label, if present
        if hasattr(self, "users_label") and self.users_label is not None:
            self.users_label.config(text=f"Online users ({len(users)})")

    def send_message(self) -> None:
        """Send message to server (same behavior)."""
        message = self.message_entry.get().strip()

        if not message:
            return

        try:
            self.sock.sendall(message.encode())
            self.message_entry.delete(0, tk.END)

            if message == "/quit":
                self.running = False
                # Stop users auto-refresh if any
                if self._users_refresh_job is not None:
                    try:
                        self.root.after_cancel(self._users_refresh_job)
                    except Exception:
                        pass
                    self._users_refresh_job = None
                self.sock.close()
                self.root.destroy()

        except Exception as e:
            self.display_message(f"\n[ERROR] Send failed: {e}\n", "red")

    def show_users(self) -> None:
        """Request and display user list (same command)."""
        try:
            self.sock.sendall(b"/users")
        except Exception as e:
            self.display_message(f"\n[ERROR] {e}\n", "red")

    def show_files(self) -> None:
        """Show available files and download options (modern dialog)."""
        try:
            self.sock.sendall(b"/files")

            dialog = tk.Toplevel(self.root)
            dialog.title("Shared Files")
            dialog.geometry("520x420")
            dialog.configure(bg=self.bg_panel)

            header = tk.Label(
                dialog,
                text="Shared Files",
                font=("Segoe UI", 14, "bold"),
                bg=self.bg_panel,
                fg=self.fg_text,
            )
            header.pack(pady=(16, 4))

            info = tk.Label(
                dialog,
                text="Type a filename from the list in the chat and click Download.",
                font=("Segoe UI", 9),
                bg=self.bg_panel,
                fg="#9ca3af",
                wraplength=460,
                justify="left",
            )
            info.pack(pady=(0, 12))

            # Input row
            row = tk.Frame(dialog, bg=self.bg_panel)
            row.pack(pady=8)

            filename_entry = self._entry(row)
            filename_entry.config(width=32)
            filename_entry.pack(side="left", padx=(0, 8))

            def do_download() -> None:
                filename = filename_entry.get().strip()
                if filename:
                    self.download_file(filename)
                    dialog.destroy()

            dl_btn = tk.Button(
                row,
                text="Download",
                command=do_download,
                font=("Segoe UI", 9, "bold"),
                bg=self.bg_button,
                fg="white",
                bd=0,
                padx=14,
                pady=6,
                cursor="hand2",
            )
            dl_btn.pack(side="left")

            close_btn = tk.Button(
                dialog,
                text="Close",
                command=dialog.destroy,
                font=("Segoe UI", 9),
                bg=self.bg_button_secondary,
                fg=self.fg_text,
                bd=0,
                padx=20,
                pady=6,
                cursor="hand2",
            )
            close_btn.pack(pady=(18, 12))

            filename_entry.focus()

        except Exception as e:
            self.display_message(f"\n[ERROR] {e}\n", "red")

    def upload_file(self) -> None:
        """Upload a file to the server (same protocol)."""
        filepath = filedialog.askopenfilename(title="Select file to upload")

        if not filepath:
            return

        upload_thread = threading.Thread(
            target=self._upload_file_thread, args=(filepath,), daemon=True
        )
        upload_thread.start()

    def _upload_file_thread(self, filepath: str) -> None:
        import time

        try:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)

            with self.receive_lock:
                self.sock.settimeout(30.0)

                self.sock.sendall(b"/upload")
                ready_msg = self.sock.recv(BUFFER_SIZE)

                if b"Ready to receive" not in ready_msg:
                    self.display_message(
                        f"[ERROR] Unexpected response: {ready_msg.decode()}\n", "red"
                    )
                    self.sock.settimeout(1.0)
                    return

                metadata = f"{filename}|{filesize}"
                self.sock.sendall(metadata.encode())

                ack = self.sock.recv(BUFFER_SIZE)
                if ack != b"READY":
                    self.display_message(
                        "[ERROR] Server not ready for transfer\n", "red"
                    )
                    self.sock.settimeout(1.0)
                    return

                self.display_message(
                    f"[UPLOAD] Uploading {filename} ({filesize} bytes)...\n", "blue"
                )

                sent = 0
                with open(filepath, "rb") as f:
                    while sent < filesize:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        self.sock.sendall(chunk)
                        sent += len(chunk)

                try:
                    confirmation = self.sock.recv(BUFFER_SIZE).decode(
                        "utf-8", "ignore"
                    )
                    self.display_message(confirmation)
                except socket.timeout:
                    self.display_message(
                        "[INFO] Upload sent, waiting for server confirmation...\n",
                        "blue",
                    )

                self.sock.settimeout(1.0)

        except socket.timeout:
            self.display_message(
                "\n[ERROR] Upload failed: Connection timeout. Server may be busy.\n",
                "red",
            )
            try:
                self.sock.settimeout(1.0)
            except Exception:
                pass
        except Exception as e:
            self.display_message(f"\n[ERROR] Upload failed: {e}\n", "red")
            try:
                self.sock.settimeout(1.0)
            except Exception:
                pass

    def download_file(self, filename: str) -> None:
        """Download a file from the server (threaded)."""
        download_thread = threading.Thread(
            target=self._download_file_thread, args=(filename,), daemon=True
        )
        download_thread.start()

    def _download_file_thread(self, filename: str) -> None:
        import time

        save_dir = "downloads"

        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            self.display_message(f"[DOWNLOAD] Requesting {filename}...\n", "blue")

            with self.receive_lock:
                self.sock.settimeout(30.0)

                self.sock.sendall(b"/download")
                time.sleep(0.1)

                self.sock.sendall(filename.encode())

                response = self.sock.recv(BUFFER_SIZE).decode("utf-8", "ignore")

                if response.startswith("ERROR"):
                    self.display_message(
                        f"[ERROR] {response.split('|')[1]}\n", "red"
                    )
                    self.sock.settimeout(1.0)
                    return

                parts = response.split("|")
                if parts[0] != "OK":
                    self.display_message(
                        f"[ERROR] Invalid server response: {response}\n", "red"
                    )
                    self.sock.settimeout(1.0)
                    return

                filesize = int(parts[1])

                self.sock.sendall(b"READY")

                filepath = os.path.join(save_dir, filename)
                received = 0

                self.display_message(
                    f"[DOWNLOAD] Downloading {filename} ({filesize} bytes)...\n",
                    "blue",
                )

                self.sock.settimeout(None)

                try:
                    with open(filepath, "wb") as f:
                        while received < filesize:
                            remaining = filesize - received
                            chunk_size = min(BUFFER_SIZE, remaining)
                            chunk = self.sock.recv(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            received += len(chunk)

                except Exception as e:
                    self.display_message(f"[ERROR] File write error: {e}\n", "red")
                    self.sock.settimeout(1.0)
                    return
                finally:
                    self.sock.settimeout(1.0)

                if received == filesize:
                    self.display_message(
                        f"[SUCCESS] Downloaded {filename} to {filepath}\n", "green"
                    )
                    self.root.after(
                        0,
                        lambda f=filepath: messagebox.showinfo(
                            "Success", f"File downloaded to:\n{f}"
                        ),
                    )
                else:
                    self.display_message(
                        f"[ERROR] Download incomplete ({received}/{filesize} bytes)\n",
                        "red",
                    )

        except socket.timeout:
            self.display_message(
                "\n[ERROR] Download failed: Connection timeout. Server may be busy.\n",
                "red",
            )
            try:
                self.sock.settimeout(1.0)
            except Exception:
                pass
        except Exception as e:
            self.display_message(f"\n[ERROR] Download failed: {e}\n", "red")
            try:
                self.sock.settimeout(1.0)
            except Exception:
                pass


def main() -> None:
    root = tk.Tk()
    app = ChatClientGUI(root)

    def on_closing() -> None:
        app.running = False
        # Cancel any pending auto-refresh job
        if getattr(app, "_users_refresh_job", None) is not None:
            try:
                root.after_cancel(app._users_refresh_job)
            except Exception:
                pass
            app._users_refresh_job = None
        if app.sock:
            try:
                app.sock.close()
            except Exception:
                pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
