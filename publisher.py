# publisher.py
import os
import json
import requests
import config
import video_creator # Использует MoviePy 2.2.1
import time

# --- БЛОК УПРАВЛЕНИЯ МАГАЗИНАМИ ---
# Индексы: 0-albert, 1-tesco, 2-penny, 3-lidl, 4-billa, 5-kaufland, 6-hrushka
ALL_STORES = ["albert", "tesco", "penny", "lidl", "billa", "kaufland", "hruska"]


CURRENT_STORES = [ALL_STORES[0]] 

def get_local_caption(store_name, category_name):
    """Локальные шаблоны с учетом твоих новых категорий"""
    templates = {
        "snacky": f"🥨 хрустяшки в {store_name.upper()}! 🍿",
        "kava_caj": f"☕ кофе и чай в {store_name.upper()}! бодрые скидки. 🍵",
        "alkohol": f"🔥 отличные цены на алкоголь в {store_name.upper()}! 🥂",
        "cistidla": f"🧼 чистота с {store_name.upper()}! бытовая химия дешевле.",
        "general": f"🛒 крутые скидки в {store_name.upper()}! забирай скорее.",
        "info": f"ℹ️ инфо от {store_name.upper()}.",
        "klobasa_sunka_salam_parky": f"🌭 колбасы и сосиски в {store_name.upper()}!",
        "maso": f"🥩 свежее мясо в {store_name.upper()}! отличный выбор.",
        "nadobi": f"🍳 посуда в {store_name.upper()}! обновляем кухню.",
        "ovoce_a_zelenina": f"🍎 фрукты и овощи в {store_name.upper()}! свежий завоз.",
        "pecivo": f"🥐 свежая выпечка в {store_name.upper()}! рогалики по акции.",
        "syry": f"🧀 сыры по акции в {store_name.upper()}! пробуем новое.",
        "svacina": f"🍱 открыл, намазал в {store_name.upper()}!"
    }
    base_text = templates.get(category_name, f"📍 актуальные акции в {store_name.upper()}!")
    return f"<b>{base_text.lower()}</b>\n\n#akce #{store_name} #{category_name} #praha"

def send_media_group(video_path, images, caption):
    """
    Универсальная отправка: 
    Сначала пробует (Видео + Фото), если видео нет — шлет только (Фото)
    """
    url = f"https://api.telegram.org/bot{config.TOKEN}/sendMediaGroup"
    media = []
    files = {}

    # 1. Проверяем, есть ли видео
    if video_path and os.path.exists(video_path):
        # Если видео есть, оно будет первым в альбоме и несет текст
        media.append({'type': 'video', 'media': 'attach://video', 'caption': caption, 'parse_mode': 'HTML'})
        files['video'] = open(video_path, 'rb')
        limit = 9 # В альбоме может быть 1 видео + 9 фото
    else:
        # Если видео нет, текст крепим к ПЕРВОЙ фотографии
        media.append({'type': 'photo', 'media': 'attach://photo_0', 'caption': caption, 'parse_mode': 'HTML'})
        limit = 10 # В альбоме может быть до 10 фото

    # 2. Добавляем фотографии
    for i, img_path in enumerate(images[:limit]):
        file_key = f'photo_{i}'
        # Если видео не было, первая картинка уже в media (через индекс i==0)
        if i == 0 and not (video_path and os.path.exists(video_path)):
            files[file_key] = open(img_path, 'rb')
        else:
            media.append({'type': 'photo', 'media': f'attach://{file_key}'})
            files[file_key] = open(img_path, 'rb')
    
    payload = {'chat_id': config.CHANNEL_ID, 'media': json.dumps(media)}
    
    try:
        print(f"📡 Отправляю альбом (Видео: {'Да' if video_path else 'Нет'})...")
        res = requests.post(url, data=payload, files=files, timeout=60)
        for f in files.values(): f.close()
        
        if res.status_code != 200:
            print(f"❌ Ошибка TG: {res.text}")
        return res.status_code == 200
    except Exception as e:
        print(f"💥 Ошибка сети: {e}")
        return False

def run_publisher():
    """Обход папок и публикация контента в любом виде"""
    base_dir = config.TEMP_DIR 
    post_count = 0

    for store in CURRENT_STORES:
        store_path = os.path.join(base_dir, store)
        if not os.path.exists(store_path):
            print(f"ℹ️ Папка магазина {store} пуста.")
            continue

        for category in os.listdir(store_path):
            cat_path = os.path.join(store_path, category)
            if not os.path.isdir(cat_path): continue

            # Собираем фото (от 2-х штук для альбома)
            imgs = [os.path.join(cat_path, f) for f in os.listdir(cat_path) if f.endswith(".jpg")]

            if len(imgs) >= 2:
                if post_count > 0:
                    print(f"⏳ Ожидание 10 минут (600 сек) перед следующим постом...")
                    time.sleep(600)

                print(f"🎬 Сборка: {store.upper()} -> {category} ({len(imgs)} фото)")
                caption = get_local_caption(store, category)
                
                # Пытаемся создать видео
                v_path = video_creator.create_store_video(imgs, f"{store}_{category}")
                
                # ОТПРАВЛЯЕМ В ЛЮБОМ СЛУЧАЕ (с видео или без)
                if send_media_group(v_path, imgs, caption):
                    print(f"🚀 ПОСТ ВЫЛОЖЕН!")
                    if v_path and os.path.exists(v_path):
                        os.remove(v_path)
                    for img in imgs:
                        os.remove(img)
                    post_count += 1
                else:
                    print(f"❌ Ошибка при отправке {store}/{category}")

    print(f"🏁 Работа завершена. Опубликовано постов: {post_count}")