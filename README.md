# Distributed Chat Application with File Sharing

A multi-client distributed chat system with real-time messaging and public file sharing capabilities, built with Python sockets and threading.

## Features

### ✨ Core Features
- **Multi-Client Support**: Multiple users can connect simultaneously
- **Real-Time Chat**: Instant message broadcasting to all connected users
- **User Notifications**: Join/leave notifications for all users
- **Concurrent Operations**: Send and receive messages simultaneously
- **Public File Sharing**: Upload and download files accessible to all users
- **Multiple Client Interfaces**: Console and GUI clients available

### 🔧 Technical Features
- TCP socket communication
- Multi-threaded server architecture
- Graceful disconnection handling
- File metadata tracking (uploader, timestamp, size)
- Progress indicators for file transfers
- Command-based interface

## Project Structure

```
dpc_lab_project/
├── server.py              # Main server with chat and file sharing
├── client_console.py      # Console-based client
├── client_gui.py          # GUI-based client (Tkinter)
├── shared_files/          # Directory for uploaded files (auto-created)
├── downloads/             # Client download directory (auto-created)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Requirements

- Python 3.7 or higher
- Standard library only (no external dependencies for core functionality)
- Tkinter (included with Python) for GUI client

## Installation

1. Clone or download this project:
```powershell
cd C:\DPC\dpc_lab_project
```

2. No additional installation needed - uses Python standard library!

## Usage

### Starting the Server

```powershell
python server.py
```

**Options:**
- `--host`: Server host address (default: 0.0.0.0)
- `--port`: Server port (default: 5000)

**Example:**
```powershell
python server.py --host 0.0.0.0 --port 5000
```

### Starting a Console Client

```powershell
python client_console.py
```

**Options:**
- `--host`: Server host address (default: 127.0.0.1)
- `--port`: Server port (default: 5000)

**Example:**
```powershell
python client_console.py --host 127.0.0.1 --port 5000
```

### Starting a GUI Client

```powershell
python client_gui.py
```

The GUI client will prompt you for connection details in a graphical interface.

## Available Commands

### Chat Commands
- `/quit` - Exit the chat
- `/users` - List all online users
- `/files` - List all shared files
- `/upload` - Upload a file to the server
- `/download` - Download a file from the server
- `/help` - Show help message

### File Operations

**Console Client:**
```
/upload path/to/file.txt        # Upload a file
/download filename.txt          # Download a file
```

**GUI Client:**
- Click "⬆️ Upload" button to select and upload a file
- Click "📁 Files" button to see files and download

## Architecture

### Server Module (`server.py`)

**Key Components:**
- **Client Handler**: Manages individual client connections
- **Broadcast System**: Sends messages to all connected clients
- **File Manager**: Handles file upload/download operations
- **Thread Pool**: Concurrent client handling using threading

**Data Structures:**
- `clients`: Dictionary mapping connections to user info
- `files_shared`: Dictionary of uploaded files with metadata

### Client Module (`client_console.py`)

**Key Components:**
- **Receive Thread**: Continuously listens for server messages
- **Send Thread**: Main thread handles user input
- **File Transfer**: Upload/download with progress tracking

### GUI Client Module (`client_gui.py`)

**Features:**
- Tkinter-based graphical interface
- Real-time message display with color coding
- File browser for uploads
- Visual progress indicators
- User-friendly button controls

## Testing the Application

### Test Scenario 1: Basic Chat

1. Start the server:
```powershell
python server.py
```

2. Start Client 1 (console):
```powershell
python client_console.py
```
Enter name: Alice

3. Start Client 2 (GUI):
```powershell
python client_gui.py
```
Enter name: Bob

4. Send messages between clients and verify broadcasting

### Test Scenario 2: File Sharing

1. From Alice's client:
```
/upload test_file.txt
```

2. From Bob's client:
```
/files
/download test_file.txt
```

3. Verify file appears in Bob's `downloads/` folder

### Test Scenario 3: Multiple Clients

1. Start 3-5 clients simultaneously
2. Send messages from different clients
3. Verify all clients receive all messages
4. Test disconnection and reconnection

## Implementation Details

### Threading Model

**Server:**
- Main thread: Accepts new connections
- Worker threads: One per client (daemon threads)
- Locks: Protect shared data structures

**Client:**
- Main thread: User input and sending
- Receive thread: Continuous message reception (daemon)

### File Transfer Protocol

**Upload Flow:**
1. Client sends `/upload` command
2. Client sends metadata: `filename|filesize`
3. Server responds with `READY`
4. Client sends file data in chunks
5. Server confirms success

**Download Flow:**
1. Client sends `/download` command
2. Client sends filename
3. Server responds with `OK|filesize` or `ERROR|message`
4. Client sends `READY`
5. Server sends file data in chunks

### Error Handling

- Connection failures are caught and reported
- Client disconnections are handled gracefully
- File transfer errors don't crash the server
- Incomplete transfers are cleaned up

## Network Configuration

### Running on Same Machine
- Server: `--host 127.0.0.1`
- Client: `--host 127.0.0.1`

### Running on Local Network
- Server: `--host 0.0.0.0` (listens on all interfaces)
- Client: `--host <server_ip_address>`

### Firewall Rules
Ensure port 5000 (or your chosen port) is open for TCP connections.

## Troubleshooting

### Connection Refused
- Verify server is running
- Check host and port settings
- Ensure firewall allows connections

### File Upload/Download Fails
- Check file permissions
- Verify file exists
- Ensure sufficient disk space

### Messages Not Appearing
- Check network connectivity
- Verify all clients are connected to same server
- Look for error messages in console

## Limitations & Future Enhancements

**Current Limitations:**
- No encryption (plaintext communication)
- No authentication system
- No private messaging
- No message history
- File size limited by memory/disk

**Potential Enhancements:**
- SSL/TLS encryption
- User authentication
- Private/direct messaging
- Message persistence (database)
- Emoji support
- File chunking for large files
- Compression for file transfers
- Web-based client interface

## Technical Specifications

- **Protocol**: TCP/IP
- **Port**: 5000 (default, configurable)
- **Buffer Size**: 4096 bytes
- **Thread Type**: Daemon threads
- **File Storage**: Local filesystem

## License

This is an educational project for learning distributed systems and network programming.

## Contributors

Created for DPC Lab Project

## Support

For issues or questions, please check:
1. Server console for error messages
2. Client console for connection issues
3. File permissions for upload/download problems

---

**Happy Chatting! 🚀💬**
