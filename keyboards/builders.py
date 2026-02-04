from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_settings_keyboard(pixel_size: int, strength: float) -> InlineKeyboardMarkup:
    # Кнопки для пикселизации
    pix_up = InlineKeyboardButton(text="Pixels +", callback_data=f"set_pix_{pixel_size + 2}")
    pix_down = InlineKeyboardButton(text="Pixels -", callback_data=f"set_pix_{max(1, pixel_size - 2)}")
    
    # Кнопки для силы нормалей
    str_up = InlineKeyboardButton(text="Strength +", callback_data=f"set_str_{round(strength + 1.0, 1)}")
    str_down = InlineKeyboardButton(text="Strength -", callback_data=f"set_str_{round(max(1.0, strength - 1.0), 1)}")
    
    # Действия
    generate_btn = InlineKeyboardButton(text="✅ Сгенерировать Map", callback_data="generate_final")
    reset_btn = InlineKeyboardButton(text="🔄 Сброс", callback_data="reset_defaults")

    keyboard = [
        [InlineKeyboardButton(text="--- Пикселизация ---", callback_data="ignore")],
        [pix_down, pix_up],
        [InlineKeyboardButton(text="--- Рельеф (Strength) ---", callback_data="ignore")],
        [str_down, str_up],
        [generate_btn],
        [reset_btn]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)