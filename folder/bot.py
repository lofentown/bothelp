import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import ChatNotFound
import asyncio
from fastapi import FastAPI
from uvicorn import run

from settings import bot_settings
from bot_menu import menu
import orm

logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello, World!"}

 #Состояния
class Form(StatesGroup):
    waiting_message = State()

class Mailing(StatesGroup):
    text = State()
    entity = State()

class Support(StatesGroup):
    waiting_for_message = State()
    waiting_for_reply = State()
    #для кнопки в админ меню
    waiting_for_user_id = State()


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Перезапустить бота'),
        ]
    )

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    text = f'Приветствуем Вас, *{message.from_user.first_name}*!\n\nНаш бот поможет разобраться в проблеме, связанной с ИИ ботом!\n Главное меню:'
    inline_markup = await menu.main_menu()
    response = orm.add_user(message.from_user.id, message.from_user.username)
    username = message.from_user.username
    if response == 1:
        users = orm.get_admins()
        for user in users:
                if message.from_user.username == None:
                    await bot.send_message(user.tg_id, text=f'Пользователь <a href="tg://user?id={message.from_user.id}">@{message.from_user.first_name}</a> присоединился', parse_mode='HTML')
                elif message.from_user.username != None:
                    await bot.send_message(user.tg_id, text=f'Пользователь <a href="tg://user?id={message.from_user.id}">@{username}</a> присоединился', parse_mode='HTML')
                else:
                   await bot.send_message(user.tg_id, text=f'Пользователь <a href="tg://user?id={message.from_user.id}">@{username}</a> присоединился', parse_mode='HTML')

    await message.answer(text, reply_markup=inline_markup, parse_mode='Markdown')
    await set_default_commands(dp)

@dp.message_handler(lambda message: orm.check_admin(message.from_user.id) == 1 and message.text == '/admin')
async def get_admin_menu(message: types.Message):
    text = 'Выберите необходимое действие'
    inline_markup = await menu.admin_menu()
    await message.answer(text, reply_markup=inline_markup)

