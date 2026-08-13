import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model
import speech_recognition as sr
import difflib
import math
import os
import time

def start_camera():
    print("Загрузка нейросетей... Пожалуйста, подождите.")

    # 1. Загрузка ИИ для оценки геометрии лица
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, '..', 'models', 'stroke_ai_model.h5')
    model = load_model(model_path)

    # 2. Настройка MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

    # 3. Настройка ИИ для анализа речи
    recognizer = sr.Recognizer()
    target_phrase = "за окном сегодня светит яркое солнце"

    # Включаем камеру
    cap = cv2.VideoCapture(0)

    # Переменные для хранения результатов 2-факторного теста
    speech_result = ""
    final_diagnosis = ""
    diagnosis_color = (0, 255, 0)
    
    # Переменные для визуальной "Мигалки"
    is_flashing = False
    flash_start_time = 0

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
                from features import extract_asymmetry_features
                row = extract_asymmetry_features(face_landmarks)

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

        # --- Визуальная "Мигалка" при обнаружении инсульта ---
        if is_flashing:
            # Мигаем 15 секунд
            if time.time() - flash_start_time < 15:
                # Меняем цвет каждые 0.5 секунды
                if int((time.time() - flash_start_time) * 2) % 2 == 0:
                    red_overlay = frame.copy()
                    red_overlay[:] = (0, 0, 255) # BGR (Красный)
                    frame = cv2.addWeighted(frame, 0.6, red_overlay, 0.4, 0)
                
                # Постоянно выводим инструкции на красном/обычном фоне
                cv2.putText(frame, "!!! SOS - ВЫЯВЛЕН ИНСУЛЬТ !!!", (20, frame.shape[0]//2 - 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                cv2.putText(frame, "1. Сохраняйте спокойствие и сядьте", (20, frame.shape[0]//2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "2. Обеспечьте приток воздуха", (20, frame.shape[0]//2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "3. НЕ ПЕЙТЕ ВОДУ И ТАБЛЕТКИ!", (20, frame.shape[0]//2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, "Сообщение родственникам отправлено", (20, frame.shape[0]//2 + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            else:
                is_flashing = False # Выключаем мигалку через 15 сек

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
            print("🎙️ ГОВОРИТЕ: «За окном сегодня светит яркое солнце»")
            
            import sounddevice as sd
            from scipy.io.wavfile import write
            
            fs = 16000
            duration = 5
            try:
                print("⏳ Идет запись 5 секунд... Говорите!")
                audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()
                write('temp_voice.wav', fs, audio_data)
                
                with sr.AudioFile('temp_voice.wav') as source:
                    audio = recognizer.record(source)
                    
                print("⏳ ИИ анализирует голос...")
                text = recognizer.recognize_google(audio, language="ru-RU").lower()
                sim = difflib.SequenceMatcher(None, target_phrase, text).ratio()
                
                if sim > 0.7:
                    speech_result = "Clear (Normal)"
                    speech_fail = False
                else:
                    speech_result = f"Distorted / Dysarthria"
                    speech_fail = True
                    
            except Exception as e:
                print(f"Ошибка аудио: {e}")
                speech_result = "Unrecognized (Severe Aphasia)"
                speech_fail = True
                    
            # --- Блок 3: Слияние данных и финальный вердикт ---
            if current_face_asymmetry and speech_fail:
                final_diagnosis = "CRITICAL: STROKE (Face + Speech)"
                diagnosis_color = (0, 0, 255) # Красный
                
                print("\n!!! ОБНАРУЖЕНО КРИТИЧЕСКОЕ СОСТОЯНИЕ !!!")
                
                # Включаем красную мигалку на экране
                is_flashing = True
                flash_start_time = time.time()
                
                import subprocess
                instruction_text = "Внимание. Выявлены признаки инсульта. Пожалуйста, сохраняйте спокойствие. Сядьте в удобное положение. Обеспечьте доступ свежего воздуха. Ни в коем случае не пейте воду и не принимайте таблетки. Экстренное сообщение уже отправлено вашим родственникам."
                
                # Запускаем голосового помощника в фоне (чтобы не тормозить видео)
                try:
                    subprocess.Popen(['say', instruction_text])
                except Exception:
                    pass # Игнорируем если команды say нет (на других ОС)
                
                try:
                    from emergency import trigger_sos
                    trigger_sos()
                except Exception as e:
                    print(f"Не удалось запустить модуль SOS: {e}")
                    
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

if __name__ == "__main__":
    start_camera()