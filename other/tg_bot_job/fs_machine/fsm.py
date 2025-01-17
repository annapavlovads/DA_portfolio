from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

class FSMApplication(StatesGroup):
    begin_application = State()
    fill_city = State()
    fill_metro = State()
    fill_experience = State()
    fill_permission = State()
    fill_when_start = State()
    fill_name = State()
    fill_mob_phone = State()
    finish_application = State()