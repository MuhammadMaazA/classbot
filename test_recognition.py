import os
import cv2
import numpy as np
import insightface

KNOWN_DIR = os.path.expanduser("~/classroom_ai/known_faces")
TEST_IMAGE = os.path.expanduser("~/classroom_ai/test_images/asad2.jpeg")

THRESHOLD = 0.45  # tune: 0.40 looser, 0.50 stricter

def norm(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v) + 1e-12)

# Load InsightFace model
app = insightface.app.FaceAnalysis()
app.prepare(ctx_id=0)

def load_known_faces():
    """
    Expects:
      known_faces/<person_name>/*.jpg
    Returns:
      db: dict[name] = list[(embedding_normed, image_path)]
    """
    db = {}

    people = [d for d in sorted(os.listdir(KNOWN_DIR)) if os.path.isdir(os.path.join(KNOWN_DIR, d))]
    if not people:
        raise RuntimeError(f"No person folders found in {KNOWN_DIR}")

    print("Loading known faces...")

    for person in people:
        person_dir = os.path.join(KNOWN_DIR, person)
        images = [f for f in sorted(os.listdir(person_dir)) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

        if not images:
            print(f"[SKIP] {person}: no images found")
            continue

        for img_name in images:
            img_path = os.path.join(person_dir, img_name)
            img = cv2.imread(img_path)

            if img is None:
                print(f"[SKIP] {person}: can't read {img_path}")
                continue

            faces = app.get(img)
            if len(faces) == 0:
                print(f"[SKIP] {person}: no face in {img_name}")
                continue

            if len(faces) > 1:
                print(f"[WARN] {person}: multiple faces in {img_name} (using first)")

            emb = norm(faces[0].embedding)
            db.setdefault(person, []).append((emb, img_path))

        print(f"Loaded: {person} ({len(db.get(person, []))} images)")

    if not db:
        raise RuntimeError("No usable face embeddings loaded. Check your images.")
    return db

def main():
    known_db = load_known_faces()

    print("\nTesting image...")
    img = cv2.imread(TEST_IMAGE)
    if img is None:
        raise FileNotFoundError(f"Could not read test image at: {TEST_IMAGE}")

    faces = app.get(img)
    if len(faces) == 0:
        print("No face found in test image.")
        return

    test_emb = norm(faces[0].embedding)

    # Best per person and overall
    per_person = []
    best_label, best_sim, best_src = "unknown", -1.0, None

    for person, emb_list in known_db.items():
        person_best_sim = -1.0
        person_best_src = None

        for known_emb, src in emb_list:
            sim = float(np.dot(test_emb, known_emb))  # cosine similarity (both normalized)
            if sim > person_best_sim:
                person_best_sim = sim
                person_best_src = src

        per_person.append((person, person_best_sim, person_best_src))

        if person_best_sim > best_sim:
            best_label, best_sim, best_src = person, person_best_sim, person_best_src

    # Print scores sorted
    per_person.sort(key=lambda x: x[1], reverse=True)
    for person, sim, src in per_person:
        print(f"Similarity with {person:10s}: {sim:.3f}   (best ref: {os.path.basename(src) if src else 'n/a'})")

    print("\nResult:")
    if best_sim >= THRESHOLD:
        print(f"Recognized as: {best_label}")
    else:
        print("Unknown person")

    print(f"Similarity score: {best_sim:.3f}")
    if best_src:
        print(f"Best matched reference: {best_src}")

if __name__ == "__main__":
    main()