#!/usr/bin/env python3
import logging
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Logging configuration
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("ChurchBot")
logging.getLogger("telegram").setLevel(logging.WARNING)

# Optional: more verbose for bot internals during development
if os.getenv("CHURCHBOT_DEBUG", "0") == "1":
    logger.setLevel(logging.DEBUG)
    logging.getLogger("telegram").setLevel(logging.DEBUG)

# Telegram Request compatibility (supports different PTB versions)
Request = None
try:
    from telegram.request import Request  # PTB >= 20
except Exception:
    try:
        from telegram.utils.request import Request  # older layouts
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

# Local imports (ensure these modules exist)
import config
from utils.json_utils import init_data_files
from utils.bot_utils import error_handler as bot_error_handler
from handlers import (
    user_handlers,
    quiz_handlers,
    admin_handlers,
    group_handlers,
)
from scheduler import start_scheduler

# Ensure data directory exists and initialize JSON files
DATA_DIR = getattr(config, "DATA_DIR", "data")
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
try:
    init_data_files(DATA_DIR)
except Exception as e:
    logger.exception("Failed to initialize data files: %s", e)
    # Continue; load_json functions should handle missing files gracefully

def build_request_from_env():
    """
    Build a telegram.request.Request object using environment variables for timeouts and proxy.
    Returns None if Request class is unavailable.
    """
    if Request is None:
        logger.debug("telegram.request.Request not available; using default request settings.")
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
        request_kwargs = {
            "connect_timeout": 10,
            "read_timeout": 20,
            "write_timeout": 20,
            "con_pool_size": 8,
        }

    if proxy:
        request_kwargs["proxy_url"] = proxy
        logger.info("Using proxy for Telegram requests: %s", proxy)

    try:
        return Request(**request_kwargs)
    except Exception:
        logger.exception("Failed to build Request object with kwargs: %s", request_kwargs)
        return None

def safe_add_command(app, command_name: str, handler_module, handler_attr: str):
    """
    Add a CommandHandler only if the handler exists in the module.
    """
    if hasattr(handler_module, handler_attr):
        handler_func = getattr(handler_module, handler_attr)
        app.add_handler(CommandHandler(command_name, handler_func))
        logger.debug("Registered /%s -> %s.%s", command_name, handler_module.__name__, handler_attr)
    else:
        logger.debug("Handler %s.%s not found; skipping /%s", handler_module.__name__, handler_attr, command_name)

def safe_add_callback(app, handler_module, handler_attr: str):
    """
    Add a CallbackQueryHandler only if the handler exists in the module.
    """
    if hasattr(handler_module, handler_attr):
        handler_func = getattr(handler_module, handler_attr)
        app.add_handler(CallbackQueryHandler(handler_func))
        logger.debug("Registered CallbackQueryHandler -> %s.%s", handler_module.__name__, handler_attr)
    else:
        logger.debug("Callback handler %s.%s not found; skipping", handler_module.__name__, handler_attr)

def register_handlers(app):
    # User commands
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

    # Quiz
    safe_add_command(app, "quiz", quiz_handlers, "quiz")
    safe_add_callback(app, quiz_handlers, "quiz_button")

    # Admin
    safe_add_command(app, "addadmin", admin_handlers, "addadmin")
    safe_add_command(app, "listadmins", admin_handlers, "listadmins")
    safe_add_command(app, "deladmin", admin_handlers, "deladmin")
    safe_add_command(app, "broadcast", admin_handlers, "broadcast_cmd")
    safe_add_command(app, "broadcast_users", admin_handlers, "broadcast_users_cmd")
    safe_add_command(app, "addevent", admin_handlers, "addevent")
    safe_add_command(app, "clearevents", admin_handlers, "clearevents")

    # Groups
    safe_add_command(app, "addgroup", group_handlers, "addgroup")
    safe_add_command(app, "listgroups", group_handlers, "listgroups")
    safe_add_command(app, "delgroup", group_handlers, "delgroup")

    # Optional message tracker
    if hasattr(user_handlers, "track_user"):
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_handlers.track_user))
        logger.debug("Registered track_user message handler.")

    # Chat member updates (bot added/removed/promoted/demoted)
    if hasattr(group_handlers, "on_my_chat_member"):
        # chat_member_types accepts strings like "my_chat_member" in PTB v20
        app.add_handler(ChatMemberHandler(group_handlers.on_my_chat_member, chat_member_types=["my_chat_member"]))
        logger.debug("Registered on_my_chat_member handler.")

    # Global error handler
    app.add_error_handler(bot_error_handler)
    logger.debug("All handlers registered.")

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
    # Validate token
    bot_token = getattr(config, "BOT_TOKEN", None)
    if not bot_token:
        logger.critical("BOT_TOKEN missing in config.py; exiting.")
        raise SystemExit("BOT_TOKEN missing in config.py")

    # Build request (with proxy/timeouts) if available
    request = build_request_from_env()
    try:
        if request is not None:
            app = ApplicationBuilder().token(bot_token).request(request).build()
        else:
            app = ApplicationBuilder().token(bot_token).build()
    except Exception:
        logger.exception("Failed to build Application; check python-telegram-bot version and Request usage.")
        raise

    # Register handlers
    register_handlers(app)

    # Start scheduler (if available)
    scheduler = None
    try:
        scheduler = start_scheduler()
        logger.info("Scheduler started.")
    except Exception:
        logger.exception("Failed to start scheduler; continuing without scheduler.")
        scheduler = None

    # Polling loop with exponential backoff on network errors
    max_retries = int(os.getenv("BOT_START_RETRIES", "6"))
    backoff_base = int(os.getenv("BOT_BACKOFF_SECONDS", "5"))
    attempt = 0

    while True:
        try:
            logger.info("Starting bot (attempt %d)", attempt + 1)
            # Drop pending updates to avoid backlog on restart
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
