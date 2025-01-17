from aiogram import types
from aiogram.filters import BaseFilter


class PhoneNumberFilter(BaseFilter):

    async def __call__(self, message: types.Message) -> bool:
        if message.text:
            phone_number = message.text
            if len(phone_number) >= 10 and len(phone_number) <= 17:
                if all(char.isdigit() or char in '-()+' for char in phone_number):
                    return True
        return False


class TextFieldFilter(BaseFilter):

    async def __call__(self, message: types.Message) -> bool:
        if len(message.text)<=100 and all(char.isalpha() or char.isspace() or char in '.,-' for char in message.text):
            return True
        return False
