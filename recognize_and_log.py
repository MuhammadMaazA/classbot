import os
import cv2
import numpy as np
import insightface
import time
import csv

BASE_DIR = os.path.expanduser("~/classroom_ai")
FACES_DIR = os.path.join(BASE_DIR, "knownfaces")
LOG_FILE = os.path.join(BASE_DIR, "logs", "attendance.csv")

os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

# Initialize InsightFace
app = insightface.app.FaceAnalysis()
app.prepare(ctx_id=0)

# Load known faces
known_embeddings = []
known_names = []

print("Loading faces...")

for file in os.listdir(FACES_DIR):
    if file.endswith(".jpg") or file.endswith(".png"):
        path = os.path.join(FACES_DIR, file)
        img = cv2.imread(path)
        faces = app.get(img)

        if len(faces) > 0:
            embedding = faces[0].embedding
            name = os.path.splitext(file)[0]

            known_embeddings.append(embedding)
            known_names.append(name)

            print(f"Loaded {name}")

# Create log file if not exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("time,name,similarity\n")

def log(name, similarity):
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{t},{name},{similarity:.3f}\n")

# Open camera
cap = cv2.VideoCapture(0)

print("Starting recognition...")

while True:

    ret, frame = cap.read()

    faces = app.get(frame)

    for face in faces:

        emb = face.embedding

        best_similarity = -1
        best_name = "unknown"

        for i, known_emb in enumerate(known_embeddings):

            similarity = np.dot(emb, known_emb) / (
                np.linalg.norm(emb) * np.linalg.norm(known_emb)
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_name = known_names[i]

        if best_similarity > 0.5:
            log(best_name, best_similarity)
            label = f"{best_name} {best_similarity:.2f}"
        else:
            label = "unknown"

        box = face.bbox.astype(int)

        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0,255,0), 2)
        cv2.putText(frame, label, (box[0], box[1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    cv2.imshow("Attendance", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()