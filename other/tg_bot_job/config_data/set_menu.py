
from aiogram import Bot
from aiogram.types import BotCommand


COMMAND_LIST: dict[str, str] = {
    '/start': 'Запустить бота и оставить отклик',
    '/help': 'Помощь по работе с ботом',
    '/contacts': 'Контакты службы персонала'
}


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in COMMAND_LIST.items()
    ]
    await bot.set_my_commands(main_menu_commands)