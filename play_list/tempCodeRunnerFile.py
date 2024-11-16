import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Function to download a single video
def download_video(video_url, save_path, quality):
    ydl_opts = {
        'format': 'best' if quality == 'High' else 'worst' if quality == 'Low' else 'b[height<=720]',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
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
            title = download_video(video_url, save_path, quality)
            listbox.insert(tk.END, f"{idx}. Downloaded: {title}")
            listbox.yview(tk.END)

            # Update progress bar
            progress = (idx / total_videos) * 100
            progress_bar['value'] = progress
            root.update_idletasks()

        messagebox.showinfo("Success", "Playlist downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download playlist: {e}")

# Function to select a folder
def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)

# Create the main window
root = tk.Tk()
root.title("YouTube Playlist Downloader with yt-dlp")
root.geometry("600x550")
root.config(bg="#F0F0F0")

# Variables
folder_path = tk.StringVar()
quality_var = tk.StringVar(value="High")

# Styles
button_style = {"font": ("Helvetica", 12), "bg": "#007BFF", "fg": "white", "activebackground": "#0056b3", "activeforeground": "white"}
label_style = {"font": ("Helvetica", 12), "bg": "#F0F0F0"}
entry_style = {"font": ("Helvetica", 12)}

# URL Input
tk.Label(root, text="YouTube Playlist URL:", **label_style).pack(pady=10)
entry_url = tk.Entry(root, width=50, **entry_style)
entry_url.pack(pady=5)

# Folder Selection
tk.Label(root, text="Select Folder to Save Videos:", **label_style).pack(pady=10)
frame_folder = tk.Frame(root, bg="#F0F0F0")
frame_folder.pack(pady=5)
entry_folder = tk.Entry(frame_folder, textvariable=folder_path, width=38, **entry_style)
entry_folder.pack(side=tk.LEFT, padx=5)
btn_browse = tk.Button(frame_folder, text="Browse", command=browse_folder, **button_style)
btn_browse.pack(side=tk.LEFT)

# Quality Selection
tk.Label(root, text="Select Video Quality:", **label_style).pack(pady=10)
quality_options = ["Low", "Medium", "High"]
quality_menu = ttk.Combobox(root, textvariable=quality_var, values=quality_options, font=("Helvetica", 12))
quality_menu.pack(pady=5)

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=20)

# Download Button
btn_download = tk.Button(root, text="Download Playlist", command=download_playlist, **button_style)
btn_download.pack(pady=10)

# Listbox to Display Status
listbox = tk.Listbox(root, width=70, height=10, font=("Helvetica", 10))
listbox.pack(pady=10)

# Run the application
root.mainloop()
