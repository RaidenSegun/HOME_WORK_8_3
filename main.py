import aiosmtplib, logging, asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import os
from email.message import EmailMessage
from config import SMTP_USER, SMTP_PASSWORD, token


SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = SMTP_USER
SMTP_PASSWORD = SMTP_PASSWORD


logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher()


products = {
    'product_1': {'name': 'Xiaomi 15 Pro', 'description': '16/512гб', 'price': 90000},
    'product_2': {'name': 'Iphone 16 Pro Max', 'description': '12/512гб', 'price': 120000},
    'product_3': {'name': 'Sumsung S24 Ultra', 'description': '16гб 1Тб', 'price': 100000},
}


current_order = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    inline_buttons = [
        [InlineKeyboardButton(text=product['name'], callback_data=product_id)]
        for product_id, product in products.items()
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
    
    await message.answer("Привет! Выберите товар для заказа:", reply_markup=markup)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "/start - начать заказ\n"
        "/help - получить помощь\n"
        "/cancel - отменить заказ"
    )
    await message.answer(help_text)

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message):
    global current_order
    current_order.clear()
    await message.answer("Ваш заказ был отменён. Выберите товар заново с помощью /start.")


@dp.callback_query(lambda c: c.data in products)
async def product_selected(callback_query: types.CallbackQuery):
    product_id = callback_query.data
    product = products[product_id]
    await bot.send_message(callback_query.from_user.id, f"Вы выбрали: {product['name']}\nОписание: {product['description']}\nЦена: {product['price']} руб.")
    current_order['product'] = product
    current_order['user_id'] = callback_query.from_user.id
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить заказ", callback_data="confirm_order")]
    ])

    await bot.send_message(callback_query.from_user.id, "Хотите подтвердить заказ?", reply_markup=markup)

@dp.callback_query(lambda c: c.data == "confirm_order")
async def confirm_order(callback_query: types.CallbackQuery):
    if 'product' in current_order:
        product = current_order['product']
        user_id = current_order['user_id']
        print(f"Заказ от пользователя {user_id}: {product['name']}, {product['description']}, {product['price']} руб.")

        current_order.clear()

        await bot.send_message(callback_query.from_user.id, "Ваш заказ подтверждён! Хотите чтобы мы отправили вам потверждение через email?")
    else:
        await bot.send_message(callback_query.from_user.id, "Ошибка. Пожалуйста, выберите товар и попробуйте снова.")



async def main():
    logging.basicConfig(level="INFO")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот приостановлен!")
