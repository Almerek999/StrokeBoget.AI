import numpy as np

def extract_asymmetry_features(face_landmarks):
    """
    Извлекает метрики асимметрии лица, инвариантные к наклону головы (2D Roll Alignment).
    Мы вычисляем угол наклона головы по глазам и виртуально "выравниваем" все точки 
    перед расчетом асимметрии. Это гораздо стабильнее, чем использование нестандартной Z-координаты.
    """
    # 1. Вычисляем угол наклона головы (roll) по внешним уголкам глаз
    left_eye = face_landmarks.landmark[33]
    right_eye = face_landmarks.landmark[263]
    
    dx_eyes = right_eye.x - left_eye.x
    dy_eyes = right_eye.y - left_eye.y
    
    # Угол наклона головы
    angle = np.arctan2(dy_eyes, dx_eyes)
    
    # 2. Вычисляем центр лица (нос)
    nose = face_landmarks.landmark[1]
    cx, cy = nose.x, nose.y
    
    # Функция для поворота точки на -angle вокруг носа (возвращает ее в ровное положение)
    def align_pt(pt):
        x = pt.x - cx
        y = pt.y - cy
        
        # Матрица поворота для выравнивания
        rot_x = x * np.cos(-angle) - y * np.sin(-angle)
        rot_y = x * np.sin(-angle) + y * np.cos(-angle)
        return np.array([rot_x, rot_y])

    # Ширина лица для нормализации масштаба (чтобы не зависеть от расстояния до камеры)
    face_width = np.sqrt(dx_eyes**2 + dy_eyes**2)
    if face_width == 0: 
        face_width = 1.0

    # 3. Симметричные пары (левая, правая точка)
    symmetric_pairs = [
        (61, 291),  # Уголки рта
        (37, 267),  # Верхняя губа
        (84, 314),  # Нижняя губа
        (33, 263),  # Внешние уголки глаз
        (133, 362), # Внутренние уголки глаз
        (159, 386), # Верхние веки
        (145, 374), # Нижние веки
        (46, 276),  # Внешние края бровей
        (55, 285),  # Внутренние края
        (147, 376), # Нижняя челюсть
        (58, 288)   # Щеки
    ]
    
    features = []
    
    for left_idx, right_idx in symmetric_pairs:
        # Получаем идеально ровные координаты
        l_pt = align_pt(face_landmarks.landmark[left_idx]) / face_width
        r_pt = align_pt(face_landmarks.landmark[right_idx]) / face_width
        
        # l_pt[0] = левый X (отрицательный), r_pt[0] = правый X (положительный)
        diff_x = abs(l_pt[0] + r_pt[0]) # Асимметрия по ширине (стянутость в одну сторону)
        diff_y = abs(l_pt[1] - r_pt[1]) # Асимметрия по высоте (опущенный уголок губы/глаза)
        
        features.extend([diff_x, diff_y])
        
    return features
