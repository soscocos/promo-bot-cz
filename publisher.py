import os
import json
import requests
import config
import video_creator
import time
import math

# Список всех магазинов
ALL_STORES = ["albert", "tesco", "penny", "lidl", "billa", "kaufland", "hruska"]
CURRENT_STORES = [ALL_STORES[1]] # Сейчас только Albert

def get_local_caption(store_name, category_name):
    """
    Полный список шаблонов для всех категорий из твоего списка
    """
    store_up = store_name.upper()
    
    templates = {
        "alkohol": f"🍷 отличные цены на алкоголь в {store_up}!",
        "snacky": f"🥨 вкусные перекусы и снеки в {store_up}!",
        "syry": f"🧀 сырная лавка в {store_up}: выбирай лучшее!",
        "maso": f"🥩 свежее мясо в {store_up}! отличный выбор для обеда.",
        "klobasa_sunka_salam_parky": f"🥓 колбасы и мясные деликатесы в {store_up}!",
        "ovoce_a_zelenina": f"🍎 витамины в {store_up}: свежие овощи и фрукты!",
        "pecivo": f"🥐 ароматная выпечка в {store_up}! свежесть каждый день.",
        "cistidla": f"🧼 чистота в доме с {store_up}: средства для уборки!",
        "nadobi": f"🍽️ товары для кухни и посуда в {store_up}!",
        "kava_caj": f"☕️ бодрящий кофе и чай в {store_up}!",
        "info": f"📢 важная информация и новости магазина {store_up}!",
        "general": f"🛒 крутые скидки в {store_up}! забирай, пока не разобрали."
    }
    
    # Если папка называется странно и её нет в списке — берем 'general'
    base_text = templates.get(category_name, templates["general"])
    
    return f"<b>{base_text}</b>\n\n#{store_name} #{category_name}"

def send_media_group(video_path, images, caption):
    """Универсальная отправка: Видео+Фото или просто Фото"""
    url = f"https://api.telegram.org/bot{config.TOKEN}/sendMediaGroup"
    media = []
    files = {}

    # Если видео есть, оно идет первым с текстом
    if video_path and os.path.exists(video_path):
        media.append({'type': 'video', 'media': 'attach://video', 'caption': caption, 'parse_mode': 'HTML'})
        files['video'] = open(video_path, 'rb')
        limit = 9
    else:
        # Если видео нет, текст крепим к первому фото
        media.append({'type': 'photo', 'media': 'attach://photo_0', 'caption': caption, 'parse_mode': 'HTML'})
        limit = 10

    # Добавляем фото в альбом
    for i, img_path in enumerate(images[:limit]):
        file_key = f'photo_{i}'
        if i == 0 and not (video_path and os.path.exists(video_path)):
            files[file_key] = open(img_path, 'rb')
        else:
            media.append({'type': 'photo', 'media': f'attach://{file_key}'})
            files[file_key] = open(img_path, 'rb')
    
    try:
        res = requests.post(url, data={'chat_id': config.CHANNEL_ID, 'media': json.dumps(media)}, files=files, timeout=60)
        for f in files.values(): f.close()
        return res.status_code == 200
    except Exception as e:
        print(f"💥 Ошибка сети: {e}")
        return False

def run_publisher():
    """Обход папок с равномерным распределением картинок по постам"""
    base_dir = config.TEMP_DIR 
    post_count = 0

    for store in CURRENT_STORES:
        store_path = os.path.join(base_dir, store)
        if not os.path.exists(store_path): continue

        for category in os.listdir(store_path):
            cat_path = os.path.join(store_path, category)
            if not os.path.isdir(cat_path): continue

            all_imgs = [os.path.join(cat_path, f) for f in os.listdir(cat_path) if f.endswith(".jpg")]
            total_count = len(all_imgs)
            
            if total_count < 2: continue

            # --- ЛОГИКА РАВНОМЕРНОГО ДЕЛЕНИЯ ---
            # 1. Считаем количество необходимых постов (макс 10 фото на пост)
            num_posts = math.ceil(total_count / 10)
            
            # 2. Вычисляем среднее количество фото в одном посте
            # Делим общее число на количество постов и округляем вверх
            avg_size = math.ceil(total_count / num_posts)
            
            print(f"📦 Всего фото: {total_count}. Делю на {num_posts} поста(ов) примерно по {avg_size} шт.")

            # 3. Режем список на равные части
            chunks = []
            for i in range(0, total_count, avg_size):
                chunks.append(all_imgs[i : i + avg_size])

            # --- ЦИКЛ ПУБЛИКАЦИИ ЧАНКОВ ---
            for index, chunk in enumerate(chunks):
                if post_count > 0:
                    print(f"⏳ Ожидание перед следующим постом...")
                    time.sleep(600)

                print(f"🎬 Пост {index + 1}/{len(chunks)}: {store.upper()} -> {category} ({len(chunk)} фото)")
                caption = get_local_caption(store, category)
                
                v_path = video_creator.create_store_video(chunk, f"{store}_{category}_{index}")
                
                if send_media_group(v_path, chunk, caption):
                    print(f"🚀 ПОРЦИЯ ВЫЛОЖЕНА!")
                    if v_path and os.path.exists(v_path): os.remove(v_path)
                    for img in chunk: os.remove(img)
                    post_count += 1
                else:
                    print(f"❌ Ошибка при отправке")

if __name__ == "__main__":
    run_publisher()