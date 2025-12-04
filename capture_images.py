import cv2
import os

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "known_faces")


def capture_images(person_name: str, num_images: int = 10) -> None:
    """
    Capture num_images images from webcam and save them into
    known_faces/<person_name>/ as JPG files.
    """

    # Folder for this person's images
    person_dir = os.path.join(KNOWN_FACES_DIR, person_name)
    os.makedirs(person_dir, exist_ok=True)

    # Open webcam (CAP_DSHOW helps on Windows)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    print(f"[INFO] Starting capture for '{person_name}'")
    print("[INFO] Press 'q' in the camera window to stop early.")

    count = 1
    while count <= num_images:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        # Show live preview
        cv2.imshow("Capturing - press Q to stop", frame)

        # Save image
        img_path = os.path.join(person_dir, f"{person_name}_{count:02d}.jpg")
        cv2.imwrite(img_path, frame)
        print(f"[SAVED] {img_path}")
        count += 1

        # Let OpenCV process window events + check for 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Stopped early by user.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Capture finished.")


if __name__ == "__main__":
    # This part only runs when you execute capture_images.py directly
    name = input("Enter person name: ").strip()
    if not name:
        print("[ERROR] Person name cannot be empty.")
        raise SystemExit(1)

    num_str = input("How many images to capture (default 10)? ").strip()
    num_images = int(num_str) if num_str else 10

    capture_images(name, num_images)
