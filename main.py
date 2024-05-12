import time
import tkinter as tk
from tkinter import messagebox, Entry, LabelFrame, END, filedialog
from tkinter.ttk import Progressbar, Style
from threading import Thread
import sys
from tkinterdnd2 import DND_FILES, TkinterDnD
from pathlib import Path
from sys import argv

import pyperclip
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from utils import get_video_info_and_shortlink

class DiscordClipUploader:

    def __init__(self, root):
        self.root = root
        self.root.title("DiscordClipUploader")
        self.root.geometry("600x500")

        self.file_path = ""
        self.upload_speed = tk.StringVar()
        self.eta = tk.StringVar()

        self.label = tk.Label(self.root, text="Clip Name: ")
        self.label.pack(pady=0)

        self.text_field = Entry(self.root, width=20)
        self.text_field.pack(pady=3)

        self.frame = LabelFrame(self.root, text="Drag and drop files here", width=400, height=200)
        self.frame.pack(pady=15)

        self.frame.drop_target_register(DND_FILES)
        self.frame.dnd_bind('<<Drop>>', self.drop)
        self.frame.bind("<Button-1>", self.browse_file)

        self.btn_upload = tk.Button(self.root, text="Upload", command=self.upload_file, padx=50, pady=5)
        self.btn_upload.pack(pady=10)

        self.lbl_drag_and_drop = tk.Label(self.root,
                                          text="Drag a file into the box above, or click to select a file.\n Then press the button")
        self.lbl_drag_and_drop.pack()

        self.progress = None
        self.lbl_speed = None
        self.lbl_eta = None

        print(self.file_path)

    def clear_progress_elements(self):
        if self.progress:
            self.progress.destroy()
        if self.lbl_speed:
            self.lbl_speed.destroy()
        if self.lbl_eta:
            self.lbl_eta.destroy()

    def upload_file(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a file first")
            return

        if not self.text_field.get():
            messagebox.showerror("Error", "Please enter a name for the clip")
            return

        self.clear_progress_elements()

        self.progress = Progressbar(
            self.root, orient="horizontal", length=300, mode="determinate"
        )
        self.progress.pack(pady=10)

        self.lbl_speed = tk.Label(self.root, textvariable=self.upload_speed)
        self.lbl_speed.pack()
        self.lbl_eta = tk.Label(self.root, textvariable=self.eta)
        self.lbl_eta.pack()

        self.btn_upload.config(state="disabled")
        upload_thread = Thread(target=self.upload_threaded)
        upload_thread.start()

    def upload_threaded(self):
        start_time = time.time()

        def callback(monitor):
            elapsed_time = time.time() - start_time
            speed = monitor.bytes_read / elapsed_time / (1024 * 1024)  # MB/s
            self.upload_speed.set(f"Speed: {speed:.2f} MB/s")

            if speed > 0:
                remaining_time = (monitor.len - monitor.bytes_read) / (
                    speed * 1024 * 1024
                )  # seconds
                self.eta.set(f"ETA: {remaining_time:.2f} seconds")

            self.progress["value"] = (monitor.bytes_read / monitor.len) * 100
            self.root.update_idletasks()

        multipart_data = MultipartEncoder(
            fields={
                "files[]": (
                    Path(self.file_path).name,
                    open(self.file_path, "rb"),
                    "text/plain",
                )
            }
        )

        monitor = MultipartEncoderMonitor(multipart_data, callback)

        url = "https://up1.fileditch.com/upload.php"

        response = requests.post(
            url, data=monitor, headers={"Content-Type": monitor.content_type}
        )
        self.eta.set("Almost there...")

        if response.status_code == 200:
            json_response = response.json()
            link = json_response["files"][0]["url"]

            tocopy = (
                "["
                + self.text_field.get()
                + "]("
                + get_video_info_and_shortlink(link, self.file_path)
                + ")"
            )
            pyperclip.copy(tocopy)
            messagebox.showinfo(
                "Success!",
                "The clip link has been copied to your clipboard! You can send it on Discord.",
            )
        else:
            messagebox.showerror(
                "Error", f"Upload failed!\nStatus code: {response.status_code}"
            )

        self.progress["value"] = 0
        self.upload_speed.set("")
        self.eta.set("")
        self.file_path = ""
        self.frame.config(text="Drag and drop files here")
        self.btn_upload.config(state="normal")
        self.text_field.delete(0, END)

    def drop(self, event):
        # added these because for some reason it adds leading { } characters and it crashes
        if event.data.startswith("{"):
            event.data = event.data[1:]
        if event.data.endswith("}"):
            event.data = event.data[:-1]
        self.file_path = event.data
        self.frame.config(text=f"Selected file: {Path(self.file_path).name}")

    def browse_file(self, event):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_path = file_path
            self.frame.config(text=f"Selected file: {Path(self.file_path).name}")

    def run(self):
        self.root.mainloop()


class AutoClipUploader:

    def __init__(self, root, file_path: str):
        self.root = root
        self.root.title("DiscordClipUploader")
        self.root.geometry("500x100")

        self.file_path = file_path
        self.clip_name = file_path.split(".")[0]
        self.upload_speed = tk.StringVar()
        self.eta = tk.StringVar()

        self.progress = None
        self.lbl_speed = None
        self.lbl_eta = None

        self.upload_file()

    def clear_progress_elements(self):
        if self.progress:
            self.progress.destroy()
        if self.lbl_speed:
            self.lbl_speed.destroy()
        if self.lbl_eta:
            self.lbl_eta.destroy()

    def upload_file(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a file first")
            return

        if not self.clip_name:
            messagebox.showerror("Error", "Please enter a name for the clip")
            return

        self.clear_progress_elements()

        self.progress = Progressbar(
            self.root, orient="horizontal", length=300, mode="determinate"
        )
        self.progress.pack(pady=10)

        self.lbl_speed = tk.Label(self.root, textvariable=self.upload_speed)
        self.lbl_speed.pack()
        self.lbl_eta = tk.Label(self.root, textvariable=self.eta)
        self.lbl_eta.pack()

        upload_thread = Thread(target=self.upload_threaded)
        upload_thread.start()

    def upload_threaded(self):
        start_time = time.time()

        def callback(monitor):
            elapsed_time = time.time() - start_time
            speed = monitor.bytes_read / elapsed_time / (1024 * 1024)  # MB/s
            self.upload_speed.set(f"Speed: {speed:.2f} MB/s")

            if speed > 0:
                remaining_time = (monitor.len - monitor.bytes_read) / (
                    speed * 1024 * 1024
                )  # seconds
                self.eta.set(f"ETA: {remaining_time:.2f} seconds")

            self.progress["value"] = (monitor.bytes_read / monitor.len) * 100
            self.root.update_idletasks()

        multipart_data = MultipartEncoder(
            fields={
                "files[]": (
                    Path(self.file_path).name,
                    open(self.file_path, "rb"),
                    "text/plain",
                )
            }
        )

        monitor = MultipartEncoderMonitor(multipart_data, callback)

        url = "https://up1.fileditch.com/upload.php"

        response = requests.post(
            url, data=monitor, headers={"Content-Type": monitor.content_type}
        )
        self.eta.set("Almost there...")

        if response.status_code == 200:
            json_response = response.json()
            link = json_response["files"][0]["url"]

            tocopy = (
                "["
                + self.clip_name
                + "]("
                + get_video_info_and_shortlink(link, self.file_path)
                + ")"
            )
            pyperclip.copy(tocopy)
            messagebox.showinfo(
                "Success!",
                "The clip link has been copied to your clipboard! You can send it on Discord.",
            )
            self.root.destroy()
        else:
            messagebox.showerror(
                "Error", f"Upload failed!\nStatus code: {response.status_code}"
            )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # If there are less then 2 arguments, no filepath was provided,
    # so don't prefill the file path field
    if len(argv) < 2:
        root = TkinterDnD.Tk()
        app = DiscordClipUploader(root)
        app.run()

    else:
        # Check if the argument provided is a file path that exists
        file_path = argv[1]
        if not Path(file_path).exists():
            messagebox.showerror(
                "Error",
                "The file path provided does not exist.\nPlease provide a valid file path or run the program without arguments to choose your video from the GUI.",
            )
        else:
            root = TkinterDnD.Tk()
            app = AutoClipUploader(root, file_path)
            app.run()
