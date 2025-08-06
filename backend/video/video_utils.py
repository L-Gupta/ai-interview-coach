import cv2

""""Estimates eye contact percentage by checking if eye region is roughly centered in the frame.""" 
def estimate_eye_contact(frames: list) -> int:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_contact_frames = 0

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            face_center_x = x + w // 2
            frame_center_x = frame.shape[1] // 2
            distance_from_center = abs(face_center_x - frame_center_x)

            # if face is near center (within 25% of width), consider as eye contact
            if distance_from_center < frame.shape[1] * 0.25:
                eye_contact_frames += 1
            break  # only consider first detected face

    if not frames:
        return 0

    return int((eye_contact_frames / len(frames)) * 100)

def count_distractions(frames: list) -> int:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    distraction_count = 0
    last_state = None  # "center" or "off"

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        state = "off"  # default state

        for (x, y, w, h) in faces:
            face_center_x = x + w // 2
            frame_center_x = frame.shape[1] // 2
            distance = abs(face_center_x - frame_center_x)

            if distance < frame.shape[1] * 0.25:
                state = "center"
            break

        if last_state == "center" and state == "off":
            distraction_count += 1

        last_state = state

    return distraction_count

""""Detects if more than one face is present in any frame using Haar cascades.""" 
def detect_multiple_faces(frames: list) -> bool:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 1:
            return True

    return False

""""Calculates how many frames had no detectable face, indicating absence or occlusion.""" 
def detect_face_absence(frames: list) -> int:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    no_face_frames = 0

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) == 0:
            no_face_frames += 1

    return no_face_frames

