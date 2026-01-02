# processor.py
import os
import fitz  # PyMuPDF
import config

def process_pdf(pdf_path):
    """
    Нарезает PDF, создает структуру папок магазина и категорий,
    применяет кроп для Albert.
    """
    filename = os.path.basename(pdf_path).lower()
    
    # 1. Определяем магазин
    store_name = "general"
    stores_list = ["albert", "tesco", "penny", "lidl", "billa", "kaufland", "hruska"]
    for s in stores_list:
        if s in filename:
            store_name = s
            break

    # 2. Создаем структуру: temp_images/магазин/ и подпапки категорий
    store_root = os.path.join(config.TEMP_DIR, store_name)
    
    # Создаем папки товаров (alkohol, maso и т.д.) внутри магазина
    for cat in config.CATEGORIES:
        os.makedirs(os.path.join(store_root, cat), exist_ok=True)
    
    # Папка для новых нарезок (склад)
    output_dir = os.path.join(store_root, "general")
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    count = 0

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 3. Логика обрезки (Crop) для Albert
        # Если это Albert, убираем пустоту справа (~4%) и снизу (~2%)
        if store_name == "albert":
            rect = page.rect
            # Создаем новую рамку: (x0, y0, x1_cropped, y1_cropped)
            # x1 * 0.96 убирает полосу справа, y1 * 0.98 убирает полосу снизу
            crop_rect = fitz.Rect(rect.x0, rect.y0, rect.x1 * 0.96, rect.y1 * 0.98)
            pix = page.get_pixmap(dpi=150, clip=crop_rect)
        else:
            # Для остальных магазинов берем страницу целиком
            pix = page.get_pixmap(dpi=150)

        # Сохраняем в папку general соответствующего магазина
        img_name = f"{store_name}_p{page_num}_{count}.jpg"
        img_path = os.path.join(output_dir, img_name)
        pix.save(img_path)
        count += 1
    
    doc.close()
    print(f"✅ Обработан {store_name.upper()}: {count} стр. -> {output_dir}")
    return store_name, count