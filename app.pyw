import tkinter as tk
from tkinter import messagebox
from pynput import keyboard
import psutil
import os
import ctypes
from ctypes import wintypes
import json
import sys
import subprocess
from pystray import Icon, Menu, MenuItem
from PIL import Image
import threading


class KeyDisplayApp:
    def __init__(self):
        self.get_settings()

        self.root = tk.Tk()
        self.root.title("Key Display")
        self.configure_window()

        self.label = tk.Label(
            self.root,
            text="",
            font=(
                self.settings.get("font-name", " Segoe UI"),
                self.settings.get("font-size", 24),
            ),
            fg="white",
            bg="black",
        )
        self.label.pack(expand=True)

        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )

        self.hide_after_id = None  # Variable to store after() ID for hiding

    def get_settings(self):
        # Load configuration from config.json
        with open("config.json", encoding="utf-8") as f:
            self.settings: dict = json.loads(f.read().strip())

        self.target_exe_path = self.settings.get("executable")
        if not self.target_exe_path:
            messagebox.showinfo(
                "Warning",
                "Specify the path to your exe file in the settings then restart "
                "the app. Right click on the tray app too see the menus",
            )

    def configure_window(self):
        x = self.settings.get("x", self.root.winfo_screenwidth() // 2 - 100)
        y = self.settings.get("y", 5)
        w = self.settings.get("w", 200)
        h = self.settings.get("h", 100)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.config(bg="black")
        self.root.wm_attributes("-transparentcolor", "black")

    def get_foreground_window_pid(self):
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return pid.value

    def is_target_exe_active(self):
        pid = self.get_foreground_window_pid()
        try:
            process = psutil.Process(pid)
            exe_path = process.exe()
            return os.path.normcase(exe_path) == os.path.normcase(self.target_exe_path)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    def on_press(self, key):
        if self.is_target_exe_active():
            if self.hide_after_id:
                # Cancel any scheduled hide if a key is pressed before the timeout
                self.root.after_cancel(self.hide_after_id)

            try:
                key_text = key.char if hasattr(key, "char") else str(key).split(".")[-1]
            except AttributeError:
                key_text = str(key)

            self.label.config(text=key_text)
            self.root.update()

    def on_release(self, key):
        # Schedule hiding the key after 1 second (1000 milliseconds)
        self.hide_after_id = self.root.after(
            self.settings.get("wait", 1) * 1000, self.hide_key_display
        )

    def hide_key_display(self):
        self.label.config(text="")
        self.root.update()

    def run(self):
        self.listener.start()
        self.root.mainloop()

    def update(self):
        self.get_settings()

        # Reconfigure the window
        self.configure_window()
        self.label.after(1, self.configure_window)
        self.label.configure(
            font=(
                self.settings.get("font-name", " Segoe UI"),
                self.settings.get("font-size", 24),
            ),
        )

        # restart the listener
        self.listener.stop()
        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listener.start()

    def stop(self):
        self.listener.stop()
        self.root.destroy()


class TrayApp:
    def __init__(self, key_display_app: KeyDisplayApp):
        self.key_display_app = key_display_app
        self.icon = Image.open("icon.ico")
        self.tray_icon = Icon("MyTrayApp", self.icon, menu=self.create_menu())

    def create_menu(self):
        return Menu(
            MenuItem("Restart", self.on_restart),
            MenuItem("Settings", self.on_settings),
            MenuItem("Exit", self.on_exit),
        )

    def on_restart(self, icon, item):
        key_display_app.update()
        messagebox.showinfo("Success", "restarted the app successfully")

    def on_settings(self, icon, item):
        try:
            subprocess.Popen(
                [sys.executable, "set_config.pyw"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        except Exception as e:
            print(f"Error launching settings: {e}")

    def on_exit(self, icon, item):
        self.key_display_app.stop()
        icon.stop()

    def run(self):
        self.tray_icon.run()


if __name__ == "__main__":
    if not os.path.exists("config.json"):
        with open("config.json", "w", encoding="utf-8") as f:
            f.write(
                json.dumps({}, indent=4, ensure_ascii=False).encode("utf8").decode()
            )

    key_display_app = KeyDisplayApp()
    tray_app = TrayApp(key_display_app)

    # Create a separate thread for the tray app
    tray_thread = threading.Thread(target=tray_app.run)
    tray_thread.daemon = True
    tray_thread.start()

    # Run the key display app
    key_display_app.run()
