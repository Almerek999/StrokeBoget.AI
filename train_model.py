import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models
import os

# 1. Загрузка собранных данных
data_path = "../input_data/landmarks_dataset.csv"
if not os.path.exists(data_path):
    print("Ошибка: Файл с данными не найден!")
    exit()

print("Читаю данные...")
data = pd.read_csv(data_path, header=None)

# Разделяем координаты (X) и ответы: 0 или 1 (y)
X = data.iloc[:, :-1].values 
y = data.iloc[:, -1].values  

# 2. Делим данные на "учебники" (80%) и "экзамен" (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Строим архитектуру нейросети (как слои в торте)
model = models.Sequential([
    layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    layers.Dropout(0.2), # Защита от "зубрежки"
    layers.Dense(64, activation='relu'),
    layers.Dense(32, activation='relu'),
    layers.Dense(1, activation='sigmoid') # Выдает результат от 0 до 1
])

# 4. Настройка и запуск обучения
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

print("\n--- Начинаю обучение нейросети ---")
# epochs=30 означает, что ИИ просмотрит данные 30 раз, чтобы лучше запомнить
model.fit(X_train, y_train, epochs=30, batch_size=16, validation_data=(X_test, y_test))

# 5. Сохранение обученной модели
if not os.path.exists("../models"): 
    os.makedirs("../models")
model.save('../models/stroke_ai_model.h5')
print("\n--- УРА! Модель обучена и сохранена в папку models ---")