# surprise-ai-bot/app.py
import os
import logging
from fastapi import FastAPI
from modules.telegram import router as telegram_router
from modules.router import router as main_router
from modules.scheduler import start_scheduler
from modules.limits import init_limits_table
from modules.database import init_db
from modules.bot import bot, dp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

PORT = int(os.getenv("PORT", 8000))
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")

app = FastAPI()

# Регіструємо маршрути в диспетчері aiogram
dp.include_router(main_router)
dp.include_router(telegram_router)

@app.on_event("startup")
async def on_startup():
    try:
        await init_db()
        await init_limits_table()
        loop = asyncio.get_event_loop()
        start_scheduler(loop)
        logging.info("✅ База, ліміти і планувальник ініціалізовані")
    except Exception as e:
        logging.error(f"❌ Помилка ініціалізації: {e}", exc_info=True)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
    logging.info("🔌 Сесія Telegram бота закрита")

@app.get("/")
async def root():
    return {"status": "Surprise Me! бот працює 🪄"}

@app.get("/healthz")
async def healthcheck():
    return {"status": "ok"}
