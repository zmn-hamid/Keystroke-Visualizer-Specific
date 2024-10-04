import os
import json
import tkinter as tk
from tkinter import messagebox


# Load config from file
def load_config():
    try:
        with open("config.json", encoding="utf-8") as f:
            return json.loads(f.read().strip())
    except FileNotFoundError:
        messagebox.showerror("Error", "Config file not found!")
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Error decoding config file!")
        return {}


# Save updated config to file
def save_config(config, do_log: bool = True):
    try:
        with open("config.json", "w", encoding="utf-8") as f:
            f.write(
                json.dumps(config, indent=4, ensure_ascii=False).encode("utf8").decode()
            )
        if do_log:
            messagebox.showinfo(
                "Success", "Config saved successfully. Restart the app!"
            )
    except Exception as e:
        messagebox.showerror("Error", f"Error saving config: {e}")


# Check if paths contain missing or invalid quotes
def validate_paths(paths):
    invalid_paths = [path for path in paths if '"' in path]
    if invalid_paths:
        messagebox.showwarning(
            "Warning",
            f"remove double quotation from these paths:\n\n" + "\n".join(invalid_paths),
        )
        return False
    return True


# Main logic for updating config based on user input
def update_config():
    changes_made = False
    executables = list(set(executable_entry.get("1.0", tk.END).strip().splitlines()))
    x = x_entry.get().strip()
    y = y_entry.get().strip()
    w = w_entry.get().strip()
    h = h_entry.get().strip()
    font_name = font_name_entry.get().strip()
    font_size = font_size_entry.get().strip()
    hide_time = hide_time_entry.get().strip()

    try:
        if not executables:
            messagebox.showwarning(
                "Warning",
                f"You shouldn't leave the executables empty. Put at least one exe path",
            )
        # Handle 'executables' field
        elif (
            executables != config.get("executables", [])
            and executables
            and validate_paths(executables)
        ):  # Update if valid
            config["executables"] = executables
            changes_made = True

        # Handle 'x' field
        if x != str(config.get("x", "")):
            if x:  # Update if non-empty
                config["x"] = int(x)
            else:  # Pop if cleared
                config.pop("x", None)
            changes_made = True

        # Handle 'y' field
        if y != str(config.get("y", "")):
            if y:  # Update if non-empty
                config["y"] = int(y)
            else:  # Pop if cleared
                config.pop("y", None)
            changes_made = True

        # Handle 'w' field
        if w != str(config.get("w", "")):
            if w:  # Update if non-empty
                config["w"] = int(w)
            else:  # Pop if cleared
                config.pop("w", None)
            changes_made = True

        # Handle 'h' field
        if h != str(config.get("h", "")):
            if h:  # Update if non-empty
                config["h"] = int(h)
            else:  # Pop if cleared
                config.pop("h", None)
            changes_made = True

        # Handle 'font-name' field
        if font_name != config.get("font-name", ""):
            if font_name:  # Update if non-empty
                config["font-name"] = font_name
            else:  # Pop if cleared
                config.pop("font-name", None)
            changes_made = True

        # Handle 'font-size' field
        if font_size != str(config.get("font-size", "")):
            if font_size:  # Update if non-empty
                config["font-size"] = int(font_size)
            else:  # Pop if cleared
                config.pop("font-size", None)
            changes_made = True

        # Handle 'hide after' field
        if hide_time != str(config.get("hide", "")):
            if hide_time:  # Update if non-empty
                config["hide"] = int(hide_time)
            else:  # Pop if cleared
                config.pop("hide", None)
            changes_made = True

        if changes_made:
            save_config(config, True)
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


if __name__ == "__main__":
    if not os.path.exists("config.json"):
        save_config({"executables": []}, False)

    # Initialize Tkinter app
    root = tk.Tk()
    root.iconbitmap("icon.ico")
    root.title("Settings Editor")

    # Load screen resolution
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()

    # Load current config
    config = load_config()

    # Display current config
    config_label = tk.Label(root, text=f"Available resolution: {sw} x {sh}")
    config_label.pack(pady=10, padx=20)

    # Create input fields with current config values
    tk.Label(root, text="Executable Paths (one per line):").pack(padx=20, anchor="w")
    executable_entry = tk.Text(root, width=50, height=5)
    executable_entry.insert("1.0", "\n".join(config.get("executables", [])))
    executable_entry.pack(pady=5, padx=20)

    tk.Label(root, text="X Position:").pack(padx=20, anchor="w")
    x_entry = tk.Entry(root, width=50)
    x_entry.insert(0, config.get("x", ""))
    x_entry.pack(pady=5, padx=20)

    tk.Label(root, text="Y Position:").pack(padx=20, anchor="w")
    y_entry = tk.Entry(root, width=50)
    y_entry.insert(0, config.get("y", ""))
    y_entry.pack(pady=5, padx=20)

    tk.Label(root, text="Width:").pack(padx=20, anchor="w")
    w_entry = tk.Entry(root, width=50)
    w_entry.insert(0, config.get("w", ""))
    w_entry.pack(pady=5, padx=20)

    tk.Label(root, text="Height:").pack(padx=20, anchor="w")
    h_entry = tk.Entry(root, width=50)
    h_entry.insert(0, config.get("h", ""))
    h_entry.pack(pady=5, padx=20)

    tk.Label(root, text="Font Name:").pack(padx=20, anchor="w")
    font_name_entry = tk.Entry(root, width=50)
    font_name_entry.insert(0, config.get("font-name", ""))
    font_name_entry.pack(pady=5, padx=20)

    tk.Label(root, text="Font Size:").pack(padx=20, anchor="w")
    font_size_entry = tk.Entry(root, width=50)
    font_size_entry.insert(0, config.get("font-size", ""))
    font_size_entry.pack(pady=5, padx=20)

    tk.Label(root, text="Hide After (seconds):").pack(padx=20, anchor="w")
    hide_time_entry = tk.Entry(root, width=50)
    hide_time_entry.insert(0, config.get("hide", ""))
    hide_time_entry.pack(pady=5, padx=20)

    # Update button
    update_button = tk.Button(root, text="Save Config", command=update_config)
    update_button.pack(pady=20, padx=20)

    # Run the Tkinter event loop
    root.mainloop()
