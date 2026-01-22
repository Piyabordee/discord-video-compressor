# app.py — GUI + CLI สำหรับบีบอัด ~9MB
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess, os, shlex, sys

TARGET_FILESIZE_MB = 8.2
AUDIO_BITRATE_KBPS = 128
MIN_VIDEO_BITRATE_KBPS = 64

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))
    if os.name == 'nt':
        ffmpeg_path  = os.path.join(app_path, 'ffmpeg.exe')
        ffprobe_path = os.path.join(app_path, 'ffprobe.exe')
    else:
        ffmpeg_path  = os.path.join(app_path, 'ffmpeg')
        ffprobe_path = os.path.join(app_path, 'ffprobe')
    if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
        return ffmpeg_path, ffprobe_path
    try:
        subprocess.run(['ffmpeg','-version'], capture_output=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        subprocess.run(['ffprobe','-version'], capture_output=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        return 'ffmpeg','ffprobe'
    except Exception:
        return None, None

def get_video_duration(ffprobe_path, input_filepath):
    cmd = [ffprobe_path,'-v','error','-show_entries','format=duration',
           '-of','default=noprint_wrappers=1:nokey=1', input_filepath]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    return float(r.stdout.strip())

def compress_once(ffmpeg_path, ffprobe_path, input_file, output_file,
                  target_mb=TARGET_FILESIZE_MB, audio_kbps=AUDIO_BITRATE_KBPS):
    if not os.path.exists(input_file):
        raise FileNotFoundError(input_file)
    dur = get_video_duration(ffprobe_path, input_file)
    target_total_kbps = (target_mb * 8 * 1024) / dur
    v_kbps = target_total_kbps - audio_kbps
    if v_kbps <= 0:
        raise RuntimeError("วิดีโอยาวเกินไปสำหรับงบขนาดไฟล์/เสียงปัจจุบัน")
    if v_kbps < MIN_VIDEO_BITRATE_KBPS:
        print(f"[เตือน] บิตเรตวิดีโอต่ำมาก: {v_kbps:.2f} kbps")
    cmd = [ffmpeg_path,'-y','-i',input_file,'-c:v','libx264','-b:v',f'{int(v_kbps)}k',
           '-preset','medium','-vsync','0','-c:a','aac','-b:a',f'{int(audio_kbps)}k', output_file]
    print("FFmpeg:", shlex.join(cmd))
    subprocess.run(cmd, capture_output=True, text=True, check=True,
                   creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    return os.path.getsize(output_file)/(1024*1024)

class App:
    def show_progress_popup(self, ffmpeg_cmd, duration):
        import threading, re, subprocess
        from tkinter import ttk
        cancelled = False
        ffmpeg_proc = None
        popup = tk.Toplevel(self.m)
        popup.title("กำลังบีบอัด…")
        popup.geometry("350x120")
        popup.resizable(False, False)
        header_frame = tk.Frame(popup)
        header_frame.pack(fill='x', pady=(8,0), padx=8)
        tk.Label(header_frame, text="กำลังบีบอัด…", font=("Arial", 12)).pack(side='left')
        def on_cancel():
            nonlocal cancelled, ffmpeg_proc
            cancelled = True
            if ffmpeg_proc:
                ffmpeg_proc.terminate()
            popup.destroy()
        cancel_btn = tk.Button(header_frame, text="ยกเลิก", command=on_cancel)
        cancel_btn.pack(side='right')
        pb = ttk.Progressbar(popup, orient="horizontal", length=300, mode="indeterminate")
        pb.pack(pady=10, padx=10)
        percent_label = tk.Label(popup, text="")
        percent_label.pack()
        pb.start(10)
        def run_ffmpeg():
            nonlocal ffmpeg_proc, cancelled
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=creationflags)
            time_re = re.compile(r'time=([0-9:.]+)')
            last_percent = 0
            while True:
                if ffmpeg_proc.stdout is not None:
                    line = ffmpeg_proc.stdout.readline()
                else:
                    break
                if not line:
                    break
                match = time_re.search(line)
                if match and duration > 0:
                    t = match.group(1)
                    h, m, s = 0, 0, 0
                    parts = t.split(':')
                    if len(parts) == 3:
                        h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
                    elif len(parts) == 2:
                        m, s = int(parts[0]), float(parts[1])
                    else:
                        s = float(parts[0])
                    sec = h*3600 + m*60 + s
                    percent = int((sec/duration)*100)
                    pb.config(mode="determinate", maximum=100)
                    pb.stop()
                    pb['value'] = percent
                    percent_label.config(text=f"{percent}%")
                    last_percent = percent
                popup.update()
                if cancelled:
                    break
            ffmpeg_proc.wait()
            popup.destroy()
        threading.Thread(target=run_ffmpeg, daemon=True).start()
        popup.grab_set()
        self.m.wait_window(popup)
        self.cancelled = cancelled
    def __init__(self, m):
        self.m=m
        m.title("โปรแกรมบีบอัดวิดีโอ (~9MB)")
        m.geometry("500x350")
        self.ffmpeg_path, self.ffprobe_path = get_ffmpeg_path()
        if not self.ffmpeg_path or not self.ffprobe_path:
            messagebox.showerror("Error","ไม่พบ FFmpeg/ffprobe")
            m.destroy(); return
        self.in_var=tk.StringVar(); self.out_var=tk.StringVar()
        tk.Label(m,text="ไฟล์วิดีโอต้นฉบับ:").pack(pady=5)
        tk.Entry(m,textvariable=self.in_var,width=50,state='readonly').pack(pady=5)
        tk.Button(m,text="เลือกไฟล์",command=self.pick_in).pack(pady=5)
        tk.Label(m,text="ไฟล์วิดีโอผลลัพธ์:").pack(pady=5)
        tk.Entry(m,textvariable=self.out_var,width=50,state='readonly').pack(pady=5)
        tk.Button(m,text="เลือกที่จัดเก็บ",command=self.pick_out).pack(pady=5)
        tk.Button(m,text="เริ่มบีบอัดให้ได้ ~9MB",bg="lightblue",command=self.run).pack(pady=20,ipady=10)
        self.status=tk.StringVar(value="สถานะ: พร้อมทำงาน")
        tk.Label(m,textvariable=self.status).pack(pady=10)

    def pick_in(self):
        f=filedialog.askopenfilename(title="เลือกไฟล์วิดีโอ",
            filetypes=(("Video","*.mp4;*.mkv;*.avi;*.mov;*.webm"),("All","*.*")))
        if f:
            self.in_var.set(f)
            d,fn=os.path.split(f); name,_=os.path.splitext(fn)
            self.out_var.set(os.path.join(d,f"{name}_compressed_9mb.mp4"))

    def pick_out(self):
        d,fn=os.path.split(self.out_var.get()) if self.out_var.get() else (None,None)
        f=filedialog.asksaveasfilename(title="ตำแหน่งผลลัพธ์",initialdir=d,initialfile=fn,
            defaultextension=".mp4",filetypes=(("MP4","*.mp4"),("All","*.*")))
        if f: self.out_var.set(f)

    def run(self):
        i, o = self.in_var.get(), self.out_var.get()
        if not i or not o:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณาเลือกไฟล์ต้นฉบับและผลลัพธ์"); return
        self.status.set("สถานะ: กำลังบีบอัด...")
        try:
            dur = get_video_duration(self.ffprobe_path, i)
            target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / dur
            v_kbps = target_total_kbps - AUDIO_BITRATE_KBPS
            if v_kbps <= 0:
                raise RuntimeError("วิดีโอยาวเกินไปสำหรับงบขนาดไฟล์/เสียงปัจจุบัน")
            if v_kbps < MIN_VIDEO_BITRATE_KBPS:
                print(f"[เตือน] บิตเรตวิดีโอต่ำมาก: {v_kbps:.2f} kbps")
            ffmpeg_cmd = [self.ffmpeg_path, '-y', '-i', i, '-c:v', 'libx264', '-b:v', f'{int(v_kbps)}k',
                         '-preset', 'medium', '-vsync', '0', '-c:a', 'aac', '-b:a', f'{int(AUDIO_BITRATE_KBPS)}k', o]
            self.show_progress_popup(ffmpeg_cmd, dur)
            if not self.cancelled:
                mb = os.path.getsize(o) / (1024 * 1024)
                self.status.set(f"เสร็จสิ้น: {mb:.2f} MB"); messagebox.showinfo("OK", f"{o}\n{mb:.2f} MB")
            else:
                self.status.set("ยกเลิกการบีบอัด")
        except subprocess.CalledProcessError as e:
            self.status.set("FFmpeg ผิดพลาด"); messagebox.showerror("FFmpeg", e.stderr[:500] + " ...")
        except Exception as e:
            self.status.set("ผิดพลาด"); messagebox.showerror("Error", str(e))

def cli_entry(p):
    # ฟังก์ชันสำหรับโหมด CLI (Command Line Interface)
    # รับ path ของไฟล์วิดีโอต้นฉบับจาก argument
    ff,fp=get_ffmpeg_path()  # หา path ffmpeg และ ffprobe
    if not ff or not fp:
        print("ไม่พบ FFmpeg/ffprobe")  # แจ้งเตือนถ้าไม่พบ ffmpeg/ffprobe
        sys.exit(1)
    d,fn=os.path.split(p)
    name,_=os.path.splitext(fn)
    out=os.path.join(d,f"{name}_compressed_9mb.mp4")  # สร้างชื่อไฟล์ผลลัพธ์
    try:
        import threading, re, subprocess
        import tkinter as tk
        from tkinter import ttk, messagebox
        dur = get_video_duration(fp, p)
        target_total_kbps = (TARGET_FILESIZE_MB * 8 * 1024) / dur
        v_kbps = target_total_kbps - AUDIO_BITRATE_KBPS
        ffmpeg_cmd = [ff, '-y', '-i', p, '-c:v', 'libx264', '-b:v', f'{int(v_kbps)}k',
                     '-preset', 'medium', '-vsync', '0', '-c:a', 'aac', '-b:a', f'{int(AUDIO_BITRATE_KBPS)}k', out]
        cancelled = False
        ffmpeg_proc = None
        root = tk.Tk()
        root.title("กำลังบีบอัด…")
        root.geometry("350x120")
        root.resizable(False, False)
        header_frame = tk.Frame(root)
        header_frame.pack(fill='x', pady=(8,0), padx=8)
        tk.Label(header_frame, text="กำลังบีบอัด…", font=("Arial", 12)).pack(side='left')
        def on_cancel():
            nonlocal cancelled, ffmpeg_proc
            cancelled = True
            if ffmpeg_proc:
                ffmpeg_proc.terminate()
            root.destroy()
        cancel_btn = tk.Button(header_frame, text="ยกเลิก", command=on_cancel)
        cancel_btn.pack(side='right')
        pb = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
        pb.pack(pady=10, padx=10)
        percent_label = tk.Label(root, text="")
        percent_label.pack()
        pb.start(10)
        def run_ffmpeg():
            nonlocal ffmpeg_proc, cancelled
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=creationflags)
            time_re = re.compile(r'time=([0-9:.]+)')
            last_percent = 0
            while True:
                if ffmpeg_proc.stdout is not None:
                    line = ffmpeg_proc.stdout.readline()
                else:
                    break
                if not line:
                    break
                match = time_re.search(line)
                if match and dur > 0:
                    t = match.group(1)
                    h, m, s = 0, 0, 0
                    parts = t.split(':')
                    if len(parts) == 3:
                        h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
                    elif len(parts) == 2:
                        m, s = int(parts[0]), float(parts[1])
                    else:
                        s = float(parts[0])
                    sec = h*3600 + m*60 + s
                    percent = int((sec/dur)*100)
                    pb.config(mode="determinate", maximum=100)
                    pb.stop()
                    pb['value'] = percent
                    percent_label.config(text=f"{percent}%")
                    last_percent = percent
                root.update()
                if cancelled:
                    break
            ffmpeg_proc.wait()
            root.destroy()
        threading.Thread(target=run_ffmpeg, daemon=True).start()
        root.grab_set()
        root.mainloop()
        if not cancelled:
            mb = os.path.getsize(out) / (1024 * 1024)
            print(f"OK: {out} ({mb:.2f} MB)")
            root2 = tk.Tk()
            root2.withdraw()
            messagebox.showinfo("บีบอัดสำเร็จ", f"{out}\n{mb:.2f} MB")
            root2.destroy()
            sys.exit(0)
        else:
            print("ยกเลิกการบีบอัด")
            sys.exit(1)
    except Exception as e:
        print("ERR:",e)
        sys.exit(2)

if __name__=="__main__":
    if len(sys.argv)>=2:
        cli_entry(sys.argv[1])
    else:
        root=tk.Tk(); App(root); root.mainloop()
