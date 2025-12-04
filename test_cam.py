import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not detected on index 0")
else:
    print("🎥 Camera OK on index 0")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Test Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
