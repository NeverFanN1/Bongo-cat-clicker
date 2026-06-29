"""
Slightly improved version of: https://steamcommunity.com/sharedfiles/filedetails/?id=3489865829


Removed issue of it making Bongo Cat rotate when cursor is over the cat.
Added a bongo counter and a timer.
"""


import pydirectinput
import win32gui
import win32con
import time
import random
import threading
import keyboard
import tkinter as tk
from tkinter import font as tkfont


pydirectinput.PAUSE = 0


bongo_count = 0
active_time = 0.0
last_start_time = None
time_label = None
count_label = None


# ── CONFIG ──────────────────────────────────────────────────────────────────
WINDOW_TITLE = "BongoCat"   # adjust if title differs in your language
TOGGLE_KEY   = "p"
INTERVAL_MIN = 0.001
INTERVAL_MAX = 0.001
HOLD_MIN     = 0.03
HOLD_MAX     = 0.04
DEBOUNCE     = 0.4


KEYS = [
    'a','b','c','d','e','g','h','i','j','k','l','m',
    'n','o','q','s','t','u','v','w','x','y','z',
    '0','1','2','3','4','5','6','7','8','9',
]
# ────────────────────────────────────────────────────────────────────────────


running      = False
lock         = threading.Lock()
_last_toggle = 0.0
status_label = None
btn_toggle   = None
root         = None


def find_and_focus():
    hwnd = win32gui.FindWindow(None, WINDOW_TITLE)
    if hwnd and win32gui.IsWindow(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return True
    return False


def press_key(key):
    global bongo_count


    try:
        pydirectinput.keyDown(key)
        time.sleep(random.uniform(HOLD_MIN, HOLD_MAX))
        pydirectinput.keyUp(key)


        bongo_count += 1
        if count_label and root:
            root.after(
                0,
                lambda: count_label.config(
                    text=f"Bongos: {bongo_count:,}"
                )
            )
    except Exception as e:
        print(f"[press] Error on '{key}': {e}")


def auto_press_loop():
    global running
    last_focus = 0.0
    while True:
        with lock:
            is_running = running


        if not is_running:
            time.sleep(0.05)
            continue


        # refocus Bongo Cat every 10 seconds so the GUI never steals focus
        now = time.time()
        if now - last_focus > 10.0:
            find_and_focus()
            last_focus = now


        try:
            press_key(random.choice(KEYS))
        except Exception as e:
            print(f"[loop] Error: {e}")


        time.sleep(random.uniform(INTERVAL_MIN, INTERVAL_MAX))


def set_status(text, color):
    if status_label and root:
        root.after(0, lambda: status_label.config(text=text, fg=color))


def toggle_running():
    global running, _last_toggle
    global last_start_time, active_time


    now = time.time()
    if now - _last_toggle < DEBOUNCE:
        return
    _last_toggle = now


    with lock:
        running = not running
        state = running


    if state:
        last_start_time = time.time()
        if not find_and_focus():
            set_status("Window not found", "#ffaa00")
            with lock:
                running = False
            return
        set_status("● Running", "#00ff88")
        btn_toggle.config(text="■ Stop  P")
    else:
        if last_start_time is not None:
            active_time += time.time() - last_start_time
            last_start_time = None
        set_status("● Stopped", "#ff4444")
        btn_toggle.config(text="▶ Start  P")


def on_hotkey(event):
    toggle_running()


def on_close():
    global running
    with lock:
        running = False
    root.destroy()


def build_gui():
    global root, status_label, btn_toggle
    global time_label, count_label


    root = tk.Tk()
    root.title("Bongo Cat Clicker")
    root.geometry("280x160")
    root.resizable(False, False)
    root.configure(bg="#1e1e2e")
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.95)


    f_title  = tkfont.Font(family="Segoe UI", size=13, weight="bold")
    f_status = tkfont.Font(family="Segoe UI", size=11)
    f_btn    = tkfont.Font(family="Segoe UI", size=10)
    f_hint   = tkfont.Font(family="Segoe UI", size=8)


    tk.Label(root, text="Bongo Cat Clicker :3",
             font=f_title, bg="#1e1e2e", fg="#cdd6f4").pack(pady=(14, 2))


    status_label = tk.Label(root, text="● Stopped",
                             font=f_status, bg="#1e1e2e", fg="#ff4444")
    status_label.pack(pady=2)


    count_label = tk.Label(
        root,
        text="Bongos: 0",
        font=f_status,
        bg="#1e1e2e",
        fg="#89b4fa"
    )
    count_label.pack()


    time_label = tk.Label(
            root,
            text="Runtime: 00:00:00",
            font=f_status,
            bg="#1e1e2e",
            fg="#f9e2af"
    )
    time_label.pack()




    btn_toggle = tk.Button(
        root, text="▶ Start  P", font=f_btn,
        bg="#313244", fg="#cdd6f4", activebackground="#45475a",
        relief="flat", padx=12, pady=6, cursor="hand2",
        command=toggle_running
    )
    btn_toggle.pack(pady=10)


    tk.Label(root, text="Bongo Cat must be open to start",
             font=f_hint, bg="#1e1e2e", fg="#6c7086").pack()


    return root


def update_stats():
    global active_time, last_start_time


    elapsed = active_time


    with lock:
        is_running = running
   
    if is_running and last_start_time is not None:
        elapsed += time.time() - last_start_time
   
    hours = int(elapsed //3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)


    if time_label:
        time_label.config(
            text=f"Runtime: {hours:02}:{minutes:02}:{seconds:02}"
        )


    root.after(250, update_stats)


if __name__ == "__main__":
    keyboard.on_press_key(TOGGLE_KEY, on_hotkey)
    threading.Thread(target=auto_press_loop, daemon=True).start()
    root = build_gui()
    update_stats()
    print("INFO P = Start/Stop | Close window to exit")
    root.mainloop()
