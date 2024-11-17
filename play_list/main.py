import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from tkinter import font
import time

# متغير للتوقف عن التحميل
stop_flag = False

# دالة للبحث عن أقرب جودة أعلى من الجودة المحددة
def get_best_available_format(available_formats, selected_quality):
    quality_map = {
        '144p': 144,
        '240p': 240,
        '360p': 360,
        '480p': 480,
        '720p': 720,
        '1080p': 1080,
        '1440p': 1440,
        '2160p': 2160
    }

    selected_height = quality_map.get(selected_quality, 360)  # الافتراضية 360p

    available_heights = []
    for fmt in available_formats:
        if 'height' in fmt and fmt['ext'] == 'mp4':
            available_heights.append((fmt['height'], fmt['format_id']))

    available_heights.sort()

    for height, format_id in available_heights:
        if height >= selected_height:
            return format_id

    return available_heights[-1][1] if available_heights else 'best'


# دالة لتحميل الفيديو
def download_video(video_url, save_path, quality, index):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            formats = info_dict.get('formats', [])

        best_format = get_best_available_format(formats, quality)

        ydl_opts = {
            'format': best_format,
            'outtmpl': os.path.join(save_path, f'{index:02d} - %(title)s.%(ext)s'),
            'quiet': True,
            'noplaylist': True  # عدم تحميل قائمة التشغيل بأكملها عند طلب فيديو واحد
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return info_dict.get('title', 'Unknown Title')
    except Exception as e:
        return f"Failed to download: {e}"

# دالة لتحميل قائمة التشغيل
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
    if not quality:
        messagebox.showerror("Error", "Please select a quality format.")
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
root.geometry("800x600")
root.config(bg="#f5f5f5")

# Variables
folder_path = tk.StringVar()
quality_var = tk.StringVar()

# قائمة الجودات القياسية
standard_qualities = ['1080p', '720p', '480p', '360p', '240p', '144p']

# Layout
tk.Label(root, text="YouTube Playlist URL:", bg="#f5f5f5").pack()
entry_url = tk.Entry(root)
entry_url.pack()

tk.Label(root, text="Select Standard Quality:").pack()
quality_menu = ttk.Combobox(root, textvariable=quality_var, values=standard_qualities)
quality_menu.pack()
quality_menu.set('720p')

tk.Label(root, text="Save Folder:").pack()
tk.Entry(root, textvariable=folder_path).pack()
tk.Button(root, text="Browse", command=browse_folder).pack()

tk.Button(root, text="Download", command=start_download_in_thread).pack()
tk.Button(root, text="Stop", command=stop_download).pack()

# Progress Bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack()
progress_label = tk.Label(root, text="0%")
progress_label.pack()

# Listbox for logs
listbox = tk.Listbox(root)
listbox.pack(fill=tk.BOTH, expand=True)

# Run the application
root.mainloop()
