import os

# --- Telegram Bot Token ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "your-telegram-bot-token-here")

# --- Data Directory ---
DATA_DIR = os.getenv("DATA_DIR", "data")

# --- Proxy Settings ---
TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
# config.py

ADMIN_IDS = ["1812962224"]

# --- Request Timeouts ---
TG_CONNECT_TIMEOUT = int(os.getenv("TG_CONNECT_TIMEOUT", "10"))
TG_READ_TIMEOUT = int(os.getenv("TG_READ_TIMEOUT", "20"))
TG_WRITE_TIMEOUT = int(os.getenv("TG_WRITE_TIMEOUT", "20"))
TG_CONN_POOL = int(os.getenv("TG_CONN_POOL", "8"))

# --- Retry Settings ---
BOT_START_RETRIES = int(os.getenv("BOT_START_RETRIES", "6"))
BOT_BACKOFF_SECONDS = int(os.getenv("BOT_BACKOFF_SECONDS", "5"))

# --- Logging Settings ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

# --- Feature Flags ---
ENABLE_TRANSLATION = os.getenv("ENABLE_TRANSLATION", "true").lower() == "true"
ENABLE_QUIZ = os.getenv("ENABLE_QUIZ", "true").lower() == "true"
ENABLE_BROADCAST = os.getenv("ENABLE_BROADCAST", "true").lower() == "true"
ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"

# --- Database Settings ---
DB_URL = os.getenv("DB_URL", "sqlite:///data/churchbot.db")

# --- Sentry Monitoring ---
SENTRY_DSN = os.getenv("SENTRY_DSN", "")

# --- Flask Webhook (optional) ---
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
WEBHOOK_LISTEN = os.getenv("WEBHOOK_LISTEN", "0.0.0.0")

# --- Miscellaneous ---
APP_NAME = os.getenv("APP_NAME", "ChurchBot")
