import asyncio
from aiogram import Bot, Dispatcher

from common.logs import LogConfig
from common.config import load_config

from bot.handlers.cmd_handlers import cmd_router


# Настройка логирования
logger = LogConfig.setup_logging()
# Загрузка конфигурации
config = load_config()

# Создание бота и диспетчера
bot = Bot(token=config.bot.api_key)  # noqa
dp = Dispatcher()


# Асинхронная функция для запуска бота
async def main():
    dp.include_router(cmd_router)
    await dp.start_polling(bot)


# Запуск бота
if __name__ == '__main__':
    try:
        logger.info('Starting bot..')
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot stopped')
