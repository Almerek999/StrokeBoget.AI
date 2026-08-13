import http.server
import socketserver
import json
import os
import urllib.parse
import webbrowser
import threading

PORT = 8080

config_path = os.path.join(os.path.dirname(__file__), 'config.json')
def load_config():
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "patient_name": "", 
        "patient_email": "", 
        "relative_name": "", 
        "relative_email": "",
        "system_email": "",
        "system_password": ""
    }

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Настройки SOS</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #121212;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        .container {
            background-color: #1e1e1e;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            width: 100%;
            max-width: 450px;
        }
        h1 {
            color: #ff4d4d;
            margin-bottom: 5px;
            text-align: center;
        }
        p {
            color: #a0a0a0;
            margin-bottom: 25px;
            font-size: 14px;
            text-align: center;
        }
        .section-title {
            color: #4CAF50;
            margin-bottom: 15px;
            margin-top: 25px;
            font-size: 18px;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
        }
        .section-title.red { color: #ff4d4d; }
        .section-title.grey { color: #888; font-size: 16px; border-bottom: 1px dashed #444; }
        .input-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            font-size: 14px;
            color: #ccc;
        }
        input[type="text"], input[type="email"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 10px;
            background-color: #2d2d2d;
            color: #ffffff;
            font-size: 15px;
            box-sizing: border-box;
        }
        input[type="text"]:focus, input[type="email"]:focus, input[type="password"]:focus {
            outline: 2px solid #ff4d4d;
        }
        button {
            background-color: #ff4d4d;
            color: white;
            border: none;
            padding: 16px;
            width: 100%;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-top: 20px;
        }
        button:hover {
            background-color: #ff3333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Анти-Инсульт</h1>
        <p>Пожалуйста, зарегистрируйтесь перед запуском сканирования.</p>
        <form method="POST" action="/save">
            
            <div class="section-title">Ваши данные (Пациент)</div>
            <div class="input-group">
                <label>Ваше Имя:</label>
                <input type="text" name="patient_name" value="{p_name}" placeholder="Например: Алмерек" required>
            </div>
            <div class="input-group">
                <label>Ваш Email (куда придет успокаивающее письмо):</label>
                <input type="email" name="patient_email" value="{p_email}" placeholder="patient@gmail.com" required>
            </div>

            <div class="section-title red">Данные Родственника (Спасатель)</div>
            <div class="input-group">
                <label>Имя родственника:</label>
                <input type="text" name="relative_name" value="{r_name}" placeholder="Например: Мама" required>
            </div>
            <div class="input-group">
                <label>Email родственника (куда придет сигнал SOS):</label>
                <input type="email" name="relative_email" value="{r_email}" placeholder="relative@gmail.com" required>
            </div>

            <div class="section-title grey">⚙️ Настройки Системы (Для отправки писем)</div>
            <div class="input-group">
                <label>Ваш системный Gmail (отправитель):</label>
                <input type="email" name="system_email" value="{s_email}" placeholder="your.bot@gmail.com">
            </div>
            <div class="input-group">
                <label>Пароль приложения Google (16 букв):</label>
                <input type="password" name="system_password" value="{s_pass}" placeholder="abcd efgh ijkl mnop">
            </div>

            <button type="submit">СОХРАНИТЬ И ЗАПУСТИТЬ</button>
        </form>
    </div>
</body>
</html>
"""

class SettingsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            config = load_config()
            html = HTML_TEMPLATE.replace("{p_name}", config.get("patient_name", ""))
            html = html.replace("{p_email}", config.get("patient_email", ""))
            html = html.replace("{r_name}", config.get("relative_name", ""))
            html = html.replace("{r_email}", config.get("relative_email", ""))
            html = html.replace("{s_email}", config.get("system_email", ""))
            html = html.replace("{s_pass}", config.get("system_password", ""))
            
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            
            config = {
                "patient_name": parsed_data.get('patient_name', [''])[0],
                "patient_email": parsed_data.get('patient_email', [''])[0],
                "relative_name": parsed_data.get('relative_name', [''])[0],
                "relative_email": parsed_data.get('relative_email', [''])[0],
                "system_email": parsed_data.get('system_email', [''])[0],
                "system_password": parsed_data.get('system_password', [''])[0]
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            success_html = """
            <html><body style='background-color:#121212; color:white; font-family:sans-serif; text-align:center; padding-top:50px;'>
            <h2 style='color:#00ff00;'>Настройки сохранены!</h2>
            <p>Вы можете закрыть эту вкладку. Камера запустится через пару секунд...</p>
            <script>setTimeout(function(){ window.close(); }, 3000);</script>
            </body></html>
            """
            self.wfile.write(success_html.encode('utf-8'))
            
            threading.Thread(target=self.server.shutdown).start()

def run_app():
    global PORT
    print(f"Запуск веб-интерфейса настроек на порту {PORT}...")
    
    while True:
        try:
            httpd = socketserver.TCPServer(("", PORT), SettingsHandler)
            break
        except OSError:
            PORT += 1

    webbrowser.open(f'http://localhost:{PORT}')
    
    httpd.serve_forever()
    httpd.server_close()
    
    print("\nЗапуск главной программы (Сканнер)...")
    import main_app
    main_app.start_camera()

if __name__ == "__main__":
    run_app()
