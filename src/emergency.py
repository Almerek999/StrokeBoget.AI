import os
import requests
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def reverse_geocode(lat, lon):
    """Преобразует GPS координаты в читаемый текстовый адрес через бесплатный API Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ru"
        headers = {'User-Agent': 'AntiStrokeApp/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('display_name', '')
    except Exception as e:
        print(f"❌ Ошибка обратного геокодирования: {e}")
    return None

def get_location():
    """Получает текущие координаты по IP (Симуляция для прототипа)"""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()
        if data['status'] == 'success':
            return data['lat'], data['lon'], data['city']
    except Exception:
        pass
    return None, None, None

def find_nearest_hospital(lat, lon):
    """Ищет ближайшую больницу через OpenStreetMap"""
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:5000,{lat},{lon});
      way["amenity"="hospital"](around:5000,{lat},{lon});
      relation["amenity"="hospital"](around:5000,{lat},{lon});
    );
    out center;
    """
    try:
        headers = {'User-Agent': 'StrokeDetectionApp/2.0'}
        response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers, timeout=10)
        data = response.json()
        if 'elements' in data and len(data['elements']) > 0:
            nearest = data['elements'][0]
            h_lat = nearest.get('lat', nearest.get('center', {}).get('lat'))
            h_lon = nearest.get('lon', nearest.get('center', {}).get('lon'))
            name = nearest.get('tags', {}).get('name', 'Неизвестная больница (Координаты)')
            return {'name': name, 'lat': h_lat, 'lon': h_lon}
    except Exception:
        pass
    return None

def send_telegram_message(bot_token, chat_id, message):
    if not bot_token or not chat_id:
        print("⚠️ Telegram отключен (не указан токен или chat_id)")
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload, timeout=5)
        print("✅ Сообщение Telegram отправлено!")
    except Exception as e:
        print(f"❌ Ошибка Telegram: {e}")

def send_emergency_email(receiver_email, subject, body):
    sender_email = os.getenv("SYSTEM_EMAIL")
    sender_password = os.getenv("SYSTEM_EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("⚠️ Email отправка отключена (настройки в .env)")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Письмо успешно отправлено на {receiver_email}!")
    except Exception as e:
        print(f"❌ Ошибка Email: {e}")

def trigger_sos(patient_name, relative_name, relative_email, phone_lat=None, phone_lon=None, fallback_address=None, tg_chat_id=None):
    print("\n🚨 [БЭКЕНД] АКТИВИРОВАН ПРОТОКОЛ SOS 🚨")
    
    # 1. Определяем координаты для карты и больницы
    if phone_lat and phone_lon:
        lat, lon = phone_lat, phone_lon
        print(f"📍 Использованы ТОЧНЫЕ GPS координаты от телефона: {lat}, {lon}")
    else:
        print("⚠️ Точные координаты не получены от браузера телефона (возможно, доступ запрещен).")
        lat, lon, city = get_location()
        if lat:
            print(f"📍 Использована приблизительная локация по IP: {lat}, {lon} ({city})")

    # 2. Определяем текст адреса для письма (Ручной ввод > GPS > IP)
    if fallback_address and fallback_address.strip():
        display_address = f"Указанный домашний адрес: {fallback_address}"
        print(f"🏠 Приоритет отдан ручному вводу: {fallback_address}")
    elif phone_lat and phone_lon:
        print("🔍 Определение точного текстового адреса (Reverse Geocoding)...")
        exact_address = reverse_geocode(lat, lon)
        if exact_address:
            display_address = f"Точный адрес по GPS: {exact_address}"
            print(f"🏠 Найден адрес: {exact_address}")
        else:
            display_address = f"GPS координаты: {lat}, {lon}"
    else:
        display_address = f"Приблизительная гео-локация по IP: {city} (может быть неточным, так как GPS был недоступен)"

    hospital = find_nearest_hospital(lat, lon) if (lat and lon) else None

    # Формируем тело сообщения (общее для Email и Telegram)
    body = f"🆘 ВНИМАНИЕ, {relative_name}!\n\nСистема зафиксировала критические признаки инсульта у {patient_name}.\n"
    
    body += f"\n📍 Локация пациента: {display_address}"
    if lat and lon:
        body += f"\n🗺 Карта: https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        
    if hospital:
        body += f"\n\n🏥 Ближайшая больница (относительно координат): {hospital['name']}"
        body += f"\n🚗 Маршрут: https://www.google.com/maps/dir/?api=1&origin={lat},{lon}&destination={hospital['lat']},{hospital['lon']}"
    
    body += "\n\nПожалуйста, немедленно свяжитесь с пациентом и вызовите скорую помощь!"
    
    # 1. Отправка Email
    subject = f"⚠️ ЭКСТРЕННО: {patient_name} - Подозрение на инсульт!"
    send_emergency_email(relative_email, subject, body)
    
    # 2. Отправка Telegram
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    final_chat_id = tg_chat_id if tg_chat_id else os.getenv("TELEGRAM_CHAT_ID")
    send_telegram_message(bot_token, final_chat_id, body)
