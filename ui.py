import os
import subprocess
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

from capture_images import capture_images  # our capture function

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATTENDANCE_CSV = os.path.join(BASE_DIR, "attendence.csv")  # keep your existing name


# --------------- Logging helper -----------------
def log_message(text_widget: tk.Text, msg: str) -> None:
    text_widget.configure(state="normal")
    text_widget.insert("end", msg + "\n")
    text_widget.see("end")
    text_widget.configure(state="disabled")


# --------------- Button handlers ----------------
def handle_capture_new_person(log_text: tk.Text):
    """Ask for a name and start capturing images in a background thread."""

    name = simpledialog.askstring("Capture New Person", "Enter person name:")
    if not name:
        log_message(log_text, "[WARN] Capture cancelled: no name entered.")
        return

    log_message(log_text, f"[INFO] Starting capture for '{name}'...")

    def worker():
        try:
            # You can change num_images if you want more/less
            capture_images(name, num_images=10)
            log_message(log_text, f"[INFO] Capture for '{name}' finished.")
        except Exception as e:
            log_message(log_text, f"[ERROR] Capture failed: {e}")
            messagebox.showerror("Error", f"Capture failed:\n{e}")

    # Run in background so the GUI doesn't freeze
    threading.Thread(target=worker, daemon=True).start()


def handle_encode_faces(log_text: tk.Text):
    """Run encode_faces.py (assumed to be in same folder)."""
    log_message(log_text, "[INFO] Running encode_faces.py ...")
    try:
        subprocess.run(["python", "encode_faces.py"], check=True)
        log_message(log_text, "[INFO] Encoding completed.")
    except subprocess.CalledProcessError as e:
        log_message(log_text, f"[ERROR] encode_faces.py failed: {e}")
        messagebox.showerror("Error", f"encode_faces.py failed:\n{e}")


def handle_start_attendance(log_text: tk.Text):
    """Run recognize.py (assumed to handle recognition and attendance CSV)."""
    log_message(log_text, "[INFO] Running recognize.py ...")
    try:
        subprocess.run(["python", "recognize.py"], check=True)
        log_message(log_text, "[INFO] Attendance session finished.")
    except subprocess.CalledProcessError as e:
        log_message(log_text, f"[ERROR] recognize.py failed: {e}")
        messagebox.showerror("Error", f"recognize.py failed:\n{e}")


def handle_open_csv(log_text: tk.Text):
    """Open the attendance CSV file with the default app (Excel)."""
    if not os.path.exists(ATTENDANCE_CSV):
        log_message(log_text, "[WARN] Attendance CSV not found.")
        messagebox.showwarning("Not found", "Attendance CSV file not found.")
        return

    log_message(log_text, "[INFO] Opening attendance CSV ...")
    try:
        # Windows:
        os.startfile(ATTENDANCE_CSV)
    except AttributeError:
        # Other OS (Linux/Mac) fallback
        subprocess.Popen(["xdg-open", ATTENDANCE_CSV])


# --------------- Main UI ----------------
def main():
    root = tk.Tk()
    root.title("Face Attendance System")
    root.geometry("900x600")
    root.configure(bg="#1b1f23")  # dark background

    # Main frames
    left_frame = tk.Frame(root, bg="#111518", width=220)
    left_frame.pack(side="left", fill="y")

    right_frame = tk.Frame(root, bg="#1b1f23")
    right_frame.pack(side="right", fill="both", expand=True)

    # Title bar on top of right frame
    title_label = tk.Label(
        right_frame,
        text="Log / Status",
        bg="#1b1f23",
        fg="white",
        font=("Segoe UI", 14, "bold"),
        anchor="w",
        pady=10,
    )
    title_label.pack(side="top", fill="x")

    # Log text widget
    log_text = tk.Text(
        right_frame,
        bg="#05080a",
        fg="#f8f8f2",
        insertbackground="white",
        font=("Consolas", 11),
        state="disabled",
        wrap="word",
    )
    log_text.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 20))

    # Initial message
    log_message(log_text, "[READY] Welcome! Choose an action on the left.")

    # Left panel title
    actions_title = tk.Label(
        left_frame,
        text="Actions",
        bg="#111518",
        fg="white",
        font=("Segoe UI", 14, "bold"),
        pady=20,
    )
    actions_title.pack()

    # Helper for buttons
    def make_button(text, command, bg="#00b894"):
        btn = tk.Button(
            left_frame,
            text=text,
            command=command,
            bg=bg,
            fg="white",
            activebackground="#019670",
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=10,
            width=18,
        )
        btn.pack(pady=8)
        return btn

    # Buttons
    make_button(
        "1. Capture New Person",
        lambda: handle_capture_new_person(log_text),
    )
    make_button(
        "2. Encode Faces",
        lambda: handle_encode_faces(log_text),
    )
    make_button(
        "3. Start Attendance",
        lambda: handle_start_attendance(log_text),
    )
    make_button(
        "4. Open Attendance CSV",
        lambda: handle_open_csv(log_text),
        bg="#0984e3",
    )

    # Exit button
    make_button(
        "Exit",
        root.destroy,
        bg="#d63031",
    )

    root.mainloop()


if __name__ == "__main__":
    main()
