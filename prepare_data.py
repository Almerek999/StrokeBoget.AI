import cv2
import mediapipe as mp
import csv
import os
import math

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)

def process_images():
    output_file = "../input_data/landmarks_dataset.csv"
    base_path = "../input_data"
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
                        # 1. Центр: кончик носа (точка 1)
                        nx = face_landmarks.landmark[1].x
                        ny = face_landmarks.landmark[1].y
                        nz = face_landmarks.landmark[1].z
                        
                        # 2. Масштаб: ширина лица (края щек - точки 234 и 454)
                        lx = face_landmarks.landmark[234].x
                        ly = face_landmarks.landmark[234].y
                        rx = face_landmarks.landmark[454].x
                        ry = face_landmarks.landmark[454].y
                        face_width = math.sqrt((rx - lx)**2 + (ry - ly)**2)
                        if face_width == 0: face_width = 1
                        
                        row = []
                        for lm in face_landmarks.landmark:
                            # 3. Высчитываем 3D расстояние от носа до каждой точки
                            dist = math.sqrt((lm.x - nx)**2 + (lm.y - ny)**2 + (lm.z - nz)**2)
                            # 4. Нормализуем (делим на ширину лица)
                            row.append(dist / face_width)
                            
                        row.append(label)
                        writer.writerow(row)

    print(f"Готово! Извлечено лиц: {total_processed}")

if __name__ == "__main__":
    process_images()