from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
from aiogram.exceptions import TelegramBadRequest

from utils.states import GenStates
from utils.texts import BotMessages
from keyboards.builders import get_settings_keyboard
from services.processing import process_full_pipeline

router = Router()

# Стандартные значения
DEFAULT_PIXEL = 1
DEFAULT_STRENGTH = 5.0

@router.message(F.photo)
async def handle_photo(message: types.Message, state: FSMContext, bot: Bot):
    # Получаем самое большое фото
    photo = message.photo[-1]
    
    # Скачиваем файл в память
    file_io = await bot.download(photo)
    image_bytes = file_io.read()
    
    # Сохраняем байты и дефолтные настройки в FSM
    await state.update_data(
        image=image_bytes,
        pixel_size=DEFAULT_PIXEL,
        strength=DEFAULT_STRENGTH
    )
    
    # Показываем меню настроек
    await message.answer(
        text=BotMessages.settings_caption(DEFAULT_PIXEL, DEFAULT_STRENGTH),
        reply_markup=get_settings_keyboard(DEFAULT_PIXEL, DEFAULT_STRENGTH)
    )
    # Явно устанавливаем состояние
    await state.set_state(GenStates.adjusting_settings)

@router.message(F.document)
async def handle_document(message: types.Message, state: FSMContext, bot: Bot):
    if message.document.mime_type and "image" in message.document.mime_type:
        file_io = await bot.download(message.document)
        image_bytes = file_io.read()
        
        await state.update_data(
            image=image_bytes,
            pixel_size=DEFAULT_PIXEL,
            strength=DEFAULT_STRENGTH
        )
        await message.answer(
            text=BotMessages.settings_caption(DEFAULT_PIXEL, DEFAULT_STRENGTH),
            reply_markup=get_settings_keyboard(DEFAULT_PIXEL, DEFAULT_STRENGTH)
        )
        await state.set_state(GenStates.adjusting_settings)
    else:
        await message.answer(BotMessages.ERROR_NO_PHOTO)

# --- CALLBACKS ДЛЯ НАСТРОЕК ---

# Убрали жесткий фильтр состояния GenStates.adjusting_settings, 
# чтобы кнопки работали даже после перезагрузки бота
@router.callback_query(F.data.startswith("set_"))
async def adjust_params(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Защита от потери данных при перезагрузке бота
    current_pixel = data.get('pixel_size', DEFAULT_PIXEL)
    current_strength = data.get('strength', DEFAULT_STRENGTH)
    
    action, value = callback.data.split("_")[1], callback.data.split("_")[2]
    
    pixel_size = current_pixel
    strength = current_strength

    if action == "pix":
        pixel_size = int(value)
        await state.update_data(pixel_size=pixel_size)
    elif action == "str":
        strength = float(value)
        await state.update_data(strength=strength)

    # Восстанавливаем состояние, чтобы FSM знал, где мы
    await state.set_state(GenStates.adjusting_settings)

    # Оборачиваем в try-except, чтобы игнорировать ошибку "message not modified"
    try:
        await callback.message.edit_text(
            text=BotMessages.settings_caption(pixel_size, strength),
            reply_markup=get_settings_keyboard(pixel_size, strength)
        )
    except TelegramBadRequest:
        pass # Ничего не делаем, если текст не изменился
        
    await callback.answer()

@router.callback_query(F.data == "reset_defaults")
async def reset_params(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(pixel_size=DEFAULT_PIXEL, strength=DEFAULT_STRENGTH)
    await state.set_state(GenStates.adjusting_settings)
    
    try:
        await callback.message.edit_text(
            text=BotMessages.settings_caption(DEFAULT_PIXEL, DEFAULT_STRENGTH),
            reply_markup=get_settings_keyboard(DEFAULT_PIXEL, DEFAULT_STRENGTH)
        )
    except TelegramBadRequest:
        pass
        
    await callback.answer("Настройки сброшены")

@router.callback_query(F.data == "generate_final")
async def generate_result(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Если бот перезагрузился, картинки в памяти нет
    if 'image' not in data:
        await callback.answer("⚠️ Данные устарели. Отправьте фото заново.", show_alert=True)
        return

    # Убираем кнопки, чтобы пользователь не нажал дважды
    try:
        await callback.message.edit_reply_markup(reply_markup=None) 
    except TelegramBadRequest:
        pass
    
    await callback.message.answer(BotMessages.get_processing_text())
    
    image_bytes = data['image']
    pixel_size = data['pixel_size']
    strength = data['strength']
    
    try:
        # Получаем КОРТЕЖ из двух файлов (см. изменения в processing.py)
        texture_bytes, normal_bytes = process_full_pipeline(image_bytes, pixel_size, strength)
        
        # 1. Отправляем текстуру (если была пикселизация или просто как исходник)
        if pixel_size > 1:
            tex_file = BufferedInputFile(texture_bytes, filename=f"Texture_Pixelated_x{pixel_size}.png")
            await callback.message.answer_document(
                document=tex_file,
                caption=f"🎨 **Текстура (Albedo)**\nПикселизация: x{pixel_size}"
            )
        
        # 2. Отправляем карту нормалей
        norm_file = BufferedInputFile(normal_bytes, filename=f"NormalMap_s{int(strength)}.png")
        await callback.message.answer_document(
            document=norm_file,
            caption=f"🔮 **Normal Map**\nСила: {strength}\n_(Подходит к текстуре выше)_"
        )
        
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при обработке: {str(e)}")
        
    # Очищаем память
    await state.clear()
    await callback.answer()