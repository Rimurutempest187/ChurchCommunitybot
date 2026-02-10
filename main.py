#!/usr/bin/env python3
import logging
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("ChurchBot")
logging.getLogger("telegram").setLevel(logging.WARNING)

if os.getenv("CHURCHBOT_DEBUG", "0") == "1":
    logger.setLevel(logging.DEBUG)
    logging.getLogger("telegram").setLevel(logging.DEBUG)

Request = None
try:
    from telegram.request import Request
except Exception:
    try:
        from telegram.utils.request import Request
    except Exception:
        Request = None

from telegram import Update
from telegram.error import NetworkError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
)

load_dotenv()

import config
from utils.json_utils import init_data_files
from handlers import (
    user_handlers,
    quiz_handlers,
    admin_handlers,
    group_handlers,
)
from scheduler import start_scheduler

DATA_DIR = getattr(config, "DATA_DIR", "data")
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
try:
    init_data_files(DATA_DIR)
except Exception:
    logger.exception("Failed to initialize data files; continuing.")

def build_request_from_env():
    if Request is None:
        logger.debug("Request class not available; using defaults.")
        return None

    proxy = os.getenv("TELEGRAM_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    try:
        request_kwargs = {
            "connect_timeout": int(os.getenv("TG_CONNECT_TIMEOUT", "10")),
            "read_timeout": int(os.getenv("TG_READ_TIMEOUT", "20")),
            "write_timeout": int(os.getenv("TG_WRITE_TIMEOUT", "20")),
            "con_pool_size": int(os.getenv("TG_CONN_POOL", "8")),
        }
    except ValueError:
        request_kwargs = {"connect_timeout": 10, "read_timeout": 20, "write_timeout": 20, "con_pool_size": 8}

    if proxy:
        request_kwargs["proxy_url"] = proxy
        logger.info("Using proxy for Telegram requests: %s", proxy)

    try:
        return Request(**request_kwargs)
    except Exception:
        logger.exception("Failed to build Request object.")
        return None

def safe_add_command(app, command_name: str, handler_module, handler_attr: str):
    if hasattr(handler_module, handler_attr):
        handler_func = getattr(handler_module, handler_attr)
        app.add_handler(CommandHandler(command_name, handler_func))
        logger.debug("Registered /%s -> %s.%s", command_name, handler_module.__name__, handler_attr)
    else:
        logger.debug("Skipping /%s; handler not found.", command_name)

def safe_add_callback(app, handler_module, handler_attr: str):
    if hasattr(handler_module, handler_attr):
        handler_func = getattr(handler_module, handler_attr)
        app.add_handler(CallbackQueryHandler(handler_func))
        logger.debug("Registered CallbackQueryHandler -> %s.%s", handler_module.__name__, handler_attr)
    else:
        logger.debug("Skipping CallbackQueryHandler; handler not found.")

def register_handlers(app):
    safe_add_command(app, "start", user_handlers, "start")
    safe_add_command(app, "cmd", user_handlers, "cmd")
    safe_add_command(app, "verse", user_handlers, "verse")
    safe_add_command(app, "prayer", user_handlers, "prayer")
    safe_add_command(app, "prayerlist", user_handlers, "prayerlist")
    safe_add_command(app, "events", user_handlers, "events")
    safe_add_command(app, "daily_inspiration", user_handlers, "daily")
    safe_add_command(app, "myid", user_handlers, "myid")
    safe_add_command(app, "chatid", user_handlers, "chatid")
    safe_add_command(app, "tran", user_handlers, "tran")

    safe_add_command(app, "quiz", quiz_handlers, "quiz")
    safe_add_callback(app, quiz_handlers, "quiz_button")

    safe_add_command(app, "addadmin", admin_handlers, "addadmin")
    safe_add_command(app, "listadmins", admin_handlers, "listadmins")
    safe_add_command(app, "deladmin", admin_handlers, "deladmin")
    safe_add_command(app, "broadcast", admin_handlers, "broadcast_cmd")
    safe_add_command(app, "broadcast_users", admin_handlers, "broadcast_users_cmd")
    safe_add_command(app, "addevent", admin_handlers, "addevent")
    safe_add_command(app, "clearevents", admin_handlers, "clearevents")

    safe_add_command(app, "addgroup", group_handlers, "addgroup")
    safe_add_command(app, "listgroups", group_handlers, "listgroups")
    safe_add_command(app, "delgroup", group_handlers, "delgroup")

    if hasattr(user_handlers, "track_user"):
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_handlers.track_user))
        logger.debug("Registered track_user message handler.")

    if hasattr(group_handlers, "on_my_chat_member"):
        app.add_handler(ChatMemberHandler(group_handlers.on_my_chat_member, chat_member_types=["my_chat_member"]))
        logger.debug("Registered on_my_chat_member handler.")

    app.add_error_handler(bot_error_handler)

def shutdown_scheduler(scheduler):
    if not scheduler:
        return
    try:
        if hasattr(scheduler, "shutdown"):
            try:
                scheduler.shutdown(wait=False)
            except TypeError:
                scheduler.shutdown()
        elif hasattr(scheduler, "stop"):
            scheduler.stop()
        logger.info("Scheduler stopped.")
    except Exception:
        logger.exception("Error stopping scheduler")

def main():
    bot_token = getattr(config, "BOT_TOKEN", None)
    if not bot_token:
        logger.critical("BOT_TOKEN missing in config.py")
        raise SystemExit("BOT_TOKEN missing in config.py")

    request = build_request_from_env()
    try:
        if request is not None:
            app = ApplicationBuilder().token(bot_token).request(request).build()
        else:
            app = ApplicationBuilder().token(bot_token).build()
    except Exception:
        logger.exception("Failed to build Application; check PTB version.")
        raise

    register_handlers(app)

    scheduler = None
    try:
        scheduler = start_scheduler()
        logger.info("Scheduler started.")
    except Exception:
        logger.exception("Failed to start scheduler; continuing without it.")
        scheduler = None

    max_retries = int(os.getenv("BOT_START_RETRIES", "6"))
    backoff_base = int(os.getenv("BOT_BACKOFF_SECONDS", "5"))
    attempt = 0

    while True:
        try:
            logger.info("Starting bot (attempt %d)", attempt + 1)
            app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
            logger.info("Bot stopped normally.")
            break
        except NetworkError as e:
            attempt += 1
            logger.exception("NetworkError while running bot: %s", e)
            if attempt >= max_retries:
                logger.error("Exceeded max retries (%d). Exiting.", max_retries)
                shutdown_scheduler(scheduler)
                sys.exit(1)
            sleep_for = backoff_base * attempt
            logger.info("Retrying in %s seconds...", sleep_for)
            time.sleep(sleep_for)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Shutting down.")
            try:
                app.stop()
            except Exception:
                pass
            shutdown_scheduler(scheduler)
            sys.exit(0)
        except Exception as e:
            logger.exception("Unexpected error: %s", e)
            try:
                app.stop()
            except Exception:
                pass
            shutdown_scheduler(scheduler)
            sys.exit(1)

if __name__ == "__main__":
    main()
