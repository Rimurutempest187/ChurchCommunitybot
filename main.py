import logging
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# --- Logging setup ---
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.DEBUG,
)
logging.getLogger("ChurchBot.bot").setLevel(logging.DEBUG)
logging.getLogger("telegram").setLevel(logging.INFO)  # reduce noise

logger = logging.getLogger("ChurchBot")

# --- Telegram imports ---
Request = None
try:
    from telegram.request import Request
except ImportError:
    try:
        from telegram.utils.request import Request
    except ImportError:
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

# --- Load environment ---
load_dotenv()

# --- Local imports ---
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

# --- Data directory setup ---
DATA_DIR = getattr(config, "DATA_DIR", "data")
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
init_data_files(DATA_DIR)

# --- Request builder ---
def build_request_from_env():
    if Request is None:
        logger.debug("telegram.request.Request not available; using default request settings.")
        return None

    proxy = os.getenv("TELEGRAM_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
    request_kwargs = {
        "connect_timeout": int(os.getenv("TG_CONNECT_TIMEOUT", "10")),
        "read_timeout": int(os.getenv("TG_READ_TIMEOUT", "20")),
        "write_timeout": int(os.getenv("TG_WRITE_TIMEOUT", "20")),
        "con_pool_size": int(os.getenv("TG_CONN_POOL", "8")),
    }
    if proxy:
        request_kwargs["proxy_url"] = proxy
        logger.info("Using proxy for Telegram requests: %s", proxy)
    try:
        return Request(**request_kwargs)
    except Exception as e:
        logger.exception("Failed to build Request object: %s", e)
        return None

# --- Handler registration helpers ---
def safe_add_command(app, command_name: str, handler_module, handler_attr: str):
    if hasattr(handler_module, handler_attr):
        handler_func = getattr(handler_module, handler_attr)
        app.add_handler(CommandHandler(command_name, handler_func))
        logger.debug("Registered /%s -> %s.%s", command_name, handler_module.__name__, handler_attr)

def safe_add_callback(app, handler_module, handler_attr: str):
    if hasattr(handler_module, handler_attr):
        handler_func = getattr(handler_module, handler_attr)
        app.add_handler(CallbackQueryHandler(handler_func))
        logger.debug("Registered CallbackQueryHandler -> %s.%s", handler_module.__name__, handler_attr)

def register_handlers(app):
    # User commands
    for cmd, func in [
        ("start", "start"),
        ("cmd", "cmd"),
        ("verse", "verse"),
        ("prayer", "prayer"),
        ("prayerlist", "prayerlist"),
        ("events", "events"),
        ("daily_inspiration", "daily"),
        ("myid", "myid"),
        ("chatid", "chatid"),
        ("tran", "tran"),
    ]:
        safe_add_command(app, cmd, user_handlers, func)

    # Quiz
    safe_add_command(app, "quiz", quiz_handlers, "quiz")
    safe_add_callback(app, quiz_handlers, "quiz_button")

    # Admin
    for cmd, func in [
        ("addadmin", "addadmin"),
        ("listadmins", "listadmins"),
        ("deladmin", "deladmin"),
        ("broadcast", "broadcast_cmd"),
        ("broadcast_users", "broadcast_users_cmd"),
        ("addevent", "addevent"),
        ("clearevents", "clearevents"),
    ]:
        safe_add_command(app, cmd, admin_handlers, func)

    # Groups
    for cmd, func in [
        ("addgroup", "addgroup"),
        ("listgroups", "listgroups"),
        ("delgroup", "delgroup"),
    ]:
        safe_add_command(app, cmd, group_handlers, func)

    # Track user messages
    if hasattr(user_handlers, "track_user"):
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_handlers.track_user))
        logger.debug("Registered track_user message handler.")

    # Chat member updates
    if hasattr(group_handlers, "on_my_chat_member"):
        app.add_handler(ChatMemberHandler(group_handlers.on_my_chat_member, chat_member_types=["my_chat_member"]))
        logger.debug("Registered on_my_chat_member handler.")

    # Error handler
    app.add_error_handler(bot_error_handler)

# --- Scheduler shutdown ---
def shutdown_scheduler(scheduler):
    try:
        if scheduler:
            if hasattr(scheduler, "shutdown"):
                try:
                    scheduler.shutdown(wait=False)
                except TypeError:
                    scheduler.shutdown()
            elif hasattr(scheduler, "stop"):
                scheduler.stop()
            logger.info("Scheduler stopped.")
    except Exception as e:
        logger.exception("Error stopping scheduler: %s", e)

# --- Main entrypoint ---
def main():
    if not getattr(config, "BOT_TOKEN", None):
        raise SystemExit("BOT_TOKEN missing in config.py")

    request = build_request_from_env()
    if request is not None:
        app = ApplicationBuilder().token(config.BOT_TOKEN).request(request).build()
    else:
        app = ApplicationBuilder().
