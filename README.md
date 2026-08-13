# StrokeBoget.AI - Intelligent Early Stroke Detection System

*[🇷🇺 Читать на русском (Read in Russian)](README_RU.md)*

StrokeBoget.AI is an AI-powered web application (leveraging computer vision and audio analysis) designed to instantly identify early signs of a stroke using the FAST (Face, Arms, Speech, Time) protocol via a smartphone or computer camera.

Upon detecting alarming symptoms, the system automatically and instantly alerts relatives via Email and Telegram, providing them with the exact GPS coordinates, physical address of the patient, and a route to the nearest hospital.

## 🌟 Key Features
1. **Neural Face Analysis**: Detects facial asymmetry (one of the primary indicators of a stroke) in real-time using a custom-trained neural network and `mediapipe`.
2. **Speech Analysis**: Evaluates speech impairment by recording the patient's voice and comparing their dictation to a reference phrase using natural language processing.
3. **Automated SOS Protocol**: Instantly broadcasts emergency alerts with the patient's geolocation (via Reverse Geocoding).
4. **Nearest Hospital Routing**: Automatically locates the nearest medical facility via the OpenStreetMap API and generates a direct navigation route.

## 🛠 Technology Stack
- **Backend:** Python, Flask, OpenCV, MediaPipe
- **Machine Learning:** TensorFlow/Keras (Dense neural network trained on a facial symmetry dataset)
- **Audio & Recognition:** SpeechRecognition, Google Web Speech API, ffmpeg
- **Integrations:** Telegram Bot API, SMTP Email, Nominatim API (Geocoding), Overpass API (Hospital mapping)
- **Frontend:** HTML5, CSS3, JavaScript, WebRTC (getUserMedia API)

## 🚀 Setup and Installation (For Developers)

### 1. Clone the Repository
```bash
git clone https://github.com/Almerek999/StrokeBoget.AI.git
cd StrokeBoget.AI
```

### 2. Install Dependencies
It is highly recommended to use a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # For Mac/Linux
# For Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

*(If `requirements.txt` is missing, install the core packages: `flask tensorflow opencv-python mediapipe SpeechRecognition requests python-dotenv static-ffmpeg`)*

### 3. Configure Environment Variables (API Keys)
Create a `.env` file in the `src/` directory and add the following settings (replace with your credentials):

```env
# Email Notification Settings (Requires a Google "App Password")
SYSTEM_EMAIL=your_email@gmail.com
SYSTEM_EMAIL_PASSWORD=your_app_password

# Telegram Settings
# Obtain a token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCDefgh12345
# Your default Chat ID (Used as a fallback if the user doesn't provide one on the website) - get it from @userinfobot
TELEGRAM_CHAT_ID=12345678
```

### 4. Run the Server
```bash
python3 src/app.py
```

Open your browser and navigate to `http://127.0.0.1:5055`. 
To test the camera on a mobile phone within the same local network, you will need to set up a secure tunnel (e.g., `localhost.run`, `ngrok`, or `localtunnel`), as modern browsers block camera access over `http` (except for localhost).

## 🔒 Privacy & Security
Video and audio data are processed on the fly (in-memory) or via temporary server files that are immediately overwritten. No personal biometric data is persistently stored in any database.

## 📝 Project Status & Disclaimer
This project is an early-stage research prototype. The neural network is trained for basic demonstration purposes and requires further clinical validation. **This system does not replace calling professional emergency medical services (911/112/103).**
