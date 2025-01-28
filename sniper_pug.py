import tkinter as tk
from tkinter import messagebox
import requests
import re
import difflib
import threading
import time
from datetime import datetime, timedelta
import os
import pytz

#GITHUB_RAW_URL = "https://raw.githubusercontent.com/pugpeanut/pugfetchnews/refs/heads/main/scripts/choose_staking.py"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/valory-xyz/trader-quickstart/refs/heads/main/scripts/choose_staking.py"
GITHUB_RAW_URL_UNIQUE = f"{GITHUB_RAW_URL}?_={int(time.time())}"
FILE_PATH = "staking_programs.txt"
API_TOKEN = "" #put token
CHAT_ID = "" #put chat id
TIME_STEP = 1800 #put time sleep, 30 minute run

def fetch_staking_programs():
    try:
        headers = {
            "Cache-Control": "no-cache",

            "Pragma": "no-cache",
        }

        response = requests.get(GITHUB_RAW_URL_UNIQUE,headers=headers)
        response.raise_for_status()

        content = response.text

        response = requests.get("https://api.github.com/rate_limit")
        print(f"rate limit: {response.json()}")

        match = re.search(r'STAKING_PROGRAMS\s*=\s*(\{.*?\})', content, re.DOTALL)

        if match:
            staking_programs_string = match.group(1)
            print("STAKING PROGRAMS MATCHED REGEX STRING:", staking_programs_string)

            utc_now = datetime.now(pytz.utc)
            utc_plus_8 = utc_now + timedelta(hours=0)
            time_str = utc_plus_8.strftime('%Y-%m-%d %H:%M:%S')
            print("UTC+0: " + time_str)

            if os.path.exists(FILE_PATH):
                with open(FILE_PATH, 'r') as file:
                    saved_programs_string = file.read()
                
                if staking_programs_string != saved_programs_string:
                    seq1 = staking_programs_string.splitlines()
                    seq2 = saved_programs_string.splitlines()

                    differ = difflib.Differ()

                    diff = differ.compare(seq1, seq2)
                    diff_dash = ''.join(map(str, diff))
                    print('\n'.join(diff))
                    print("Differences detected!")
                    send_message(API_TOKEN,CHAT_ID,"new program available, do git pull quickstart!")

                    #show_difference(staking_programs_string, diff_dash)

            with open(FILE_PATH, 'w') as file:
                file.write(staking_programs_string)

    except Exception as e:
        print(f"An error occurred: {e}")

def show_difference(new_string, diff_dash):
    custom_messagebox("Staking Programs Update! New Program Available", diff_dash)

def pub_msg_telegram(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=payload)

    return response.json()


def send_message(token, chat_id, message):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        print('Message sent successfully!')
    else:
        print('Failed to send message:', response.text)


def start_checking():
    while True:
        fetch_staking_programs()
        time.sleep(TIME_STEP)

def custom_messagebox(title, message):
    top = tk.Toplevel()
    top.title(title)

    top.geometry("640x480")

    label = tk.Label(top, text=message)
    label.pack(padx=20, pady=20)

    ok_button = tk.Button(top, text="OK", command=top.destroy)
    ok_button.pack(pady=(0, 20))

    top.transient()
    top.grab_set()
    top.focus_set()
    top.wait_window()

def on_start_button_click():
    thread = threading.Thread(target=start_checking)
    thread.daemon = True
    thread.start()
    messagebox.showinfo("Info", "Started checking for STAKING_PROGRAMS every 30 minutes.")

root = tk.Tk()
root.title("Staking Programs Checker")
start_button = tk.Button(root, text="Start Checking", command=on_start_button_click)
start_button.pack(pady=20)
root.mainloop()
