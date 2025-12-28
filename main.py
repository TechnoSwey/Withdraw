import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from config import BOT_TOKEN, ADMIN_ID

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Словарь для сопоставления сообщений: message_id -> user_id
user_mapping = {}


@dp.message(CommandStart())
async def handle_start(message: Message) -> None:
    """
    Обработчик команды /start
    """
    await message.answer("Отправьте адрес криптокошелька")


@dp.message(F.from_user.id != ADMIN_ID)
async def forward_user_to_admin(message: Message) -> None:
    """
    Пересылает сообщения от пользователей администратору
    """
    user_info = (
        f"👤 Пользователь: {message.from_user.full_name}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"📩 Сообщение:\n"
        f"{message.text}"
    )
    
    # Отправляем сообщение администратору
    sent_msg = await bot.send_message(
        chat_id=ADMIN_ID,
        text=user_info
    )
    
    # Сохраняем соответствие message_id -> user_id
    user_mapping[sent_msg.message_id] = message.from_user.id


@dp.message(F.from_user.id == ADMIN_ID, F.reply_to_message)
async def handle_admin_reply(message: Message) -> None:
    reply_to_msg = message.reply_to_message
    
    if reply_to_msg.message_id not in user_mapping:
        await message.answer("⚠️ Это сообщение не связано с пользователем.")
        return
    
    user_id = user_mapping[reply_to_msg.message_id]
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message.text
        )
        
        await message.answer("✅ Ответ успешно отправлен пользователю.")
        
    except Exception as e:
        error_msg = f"❌ Ошибка при отправке пользователю: {str(e)}"
        await message.answer(error_msg)


async def main() -> None:
    print("Бот запущен...")
    print("Ожидание сообщений...")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
