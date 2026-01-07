from google import genai
from google.genai import types
import config
import os
import time
from PIL import Image

def analyze_image(image_path):
    """
    Анализ через Gemini 2.0 Flash (единственная стабильная, доступная тебе)
    """
    filename = os.path.basename(image_path)
    
    # Эта модель была в твоем списке "check_models.py"
    MODEL_NAME = "gemini-2.0-flash" 
    
    max_retries = 10 # Увеличил количество попыток, чтобы наверняка пробиться
    
    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=config.TOKEN_GEMINI)
            
            with Image.open(image_path) as image:
                response = client.models.generate_content(
                    model=MODEL_NAME, 
                    contents=[image, "Какая это категория?"],
                    config=types.GenerateContentConfig(
                        system_instruction=config.SYSTEM_PROMPT,
                        temperature=0.1,
                    )
                )
                text_response = response.text

            if text_response:
                result = text_response.strip().lower()
                if result in config.VALID_CATEGORIES:
                    return result
                else:
                    return "general"
            return "general"

        except Exception as e:
            error_str = str(e)
            
            # Если модели нет (404) - значит Google совсем сошел с ума
            if "404" in error_str:
                print(f"❌ Ошибка 404: Модель {MODEL_NAME} не найдена. Попробуй 'gemini-2.5-flash'.")
                return "general"

            # ЛИМИТЫ (429) - Самое важное
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                # Ждем с нарастанием: 10, 20, 30 сек...
                wait_time = 10 + (attempt * 10)
                print(f"\n⏳ Лимит (RPM). Жду {wait_time} сек и пробую снова...")
                time.sleep(wait_time)
                continue
            
            print(f"❌ Ошибка API ({filename}): {e}")
            return "general"

    print("❌ Не удалось обработать файл (слишком много ошибок лимитов).")
    return "general"

if __name__ == "__main__":
    pass