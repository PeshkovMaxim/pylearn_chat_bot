import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
import os

from config_reader import config
from imageai.Detection import ObjectDetection

detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath("yolo.h5")
detector.loadModel()

# Объект бота
bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Этот бот возвращает изображение с распознанными объектами")


@dp.message(content_types="photo")
async def download_photo(message: types.Message, bot: Bot):
    await bot.download(message.photo[-1], destination=f"images/{message.photo[-1].file_id}.jpg")
    # распознавание объектов и сохранение файла
    detections = detector.detectObjectsFromImage(input_image=f"images/{message.photo[-1].file_id}.jpg",
                                                 output_image_path=f"images/new_{message.photo[-1].file_id}.jpg",
                                                 minimum_percentage_probability=30)
    photo = FSInputFile(f"images/new_{message.photo[-1].file_id}.jpg", filename='file')
    print(message.chat.id)
    # отправка обработанного фото
    await bot.send_photo(chat_id=message.chat.id, photo=photo)
    # удаление фото из файловой системы
    os.remove(f"images/new_{message.photo[-1].file_id}.jpg")
    os.remove(f"images/{message.photo[-1].file_id}.jpg")



# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
