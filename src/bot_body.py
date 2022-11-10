import asyncio
from sys import exit
import sqlite3
from sqlite3 import Error
from random import randint

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BotBlocked
from config import TOKEN, admin_id, database_dir
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db_cards import execute_query, create_connection, add_value, execute_read_query, rows_rows, get_photo_id, get_all_photo_paths, get_all_photo_names_ids, delete_value

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
connection = create_connection(database_dir + "/cards.db")


class StateCards(StatesGroup):
    take_card = State()
    add_card_pic = State()
    add_card_name = State()
    delete_card = State()
    delete_confirm = State()


def get_card_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("Получить карту")
    # b2 = KeyboardButton("test")
    kb.add(b1)
    return kb


def cancel_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("Отменить")
    kb.add(b1)
    return kb


def delete_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton("Точно")
    b2 = KeyboardButton("Отменить")
    kb.add(b1, b2)
    return kb


async def get_card(message: types.Message):
    # await message.answer(text="вот карта", reply_markup=get_card_keyboard())
    count = execute_read_query(connection, get_all_photo_paths())
    if len(count) < 1:
        await message.answer("Карт в базе нет!")
        return
    val = randint(0, len(count)-1)
    photo_id = count[val][0]
    try:
        await message.answer_photo(photo_id, caption=count[val][1])
    except:
        await message.answer(photo_id)


async def process_start_command(message: types.Message, state: FSMContext):
    await message.answer("Привет!\nЧтобы получить случайную карту, нажми на кнопку снизу.", reply_markup=get_card_keyboard())
    await StateCards.take_card.set()
    # await message.answer(text=execute_read_query(connection, rows_rows()))
    # execute_query(connection, add_value("xxxx", "98", "zzzz"))


async def add_new(message: types.Message, state: FSMContext):
    if (admin_id != 0 and admin_id != message.from_id):
        return
    kb = cancel_kb()
    await message.answer("Пожалуйта, пришли изображение карты", reply_markup=kb)
    await StateCards.add_card_pic.set()


async def cansel_pressed(message: types.Message, state: FSMContext):
    await message.answer("действие отменено")
    await message.answer("Чтобы получить случайную карту, нажми на кнопку снизу.", reply_markup=get_card_keyboard())
    await StateCards.take_card.set()


async def handle_photo(message: types.Message, state: FSMContext):
    if (admin_id != 0 and admin_id != message.from_id):
        return
    id_photo = message.photo[-1].file_id
    await state.update_data(id_photo=id_photo)
    await message.answer("Чтобы добавить фото, напиши его название", reply_markup=cancel_kb())
    await StateCards.add_card_name.set()


async def handle_photo_name(message: types.Message, state: FSMContext):
    picName = message.text
    user_data = await state.get_data()
    execute_query(connection, add_value(
        user_data["id_photo"], picName, "zero"))
    await message.answer("Добавлено в базу", reply_markup=get_card_keyboard())
    await StateCards.take_card.set()


async def delete_photo(message: types.Message, state: FSMContext):
    if (admin_id != 0 and admin_id != message.from_id):
        return
    dict = execute_read_query(connection, get_all_photo_names_ids())
    output = []
    for i in range(len(dict)):
        output.append(str(dict[i][0]) + " - " + dict[i][1])
    out = "\n".join(output)
    await message.answer("Вот названия всех карт:\n\n" + out, reply_markup=cancel_kb())
    await message.answer("Введи номер карты, которую хочешь удалить")
    await StateCards.delete_card.set()


async def delete_photo_confirm(message: types.Message, state: FSMContext):
    dict = execute_read_query(connection, get_photo_id(message.text))
    if len(dict) < 1:
        await message.answer("Такого номера нет", reply_markup=cancel_kb())
        return
    id_photo = dict[0][1]
    await state.update_data(delete_id=message.text)
    await message.answer_photo(id_photo, caption=dict[0][0])
    await message.answer("Точно хочешь удалить?", reply_markup=delete_kb())
    await StateCards.delete_confirm.set()


async def finish_delete(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    execute_query(connection, delete_value(user_data['delete_id']))
    await message.answer("Карта успешно удалена")
    await message.answer("Чтобы получить случайную карту, нажми на кнопку снизу.", reply_markup=get_card_keyboard())
    await StateCards.take_card.set()


def inline_register_handlers_booking(dp: Dispatcher):
    dp.register_message_handler(
        process_start_command, commands="start", state="*")
    dp.register_message_handler(
        cansel_pressed, text="Отменить", state="*")
    dp.register_message_handler(
        handle_photo, content_types=['photo'], state=StateCards.take_card)
    dp.register_message_handler(
        handle_photo_name, state=StateCards.add_card_name)
    dp.register_message_handler(
        add_new, commands="add", state=StateCards.take_card)
    dp.register_message_handler(
        get_card, text="Получить карту", state=StateCards.take_card)
    dp.register_message_handler(
        delete_photo, commands="del", state=StateCards.take_card)
    dp.register_message_handler(
        delete_photo_confirm, state=StateCards.delete_card)
    dp.register_message_handler(
        finish_delete, state=StateCards.delete_confirm)


inline_register_handlers_booking(dp)
if __name__ == '__main__':

    executor.start_polling(dp)
