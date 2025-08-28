import cv2
import face_recognition
import os
import numpy as np
import tkinter as tk
from tkinter import messagebox, scrolledtext
import pickle
import time
import threading
from cryptography.fernet import Fernet
from tkinter import filedialog
package = "Audrey_face_data.pkl"
 
def load():
    try:
        with open(package, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("run register first!!!")
        return []


class Screen:
    def __init__(self, r, h):
        self.root = r
        self.callback = h
        self.frame = None

    def show(self):
        self.frame = tk.Toplevel(self.root)
        self.frame.geometry("800x500")
        self.frame.configure(bg="black")

        tk.Label(self.frame, text="🔒 System is Locked", font=("Arial", 24), fg="white", bg="black").pack(pady=100)
        tk.Label(self.frame, text="Scanning to unlock...", font=("Arial", 16), fg="white", bg="black").pack(pady=20)

        threading.Thread(target=self.unlock, daemon=True).start()

    def hide(self):
        self.frame.destroy()
        self.frame = None

    def unlock(self):
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        for i in encodings:
            dist = face_recognition.face_distance(load(), i)
            best = np.argmin(dist)
            conf = 1 - dist[best]
            print(f"conf: {conf:.2f}")

            if conf >= 0.70:
                camera.release()
                self.callback()
                return
            time.sleep(1)

        camera.release()


class LockApp:
    def __init__(self, r):
        self.root = r
        self.root.geometry("800x500")
        self.root.configure(bg="black")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.active = True
        self.interval = 5
        self.password = "letmein"
        self.known = load()
        self.dot_num = 0
        self.locks = None
        self.i_thread = threading.Thread(target=self.check, daemon=True)
        self.m_time = 60
        self.l_active = time.time()
        self.unl = False 

        self.rocket = tk.Label(r, text="🚀", font=("Arial", 60), bg="black", fg="white")
        self.rocket.pack(pady=20)

        self.s = tk.Label(r, text="Scanning for face", font=("Arial", 16), fg="white", bg="black")
        self.s.pack(pady=10)

        self.gate = tk.Label(r, text="🔒", font=("Arial", 12), fg="blue", bg="black", cursor="hand2")
        self.gate.place(relx=0.98, rely=0.98, anchor="se")
        self.gate.bind("<Button-1>", self.p_screen)

        self.root.bind('<Motion>', self.r_timer)
        self.root.bind('<KeyPress>', self.r_timer)

        threading.Thread(target=self.face_c, daemon=True).start()
        self.i_thread.start()
        self.dot_ani()

    def r_timer(self, event=None):
        self.l_active = time.time()

    def check(self):
        while not self.unl: 
            time.sleep(1)
            if time.time() - self.l_active > self.m_time:
                if self.locks is None:
                    self.locks = Screen(self.root, self.unlock)
                    self.locks.show()

    def dot_ani(self):
        dots = '.' * (self.dot_num % 4)
        self.s.config(text=f"Scanning for face{dots}")
        self.dot_num += 1
        self.root.after(500, self.dot_ani)

    def p_screen(self, event=None):
        pw_win = tk.Toplevel(self.root)
        pw_win.geometry("300x150")
        pw_win.configure(bg="black")

        tk.Label(pw_win, text="Enter Password:", fg="white", bg="black").pack(pady=10)
        pw_entry = tk.Entry(pw_win, show="*", width=25)
        pw_entry.pack()

        def check_pw():
            if pw_entry.get() == self.password:
                pw_win.destroy()
                self.unlock()
            else:
                messagebox.showerror("Error", "Incorrect password.")

        tk.Button(pw_win, text="Unlock", command=check_pw).pack(pady=10)

    def face_c(self):
        camera = cv2.VideoCapture(0)

        while self.active:
            ret, frame = camera.read()
            if not ret:
                time.sleep(self.interval)
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, faces)

            for i in encodings:
                if not self.known:
                    continue
                dist = face_recognition.face_distance(self.known, i)
                if len(dist) > 0:
                    best = np.argmin(dist)
                    conf = 1 - dist[best]
                    print(f"{conf:.2f}")
                    if conf >= 0.70:
                        camera.release()
                        self.unlock()
                        return
            time.sleep(self.interval)

        camera.release()

    def unlock(self):
        self.active = False
        self.unl = True 
        if self.locks:
            self.locks.hide()
            self.locks = None
        self.open_main()

    def open_main(self):
        if hasattr(self, 'is_open') and self.is_open:
            return

        self.is_open = True

        hub = tk.Tk()
        hub.geometry("800x500")
        hub.configure(bg="#1e1e1e")

        tk.Label(hub, text="Welcome!", font=("Arial", 24), fg="white", bg="#1e1e1e").pack(pady=20)

        tk.Button(hub, text="   Notes   ", font=("Arial", 16), command=open_notes, width=20).pack(pady=10)
        tk.Button(hub, text="   Files   ", font=("Arial", 16), state="disabled", width=30).pack(pady=10)
        tk.Button(hub, text="  Settings ", font=("Arial", 16), command=open_setting, width=30).pack(pady=10)

        def close_h():
            hub.destroy()
            self.root.destroy()

        tk.Button(hub, text="Exit", command=close_h, width=15).pack(pady=30)

        hub.mainloop()



