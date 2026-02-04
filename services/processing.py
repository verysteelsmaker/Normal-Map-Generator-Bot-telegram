import numpy as np
from PIL import Image
import io

def process_pixelation(image_bytes: bytes, pixel_size: int) -> Image.Image:
    """Пикселизирует изображение: уменьшает и резко увеличивает обратно."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    if pixel_size <= 1:
        return img

    w, h = img.size
    # Уменьшаем (Nearest Neighbor для сохранения жестких краев)
    small_img = img.resize((w // pixel_size, h // pixel_size), Image.Resampling.NEAREST)
    # Увеличиваем обратно
    result = small_img.resize((w, h), Image.Resampling.NEAREST)
    return result

def image_to_bytes(img: Image.Image) -> bytes:
    """Вспомогательная функция: сохраняет PIL Image в байты."""
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output.getvalue()

def generate_normal_map(img: Image.Image, strength: float = 2.0) -> bytes:
    """Генерирует Normal Map из изображения (принимает PIL Image)."""
    # Конвертируем в оттенки серого (карта высот)
    gray = np.array(img.convert("L")).astype(np.float64)

    # Вычисляем градиенты
    gradients = np.gradient(gray)
    dy = gradients[0] * strength
    dx = gradients[1] * strength

    dz = np.ones_like(dx) * 255.0 / strength 
    norm = np.dstack((dx, -dy, dz)) 

    norm_len = np.sqrt(np.sum(norm**2, axis=2))
    norm = norm / np.dstack([norm_len]*3)

    norm = (norm + 1.0) / 2.0 * 255.0
    norm = norm.astype(np.uint8)

    normal_map_img = Image.fromarray(norm, 'RGB')
    return image_to_bytes(normal_map_img)

def process_full_pipeline(image_bytes: bytes, pixel_size: int, strength: float):
    """
    Полный цикл.
    Возвращает КОРТЕЖ: (байты_картинки, байты_нормалей)
    """
    # 1. Делаем пикселизацию
    processed_img = process_pixelation(image_bytes, pixel_size)
    
    # 2. Сохраняем пикселизированную картинку в байты
    processed_img_bytes = image_to_bytes(processed_img)
    
    # 3. Генерируем нормали на основе этой (уже пикселизированной) картинки
    normal_map_bytes = generate_normal_map(processed_img, strength)
    
    return processed_img_bytes, normal_map_bytes