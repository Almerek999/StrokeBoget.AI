import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model
import speech_recognition as sr
import difflib
import math
import os

print("Загрузка нейросетей... Пожалуйста, подождите.")

# 1. Загрузка ИИ для оценки геометрии лица
model_path = '../models/stroke_ai_model.h5'
model = load_model(model_path)

# 2. Настройка MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# 3. Настройка ИИ для анализа речи
recognizer = sr.Recognizer()
target_phrase = "You can't teach an old dog new tricks"

# Включаем камеру
cap = cv2.VideoCapture(0)

# Переменные для хранения результатов 2-факторного теста
speech_result = ""
final_diagnosis = ""
diagnosis_color = (0, 255, 0)

print("\n=== СИСТЕМА ГОТОВА ===")
print("Нажмите клавишу 'T' (английскую) в окне камеры, чтобы запустить тест FAST.")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    current_face_asymmetry = False

    # Блок 1: Постоянный мониторинг лица
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Математика расстояний
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

            input_data = np.array([row])
            prediction = model.predict(input_data, verbose=0)[0][0]
            
            if prediction > 0.5:
                current_face_asymmetry = True
                cv2.putText(frame, "Face Monitor: ASYMMETRY DETECTED", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "Face Monitor: NORMAL", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Отрисовка интерфейса
    cv2.putText(frame, "Press 'T' to start FAST Stroke Test", (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    if final_diagnosis != "":
        cv2.putText(frame, final_diagnosis, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, diagnosis_color, 2)
        cv2.putText(frame, f"Speech: {speech_result}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow('2-Factor Stroke Detection AI', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 27: # ESC для выхода
        break
    elif key == ord('t') or key == ord('T'):
        # --- Блок 2: ЗАПУСК 2-ФАКТОРНОГО ТЕСТА ---
        cv2.putText(frame, "LISTENING... SPEAK NOW!", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        cv2.imshow('2-Factor Stroke Detection AI', frame)
        cv2.waitKey(1) # Заморозка кадра на время записи звука
        
        print("\n" + "="*30)
        print("🎙️ Speak: «You can't teach an old dog new tricks»")
        
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("⏳ ИИ анализирует голос...")
                text = recognizer.recognize_google(audio, language="ru-RU").lower()
                sim = difflib.SequenceMatcher(None, target_phrase, text).ratio()
                
                if sim > 0.7:
                    speech_result = "Clear (Normal)"
                    speech_fail = False
                else:
                    speech_result = f"Distorted / Dysarthria"
                    speech_fail = True
                    
            except Exception:
                speech_result = "Unrecognized (Severe Aphasia)"
                speech_fail = True
                
        # --- Блок 3: Слияние данных и финальный вердикт ---
        if current_face_asymmetry and speech_fail:
            final_diagnosis = "CRITICAL: STROKE (Face + Speech)"
            diagnosis_color = (0, 0, 255) # Красный
        elif current_face_asymmetry or speech_fail:
            final_diagnosis = "WARNING: Partial signs detected"
            diagnosis_color = (0, 165, 255) # Оранжевый
        else:
            final_diagnosis = "STATUS: 100% HEALTHY"
            diagnosis_color = (0, 255, 0) # Зеленый
            
        print(f"✅ Тест завершен. Вердикт: {final_diagnosis}")
        print("="*30)

cap.release()
cv2.destroyAllWindows()
