import speech_recognition as sr
import difflib

def test_speech_factor():
    recognizer = sr.Recognizer()
    # Фраза, которую нужно будет прочитать (специально с шипящими и звонкими)
    target_phrase = "за окном сегодня светит яркое солнце"
    
    with sr.Microphone() as source:
        print("\n" + "="*40)
        print("   МОДУЛЬ 2: АНАЛИЗ ЧИСТОТЫ РЕЧИ")
        print("="*40)
        print(f"\nПожалуйста, четко произнесите фразу:\n«{target_phrase}»")
        
        print("\n[Калибровка шума...] Помолчите 1 секунду.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("\n🎤 ГОВОРИТЕ! (Запись идет 5 секунд)...")
        
        try:
            # Слушаем микрофон (максимум 5 секунд на фразу)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("⏳ Обработка аудио нейросетью Google...")
            
            # Отправляем аудио на распознавание (язык - русский)
            text = recognizer.recognize_google(audio, language="ru-RU").lower()
            
            print(f"\nВы сказали: «{text}»")
            print(f"Ожидалось:  «{target_phrase}»")
            
            # Математически сравниваем строки (от 0.0 до 1.0)
            similarity = difflib.SequenceMatcher(None, target_phrase, text).ratio()
            print(f"\n📊 Точность артикуляции: {similarity * 100:.1f}%")
            
            # Логика принятия решений
            if similarity > 0.7:
                print("✅ Вердикт: Речь чистая, признаков дизартрии нет.")
            else:
                print("❌ Вердикт: ВНИМАНИЕ! Речь сильно искажена (возможен инсульт).")
                
        except sr.UnknownValueError:
            # Если ИИ вообще не понял ни слова (сильное искажение)
            print("\n❌ Вердикт: ВНИМАНИЕ! Программа не смогла разобрать ни одного слова. Возможна тяжелая афазия.")
        except sr.RequestError as e:
            print(f"\n⚠️ Ошибка связи с сервером: {e}")
        except Exception as e:
            print(f"\n⚠️ Ошибка: {e}")

if __name__ == "__main__":
    test_speech_factor()