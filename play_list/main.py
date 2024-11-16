import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from tkinter import font

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
        ydl_opts = {
            'quiet': True,
            'extract_flat': 'in_playlist',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            video_urls = [video['url'] for video in playlist_info['entries']]

        progress_bar['value'] = 0
        total_videos = len(video_urls)

        for idx, video_url in enumerate(video_urls, start=1):
            if stop_flag:
                listbox.insert(tk.END, "Download stopped.")
                listbox.yview(tk.END)
                break

            title = download_video(video_url, save_path, quality, idx)
            listbox.insert(tk.END, f"{idx}. Downloaded: {title}")
            listbox.yview(tk.END)

            # Update progress bar
            progress = (idx / total_videos) * 100
            progress_bar['value'] = progress
            progress_label.config(text=f"{progress:.2f}%")
            root.update_idletasks()

        if not stop_flag:
            messagebox.showinfo("Success", "Playlist downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download playlist: {e}")

# Function to select a folder
def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)

# Function to start download in a separate thread
def start_download_in_thread():
    global stop_flag
    stop_flag = False  # إعادة تعيين العلم إلى False قبل بدء التحميل
    download_thread = threading.Thread(target=download_playlist)
    download_thread.start()

# Function to stop the download
def stop_download():
    global stop_flag
    stop_flag = True

# Create the main window
root = tk.Tk()
root.title("YouTube Playlist Downloader with yt-dlp")
root.geometry("700x700")
root.config(bg="#ECF0F1")  # Light background color

# Variables
folder_path = tk.StringVar()
quality_var = tk.StringVar(value="High")

# Fonts and styles
custom_font = font.Font(family="Roboto", size=12)
heading_font = font.Font(family="Poppins", size=16, weight="bold")
button_style = {"font": custom_font, "bg": "#3498db", "fg": "white", "activebackground": "#2980b9", "activeforeground": "white", "relief": "flat", "padx": 15, "pady": 10}
label_style = {"font": custom_font, "bg": "#ECF0F1", "fg": "#2C3E50"}
entry_style = {"font": custom_font, "width": 50, "bd": 2, "relief": "solid", "fg": "#2C3E50"}

# URL Input
tk.Label(root, text="YouTube Playlist URL:", **label_style).grid(row=0, column=0, pady=10, padx=10, sticky="w")
entry_url = tk.Entry(root, **entry_style)
entry_url.grid(row=0, column=1, pady=5, padx=10)

# Folder Selection
tk.Label(root, text="Select Folder to Save Videos:", **label_style).grid(row=1, column=0, pady=10, padx=10, sticky="w")
frame_folder = tk.Frame(root, bg="#ECF0F1")
frame_folder.grid(row=1, column=1, pady=5, padx=10, sticky="w")
entry_folder = tk.Entry(frame_folder, textvariable=folder_path, **entry_style)
entry_folder.grid(row=0, column=0, padx=5)
btn_browse = tk.Button(frame_folder, text="Browse", command=browse_folder, **button_style)
btn_browse.grid(row=0, column=1)

# Quality Selection
tk.Label(root, text="Select Video Quality:", **label_style).grid(row=2, column=0, pady=10, padx=10, sticky="w")
quality_options = ["Low", "Medium", "High"]
quality_menu = ttk.Combobox(root, textvariable=quality_var, values=quality_options, font=custom_font, width=15)
quality_menu.grid(row=2, column=1, pady=5, padx=10)

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=2, pady=20)

# Progress Label
progress_label = tk.Label(root, text="0%", **label_style)
progress_label.grid(row=3, column=2, padx=10)

# Download Button
btn_download = tk.Button(root, text="Download Playlist", command=start_download_in_thread, **button_style)
btn_download.grid(row=4, column=0, columnspan=2, pady=10)

# Stop Button
btn_stop = tk.Button(root, text="Stop", command=stop_download, **button_style)
btn_stop.grid(row=5, column=0, columnspan=2, pady=10)

# Listbox to Display Status
listbox = tk.Listbox(root, width=70, height=10, font=("Arial", 10), bd=0, bg="#ECF0F1", highlightthickness=0)
listbox.grid(row=6, column=0, columnspan=2, pady=10)

# Function for button hover effects
def on_enter(event):
    event.widget.config(bg="#2980b9")

def on_leave(event):
    event.widget.config(bg="#3498db")

# Apply hover effect to buttons
btn_download.bind("<Enter>", on_enter)
btn_download.bind("<Leave>", on_leave)

btn_stop.bind("<Enter>", on_enter)
btn_stop.bind("<Leave>", on_leave)

# Run the application
root.mainloop()
