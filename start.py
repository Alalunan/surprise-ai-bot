# start.py
import os
import logging
from fastapi import Request
from aiogram import Dispatcher, Bot
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
import uvicorn

from app import app  # Імпортуємо FastAPI-додаток
from modules.bot import bot, dp
from modules.router import router as main_router
from modules.telegram import router as telegram_router

logging.basicConfig(level=logging.INFO)

WEBHOOK_DOMAIN = os.getenv("RENDER_EXTERNAL_URL")
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8000))

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_DOMAIN}{WEBHOOK_PATH}"

# Ініціалізація маршрутів
dp.include_router(main_router)
dp.include_router(telegram_router)

@app.on_event("startup")
async def on_startup_webhook():
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Установлено webhook: {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown_webhook():
    await bot.delete_webhook()
    await bot.session.close()
    logging.info("🔌 Webhook видалено і бот зупинено")

@app.post(WEBHOOK_PATH)
async def handle_webhook(request: Request):
    update = await request.json()
    telegram_update = Update.model_validate(update)
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=PORT, log_level="info")
