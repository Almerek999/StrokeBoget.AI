import cv2
import os

# Создаем папки, если их случайно удалили
os.makedirs('../input_data/healthy', exist_ok=True)
os.makedirs('../input_data/stroke', exist_ok=True)

cap = cv2.VideoCapture(0)

print("\n=== ИНСТРУКЦИЯ ПО СБОРУ ДАННЫХ ===")
print("1. Смотри в камеру.")
print("2. Нажми и УДЕРЖИВАЙ клавишу '0' (ноль), чтобы записывать ЗДОРОВОЕ лицо.")
print("3. Сделай асимметрию, нажми и УДЕРЖИВАЙ '1' (один), чтобы записывать ПРИЗНАКИ ИНСУЛЬТА.")
print("4. Для выхода нажми 'q'.\n")

count_healthy = 0
count_stroke = 0

while True:
    success, frame = cap.read()
    if not success: break
    
    # Зеркалим для удобства
    frame = cv2.flip(frame, 1)
    clone = frame.copy()
    
    # Вывод счетчиков на экран
    cv2.putText(clone, f"Healthy (Press 0): {count_healthy}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(clone, f"Stroke (Press 1): {count_stroke}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    cv2.imshow("Data Collector - Hold Keys!", clone)
    
    key = cv2.waitKey(1) & 0xFF
    
    # Если зажат 0 - сохраняем в healthy
    if key == ord('0'):
        cv2.imwrite(f"../input_data/healthy/my_face_h_{count_healthy}.jpg", frame)
        count_healthy += 1
        
    # Если зажата 1 - сохраняем в stroke
    elif key == ord('1'):
        cv2.imwrite(f"../input_data/stroke/my_face_s_{count_stroke}.jpg", frame)
        count_stroke += 1
        
    # Выход
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Готово! Собрано Здоровых: {count_healthy}, С признаками: {count_stroke}")