import logging
import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BLOCKS = [{'id': 231, 'type': 'start', 'title': 'Старт', 'content': '', 'buttons': [], 'fields': [], 'outgoing': [232]}, {'id': 232, 'type': 'message', 'title': 'Сообщение', 'content': 'привет', 'buttons': [], 'fields': [], 'outgoing': [233]}, {'id': 233, 'type': 'menu', 'title': 'Меню', 'content': 'это меню', 'buttons': [{'text': 'сбор данных', 'target_block': 234}, {'text': 'сообщение', 'target_block': 238}], 'fields': [], 'outgoing': []}, {'id': 234, 'type': 'data_capture', 'title': 'Сбор данных', 'content': '', 'buttons': [{'text': 'назад', 'target_block': 233}, {'text': 'сообщение', 'target_block': 235}], 'fields': ['email', 'birth_date', 'username', 'gender', 'phone'], 'outgoing': []}, {'id': 235, 'type': 'message', 'title': 'Сообщение', 'content': 'пока', 'buttons': [], 'fields': [], 'outgoing': [236]}, {'id': 236, 'type': 'message', 'title': 'Сообщение', 'content': 'или не пока', 'buttons': [], 'fields': [], 'outgoing': [237]}, {'id': 237, 'type': 'message', 'title': 'Сообщение', 'content': 'пока)', 'buttons': [], 'fields': [], 'outgoing': []}, {'id': 238, 'type': 'message', 'title': 'Сообщение', 'content': 'дальше', 'buttons': [], 'fields': [], 'outgoing': [235]}]
START_BLOCK_ID = 231

block_map = {b["id"]: b for b in BLOCKS}
user_states = {}
user_data = {}

bot = Bot(token="token")
dp = Dispatcher(storage=MemoryStorage())

class DataCapture(StatesGroup):
    filling = State()

def get_next_block_id(current_id, user_input):
    block = block_map.get(current_id)
    if not block:
        return None

    if block["type"] in ["menu", "data_capture"]:
        for btn in block.get("buttons", []):
            if btn["text"].strip().lower() == user_input.strip().lower():
                return btn.get("target_block")

    if block.get("outgoing"):
        return block["outgoing"][0]

    return None

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_states[user_id] = START_BLOCK_ID
    user_data[user_id] = {}
    await handle_block(message, START_BLOCK_ID, state)

async def handle_block(message: types.Message, block_id: int, state: FSMContext):
    block = block_map.get(block_id)
    if not block:
        await message.answer("Ошибка: блок не найден.")
        return

    user_id = message.from_user.id
    user_states[user_id] = block_id

    if block["type"] == "start":
        next_id = get_next_block_id(block_id, "")
        if next_id:
            await handle_block(message, next_id, state)
        return

    elif block["type"] == "message":
        text = block.get("content", "").strip()
        if text:
            await message.answer(text)
        next_id = get_next_block_id(block_id, "")
        if next_id:
            await handle_block(message, next_id, state)

    elif block["type"] == "menu":
        text = block.get("content", "").strip()
        buttons = block.get("buttons", [])
        kb = ReplyKeyboardBuilder()
        for btn in buttons:
            kb.add(KeyboardButton(text=btn["text"]))
        await message.answer(text or "Выберите:", reply_markup=kb.as_markup(resize_keyboard=True))

    elif block["type"] == "data_capture":
        await state.set_state(DataCapture.filling)
        await send_data_capture_menu(message, block, user_data.get(user_id, {}), state)

async def send_data_capture_menu(message, block, collected_data, state: FSMContext):
    fields = block["fields"]
    if "email" in fields:
        fields = ["email"] + [f for f in fields if f != "email"]
    remaining_fields = [f for f in fields if f not in collected_data]

    kb = ReplyKeyboardBuilder()

    if not remaining_fields:
        await state.clear()
        for btn in block.get("buttons", []):
            kb.add(KeyboardButton(text=btn["text"]))
        await message.answer("Выберите дальнейшее действие:", reply_markup=kb.as_markup(resize_keyboard=True))
        return

    field_names = {
        "email": "Email",
        "birth_date": "Дата рождения",
        "username": "Имя и фамилия",
        "gender": "Пол",
        "phone": "Телефон"
    }
    for field in remaining_fields:
        kb.add(KeyboardButton(text=field_names.get(field, field)))

    await message.answer("Пожалуйста, выберите поле для ввода:", reply_markup=kb.as_markup(resize_keyboard=True))

@dp.message()
async def handle_all_messages(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    current_state = await state.get_state()

    if current_state == DataCapture.filling.state:
        field = data.get("current_field")
        if not field:
            field_map = {
                "email": "email",
                "дата рождения": "birth_date",
                "имя и фамилия": "username",
                "пол": "gender",
                "телефон": "phone"
            }
            text = message.text.strip().lower()
            field = field_map.get(text)
            if not field or field not in block_map[user_states[user_id]]["fields"]:
                await message.answer("Выберите поле из предложенного списка.")
                return
            await state.update_data(current_field=field)
            if field == "gender":
                kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="М")], [KeyboardButton(text="Ж")]], resize_keyboard=True)
                await message.answer("Выберите пол:", reply_markup=kb)
            else:
                await message.answer(f"Введите значение для: {text.capitalize()}", reply_markup=ReplyKeyboardRemove())
            return

        value = message.text.strip()
        valid = True

        if field == "gender" and value.lower() not in ["м", "ж"]:
            valid = False
        elif field == "phone":
            valid = value.isdigit() and len(value) == 11 or (value.startswith('+') and len(value) == 12 and value[1:].isdigit())
        elif field == "email":
            valid = re.match(r"[^@]+@[^@]+\.[^@]+", value) is not None
        elif field == "birth_date":
            valid = re.match(r"^\d{2}\.\d{2}\.\d{4}$", value) is not None
        elif field == "username":
            valid = re.match(r"^[A-Za-zА-Яа-яёЁ]+(?:[- ][A-Za-zА-Яа-яёЁ]+)+$", value) is not None

        if not valid:
            await message.answer("Проверьте написание. Попробуйте снова.")
            return

        user_data.setdefault(user_id, {})[field] = value
        await state.update_data(current_field=None)
        block_id = user_states[user_id]
        block = block_map.get(block_id)
        await send_data_capture_menu(message, block, user_data[user_id], state)
        return

    current_block_id = user_states.get(user_id)
    current_block = block_map.get(current_block_id)

    if current_block and current_block["type"] in ["menu", "data_capture"]:
        next_id = get_next_block_id(current_block_id, message.text)
        if next_id:
            await handle_block(message, next_id, state)
        else:
            await message.answer("Выберите пункт из списка.")
        return

async def main():
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
