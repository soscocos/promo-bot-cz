from google import genai
from google.genai import types
import config
import os
from PIL import Image

def analyze_image(image_path):
    """
    Анализ картинки через Gemini 2.5 Flash.
    Настройки (промпт и категории) берет из config.py
    """
    filename = os.path.basename(image_path)
    # print(f"🧠 Gemini 2.5 смотрит на: {filename}...") # Можешь раскомментировать для отладки
    
    try:
        # 1. Авторизация
        client = genai.Client(api_key=config.TOKEN_GEMINI)
        
        # 2. Открываем картинку
        image = Image.open(image_path)

        # 3. Запрос к модели
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[image, "Какая это категория?"],
            config=types.GenerateContentConfig(
                system_instruction=config.SYSTEM_PROMPT, # Берем инструкцию из конфига
                temperature=0.1,
            )
        )
        
        # 4. Обработка ответа
        if response.text:
            result = response.text.strip().lower()
        else:
            return "general"
        
        # 5. Проверка по списку из конфига
        if result in config.VALID_CATEGORIES:
            return result
        else:
            print(f"⚠️ Gemini придумала: '{result}' (файл {filename}). Кидаю в general.")
            return "general"

    except Exception as e:
        print(f"❌ Ошибка API ({filename}): {e}")
        return "general"

if __name__ == "__main__":
    pass