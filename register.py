import face_recognition
import os
import pickle

folder = "faces"
images = []

for f in os.listdir(folder):
    if f.lower().endswith((".jpg", ".png", ".jpeg")):
        path = os.path.join(folder, f)
        image = face_recognition.load_image_file(path)
        nex = face_recognition.face_encodings(image)
        if nex:
            images.append(nex[0])

if images:
    with open("Audrey_face_data.pkl", "wb") as f:
        pickle.dump(images, f)
    print("Done.")
else:
    print("Didn't work :(")
