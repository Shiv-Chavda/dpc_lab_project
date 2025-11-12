# Demo Script - Distributed Chat Application
# Follow these steps to demonstrate all features

## PREPARATION (Before Demo)

1. Open 4 terminal windows/tabs:
   - Terminal 1: Server
   - Terminal 2: Client 1 (Console - Alice)
   - Terminal 3: Client 2 (Console - Bob)
   - Terminal 4: Client 3 (GUI - Carol)

2. Navigate all terminals to project directory:
   cd C:\DPC\dpc_lab_project

## DEMO SCRIPT

### Step 1: Start Server (Terminal 1)
```powershell
python server.py
```
Expected Output:
- Server banner displayed
- "Listening on 0.0.0.0:5000"
- "Waiting for connections..."

### Step 2: Connect Client 1 - Alice (Terminal 2)
```powershell
python client_console.py
```
- When prompted, enter name: Alice
- See welcome message with commands

Server should show:
- "[JOIN] Alice connected from..."

### Step 3: Connect Client 2 - Bob (Terminal 3)
```powershell
python client_console.py
```
- When prompted, enter name: Bob

Alice should see:
- "* Bob joined the chat *"

Server should show:
- "[JOIN] Bob connected from..."

### Step 4: Connect Client 3 - Carol (Terminal 4)
```powershell
python client_gui.py
```
- Enter host: 127.0.0.1
- Enter port: 5000
- Enter name: Carol
- Click "Connect"

All clients should see:
- "* Carol joined the chat *"

### Step 5: Basic Chat Demo

Alice types:
```
Hello everyone!
```

All other clients see:
```
[HH:MM:SS] Alice: Hello everyone!
```

Bob types:
```
Hi Alice! Hi Carol!
```

Carol types in GUI:
```
Hey there! This GUI is nice!
```

### Step 6: List Users Command

Any client types:
```
/users
```

Should see:
```
[USERS] Online users:
  1. Alice
  2. Bob
  3. Carol
```

### Step 7: File Upload Demo

Alice uploads the test file:
```
/upload sample_test_file.txt
```

Watch progress bar:
```
[UPLOAD] Uploading sample_test_file.txt (214 bytes)...
[UPLOAD] Progress: 100.0%
[SUCCESS] File uploaded successfully!
```

All clients see:
```
[FILE] Alice uploaded 'sample_test_file.txt' (214 bytes)
```

Server shows:
```
[FILE] sample_test_file.txt uploaded by Alice
```

### Step 8: List Files Command

Bob types:
```
/files
```

Should see:
```
[FILES] Available files:
  1. sample_test_file.txt (214 bytes) - uploaded by Alice at 2025-11-12 HH:MM:SS
```

### Step 9: File Download Demo

Bob downloads the file:
```
/download sample_test_file.txt
```

Watch progress:
```
[DOWNLOAD] Downloading sample_test_file.txt (214 bytes)...
[DOWNLOAD] Progress: 100.0%
[SUCCESS] File saved to downloads\sample_test_file.txt
```

### Step 10: GUI Features Demo (Carol)

In GUI client:
1. Click "Users" button → See user list in chat
2. Click "Files" button → Opens file dialog
3. Click "Upload" button → File browser opens
4. Select a file and upload
5. All clients see the upload notification

### Step 11: Client Disconnection

Alice types:
```
/quit
```

Alice sees:
```
[BYE] Goodbye!
[DISCONNECTED] Connection closed.
```

All other clients see:
```
* Alice left the chat *
```

Server shows:
```
[LEAVE] Alice disconnected
```

### Step 12: Verify Remaining Clients

Bob types:
```
/users
```

Should now see:
```
[USERS] Online users:
  1. Bob
  2. Carol
```

### Step 13: Help Command

Bob types:
```
/help
```

Should see complete command list and usage instructions.

### Step 14: Shutdown

1. Bob: `/quit`
2. Carol: Type `/quit` in GUI or close window
3. Server: Press Ctrl+C

All shutdowns should be clean with no errors.

## VERIFICATION CHECKLIST

After demo, verify:
- [ ] All messages broadcasted correctly
- [ ] Join/leave notifications appeared
- [ ] File was uploaded successfully
- [ ] File was downloaded successfully
- [ ] Both console and GUI clients worked
- [ ] Commands executed properly
- [ ] No error messages or crashes
- [ ] Clean disconnections
- [ ] Files exist in directories:
  - [ ] shared_files/sample_test_file.txt
  - [ ] downloads/sample_test_file.txt

## ADVANCED DEMO (Optional)

### Multiple File Types
```
/upload image.jpg
/upload document.pdf
/upload code.py
/files
```

### Stress Test
- Open 5-10 clients simultaneously
- All send messages at same time
- Verify all receive all messages

### Network Demo
- Run server on one computer
- Connect clients from other computers on LAN
- Use server's IP address

### Error Handling
- Try to download non-existent file
- Upload very large file
- Disconnect client during file transfer
- Verify graceful handling

## TALKING POINTS

1. **Architecture**: Multi-threaded server with worker threads per client
2. **Concurrency**: Clients can send/receive simultaneously
3. **Thread Safety**: Locks protect shared data structures
4. **Protocol**: Custom TCP-based protocol for chat and file transfer
5. **User Experience**: Both console and GUI interfaces
6. **Scalability**: Can handle many concurrent clients
7. **Reliability**: Graceful error handling and disconnection
8. **Features**: Real-time chat + public file sharing
9. **Simplicity**: No external dependencies needed
10. **Cross-platform**: Works on Windows, Linux, macOS

## COMMON QUESTIONS & ANSWERS

Q: How many clients can connect?
A: Limited by system resources, tested with 10+ clients

Q: What file types are supported?
A: All file types (binary and text)

Q: Is it secure?
A: No encryption (educational project), could add SSL/TLS

Q: Can clients private message?
A: Currently broadcast only, private messaging is possible enhancement

Q: Does it save chat history?
A: No persistence, could add database for history

Q: What happens if server crashes?
A: Clients detect disconnection and exit gracefully

Q: Can I run this over the internet?
A: Yes, but need port forwarding and consider security

---

**Demo Duration**: 10-15 minutes

**Preparation Time**: 2 minutes

**Difficulty**: Easy - Works out of the box!
