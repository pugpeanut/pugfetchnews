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

GITHUB_RAW_URL = "https://raw.githubusercontent.com/pugpeanut/pugfetchnews/refs/heads/main/scripts/choose_staking.py"
FILE_PATH = "staking_programs.txt"

def fetch_staking_programs():
    try:
        response = requests.get(GITHUB_RAW_URL)
        response.raise_for_status()

        content = response.text

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
                    show_difference(staking_programs_string, diff_dash)

            with open(FILE_PATH, 'w') as file:
                file.write(staking_programs_string)

    except Exception as e:
        print(f"An error occurred: {e}")

def show_difference(new_string, diff_dash):
    custom_messagebox("Staking Programs Update", diff_dash)

def start_checking():
    while True:
        fetch_staking_programs()
        time.sleep(30)

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
