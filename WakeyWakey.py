import cv2
import numpy as np
import time
import sys
import os
import tkinter as tk
from tkinter import messagebox
import threading
import winsound  # Native Windows sound, replaces pygame

# --- CONFIGURATION ---
CLOSED_DURATION_SEC = 3   # Seconds eyes must be closed before alarm
ALARM_INTERVAL_SEC  = 1.5     # Min gap between repeated alarms
CAMERA_INDEX        = 0      # Change to 1, 2 etc. if wrong camera

# Global state to control the background thread
is_running = False

# ─────────────────────────────────────────────
#  LOAD HAAR CASCADES 
# ─────────────────────────────────────────────
def load_cascades():
    cv2_data = cv2.data.haarcascades
    face_path = os.path.join(cv2_data, "haarcascade_frontalface_default.xml")
    eye_path  = os.path.join(cv2_data, "haarcascade_eye_tree_eyeglasses.xml")

    face_cascade = cv2.CascadeClassifier(face_path)
    eye_cascade  = cv2.CascadeClassifier(eye_path)

    if face_cascade.empty() or eye_cascade.empty():
        return None, None

    return face_cascade, eye_cascade

# ─────────────────────────────────────────────
#  AUDIO PATHING
# ─────────────────────────────────────────────
def get_audio_path(filename="faaah.wav"):
    """Finds the exact folder the .exe or .py file is running from."""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_dir, filename)

# ─────────────────────────────────────────────
#  HUD
# ─────────────────────────────────────────────
def draw_hud(frame, face_found, eyes_found, alarm_active, closed_duration):
    h, w = frame.shape[:2]

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 65), (10, 10, 10), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    if not face_found:
        sc, st = (120, 120, 255), "No face detected"
    elif alarm_active:
        sc, st = (0, 0, 255), f"DROWSY ALERT!  ({closed_duration:.1f}s eyes closed)"
    elif not eyes_found:
        sc, st = (0, 165, 255), f"Eyes closed / not visible  ({closed_duration:.1f}s)"
    else:
        sc, st = (0, 220, 80), f"Awake  -  Eyes open  :)"

    cv2.putText(frame, st, (14, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.75, sc, 2, cv2.LINE_AA)

    if alarm_active:
        flash = frame.copy()
        cv2.rectangle(flash, (0, 0), (w, h), (0, 0, 200), -1)
        cv2.addWeighted(flash, 0.18, frame, 0.82, 0, frame)

# ─────────────────────────────────────────────
#  BACKGROUND DETECTOR THREAD
# ─────────────────────────────────────────────
def detector_loop():
    global is_running
    
    face_cascade, eye_cascade = load_cascades()
    if not face_cascade:
        is_running = False
        print("[ERROR] Missing Cascades.")
        return

    # Get the verified path for the audio
    wav_path = get_audio_path("faaah.wav")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        is_running = False
        print(f"[ERROR] Cannot open camera {CAMERA_INDEX}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    eyes_gone_start = None
    last_alarm_time = 0.0
    alarm_active    = False

    while is_running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w  = frame.shape[:2]
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray  = cv2.equalizeHist(gray)

        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.15, minNeighbors=5, minSize=(120, 120), flags=cv2.CASCADE_SCALE_IMAGE
        )

        face_found = len(faces) > 0
        eyes_found = False

        for (fx, fy, fw, fh) in faces:
            cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), (80, 80, 255), 2)
            roi_gray  = gray[fy: fy + int(fh * 0.6), fx: fx + fw]
            roi_color = frame[fy: fy + int(fh * 0.6), fx: fx + fw]

            eyes = eye_cascade.detectMultiScale(
                roi_gray, scaleFactor=1.1, minNeighbors=4, minSize=(25, 25)
            )

            if len(eyes) >= 1:
                eyes_found = True
                for (ex, ey, ew, eh) in eyes:
                    cx, cy = ex + ew // 2, ey + eh // 2
                    cv2.circle(roi_color, (cx, cy), ew // 2, (0, 255, 120), 2)

        eyes_missing = face_found and not eyes_found
        now = time.time()

        if eyes_missing:
            if eyes_gone_start is None:
                eyes_gone_start = now
            closed_duration = now - eyes_gone_start

            if closed_duration >= CLOSED_DURATION_SEC:
                alarm_active = True
                if now - last_alarm_time >= ALARM_INTERVAL_SEC:
                    # NATIVE WINDOWS SOUND PLAYBACK
                    winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    last_alarm_time = now
            else:
                alarm_active = False
        else:
            eyes_gone_start = None
            alarm_active    = False
            closed_duration = 0.0

        draw_hud(frame, face_found, eyes_found, alarm_active, closed_duration if eyes_missing else 0.0)
        #cv2.imshow("Sleepiness Camera Feed", frame)
       # cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()

# ─────────────────────────────────────────────
#  GUI CONTROLS
# ─────────────────────────────────────────────
def start_app():
    global is_running
    
    #Verify audio file exists before starting
    wav_path = get_audio_path("faaah.wav")
    if not os.path.exists(wav_path):
        messagebox.showerror("Audio Missing", f"Could not find faaah.wav!\n\nThe app is looking exactly here:\n{wav_path}\n\nPlease paste your audio file in that folder.")
        return

    if not is_running:
        is_running = True
        status_label.config(text="Status: Active and Monitoring", fg="green")
        start_btn.config(state=tk.DISABLED)
        stop_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=detector_loop, daemon=True).start()

def stop_app():
    global is_running
    is_running = False
    status_label.config(text="Status: Inactive", fg="red")
    start_btn.config(state=tk.NORMAL)
    stop_btn.config(state=tk.DISABLED)

def on_closing():
    stop_app()
    root.destroy()

# ─────────────────────────────────────────────
#  MAIN WINDOW SETUP
# ─────────────────────────────────────────────
root = tk.Tk()
root.title("Study Monitor")
root.geometry("350x280") # Increased height slightly to fit the footer
root.protocol("WM_DELETE_WINDOW", on_closing)

# Title
title_label = tk.Label(root, text="Dozing Detector", font=("Helvetica", 18, "bold"))
title_label.pack(pady=20)

# Status
status_label = tk.Label(root, text="Status: Inactive", fg="red", font=("Helvetica", 12))
status_label.pack(pady=10)

# Buttons
start_btn = tk.Button(root, text="Start Tracking", width=20, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"), command=start_app)
start_btn.pack(pady=5)

stop_btn = tk.Button(root, text="Stop Tracking", width=20, bg="#f44336", fg="white", font=("Helvetica", 10, "bold"), command=stop_app, state=tk.DISABLED)
stop_btn.pack(pady=5)

# Signature footer
footer_label = tk.Label(root, text="made by praise🩷", font=("Helvetica", 8), fg="gray")
footer_label.pack(side="bottom", pady=10)

if __name__ == "__main__":
    root.mainloop()