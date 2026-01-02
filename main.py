# main.py
import os
import time
import config
import processor
import shutil

def run_manual_pipeline():
    print("🚀 Система нарезки запущена.")
    print(f"1. Клади PDF в папку: {config.INPUT_DIR}")
    print("2. Ищи нарезки в temp_images/[МАГАЗИН]/general")
    print("3. Просто перетаскивай их в соседние папки категорий для сортировки.")
    
    # Создаем базовые папки, если их нет
    os.makedirs(config.INPUT_DIR, exist_ok=True)
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)

    while True:
        # Ищем новые PDF файлы
        files = [f for f in os.listdir(config.INPUT_DIR) if f.endswith('.pdf')]
        
        if not files:
            time.sleep(5) # Ждем 5 секунд и проверяем снова
            continue

        for pdf_name in files:
            pdf_full_path = os.path.join(config.INPUT_DIR, pdf_name)
            print(f"📦 Начинаю обработку: {pdf_name}")
            
            try:
                # Нарезаем, создаем папки магазина и применяем кроп (для Albert)
                store_detected, count = processor.process_pdf(pdf_full_path)
                
                # Переносим оригинал в архив
                shutil.move(
                    pdf_full_path,
                    os.path.join(config.PROCESSED_DIR, pdf_name)
                )
                print(f"✅ Готово! Магазин: {store_detected.upper()}. Нарезано страниц: {count}")
                print(f"📍 Файлы ждут здесь: {config.TEMP_DIR}/{store_detected}/general")
                
            except Exception as e:
                print(f"❌ Ошибка при обработке {pdf_name}: {e}")

if __name__ == "__main__":
    run_manual_pipeline()