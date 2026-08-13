import os
import cv2
import base64
import numpy as np
import difflib
import subprocess
from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
import mediapipe as mp
import speech_recognition as sr
from features import extract_asymmetry_features
from emergency import trigger_sos
import tempfile

app = Flask(__name__)

# --- Загрузка ИИ Моделей ---
print("Загрузка ИИ для оценки геометрии лица...")
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, '..', 'models', 'stroke_ai_model.h5')
try:
    model = load_model(model_path)
except Exception as e:
    print(f"Ошибка загрузки модели ИИ: {e}")
    model = None

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)

recognizer = sr.Recognizer()
TARGET_PHRASE = "за окном сегодня светит яркое солнце"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze_face', methods=['POST'])
def analyze_face():
    try:
        data = request.json
        image_data = data['image'].split(',')[1]
        decoded_data = base64.b64decode(image_data)
        np_data = np.frombuffer(decoded_data, np.uint8)
        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                row = extract_asymmetry_features(face_landmarks)
                input_data = np.array([row])
                prediction = model.predict(input_data, verbose=0)[0][0]
                
                return jsonify({
                    "success": True,
                    "asymmetry": bool(prediction > 0.5),
                    "score": float(prediction)
                })
                
        return jsonify({"success": True, "asymmetry": False, "score": 0.0, "message": "No face detected"})
    except Exception as e:
        print(f"Error in analyze_face: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/analyze_voice', methods=['POST'])
def analyze_voice():
    try:
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({"success": False, "error": "No audio provided"})
        
        # Сохраняем WebM/MP4 файл с фронтенда
        temp_dir = tempfile.gettempdir()
        temp_video_path = os.path.join(temp_dir, 'temp_audio.webm')
        temp_wav_path = os.path.join(temp_dir, 'temp_audio.wav')
        
        audio_file.save(temp_video_path)
        
        # Получаем локальный ffmpeg
        import static_ffmpeg
        static_ffmpeg.add_paths()
        
        # Конвертируем в WAV (используем встроенный ffmpeg)
        subprocess.run(['ffmpeg', '-y', '-i', temp_video_path, '-ar', '16000', '-ac', '1', temp_wav_path], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Анализ речи
        with sr.AudioFile(temp_wav_path) as source:
            audio = recognizer.record(source)
        
        text = recognizer.recognize_google(audio, language="ru-RU").lower()
        sim = difflib.SequenceMatcher(None, TARGET_PHRASE, text).ratio()
        
        speech_fail = bool(sim <= 0.7)
        
        return jsonify({
            "success": True,
            "text": text,
            "fail": speech_fail,
            "similarity": float(sim)
        })
        
    except sr.UnknownValueError:
        return jsonify({"success": True, "fail": True, "text": "Не удалось распознать речь", "similarity": 0.0})
    except Exception as e:
        print(f"Error in analyze_voice: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/sos', methods=['POST'])
def sos():
    try:
        data = request.json
        patient_name = data.get('patient_name', 'Пациент')
        relative_name = data.get('relative_name', 'Родственник')
        relative_email = data.get('relative_email', '')
        
        # Получаем GPS-координаты от телефона (если есть)
        lat = data.get('lat')
        lon = data.get('lon')
        
        fallback_address = data.get('fallback_address', '')
        tg_chat_id = data.get('tg_chat_id', '')
        
        import threading
        # Запуск SOS логики (Telegram + Email) в фоновом потоке, чтобы не блокировать интерфейс
        threading.Thread(target=trigger_sos, args=(patient_name, relative_name, relative_email, lat, lon, fallback_address, tg_chat_id)).start()
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    import socket
    
    # Получаем локальный IP компьютера в сети Wi-Fi
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
        
    print("\n" + "="*50)
    print("🚀 СЕРВЕР ЗАПУЩЕН!")
    print(f"Для тестирования с ТЕЛЕФОНА (в одной сети Wi-Fi) откройте:")
    print(f"👉 https://{local_ip}:5050 👈")
    print("Важно: Браузер напишет 'Подключение не защищено'.")
    print("Нажмите 'Дополнительно' -> 'Перейти на сайт'.")
    print("="*50 + "\n")
    
    # Запускаем Flask с нативными ключами, чтобы работал HTTPS без внешних библиотек
    # Принудительно отключаем локальный HTTPS для совместимости с внешним туннелем (ngrok/localhost.run)
    app.run(host='0.0.0.0', port=5055, debug=False)
