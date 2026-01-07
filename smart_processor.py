import os
import glob
import time
import shutil
from pdf2image import convert_from_path
import config  # <-- Отсюда берем настройки (INPUT_DIR, TEMP_DIR)
import gemini_engine

def clear_temp_folders():
    """Удаляет старую папку temp_images перед запуском"""
    print(f"🧹 Очистка папки {config.TEMP_DIR}...")
    if os.path.exists(config.TEMP_DIR):
        try:
            shutil.rmtree(config.TEMP_DIR)
        except Exception as e:
            print(f"⚠️ Не удалось удалить старую папку (возможно открыта): {e}")
    os.makedirs(config.TEMP_DIR, exist_ok=True)

def process_pdfs_with_ai():
    # 1. Проверяем, существует ли папка с PDF
    # os.path.abspath покажет полный путь, где скрипт ищет папку (для отладки)
    full_input_path = os.path.abspath(config.INPUT_DIR)
    print(f"📂 Ищу PDF файлы здесь: {full_input_path}")

    if not os.path.exists(full_input_path):
        print(f"❌ ОШИБКА: Папка '{config.INPUT_DIR}' не найдена!")
        print(f"   Создай папку '{config.INPUT_DIR}' и положи туда PDF.")
        return

    # 2. Ищем файлы .pdf
    pdf_files = glob.glob(os.path.join(full_input_path, "*.pdf"))
    
    if not pdf_files:
        print(f"⚠️ В папке пусто! (Или файлы не имеют расширения .pdf)")
        return

    print(f"📄 Найдено файлов: {len(pdf_files)}")
    clear_temp_folders()

    # 3. Перебор файлов
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"\n------------------------------------------------")
        print(f"🎬 Обработка файла: {filename}")

        # Проверка на "_" в имени
        if "_" not in filename:
            print(f"⛔ ПРОПУСК: Имя файла '{filename}' не содержит '_'.")
            print(f"   Переименуй в формат: магазин_неделя.pdf (например: tesco_1.pdf)")
            continue

        store_name = filename.split('_')[0].lower()
        print(f"🛒 Магазин определен как: {store_name.upper()}")

        # Список известных магазинов
        known_stores = ["albert", "tesco", "penny", "lidl", "billa", "kaufland", "hruska", "globus"]
        if store_name not in known_stores:
            print(f"⚠️ Магазин '{store_name}' не в списке известных. Пропускаю.")
            continue

        try:
            print("🔨 Нарезаю PDF на картинки (это может занять время)...")
            
            # --- ФИКС ДЛЯ POPPLER ---
            # Указываем путь к папке bin ВНУТРИ папки проекта
            # os.getcwd() - это текущая папка, где лежит скрипт
            project_dir = os.getcwd()
            poppler_path = os.path.join(project_dir, "poppler", "Library", "bin")
            
            # Проверка для отладки
            if not os.path.exists(poppler_path):
                 print(f"⚠️ ВНИМАНИЕ: Скрипт не видит Poppler по пути: {poppler_path}")
                 print("Убедись, что ты распаковал архив в папку 'poppler' рядом со скриптом!")

            # Явно передаем путь в функцию
            pages = convert_from_path(pdf_path, dpi=200, poppler_path=poppler_path)
            # ------------------------
            
            print(f"📸 Получено страниц: {len(pages)}")

            for i, page in enumerate(pages):
                # Сохраняем "сырую" картинку
                temp_filename = f"{store_name}_{i+1}.jpg"
                temp_processing_path = os.path.join(config.TEMP_DIR, "processing.jpg")
                page.save(temp_processing_path, 'JPEG')

                # Спрашиваем Gemini
                print(f"🧠 Стр {i+1}: Спрашиваю Gemini...", end=" ")
                category = gemini_engine.analyze_image(temp_processing_path)
                print(f"-> {category.upper()}")

                # Создаем папку категории (например temp_images/tesco/maso)
                final_folder = os.path.join(config.TEMP_DIR, store_name, category)
                os.makedirs(final_folder, exist_ok=True)

                # Перемещаем файл
                final_path = os.path.join(final_folder, temp_filename)
                
                # Используем copy + remove вместо move для надежности на Windows
                shutil.copy(temp_processing_path, final_path)
                
        except Exception as e:
            print(f"❌ ОШИБКА при обработке {filename}:")
            print(e)
            print("💡 Совет: Если ошибка связана с 'poppler', проверь его установку.")

    print("\n🏁 ГОТОВО! Все файлы обработаны.")

if __name__ == "__main__":
    try:
        process_pdfs_with_ai()
    except Exception as e:
        print(f"\n🔥 КРИТИЧЕСКАЯ ОШИБКА ЗАПУСКА: {e}")
        import traceback
        traceback.print_exc()
    
    # Чтобы окно не закрывалось сразу
    print("\nНажми Enter, чтобы выйти...")
    input()