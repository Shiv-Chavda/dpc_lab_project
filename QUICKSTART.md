# Quick Start Guide - Distributed Chat Application

## Quick Setup (5 minutes)

### Step 1: Start the Server (Terminal 1)
```powershell
cd C:\DPC\dpc_lab_project
python server.py
```
You should see:
```
========================================================
  DISTRIBUTED CHAT SERVER WITH FILE SHARING
========================================================
[SERVER] Listening on 0.0.0.0:5000
[SERVER] Waiting for connections...
```

### Step 2: Start First Client (Terminal 2)
```powershell
cd C:\DPC\dpc_lab_project
python client_console.py
```
- Enter your name when prompted (e.g., "Alice")
- You should see the welcome message

### Step 3: Start Second Client (Terminal 3)
```powershell
cd C:\DPC\dpc_lab_project
python client_gui.py
```
- Enter connection details (default: 127.0.0.1:5000)
- Enter your name (e.g., "Bob")
- Click "Connect"

### Step 4: Test Chat
From any client, type a message and press Enter. It should appear on all other clients!

### Step 5: Test File Sharing

**Upload a file (Console Client):**
```
/upload C:\path\to\your\file.txt
```

**List files (Any Client):**
```
/files
```

**Download a file (Console Client):**
```
/download file.txt
```

## Common Commands

| Command | Description |
|---------|-------------|
| `/users` | Show who's online |
| `/files` | List shared files |
| `/help` | Show all commands |
| `/quit` | Exit chat |

## Test File for Demo

Create a test file:
```powershell
echo "Hello from Distributed Chat!" > test.txt
```

Then upload it:
```
/upload test.txt
```

## Troubleshooting

**"Connection refused"**
- Make sure server is running first
- Check if port 5000 is available

**Can't see messages**
- Verify all clients connected to same server
- Check network connectivity

**File upload fails**
- Check file path is correct
- Ensure you have read permissions

## Network Setup

### Same Computer (localhost)
- Server: `python server.py`
- Client: `python client_console.py` (uses 127.0.0.1 by default)

### Different Computers (LAN)
- Server: `python server.py --host 0.0.0.0`
- Find server IP: `ipconfig` (look for IPv4)
- Client: `python client_console.py --host <server_ip>`

## Tips

1. **Start server first** before any clients
2. **Use GUI client** for easier file operations
3. **Create test files** in the project directory for easy uploads
4. **Check server console** to see all activity
5. **Open multiple terminals** to test with multiple clients

## Next Steps

- Try connecting from different computers
- Test with 3+ clients simultaneously
- Upload different file types
- Check the `shared_files/` and `downloads/` directories

---

**Need help?** Check README.md for detailed documentation.
