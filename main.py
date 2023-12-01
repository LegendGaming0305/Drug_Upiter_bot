from aiogram import Bot, Dispatcher, executor
from config import API_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

async def on_startup(_):
    print('Бот запущен!')

async def on_shutdown(_):
    print('Бот выключен!')

if __name__ == '__main__':
    from new_handlers import dp
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)