@dp.callback_query_handler(lambda c: c.data == 'answer')
async def handle_reply_button(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Введите ID пользователя для ответа:")
    await Support.waiting_for_user_id.set()

@dp.message_handler(state=Support.waiting_for_user_id)
async def get_user_id(message: types.Message, state: FSMContext):
    user_id = message.text
    try:
        user_id = int(user_id)  # Проверяем, что это целое число
        await state.update_data(user_id=user_id)
        await message.answer(f"Вы выбрали ID: {user_id}. Теперь введите ваш ответ для пользователя.")
        await Support.waiting_for_reply.set()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID пользователя.")

@dp.callback_query_handler(lambda c: c.data == 'help')
async def handle_reply_button(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Введите описание вашей проблемы:")
    await Support.waiting_for_message.set()

@dp.message_handler(state=Support.waiting_for_message)
async def receive_problem(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Пользователь"
    username = f"@{message.from_user.username}" if message.from_user.username else "нет имени пользователя"

    # Клавиатура с кнопкой "Ответить", содержащей ID пользователя
    reply_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Ответить", callback_data=f"reply:{user_id}")
    )
    users = orm.get_admins()
    for user in users:
        try:
            await bot.send_message(
                chat_id=user.tg_id,
                text=f"ID пользователя: {user_id}. Сообщение от {user_name} ({username}):\n\n{message.text}",
                reply_markup=reply_markup
            )
        except ChatNotFound:
            print(f"Чат с пользователем {user.tg_id} не найден.")
        except Exception as e:
            print(f"Ошибка отправки сообщения пользователю {user.tg_id}: {e}")

    orm.add_problem(user_id, message.text)
    await message.answer("Ваше сообщение отправлено в техподдержку. Ожидайте ответа!")
    await state.finish()

# Обработка кнопки "Ответить" с привязкой к пользователю
@dp.callback_query_handler(lambda c: c.data.startswith("reply"))
async def handle_reply_button(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.data.split(":")[1]  # Извлекаем ID пользователя из callback data
    await state.update_data(user_id=user_id)
    await callback_query.message.answer("Введите ваш ответ пользователю:")
    await Support.waiting_for_reply.set()

# Отправка ответа пользователю
@dp.message_handler(state=Support.waiting_for_reply)
async def send_reply(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data.get("user_id")

    if not user_id:
        await message.answer("Ошибка: не найден ID пользователя для ответа.")
        await state.finish()
        return

    try:
        # Отправляем сообщение пользователю
        await bot.send_message(chat_id=user_id, text=f"Ответ техподдержки:\n\n{message.text}")
        await message.answer("Ответ успешно отправлен.")
    except Exception as e:
        await message.answer(f"Ошибка при отправке ответа: {str(e)}")
    finally:
        await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'create_mailing')
async def create_mailing(callback_query: types.CallbackQuery):
    text = 'Введите текст, который хотите разослать'
    await bot.send_message(callback_query.from_user.id, text, parse_mode='Markdown')
    await Mailing.text.set()


@dp.message_handler(state=Mailing.text)
async def mailing(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text, entity=message.entities)
    state_data = await state.get_data()
    text = state_data.get('text')
    entity = state_data.get('entity')
    users = orm.get_all_users()
    await message.answer('Начинаю рассылку', parse_mode='Markdown')
    count = 0
    count_of_banned = 0
    for user in users:
        try:
            await bot.send_message(user.tg_id, text=text, entities=entity, disable_web_page_preview=True)
            count += 1
            if count == 15:
                await asyncio.sleep(5)
                count = 0
        except:
            count_of_banned += 1
    answer = f'Отправка рыссылки завершена\nВсего пользователей: {len(users)}\nОтправлено успешно: {len(users)-count_of_banned}\nУдалили чат с ботом: {count_of_banned}'
    orm.add_blocked(count_of_banned)
    await message.answer(answer, parse_mode='Markdown')
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == 'information')
async def exit(message: types.Message):
    text = f'''🌟 <b>Описание бота техподдержки</b> 🌟  

Наш бот техподдержки 📩 предназначен для пользователей бота <b>Терапия</b>, столкнувшихся с проблемами. Когда у вас возникает вопрос или неполадка, просто отправьте сообщение боту с описанием проблемы. 🚀  

🔄 <b>Как это работает:</b>  
1️⃣ Вы отправляете сообщение о возникшей проблеме. 📝  
2️⃣ Специалист техподдержки получает ваш запрос и оперативно его обрабатывает. 🛠  
3️⃣ После анализа вы получите обратную связь 📬, включая объяснение причины проблемы. ✅  

🎯 Этот бот создан для обеспечения быстрого и удобного решения ваших вопросов! 🕒✨'''
    inline_markup = await menu.main_menu()
    await bot.send_message(message.from_user.id, text, reply_markup=inline_markup, parse_mode='HTML')

@dp.callback_query_handler(lambda c: c.data == 'spisok')
async def handle_reply_button(callback_query: types.CallbackQuery):
    zadaniya = orm.get_all_users()
    for zadanie in zadaniya:
        username = f"@{zadanie.username}" if zadanie.username else "нет имени пользователя"
        await callback_query.message.answer(f"У пользователя с ID: {zadanie.tg_id} {username} была проблема: {zadanie.problem_text}")


@dp.callback_query_handler(lambda c: c.data == 'menu')
async def exit(message: types.Message):
    text = 'Главное меню:'
    inline_markup = await menu.main_menu()
    await bot.send_message(message.from_user.id, text, reply_markup=inline_markup)

@app.get("/bot_status")
async def bot_status():
    return {"status": "running", "bot_name": "TherapyBot"}

# Функция запуска FastAPI
def start_fastapi():
    run(app, host="0.0.0.0", port=8000)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
