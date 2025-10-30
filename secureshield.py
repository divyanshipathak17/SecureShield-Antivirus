import os
import hashlib
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from tkinter import filedialog

# ---------------- CONFIG ----------------
APP_NAME = "🛡️ SecureShield Antivirus"
QUARANTINE_DIR = "quarantine"
SUSPICIOUS_SIGNATURES = ["virus", "trojan", "worm", "malware", "attack", "payload"]

os.makedirs(QUARANTINE_DIR, exist_ok=True)

# ---------------- CORE ------------------
def is_infected(file_path):
    """Simulate malware detection based on keyword signatures."""
    if not os.path.isfile(file_path):
        return False, None
    try:
        with open(file_path, "rb") as f:
            data = f.read().lower()
            for sig in SUSPICIOUS_SIGNATURES:
                if sig.encode() in data:
                    return True, f"Matched signature '{sig}'"
        return False, None
    except Exception as e:
        return False, str(e)

def quarantine_file(file_path):
    """Move detected file to quarantine folder."""
    try:
        shutil.move(file_path, os.path.join(QUARANTINE_DIR, os.path.basename(file_path)))
        return True
    except Exception as e:
        return False, str(e)

# ---------------- UI --------------------
class AntivirusApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("750x560")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.path_var = tk.StringVar()
        self.progress_var = tk.DoubleVar()
        self.create_widgets()

    def create_widgets(self):
        # Header
        ctk.CTkLabel(self, text=APP_NAME, font=("Segoe UI", 24, "bold")).pack(pady=15)

        # Path frame
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=20, fill="x")

        self.path_entry = ctk.CTkEntry(frame, textvariable=self.path_var, placeholder_text="Select a folder to scan...")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        ctk.CTkButton(frame, text="Browse", command=self.browse_folder).pack(side="right", padx=10)

        # Scan Button
        ctk.CTkButton(self, text="Start Scan", fg_color="#00cc66", hover_color="#00994d", command=self.start_scan).pack(pady=10)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self, variable=self.progress_var, width=600)
        self.progress.pack(pady=5)
        self.progress.set(0)

        # Result box
        self.result_box = tk.Text(self, height=18, bg="#1e1e1e", fg="white", insertbackground="white", relief="flat", wrap="word")
        self.result_box.pack(padx=20, pady=10, fill="both", expand=True)

        # Bottom Buttons
        bottom = ctk.CTkFrame(self)
        bottom.pack(pady=5)

        ctk.CTkButton(bottom, text="Open Quarantine", command=self.open_quarantine, fg_color="#ff6666", hover_color="#cc0000").pack(side="left", padx=10)
        ctk.CTkButton(bottom, text="Clear Log", command=self.clear_log).pack(side="right", padx=10)

    # ---- Utility methods ----
    def browse_folder(self):
        """Open Windows folder dialog safely."""
        self.withdraw()  # Temporarily hide main window
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        self.deiconify()  # Show it again
        if folder:
            self.path_var.set(folder)

    def append_log(self, text, color="white"):
        self.result_box.insert(tk.END, text + "\n")
        self.result_box.see(tk.END)
        self.result_box.update()

    def clear_log(self):
        self.result_box.delete(1.0, tk.END)

    def start_scan(self):
        folder = self.path_var.get().strip()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("Warning", "Please choose a valid folder.")
            return

        self.clear_log()
        infected_files = 0
        self.append_log(f"🔍 Scanning folder: {folder}\n", "cyan")

        # Get all files first to show progress
        all_files = []
        for root, _, files in os.walk(folder):
            for f in files:
                all_files.append(os.path.join(root, f))

        total = len(all_files)
        if total == 0:
            self.append_log("⚠️ No files found in this folder.")
            return

        for i, file_path in enumerate(all_files, 1):
            infected, reason = is_infected(file_path)
            if infected:
                ok, err = quarantine_file(file_path)
                infected_files += 1
                if ok:
                    self.append_log(f"🚨 Infected: {file_path} → Quarantined", "red")
                else:
                    self.append_log(f"⚠️ Failed to quarantine {file_path}: {err}", "yellow")
            else:
                self.append_log(f"✅ Clean: {file_path}", "green")

            # Update progress bar
            self.progress_var.set(i / total)
            self.update_idletasks()

        # Final message
        if infected_files == 0:
            self.append_log("\n✨ No threats found. Your folder is clean!")
        else:
            self.append_log(f"\n⚠️ {infected_files} infected file(s) quarantined.")

        self.progress_var.set(1.0)

    def open_quarantine(self):
        """Open quarantine folder in Windows Explorer."""
        try:
            os.startfile(os.path.abspath(QUARANTINE_DIR))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open quarantine folder:\n{e}")


# ---------------- RUN -------------------
if __name__ == "__main__":
    app = AntivirusApp()
    app.mainloop()