key = b'oTU7pkUeh-JZCOnq5ZDih35gjM4vYGNSDhlgqCiK1TQ='
cipher = Fernet(key)

default = "stuff/notes.enc"
os.makedirs("stuff", exist_ok=True)

def open_setting():
    setting_win = tk.Toplevel()
    setting_win.title("Settings")
    setting_win.geometry("600x450")
    setting_win.configure(bg="black")
    s_frame = tk.Frame(setting_win, bg="#1e1e1e")
    tk.Label(s_frame, text="Settings")




def open_notes():
    notes_win = tk.Toplevel()
    notes_win.title("Notes")
    notes_win.geometry("600x450")
    notes_win.configure(bg="white")

    c_frame = tk.Frame(notes_win, bg="white")
    c_frame.pack(expand=True, fill='both')

    text = scrolledtext.ScrolledText(c_frame, wrap=tk.WORD, font=("Arial", 12))
    text.pack(expand=True, fill='both', padx=10, pady=10)

    c_path = None

    def load_n(path):
        try:
            with open(path, "rb") as f:
                encrypted = f.read()
                decrypted = cipher.decrypt(encrypted).decode("utf-8")
                text.delete("1.0", tk.END)
                text.insert(tk.END, decrypted)
                
                nonlocal c_path
                c_path = path
        except Exception:
            messagebox.showerror("Error", "Couldn't open file :(")

    load_n(default)

    def save_n(path):
        try:
            content = text.get("1.0", tk.END).strip().encode("utf-8")
            encrypted = cipher.encrypt(content)
            with open(path, "wb") as f:
                f.write(encrypted)
            messagebox.showinfo("Saved", f"Notes saved to:\n{path}")
        except Exception:
            messagebox.showerror("Error", "Notes weren't saved :(")

    buttons = tk.Frame(notes_win, bg="white")
    buttons.pack(fill='x', side='bottom', pady=5)

    tk.Button(buttons, text="Open", font=("Arial", 12), command=lambda: file_opener()).pack(side='left', padx=10)

    tk.Button(buttons, text="Save", font=("Arial", 12), bg="#4CAF50", fg="white", command=lambda: save_n(c_path if c_path else default)).pack(side='left', padx=10)

    tk.Button(buttons, text="Save As", font=("Arial", 12), bg="#2196F3", fg="white", command=lambda: saving()).pack(side='right', padx=10)

    def file_opener():
        path = filedialog.askopenfilename(title="Open Encrypted Notes", filetypes=[("Encrypted Notes", "*.enc *.txt"), ("All Files", "*.*")])
        if path:
            load_n(path)
        else: messagebox.showerror("Error", "Cannot open file")
            
    def saving():
        path = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted Notes", "*.enc"), ("All Files", "*.*")])
        save_n(path)
        nonlocal c_path  
        c_path = path 



hola = tk.Tk()
app = LockApp(hola)
hola.mainloop()
