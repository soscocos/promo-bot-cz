import os
import glob
import time
import shutil
from pdf2image import convert_from_path
import config
import gemini_engine  # Наш новый мозг

def clear_temp_folders():
    """Очищает старые картинки перед новым запуском, чтобы не путаться"""
    print("🧹 Очистка папок...")
    if os.path.exists(config.TEMP_DIR):
        shutil.rmtree(config.TEMP_DIR)
    os.makedirs(config.TEMP_DIR, exist_ok=True)

def process_pdfs_with_ai():
    # 1. Ищем все PDF в папке input
    pdf_files = glob.glob(os.path.join(config.INPUT_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"❌ Нет PDF файлов в папке {config.INPUT_DIR}")
        return

    # Чистим старое
    clear_temp_folders()

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        # Определяем магазин по имени файла (например "albert_02.pdf" -> "albert")
        store_name = filename.split('_')[0].lower()
        
        # Если магазин неизвестен, пропускаем или кидаем в 'unknown'
        if store_name not in ["albert", "tesco", "penny", "lidl", "billa", "kaufland", "hruska"]:
            print(f"⚠️ Неизвестный магазин в файле: {filename}. Пропускаю.")
            continue

        print(f"\n📄 Обработка каталога: {store_name.upper()} ({filename})")
        
        try:
            # 2. Конвертируем PDF в картинки
            # dpi=200 - хорошее качество для Gemini, но не слишком тяжелое
            pages = convert_from_path(pdf_path, dpi=200)
            print(f"   Найдено страниц: {len(pages)}")

            for i, page in enumerate(pages):
                # Пропускаем первую и последнюю страницу (обложки часто мусорные), если хочешь
                # if i == 0 or i == len(pages) - 1: continue 

                # 3. Сохраняем картинку во временный файл
                temp_filename = f"{store_name}_{i+1}.jpg"
                temp_path = os.path.join(config.TEMP_DIR, "temp_processing.jpg")
                page.save(temp_path, 'JPEG')

                # 4. СПРАШИВАЕМ GEMINI
                # Делаем паузу, чтобы не словить бан (хотя Flash быстрый)
                time.sleep(1) 
                
                category = gemini_engine.analyze_image(temp_path)
                
                # 5. Перемещаем в правильную папку
                final_folder = os.path.join(config.TEMP_DIR, store_name, category)
                os.makedirs(final_folder, exist_ok=True)
                
                final_path = os.path.join(final_folder, temp_filename)
                
                # Перемещаем (переименовываем) файл из temp в итоговую папку
                shutil.move(temp_path, final_path)
                
                print(f"   ✅ Стр {i+1} -> 📂 {category.upper()}")

        except Exception as e:
            print(f"❌ Ошибка при обработке {filename}: {e}")

    print("\n🏁 Готово! Все PDF разобраны по категориям.")

if __name__ == "__main__":
    process_pdfs_with_ai()