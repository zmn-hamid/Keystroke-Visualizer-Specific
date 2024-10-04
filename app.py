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
import enum


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
                self.settings.get("font-size", 18),
            ),
            fg="white",
            bg="black",
        )
        self.label.pack(expand=True)

        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )

        self.cancel_after_ids = []  # Variable to store after() IDs
        self.stacked_keys = []

    def get_settings(self):
        # Load configuration from config.json
        with open("config.json", encoding="utf-8") as f:
            self.settings: dict = json.loads(f.read().strip())

        self.target_exe_paths = self.settings.get("executables")
        if not self.target_exe_paths:
            messagebox.showinfo(
                "Warning",
                "Specify at least one application (path to the exe file) in the settings, then restart "
                "the app. Right click on the tray icon for more information.",
            )

    def configure_window(self):
        x = self.settings.get("x", self.root.winfo_screenwidth() // 2 - 200)
        y = self.settings.get("y", 5)
        w = self.settings.get("w", 400)
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
            return os.path.normcase(exe_path) in [
                os.path.normcase(target) for target in self.target_exe_paths
            ]
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    def on_press(self, key: enum.Enum | keyboard.KeyCode):
        if self.is_target_exe_active():
            if self.cancel_after_ids:
                # Cancel any scheduled hide if a key is pressed before the timeout
                for _id in self.cancel_after_ids:
                    self.root.after_cancel(_id)
                self.cancel_after_ids = []

            keys_to_print = [item for item in self.stacked_keys]
            try:
                key_text = str(key.char)
                self.stacked_keys = []
                keys_to_print.append(key_text)
            except AttributeError:
                key_text = str(key).split(".")[-1].split("_")[0]
                if key_text.lower() not in ["ctrl", "shift", "alt", "cmd"]:
                    self.stacked_keys = []
                    keys_to_print.append(key_text)
                elif key_text in self.stacked_keys:
                    self.stacked_keys = keys_to_print = [key_text]
                else:
                    self.stacked_keys.append(key_text)
                    keys_to_print.append(key_text)

            self.label.config(text="+".join(keys_to_print).upper())
            self.root.update()

    def on_release(self, key):
        # Schedule hiding the key after 1 second (1000 milliseconds)
        self.cancel_after_ids.append(
            self.root.after(self.settings.get("hide", 1) * 1000, self.hide_key_display)
        )
        self.stacked_keys = []

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


class ConfigEditor:
    def __init__(self, key_display_app: KeyDisplayApp):
        self.key_display_app = key_display_app
        self.config_file = "config.json"
        self.config = self.load_config()
        self.root = tk.Tk()
        self.root.iconbitmap("icon.ico")
        self.root.title("Settings Editor")
        self.sw, self.sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.create_widgets()

    # Load config from file
    def load_config(self):
        try:
            with open(self.config_file, encoding="utf-8") as f:
                return json.loads(f.read().strip())
        except FileNotFoundError:
            messagebox.showerror("Error", "Config file not found!")
            return {}
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Error decoding config file!")
            return {}

    # Save updated config to file
    def save_config(self, config):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                f.write(
                    json.dumps(config, indent=4, ensure_ascii=False)
                    .encode("utf8")
                    .decode()
                )
            self.key_display_app.update()
            messagebox.showinfo("Success", "Settings successfully changed!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving config: {e}")

    # Check if paths contain missing or invalid quotes
    def validate_paths(self, paths):
        invalid_paths = [path for path in paths if '"' in path]
        if invalid_paths:
            messagebox.showwarning(
                "Warning",
                f"Remove double quotation marks from these paths:\n\n"
                + "\n".join(invalid_paths),
            )
            return False
        return True

    # Main logic for updating config based on user input
    def update_config(self):
        changes_made = False
        executables = list(
            set(self.executable_entry.get("1.0", tk.END).strip().splitlines())
        )
        x = self.x_entry.get().strip()
        y = self.y_entry.get().strip()
        w = self.w_entry.get().strip()
        h = self.h_entry.get().strip()
        font_name = (
            self.font_name_entry.get().strip()
        )  # Use 'font_name' with underscore
        font_size = self.font_size_entry.get().strip()
        hide_time = self.hide_entry.get().strip()  # Corrected to 'hide_entry'

        try:
            if not executables:
                messagebox.showwarning(
                    "Warning",
                    "You shouldn't leave the executables empty. Put at least one exe path.",
                )
            elif (
                executables != self.config.get("executables", [])
                and executables
                and self.validate_paths(executables)
            ):
                self.config["executables"] = executables
                changes_made = True

            if x != str(self.config.get("x", "")):
                if x:
                    self.config["x"] = int(x)
                else:
                    self.config.pop("x", None)
                changes_made = True

            if y != str(self.config.get("y", "")):
                if y:
                    self.config["y"] = int(y)
                else:
                    self.config.pop("y", None)
                changes_made = True

            if w != str(self.config.get("w", "")):
                if w:
                    self.config["w"] = int(w)
                else:
                    self.config.pop("w", None)
                changes_made = True

            if h != str(self.config.get("h", "")):
                if h:
                    self.config["h"] = int(h)
                else:
                    self.config.pop("h", None)
                changes_made = True

            if font_name != self.config.get(
                "font-name", ""
            ):  # Use 'font-name' in config
                if font_name:
                    self.config["font-name"] = font_name
                else:
                    self.config.pop("font-name", None)
                changes_made = True

            if font_size != str(self.config.get("font-size", "")):
                if font_size:
                    self.config["font-size"] = int(font_size)
                else:
                    self.config.pop("font-size", None)
                changes_made = True

            if hide_time != str(self.config.get("hide", "")):
                if hide_time:
                    self.config["hide"] = int(hide_time)
                else:
                    self.config.pop("hide", None)
                changes_made = True

            if changes_made:
                self.save_config(self.config)
            else:
                messagebox.showinfo("No changes", "No changes were made to the config.")
        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter valid numeric values for x, y, width, height, font size, and hide time!",
            )
        except KeyError as e:
            messagebox.showerror("Error", f"Error updating config: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")

    # Create input fields and layout
    def create_widgets(self):
        tk.Label(self.root, text=f"Available resolution: {self.sw} x {self.sh}").pack(
            pady=10, padx=20
        )

        tk.Label(self.root, text="Executable Paths (one per line):").pack(
            padx=20, anchor="w"
        )
        self.executable_entry = tk.Text(self.root, width=50, height=5)
        self.executable_entry.insert(
            "1.0", "\n".join(self.config.get("executables", []))
        )
        self.executable_entry.pack(pady=5, padx=20)

        self.create_entry("X Position:", "x", 50)
        self.create_entry("Y Position:", "y", 50)
        self.create_entry("Width:", "w", 50)
        self.create_entry("Height:", "h", 50)
        self.create_entry(
            "Font Name:", "font_name", 50
        )  # Use underscore in entry names
        self.create_entry("Font Size:", "font_size", 50)
        self.create_entry(
            "Hide After (seconds):", "hide", 50
        )  # Corrected the key to "hide"

        tk.Button(self.root, text="Apply Settings", command=self.update_config).pack(
            pady=20, padx=20
        )

        self.root.mainloop()

    # Create a labeled entry widget
    def create_entry(self, label, config_key, width):
        tk.Label(self.root, text=label).pack(padx=20, anchor="w")
        entry = tk.Entry(self.root, width=width)
        entry.insert(
            0, self.config.get(config_key.replace("_", "-"), "")
        )  # Replace underscore with hyphen for config keys
        entry.pack(pady=5, padx=20)

        # Dynamically assign the entry widget to the instance based on config_key
        setattr(self, f"{config_key}_entry", entry)


