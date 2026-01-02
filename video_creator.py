# video_creator.py
import os
from moviepy import ImageClip, CompositeVideoClip, concatenate_videoclips

def create_store_video(image_list, output_name):
    """Создает видео 9:16 для Telegram (MoviePy 2.2.1)"""
    if not image_list or len(image_list) < 4:
        return None

    try:
        processed_clips = []
        target_size = (1080, 1920) 

        for img_path in image_list:
            # Загружаем, ставим 1 сек, подгоняем размер
            clip = ImageClip(img_path).with_duration(1.0).resized(width=target_size[0])
            if clip.h > target_size[1]:
                clip = clip.resized(height=target_size[1])

            # Центрируем на холсте
            centered = CompositeVideoClip([clip.with_position("center")], size=target_size).with_duration(1.0)
            processed_clips.append(centered)

        final_video = concatenate_videoclips(processed_clips, method="compose")
        output_path = f"{output_name}.mp4"
        
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio=False, logger=None)
        
        final_video.close()
        return output_path
    except Exception as e:
        print(f"❌ Ошибка видео: {e}")
        return None