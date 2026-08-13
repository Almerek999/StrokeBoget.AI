import cv2
import mediapipe as mp
import csv
import os
import math

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)

def process_images():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(current_dir, "..", "input_data")
    output_file = os.path.join(base_path, "landmarks_dataset.csv")
    categories = {'healthy': 0, 'stroke': 1}
    
    total_processed = 0

    with open(output_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        
        for category, label in categories.items():
            folder_path = os.path.join(base_path, category)
            print(f"Обрабатываю: {category}...")
            
            if not os.path.exists(folder_path): continue
            
            for filename in os.listdir(folder_path):
                if not filename.endswith(('.jpg', '.png')): continue
                img_path = os.path.join(folder_path, filename)
                image = cv2.imread(img_path)
                if image is None: continue

                results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                if results.multi_face_landmarks:
                    total_processed += 1
                    for face_landmarks in results.multi_face_landmarks:
                        from features import extract_asymmetry_features
                        row = extract_asymmetry_features(face_landmarks)
                        row.append(label)
                        writer.writerow(row)

    print(f"Готово! Извлечено лиц: {total_processed}")

if __name__ == "__main__":
    process_images()