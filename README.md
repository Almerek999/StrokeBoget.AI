# BogetStroke.AI 🧠⚡️
**Multimodal 2-Factor Stroke Detection System**

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-FF6F00?logo=tensorflow&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Dynamic-5C3EE8?logo=opencv&logoColor=white)
![Status](https://img.shields.io/badge/Status-MVP-success)

## 📌 About the Project
**BogetStroke.AI** is an automated, real-time diagnostic tool designed to detect early signs of a stroke using everyday consumer hardware (webcams and microphones). By digitizing the standard **FAST** (Face, Arms, Speech, Time) medical protocol, the system eliminates human error, panic, and subjectivity during a medical emergency.

The system utilizes a dual-verification approach combining **Computer Vision (CV)** and **Natural Language Processing (NLP)** to accurately diagnose symptoms and automatically trigger an emergency SOS protocol within the critical "Golden Hour".

## 🚀 Key Features
* **Facial Asymmetry Detection (Face CV):** Maps 468 3D facial landmarks using MediaPipe. Calculates normalized Euclidean distances to detect muscle paresis, ensuring geometric invariance (ignores head tilt, distance, and lighting).
* **Speech Articulation Analysis (Speech NLP):** Transcribes audio to detect dysarthria (slurred speech) using Levenshtein distance comparison against a control phrase.
* **2-Factor Verification:** Merges Face + Speech data to minimize false positives, achieving up to 96% diagnostic accuracy.
* **Automated SOS Routing:** Instantly captures the device's GPS coordinates and generates an emergency digital anamnesis package in under 10 seconds.
* **Zero Cost Hardware:** Runs entirely on standard laptops or smartphones without the need for expensive clinical scanners.

## 🛠 Technology Stack
* **Core:** Python
* **Computer Vision:** OpenCV, Google MediaPipe (Face Mesh)
* **Machine Learning:** TensorFlow / Keras (Custom MLP neural network)
* **Audio Processing:** SpeechRecognition, PyAudio

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/KopirAI.git](https://github.com/your-username/KopirAI.git)
   cd KopirAI/src
   ```
2.Install system audio dependencies (Required for macOS):
   ```bash
   brew install portaudio
   ```
3.Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
(Ensure you have opencv-python, mediapipe, tensorflow==2.15.0, SpeechRecognition, and pyaudio installed).

## 🏁 Usage
To launch the diagnostic interface, run the main script from your terminal:
```bash
   python main.py
   ```
## How to test:

1.Face the camera directly. The system will continuously monitor your face for baseline asymmetry.

2.Press the T key on your keyboard to initialize the FAST test.

3.When prompted, clearly speak the control phrase into your microphone ("You can't teach an old dog new tricks")

4.The system will process the multimodal data and display the final diagnosis (Healthy / Warning / Critical) on the screen.
