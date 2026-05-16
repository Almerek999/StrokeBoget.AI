import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model
import os
import math

model_path = '../models/stroke_ai_model.h5'
model = load_model(model_path)

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            
            # --- ГЕОМЕТРИЧЕСКИЕ ПРИЗНАКИ ---
            nx = face_landmarks.landmark[1].x
            ny = face_landmarks.landmark[1].y
            nz = face_landmarks.landmark[1].z
            
            lx = face_landmarks.landmark[234].x
            ly = face_landmarks.landmark[234].y
            rx = face_landmarks.landmark[454].x
            ry = face_landmarks.landmark[454].y
            face_width = math.sqrt((rx - lx)**2 + (ry - ly)**2)
            if face_width == 0: face_width = 1
            
            row = []
            for lm in face_landmarks.landmark:
                dist = math.sqrt((lm.x - nx)**2 + (lm.y - ny)**2 + (lm.z - nz)**2)
                row.append(dist / face_width)
            # --------------------------------

            input_data = np.array([row])
            prediction = model.predict(input_data, verbose=0)[0][0]
            
            if prediction > 0.5:
                label = "WARNING: ASYMMETRY"
                color = (0, 0, 255)
            else:
                label = "Status: Healthy"
                color = (0, 255, 0)
                
            cv2.putText(frame, label, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"Conf: {prediction*100:.1f}%", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow('Stroke Diagnosis System', frame)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()