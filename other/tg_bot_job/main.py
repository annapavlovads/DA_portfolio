import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import Config, load_config
from config_data.set_menu import set_main_menu
from handlers import menu_handlers, application_form_handlers


async def main() -> None:
    '''
    main couroutine
    '''
    
    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    await set_main_menu(bot)
    
    dp.include_router(menu_handlers.router)
    dp.include_router(application_form_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    #  logging.basicConfig(level=logging.ERROR, filename='logs.py') - включить на проде
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
