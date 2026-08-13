import tkinter as tk
from tkinter import messagebox
import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"relative_email": "", "relative_phone": ""}

def save_config_and_start(root, email_var, phone_var):
    email = email_var.get().strip()
    phone = phone_var.get().strip()
    
    if not email and not phone:
        messagebox.showwarning("Внимание", "Пожалуйста, введите хотя бы один контакт (Почту или Телефон).")
        return
        
    config = {
        "relative_email": email,
        "relative_phone": phone
    }
    
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Ошибка сохранения:", e)
        
    # Закрываем окно настроек
    root.destroy()
    
    # Запускаем главную программу
    import main_app
    main_app.start_camera()

def run_ui():
    root = tk.Tk()
    root.title("Настройки SOS")
    root.geometry("400x500")
    root.configure(bg="#1e1e1e") # Темная тема
    
    # Центрирование окна
    root.eval('tk::PlaceWindow . center')
    
    config = load_config()
    
    # Заголовок
    title_label = tk.Label(root, text="Анти-Инсульт\nНастройки SOS", font=("Helvetica", 24, "bold"), bg="#1e1e1e", fg="#ffffff")
    title_label.pack(pady=30)
    
    # Описание
    desc_label = tk.Label(root, text="Укажите контакты родственников,\nкоторым система отправит координаты\nи маршрут к больнице в случае приступа.", 
                          font=("Helvetica", 12), bg="#1e1e1e", fg="#a0a0a0", justify=tk.CENTER)
    desc_label.pack(pady=10)
    
    # Поле Почты
    email_frame = tk.Frame(root, bg="#1e1e1e")
    email_frame.pack(fill="x", padx=40, pady=10)
    
    tk.Label(email_frame, text="Email родственника:", font=("Helvetica", 14), bg="#1e1e1e", fg="#ffffff").pack(anchor="w")
    email_var = tk.StringVar(value=config.get("relative_email", ""))
    email_entry = tk.Entry(email_frame, textvariable=email_var, font=("Helvetica", 16), bg="#2d2d2d", fg="#ffffff", insertbackground="white", relief="flat")
    email_entry.pack(fill="x", pady=5, ipady=5)
    
    # Поле Телефона
    phone_frame = tk.Frame(root, bg="#1e1e1e")
    phone_frame.pack(fill="x", padx=40, pady=10)
    
    tk.Label(phone_frame, text="Телефон (В будущем для СМС):", font=("Helvetica", 14), bg="#1e1e1e", fg="#ffffff").pack(anchor="w")
    phone_var = tk.StringVar(value=config.get("relative_phone", ""))
    phone_entry = tk.Entry(phone_frame, textvariable=phone_var, font=("Helvetica", 16), bg="#2d2d2d", fg="#ffffff", insertbackground="white", relief="flat")
    phone_entry.pack(fill="x", pady=5, ipady=5)
    
    # Кнопка Запуска
    start_btn = tk.Button(root, text="СОХРАНИТЬ И ЗАПУСТИТЬ", font=("Helvetica", 14, "bold"), bg="#ff4d4d", fg="#ffffff", 
                          activebackground="#ff3333", activeforeground="white", relief="flat",
                          command=lambda: save_config_and_start(root, email_var, phone_var))
    start_btn.pack(pady=30, ipady=10, fill="x", padx=40)
    
    # Делаем кнопку красной на Mac (Mac требует хитростей, но bg тут работает сносно)
    # Используем highlightbackground как хак для Mac
    start_btn.configure(highlightbackground="#1e1e1e")
    
    root.mainloop()

if __name__ == "__main__":
    run_ui()
