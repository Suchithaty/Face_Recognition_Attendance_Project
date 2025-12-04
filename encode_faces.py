import os
import pickle
import face_recognition

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "known_faces")
ENCODINGS_PATH = os.path.join(BASE_DIR, "encodings.pkl")


def main():
    print("=== FACE ENCODING STARTED ===")

    if not os.path.exists(KNOWN_FACES_DIR):
        print(f"[ERROR] Folder not found: {KNOWN_FACES_DIR}")
        return

    all_encodings = []
    all_names = []

    people = [
        d for d in os.listdir(KNOWN_FACES_DIR)
        if os.path.isdir(os.path.join(KNOWN_FACES_DIR, d))
    ]

    if not people:
        print("[WARNING] No person folders found in 'known_faces'.")
        return

    for person_name in people:
        person_folder = os.path.join(KNOWN_FACES_DIR, person_name)
        print(f"\n[INFO] Processing person: {person_name}")

        image_files = [
            f for f in os.listdir(person_folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        if not image_files:
            print(f"[WARNING] No image files found in {person_folder}")
            continue

        for filename in image_files:
            image_path = os.path.join(person_folder, filename)
            print(f"  -> Encoding file: {filename}")

            try:
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image)

                if len(face_locations) == 0:
                    print(f"     [SKIP] No face found in: {filename}")
                    continue

                face_encodings = face_recognition.face_encodings(
                    image, known_face_locations=face_locations
                )

                if len(face_encodings) == 0:
                    print(f"     [SKIP] Could not extract encodings for: {filename}")
                    continue

                all_encodings.append(face_encodings[0])
                all_names.append(person_name)
                print("     [OK] Face encoded.")

            except Exception as e:
                print(f"     [ERROR] Failed on file {filename}: {e}")

    if not all_encodings:
        print("\n[WARNING] No encodings were generated. Check your images.")
        return

    data = {"encodings": all_encodings, "names": all_names}

    try:
        with open(ENCODINGS_PATH, "wb") as f:
            pickle.dump(data, f)
        print(f"\n[SUCCESS] Saved {len(all_encodings)} encodings to: {ENCODINGS_PATH}")
    except Exception as e:
        print(f"[ERROR] Could not save encodings file: {e}")

    print("=== FACE ENCODING FINISHED ===")


if __name__ == "__main__":
    main()
