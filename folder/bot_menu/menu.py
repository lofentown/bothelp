from aiogram import types

async def main_menu():
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton(
            text='📖Описание бота📖',
            callback_data='information'
        ))
    inline_markup.add(types.InlineKeyboardButton(
            text='❗️Сообщить о проблеме❗️',
            callback_data='help'
        ))
    return inline_markup

async def admin_menu():
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton(
            text='Отправить ответ',
            callback_data='answer'
        ))
    inline_markup.add(types.InlineKeyboardButton(
            text='Получить список нерешенных проблем',
            callback_data='spisok'
        ))
    inline_markup.add(types.InlineKeyboardButton(
            text='Создать рассылку',
            callback_data='create_mailing'
        ))
    inline_markup.add(types.InlineKeyboardButton(
            text='Вернуться в обычное меню',
            callback_data='menu'
        ))
    return inline_markup



