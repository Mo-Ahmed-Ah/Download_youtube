import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import re
import subprocess
import requests
import zipfile
import shutil

# متغير للتوقف عن التحميل
stop_flag = False

# رابط تنزيل FFmpeg الرسمي
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

# دالة للتحقق من تثبيت FFmpeg
def check_and_install_ffmpeg():
    try:
        # محاولة تشغيل ffmpeg للتحقق من تثبيته
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("FFmpeg is already installed.")
    except FileNotFoundError:
        # في حالة عدم العثور على ffmpeg
        print("FFmpeg not found. Installing...")
        install_ffmpeg()

# دالة لتحميل وتثبيت FFmpeg
def install_ffmpeg():
    try:
        # تنزيل الملف المضغوط
        response = requests.get(FFMPEG_URL, stream=True)
        zip_file_path = os.path.join(os.getcwd(), "ffmpeg.zip")
        
        with open(zip_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        
        print("FFmpeg downloaded successfully.")

        # فك ضغط الملف
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall("ffmpeg_temp")

        # نقل الملفات إلى مجلد FFmpeg
        ffmpeg_dir = os.path.join("ffmpeg_temp", os.listdir("ffmpeg_temp")[0], "bin")
        ffmpeg_exe = os.path.join(ffmpeg_dir, "ffmpeg.exe")
        ffprobe_exe = os.path.join(ffmpeg_dir, "ffprobe.exe")
        
        # نقل الملفات إلى المسار الحالي
        shutil.move(ffmpeg_exe, os.path.join(os.getcwd(), "ffmpeg.exe"))
        shutil.move(ffprobe_exe, os.path.join(os.getcwd(), "ffprobe.exe"))

        # تنظيف الملفات
        shutil.rmtree("ffmpeg_temp")
        os.remove(zip_file_path)
        
        print("FFmpeg installed successfully.")
        messagebox.showinfo("FFmpeg Installed", "FFmpeg has been installed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to install FFmpeg: {e}")

# إضافة ffmpeg إلى PATH
def add_ffmpeg_to_path():
    current_path = os.environ.get("PATH", "")
    ffmpeg_path = os.getcwd()
    if ffmpeg_path not in current_path:
        os.environ["PATH"] += os.pathsep + ffmpeg_path

# دالة لإزالة الأحرف غير الصالحة من أسماء الملفات
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

# دالة للتحقق من صلاحية المسار
def is_valid_path(path):
    """التحقق إذا كان المسار صالحًا وقابلًا للكتابة"""
    return os.path.isdir(path) and os.access(path, os.W_OK)

# دالة لضبط مسار التحميل
def adjust_path(path):
    """ضبط المسار ليكون مسارًا صحيحًا وقابلًا للكتابة"""
    if not is_valid_path(path):
        default_path = os.path.expanduser("~/Documents")
        messagebox.showinfo("Path Issue", f"The selected path is invalid. Using default path: {default_path}")
        return default_path
    return path

# دالة لتحديث شريط التقدم
def update_progress(d):
    if d['status'] == 'downloading':
        progress = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        progress_bar['value'] = progress
        progress_label.config(text=f"{progress:.2f}%")
        root.update_idletasks()
    elif d['status'] == 'finished':
        progress_bar['value'] = 100
        progress_label.config(text="100%")
        root.update_idletasks()

# دالة لتحميل الفيديو
def download_video(video_url, save_path, quality, index):
    try:
        save_path = adjust_path(save_path)
        format_option = f"bestvideo[height<={quality[:-1]}]+bestaudio/best"
        file_name = sanitize_filename(f'{index:02d} - %(title)s.mp4').replace(" ", "_")
        file_path = os.path.join(save_path, file_name)
        
        ydl_opts = {
            'format': format_option,
            'outtmpl': file_path,
            'quiet': True,
            'noplaylist': True,
            'progress_hooks': [update_progress],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            return info_dict.get('title', 'Unknown Title')
    except Exception as e:
        print(f"Download failed: {e}")
        return f"Failed to download: {e}"

# دالة لتحميل قائمة التشغيل
def download_playlist():
    global stop_flag
    stop_flag = False
    playlist_url = entry_url.get()
    save_path = folder_path.get()
    quality = quality_var.get()

    if not playlist_url or not save_path or not quality:
        messagebox.showerror("Error", "Please fill in all fields.")
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
                break
            title = download_video(video_url, save_path, quality, idx)
            listbox.insert(tk.END, f"{idx}. Downloaded: {title}")
            listbox.itemconfig(tk.END, {'bg': '#1abc9c'})
            listbox.yview(tk.END)
            progress = (idx / total_videos) * 100
            progress_bar['value'] = progress
            progress_label.config(text=f"{progress:.2f}%")
            root.update_idletasks()

        if not stop_flag:
            messagebox.showinfo("Success", "Playlist downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download playlist: {e}")

# دالة لاختيار المجلد
def browse_folder():
    folder_selected = filedialog.askdirectory()
    if is_valid_path(folder_selected):
        folder_path.set(folder_selected)
    else:
        messagebox.showerror("Invalid Path", "The selected folder is not writable or does not exist.")

def start_download_in_thread():
    global stop_flag
    stop_flag = False
    threading.Thread(target=download_playlist).start()

def stop_download():
    global stop_flag
    stop_flag = True
    messagebox.showinfo("Stopped", "Download has been stopped.")

# التحقق من FFmpeg عند بدء البرنامج
check_and_install_ffmpeg()
add_ffmpeg_to_path()

# إنشاء نافذة التطبيق
root = tk.Tk()
root.title("YouTube Playlist Downloader")
root.geometry("800x600")
root.config(bg="#f5f5f5")

folder_path = tk.StringVar()
quality_var = tk.StringVar()

standard_qualities = ['1080p', '720p', '480p', '360p', '240p', '144p']

tk.Label(root, text="YouTube Playlist URL:", bg="#f5f5f5").pack(pady=10)
entry_url = tk.Entry(root, width=60)
entry_url.pack()

tk.Label(root, text="Select Standard Quality:", bg="#f5f5f5").pack(pady=10)
quality_menu = ttk.Combobox(root, textvariable=quality_var, values=standard_qualities, width=20)
quality_menu.pack()
quality_menu.set('720p')

tk.Label(root, text="Save Folder:", bg="#f5f5f5").pack(pady=10)
tk.Entry(root, textvariable=folder_path, width=60).pack(pady=5)
tk.Button(root, text="Browse", command=browse_folder).pack(pady=5)

tk.Button(root, text="Download", command=start_download_in_thread, width=20).pack(pady=10)
tk.Button(root, text="Stop", command=stop_download, width=20).pack(pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=20)
progress_label = tk.Label(root, text="0%", bg="#f5f5f5")
progress_label.pack()

listbox = tk.Listbox(root, height=10, width=80, selectmode=tk.SINGLE)
listbox.pack(fill=tk.BOTH, expand=True, pady=10)

root.mainloop()