class TrayApp:
    def __init__(self, key_display_app: KeyDisplayApp):
        self.key_display_app = key_display_app
        self.icon = Image.open("icon.ico")
        self.tray_icon = Icon("MyTrayApp", self.icon, menu=self.create_menu())

    def create_menu(self):
        return Menu(
            MenuItem("Settings", self.on_settings),
            MenuItem("Exit", self.on_exit),
        )

    def on_settings(self, icon, item):
        def _foo():
            try:
                ConfigEditor(key_display_app)
                # key_display_app.update()
            except Exception as e:
                print(f"Error launching settings: {e}")

        settings_thread = threading.Thread(target=_foo)
        settings_thread.daemon = True
        settings_thread.start()

    def on_exit(self, icon, item):
        self.key_display_app.stop()
        icon.stop()

    def run(self):
        self.tray_icon.run()


if __name__ == "__main__":
    if not os.path.exists("config.json"):
        with open("config.json", "w", encoding="utf-8") as f:
            f.write(
                json.dumps({"executables": []}, indent=4, ensure_ascii=False)
                .encode("utf8")
                .decode()
            )

    key_display_app = KeyDisplayApp()

    tray_app = TrayApp(key_display_app)
    tray_thread = threading.Thread(target=tray_app.run)
    tray_thread.daemon = True
    tray_thread.start()

    key_display_app.run()
