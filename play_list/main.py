import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from tkinter import font
import time

# متغير للتوقف عن التحميل
stop_flag = False

# Function to download a single video
def download_video(video_url, save_path, quality, index):
    ydl_opts = {
        'format': 'best' if quality == 'High' else 'worst' if quality == 'Low' else 'b[height<=720]',
        'outtmpl': os.path.join(save_path, f'{index:02d} - %(title)s.%(ext)s'),
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return info_dict.get('title', 'Unknown Title')
    except Exception as e:
        return f"Failed to download: {e}"

# Function to download a playlist
def download_playlist():
    global stop_flag
    playlist_url = entry_url.get()
    save_path = folder_path.get()
    quality = quality_var.get()

    if not playlist_url:
        messagebox.showerror("Error", "Please enter a YouTube playlist URL.")
        return
    if not save_path:
        messagebox.showerror("Error", "Please select a folder to save videos.")
        return

    try:
        ydl_opts = {'quiet': True, 'extract_flat': 'in_playlist'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            video_urls = [video['url'] for video in playlist_info['entries']]

        progress_bar['value'] = 0
        total_videos = len(video_urls)

        for idx, video_url in enumerate(video_urls, start=1):
            if stop_flag:
                listbox.insert(tk.END, "Download stopped.")
                listbox.itemconfig(tk.END, {'bg': '#f39c12'})
                listbox.yview(tk.END)
                break

            title = download_video(video_url, save_path, quality, idx)
            listbox.insert(tk.END, f"{idx}. Downloaded: {title}")
            listbox.itemconfig(tk.END, {'bg': '#1abc9c'})
            listbox.yview(tk.END)

            progress = (idx / total_videos) * 100
            animate_progress(progress)
            progress_label.config(text=f"{progress:.2f}%")
            root.update_idletasks()

        if not stop_flag:
            messagebox.showinfo("Success", "Playlist downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download playlist: {e}")

# Animation for progress bar
def animate_progress(progress):
    current_value = progress_bar['value']
    step = (progress - current_value) / 10
    for i in range(10):
        current_value += step
        progress_bar['value'] = current_value
        time.sleep(0.02)
        root.update_idletasks()

# Function to select a folder
def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)

# Function to start download in a separate thread
def start_download_in_thread():
    global stop_flag
    stop_flag = False
    threading.Thread(target=download_playlist).start()

# Function to stop the download
def stop_download():
    global stop_flag
    stop_flag = True

# Create the main window
root = tk.Tk()
root.title("YouTube Playlist Downloader")

# إضافة الأيقونة المخصصة
root.iconbitmap('icon/download.ico')  # تأكد من وجود ملف الأيقونة icon.ico في نفس المجلد

# تحديد الحد الأدنى لحجم النافذة
root.minsize(800, 600)

# إعدادات النافذة
root.geometry("800x600")
root.config(bg="#f5f5f5")

# Variables
folder_path = tk.StringVar()
quality_var = tk.StringVar(value="High")

# Fonts and styles
heading_font = font.Font(family="Helvetica", size=16, weight="bold")
button_font = font.Font(family="Helvetica", size=12)
label_font = font.Font(family="Helvetica", size=12)

# Layout
root.columnconfigure(1, weight=1)
root.rowconfigure(6, weight=1)

# URL Input
tk.Label(root, text="YouTube Playlist URL:", font=label_font, bg="#f5f5f5", fg="#34495e").grid(row=0, column=0, pady=5, padx=5, sticky="w")
entry_url = tk.Entry(root, font=label_font, bg="#ecf0f1", fg="#2c3e50")
entry_url.grid(row=0, column=1, pady=5, padx=5, sticky="ew")

# Folder Selection
tk.Label(root, text="Save Folder:", font=label_font, bg="#f5f5f5", fg="#34495e").grid(row=1, column=0, pady=5, padx=5, sticky="w")
entry_folder = tk.Entry(root, textvariable=folder_path, font=label_font, bg="#ecf0f1", fg="#2c3e50")
entry_folder.grid(row=1, column=1, pady=5, padx=5, sticky="ew")
tk.Button(root, text="Browse", font=button_font, bg="#3498db", fg="white", command=browse_folder).grid(row=1, column=2, pady=5, padx=5)

# Quality Selection
tk.Label(root, text="Select Quality:", font=label_font, bg="#f5f5f5", fg="#34495e").grid(row=2, column=0, pady=5, padx=5, sticky="w")
quality_menu = ttk.Combobox(root, textvariable=quality_var, values=["Low", "Medium", "High"], font=label_font)
quality_menu.grid(row=2, column=1, pady=5, padx=5, sticky="w")

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

# Progress Label
progress_label = tk.Label(root, text="0%", font=label_font, bg="#f5f5f5", fg="#2c3e50")
progress_label.grid(row=3, column=2, padx=10)

# Control Buttons
tk.Button(root, text="Download", font=button_font, bg="#1abc9c", fg="white", command=start_download_in_thread).grid(row=4, column=1, pady=5)
tk.Button(root, text="Stop", font=button_font, bg="#e74c3c", fg="white", command=stop_download).grid(row=4, column=2, pady=5)

# Listbox with Scrollbar
list_frame = ttk.Frame(root)
list_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")
scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Helvetica", 10))
listbox.pack(expand=True, fill=tk.BOTH)
scrollbar.config(command=listbox.yview)

# Run the application
root.mainloop()
