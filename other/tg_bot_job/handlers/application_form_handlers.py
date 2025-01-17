from typing import Union

from datetime import datetime
from aiogram import Router
from aiogram import types, F

from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from config_data.config import GROUP_CHAT_ID
from fs_machine.fsm import FSMApplication
from custom_filters.filters import PhoneNumberFilter, TextFieldFilter

router = Router()
data_dict: dict[int, dict[str, str | int | bool]] = {}


@router.callback_query(F.data == 'see_contacts')
async def see_contacts(query: types.CallbackQuery) -> None:
    '''
    Показывает контакты службы персонала
    '''
    await query.message.answer('Контактные телефоны службы персонала:\n +79990615866 \n+79311015158')


@router.callback_query(F.data == 'send_application', StateFilter(FSMApplication.begin_application))
async def get_vacancy(query: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Отвечает на сообщение по кнопке о вакансиях и поиске работы
    '''
    data_dict[query.from_user.id] = {'vacancy': None,
                                     'city': None,
                                     'metro': '-',
                                     'experience': None,
                                     'when_start': None,
                                     'permission': None,
                                     'mob_phone': None,
                                     'name': None,
                                     'tg_username': query.from_user.username,
                                     'date_time': None}

    kb = [
        [
            types.InlineKeyboardButton(text="Официант", callback_data="Официант"),
            types.InlineKeyboardButton(text="Повар", callback_data="Повар"),
            types.InlineKeyboardButton(text="Курьер", callback_data="Курьер")
            ],
        [
            types.InlineKeyboardButton(text="Бармен", callback_data="Бармен"),
            types.InlineKeyboardButton(text="Хостес", callback_data="Хостес"),
            types.InlineKeyboardButton(text="Су-шеф", callback_data="Су-шеф")
            ],
        [
         
            types.InlineKeyboardButton(text="Менеджер доставки", callback_data="Менеджер доставки"),
            types.InlineKeyboardButton(text="Мойщик/ца посуды", callback_data="Мойщик/ца посуды")
            ]
        ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await query.message.answer("Выберите вакансию",
                               reply_markup=keyboard)
    await state.set_state(FSMApplication.fill_city)


@router.callback_query(StateFilter(FSMApplication.fill_city))
async def get_city(query: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Появляется после выбора вакансии, заполняется город
    '''

    data_dict[query.from_user.id]['vacancy'] = query.data

    kb = [
        [types.InlineKeyboardButton(text="С-Петербург", callback_data="С-Петербург"),
         types.InlineKeyboardButton(text="Новоселье", callback_data='Новоселье'),
         types.InlineKeyboardButton(text="Всеволожск", callback_data='Всеволожск'), 
         types.InlineKeyboardButton(text="Гатчина", callback_data='Гатчина')], 
        [types.InlineKeyboardButton(text="Мурино", callback_data='Мурино'),
         types.InlineKeyboardButton(text="Кудрово", callback_data='Кудрово'),
         types.InlineKeyboardButton(text="В.Новгород", callback_data='В.Новгород'),
         types.InlineKeyboardButton(text="Псков", callback_data='Псков')]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await query.message.answer(f"Вы выбрали вакансию {query.data}. Выберите город",
                               reply_markup=keyboard)
    await state.set_state(FSMApplication.fill_experience)


@router.callback_query(F.data == 'С-Петербург', StateFilter(FSMApplication.fill_experience))
async def get_metro_station(query: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Отвечает на сообщение по кнопке c выбором города С-Петербург
    '''

    data_dict[query.from_user.id]['city'] = query.data

    await query.message.answer("Укажите удобную станцию метро")
    await state.set_state(FSMApplication.fill_metro)


@router.message(F.content_type == types.ContentType.TEXT, ~TextFieldFilter(), StateFilter(FSMApplication.fill_metro))
async def handle_incorrect_name(message: types.Message, state: FSMContext) -> None:
    '''
    Отвечает на некорректное название станции метро
    '''
    await message.answer("Укажите корректное название станции метро")


@router.message(F.content_type == types.ContentType.TEXT, TextFieldFilter(), StateFilter(FSMApplication.fill_metro))
@router.callback_query(StateFilter(FSMApplication.fill_experience))
async def get_expirience(mess: Union[types.CallbackQuery, types.Message], state: FSMContext) -> None:
    '''
    Отвечает на сообщение по кнопке c выбором города-спутника или станции метро
    '''
    kb = [
        [types.InlineKeyboardButton(text="Нет опыта", callback_data="Нет опыта"), 
         types.InlineKeyboardButton(text="1-3 года", callback_data="1-3 года"), 
         types.InlineKeyboardButton(text="Более 3 лет", callback_data="Более 3 лет")]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    reply = "Укажите свой опыт работы в этой сфере"

    if isinstance(mess, types.Message):
        data_dict[mess.from_user.id]['metro'] = mess.text
        await mess.answer(reply, reply_markup=keyboard)
    elif isinstance(mess, types.CallbackQuery):
        data_dict[mess.from_user.id]['city'] = mess.data
        await mess.message.answer(reply, reply_markup=keyboard)

    await state.set_state(FSMApplication.fill_permission)


@router.callback_query(F.data == 'Нет опыта', StateFilter(FSMApplication.fill_permission))
@router.callback_query(F.data == '1-3 года', StateFilter(FSMApplication.fill_permission))
@router.callback_query(F.data == 'Более 3 лет', StateFilter(FSMApplication.fill_permission))
async def get_permission(query: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Отвечает на сообщение по кнопке c выбором опыта работы, узнает разрешение/гражданство
    '''
    data_dict[query.from_user.id]['experience'] = query.data

    kb = [
        [types.InlineKeyboardButton(text="Да", callback_data='Да'), 
         types.InlineKeyboardButton(text="Нет", callback_data='Нет')],
        [types.InlineKeyboardButton(text="Не требуется (гражданство РФ)", callback_data='Не требуется (гражданство РФ)')]
        ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    await query.message.answer("Есть ли у вас разрешение на работу?",
                               reply_markup=keyboard)
    await state.set_state(FSMApplication.fill_when_start)


@router.callback_query(F.data == 'Да', StateFilter(FSMApplication.fill_when_start))
@router.callback_query(F.data == 'Нет', StateFilter(FSMApplication.fill_when_start))
@router.callback_query(F.data == 'Не требуется (гражданство РФ)', StateFilter(FSMApplication.fill_when_start))
async def get_time_to_start(query: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Отвечает на сообщение по кнопке c выбором разрешения на работу, 
    узнает срок выхода на работу
    '''
    data_dict[query.from_user.id]['permission'] = query.data

    kb = [
        [
            types.InlineKeyboardButton(text="Завтра", callback_data='Завтра'),
            types.InlineKeyboardButton(text="Через 2 недели", callback_data='Через 2 недели')
            ],
        [
            types.InlineKeyboardButton(text="Через месяц и более", callback_data='Через месяц и более')
            ]
        ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

    await query.message.answer("Когда вы готовы приступить к работе?", 
                       reply_markup=keyboard)
    await state.set_state(FSMApplication.fill_name)


@router.callback_query(F.data == 'Завтра', StateFilter(FSMApplication.fill_name))
@router.callback_query(F.data == 'Через 2 недели', StateFilter(FSMApplication.fill_name))
@router.callback_query(F.data == 'Через месяц и более', StateFilter(FSMApplication.fill_name))
async def get_name(query: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Отвечает на сообщение по кнопке c указанием срока выхода на работу,
    '''
    data_dict[query.from_user.id]['when_start'] = query.data
    await query.message.answer("Как вас зовут?")
    await state.set_state(FSMApplication.fill_mob_phone)


@router.message((F.content_type == types.ContentType.TEXT), TextFieldFilter(), StateFilter(FSMApplication.fill_mob_phone))
async def get_contact(message: types.Message, state: FSMContext) -> None:
    '''
    Отвечает на сообщение по кнопке c указанием имени
    '''
    data_dict[message.from_user.id]['name'] = message.text

    kb = [[types.KeyboardButton(text='Прикрепить контакт Telegram', request_contact=True)]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Укажите контактный номер телефона",
                               reply_markup=keyboard)
    await state.set_state(FSMApplication.finish_application)


@router.message((F.content_type == types.ContentType.TEXT), ~TextFieldFilter(), StateFilter(FSMApplication.fill_mob_phone))
async def handle_incorrect_name(message: types.Message, state: FSMContext) -> None:
    '''
    Отвечает на сообщение по кнопке c указанием имени
    '''
    await message.answer("Укажите корректное имя")
    await state.set_state(FSMApplication.fill_mob_phone)


@router.message((F.content_type == types.ContentType.TEXT), PhoneNumberFilter(), StateFilter(FSMApplication.finish_application))
@router.message(F.contact, StateFilter(FSMApplication.finish_application))
async def handle_contact(message: types.Message, state: FSMContext):
    '''
    Отвечает на отправленный контакт Телеграм
    '''
    if message.contact:
        data_dict[message.from_user.id]['mob_phone'] = message.contact.phone_number
    elif message.text: 
        data_dict[message.from_user.id]['mob_phone'] = message.text

    chat_id = GROUP_CHAT_ID

    data_dict[message.from_user.id]['date_time'] = datetime.now().strftime("%d.%m.%Y %H:%M")

    message_to_chat = f'''
    Новый отклик на вакансию: {data_dict[message.from_user.id]['vacancy']}
    Город: {data_dict[message.from_user.id]['city']}
    Станция метро: {data_dict[message.from_user.id]['metro']}
    Опыт работы: {data_dict[message.from_user.id]['experience']}
    Разрешение на работу: {data_dict[message.from_user.id]['permission']}
    Когда готов приступить: {data_dict[message.from_user.id]['when_start']}
    Имя: {data_dict[message.from_user.id]['name']}
    Контактный телефон: {data_dict[message.from_user.id]['mob_phone']}
    Пользователь Телеграм: @{data_dict[message.from_user.id]['tg_username']}
    Дата и время отклика: {data_dict[message.from_user.id]['date_time']}
'''

    await message.bot.send_message(chat_id, message_to_chat)
    await message.answer("Ваш отклик успешно отправлен!", reply_markup=types.ReplyKeyboardRemove())
    await message.answer_sticker(
        sticker='CAACAgIAAxkBAAELfvBngQbkrmqGzHzlSTPesjasX3fVAAN0DgACBpZISn-DqUbWeMMMNgQ'
        )
    await message.answer("Мы свяжемся с вами в ближайшее время!")
    await state.set_state(default_state)


@router.message((F.content_type == types.ContentType.TEXT), ~PhoneNumberFilter(), StateFilter(FSMApplication.finish_application))
async def incorrect_phone(message: types.Message, state: FSMContext):
    '''
    Отвечает на некорректный номер телефона
    '''

    kb = [[types.KeyboardButton(text='Прикрепить контакт Telegram', request_contact=True)]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Укажите корректный номер телефона или прикрепите контакт Телеграм",
                               reply_markup=keyboard)
    await state.set_state(FSMApplication.finish_application)


@router.message(StateFilter(default_state))
@router.message(StateFilter(FSMApplication.begin_application))
async def text_row_in_the_beginning(message: types.Message) -> None:
    '''
    Обрабатывает ввод текста в состоянии по умолчанию (не начато заполнение анкеты)
    '''
    await message.answer(
        'Нажмите кнопку "Откликнуться на вакансию" для того, чтобы заполнить анкету',
        )


@router.message(StateFilter(FSMApplication.fill_city))
@router.message(StateFilter(FSMApplication.fill_experience))
@router.message(StateFilter(FSMApplication.fill_permission))
@router.message(StateFilter(FSMApplication.fill_when_start))
@router.message(StateFilter(FSMApplication.fill_name))
async def text_row_when_waiting_button(message: types.Message) -> None:
    '''
    Обрабатывает ввод текста в процессе заполнения анкеты, где ожидается нажатие на кнопку
    '''
    await message.answer(
        'Нажмите одну из кнопок выше, чтобы продолжить заполнение анкеты'
        )