
"""
Created on Fri Apr 25 18:37:55 2025

@author: naman
"""

import cv2
import face_recognition
import pickle
import numpy as np


with open("Audrey_face_data.pkl", "rb") as f:
    known = pickle.load(f)


video = cv2.VideoCapture(0)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


while True:
    ret, fr = video.read()
    rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    l = face_recognition.face_locations(rgb)
    enc = face_recognition.face_encodings(rgb, l)

    for f in enc:
        dist = face_recognition.face_distance(known, f)
        best_match_index = np.argmin(dist)
        best = dist[best_match_index]

        percent = (1 - best) * 100
        print(f"Distance: {best:.4f} | Confidence: {percent:.2f}%")

        t, r, b, le = l[0]
        col = (0, 255, 0) if percent > 70 else (0, 0, 255)
        cv2.rectangle(fr, (le, t), (r, b), col, 2)
        cv2.putText(fr, f"{percent:.2f}%", (le, t - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)

    cv2.imshow("hi", fr)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
