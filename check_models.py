from google import genai
import config

# Подключаемся с твоим ключом
client = genai.Client(api_key=config.TOKEN_GEMINI)

print("🔍 СПИСОК ДОСТУПНЫХ МОДЕЛЕЙ:")
print("-" * 30)

try:
    # Запрашиваем список у Google
    for model in client.models.list():
        # Нам нужны только те, что умеют генерировать контент
        if "generateContent" in model.supported_actions:
            # Выводим чистое имя (например: models/gemini-1.5-flash)
            # Мы убираем приставку "models/", чтобы тебе было проще читать
            clean_name = model.name.replace("models/", "")
            print(f"✅ {clean_name}")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")

print("-" * 30)
input("\nНажми Enter, чтобы закрыть...")