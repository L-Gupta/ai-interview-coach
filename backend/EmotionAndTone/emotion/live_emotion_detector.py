import cv2
import numpy as np
import keras
from keras.models import load_model
from collections import deque
import time

# Load models
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
emotion_model = load_model('fer2013_mini_XCEPTION.102-0.66.hdf5', compile=False)

# Emotion labels
emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Track emotions over time (last 10 frames)
emotion_history = deque(maxlen=10)
feedback = ""
last_feedback_time = time.time()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        face_roi = gray[y:y+h, x:x+w]

        try:
            face_roi = cv2.resize(face_roi, (48, 48))
            face_roi = np.expand_dims(face_roi, axis=0)
            face_roi = np.expand_dims(face_roi, axis=-1)
            face_roi = face_roi.astype('float32') / 255.0

            emotion_prediction = emotion_model.predict(face_roi)
            emotion_index = np.argmax(emotion_prediction)
            emotion_text = emotion_labels[emotion_index]
            emotion_history.append(emotion_index)

            # Analyze emotions over time
            if len(emotion_history) == 10:
                avg_emotion = max(set(emotion_history), key=emotion_history.count)
                dominant_emotion = emotion_labels[avg_emotion]

                # Provide feedback every 5 seconds
                if time.time() - last_feedback_time > 5:
                    if dominant_emotion == 'Fear' or dominant_emotion == 'Sad':
                        feedback = "Try to relax and smile more!"
                    elif dominant_emotion == 'Angry':
                        feedback = "You seem tense. Take a deep breath."
                    elif dominant_emotion == 'Happy':
                        feedback = "Great! You appear confident."
                    elif dominant_emotion == 'Neutral':
                        feedback = "Try showing more enthusiasm."
                    else:
                        feedback = "Keep going!"
                    
                    last_feedback_time = time.time()

            cv2.putText(frame, f"Emotion: {emotion_text}", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Feedback: {feedback}", (20, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        except Exception as e:
            print(f"Error: {e}")

    cv2.imshow('AI Interview Coach', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()