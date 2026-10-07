import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.config import BACKUP_HOURS, BASE_URL, BOT_TOKEN, OWNER_ID, PORT, WEBHOOK_SECRET
from app.db import db
from app.handlers import admin, user
from app.middlewares import ThrottleMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("main")
_tasks: list[asyncio.Task] = []


async def backup_loop(bot: Bot):
    """Render bepul tarifida disk o'chib ketishi mumkin — bazani egasiga muntazam yuboramiz."""
    while True:
        await asyncio.sleep(BACKUP_HOURS * 3600)
        try:
            path = await db.make_backup()
            await bot.send_document(OWNER_ID, FSInputFile(path, filename="bot_backup.db"), caption="💾 Avto-zaxira")
        except Exception as e:  # noqa
            log.warning("Backup xatosi: %s", e)


async def on_startup(bot: Bot, dispatcher: Dispatcher):
    await db.connect()
    await db.ensure_owner(OWNER_ID)
    if BASE_URL:
        await bot.set_webhook(f"{BASE_URL}/webhook", secret_token=WEBHOOK_SECRET,
                              allowed_updates=dispatcher.resolve_used_update_types())
        log.info("Webhook o'rnatildi: %s/webhook", BASE_URL)
    else:
        await bot.delete_webhook()
    if BACKUP_HOURS > 0 and OWNER_ID:
        _tasks.append(asyncio.create_task(backup_loop(bot)))


async def on_shutdown(bot: Bot):
    for t in _tasks:
        t.cancel()
    await db.close()


async def on_error(event):
    log.exception("Handler xatosi: %s", event.exception)
    return True


def build():
    if not BOT_TOKEN or not OWNER_ID:
        raise SystemExit("BOT_TOKEN va OWNER_ID muhit o'zgaruvchilarini kiriting!")
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.outer_middleware(ThrottleMiddleware(0.35))
    dp.include_router(admin.router)  # admin birinchi
    dp.include_router(user.router)
    dp.errors.register(on_error)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    return bot, dp


async def health(_):
    return web.Response(text="OK")


def main():
    bot, dp = build()
    if BASE_URL:  # Render (webhook) rejimi
        app = web.Application()
        app.router.add_get("/", health)
        app.router.add_get("/health", health)
        SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path="/webhook")
        setup_application(app, dp, bot=bot)
        web.run_app(app, host="0.0.0.0", port=PORT)
    else:  # lokal (polling) rejimi
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
