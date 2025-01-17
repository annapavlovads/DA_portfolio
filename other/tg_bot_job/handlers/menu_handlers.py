from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram import types
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from fs_machine.fsm import FSMApplication

router = Router()


@router.message(Command(commands=['start']))
async def process_start_command(message: types.Message, state: FSMContext) -> None:
    '''
    Обрабатывает команду /start
    '''
    kb = [
        [types.InlineKeyboardButton(text="Откликнуться на вакансию", 
                                    callback_data="send_application")],
        [types.InlineKeyboardButton(text="Контакты службы персонала", 
                                    callback_data="see_contacts")]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await message.answer(
        f'Добрый день, {hbold(message.from_user.full_name)}!\n'+
        'Оставьте отклик на вакансии в ресторанах "ПхалиХинкали" и "Хачо и Пури"!',
        reply_markup=keyboard
        )
    await state.set_state(FSMApplication.begin_application)


@router.message(Command(commands='help'))
async def process_help_command(message: types.Message) -> None:
    '''
    Обработка команды /help
    '''
    await message.answer(
        'Это бот для откликов на вакансии. Чтобы откликнуться, запустите бота с помощью команды /start'
        )

@router.message(Command(commands='contacts'))
async def process_contacts_command(message: types.Message) -> None:
    '''
    Обработка команды /contacts
    '''
    await message.answer(
        'Контактные телефоны службы персонала:\n +79990615866 \n+79311015158'
        )
