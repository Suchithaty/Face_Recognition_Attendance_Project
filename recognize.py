import face_recognition
import cv2
import os
import pickle
import csv
from datetime import datetime

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENCODINGS_FILE = os.path.join(BASE_DIR, "encodings.pkl")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendence.csv")


# -----------------------------
# Attendance writer
# -----------------------------
def mark_attendance(name):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")   # e.g. 2025-12-03
    time_str = now.strftime("%H:%M:%S")   # e.g. 13:57:32

    # Check if file exists and if it is empty (no header yet)
    file_exists = os.path.exists(ATTENDANCE_FILE)
    file_empty = True
    if file_exists and os.path.getsize(ATTENDANCE_FILE) > 0:
        file_empty = False

    try:
        with open(ATTENDANCE_FILE, "a", newline="") as f:
            writer = csv.writer(f)

            # Write header once if file is new/empty
            if file_empty:
                writer.writerow(["date", "time", "personName", "status"])

            # Write the actual attendance row
            writer.writerow([date_str, time_str, name, "Present"])

        print(f"[INFO] Attendance marked for {name}")
    except PermissionError:
        print("[ERROR] Cannot write to attendence.csv.")
        print("Please CLOSE the file in Excel and try again.")


# -----------------------------
# Load encodings
# -----------------------------
if not os.path.exists(ENCODINGS_FILE):
    print("[ERROR] encodings.pkl not found. Run Encode Faces first.")
    raise SystemExit(1)

print("[INFO] Loading encodings...")
with open(ENCODINGS_FILE, "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]
print("[INFO] Encodings loaded.")


# -----------------------------
# Start webcam
# -----------------------------
video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not video.isOpened():
    print("[ERROR] Cannot open webcam.")
    raise SystemExit(1)

print("[INFO] Starting attendance...")


# -----------------------------
# Recognition Loop
# -----------------------------
marked_today = set()  # avoid marking same person multiple times in one run

while True:
    ret, frame = video.read()
    if not ret:
        print("[ERROR] Failed to grab frame.")
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)

    names_in_frame = []

    for encoding in encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding)
        name = "Unknown"

        if True in matches:
            matched_idxs = [i for i, m in enumerate(matches) if m]
            counts = {}

            for i in matched_idxs:
                name_i = known_names[i]
                counts[name_i] = counts.get(name_i, 0) + 1

            name = max(counts, key=counts.get)

            if name not in marked_today:
                mark_attendance(name)
                marked_today.add(name)

        names_in_frame.append(name)

    # Draw boxes & names
    for ((top, right, bottom, left), name) in zip(boxes, names_in_frame):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Attendance - Press Q to Quit", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
print("[INFO] Attendance session ended.")
