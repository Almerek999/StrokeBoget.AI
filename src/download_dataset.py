import os
import requests
from duckduckgo_search import DDGS
import time

def download_images(query, folder, max_images=30):
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    print(f"Ищу картинки по запросу: {query}")
    
    with DDGS() as ddgs:
        results = list(ddgs.images(
            query,
            region="wt-wt",
            safesearch="moderate",
            size="Medium",
            type_image="photo",
            max_results=max_images
        ))
        
    count = 0
    for i, res in enumerate(results):
        url = res.get('image')
        if not url: continue
        
        try:
            print(f"Скачиваю: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                ext = url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png']:
                    ext = 'jpg'
                
                filepath = os.path.join(folder, f"img_{count}.{ext}")
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                count += 1
        except Exception as e:
            print(f"Ошибка при скачивании {url}: {e}")
            
        time.sleep(0.5) # Немного ждем, чтобы не заблокировали

    print(f"Готово! Скачано {count} картинок в {folder}\n")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_data_dir = os.path.join(current_dir, "..", "input_data")
    
    stroke_dir = os.path.join(input_data_dir, "stroke")
    healthy_dir = os.path.join(input_data_dir, "healthy")
    
    print("Начинаю автоматический сбор датасета...")
    # Скачиваем лица с инсультом / параличом
    download_images("stroke patient facial droop", stroke_dir, max_images=40)
    download_images("Bell's palsy face", stroke_dir, max_images=40)
    
    # Скачиваем здоровые лица
    download_images("healthy person face looking straight", healthy_dir, max_images=60)
    
    print("Сбор завершен! Теперь вы можете запустить prepare_data.py")
