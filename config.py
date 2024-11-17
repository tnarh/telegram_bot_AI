import os
from dotenv import load_dotenv
import redis  # Redis client for synchronous interaction

# Load environment variables
load_dotenv()

# Database and Redis Configuration
DATABASE = "sqlite+aiosqlite:///database.db"

# Azure Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
USE_SSL = "ssl" in REDIS_URL  # Automatically detect if SSL is required

# Initialize Redis client
try:
    redis_client = redis.StrictRedis.from_url(REDIS_URL, ssl=USE_SSL)
    # Test Redis connection
    redis_client.ping()
    print("Connected to Redis successfully!")
except Exception as e:
    print(f"Error connecting to Redis: {e}")
    redis_client = None

# Telegram Bot Configuration
TELEGRAM_CHANEL_ID = os.getenv("TELEGRAM_CHANEL_ID", "default_channel_id")
TELEGRAM_CHANEL_URL = os.getenv("TELEGRAM_CHANEL_URL", "https://t.me/mersoft_ai_bot")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YKASSA_PAYMENT_TOKEN = os.getenv("YKASSA_PAYMENT_TOKEN", "")
STRIPE_PAYMENT_TOKEN = os.getenv("STRIPE_PAYMENT_TOKEN", "")
ADMIN_LIST = list(map(int, os.getenv("ADMIN_LIST", "5431876685,7297304134,438918925,796204001").split(',')))

# Validate critical variables
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is required but not set in environment variables.")

# Third-party API Tokens
LEONARDO_AI_TOKEN = os.getenv("LEONARDO_AI_TOKEN", "")
LUMA_API_TOKEN = os.getenv("LUMA_API_TOKEN", "")
SUNO_COOKIE = os.getenv("SUNO_COOKIE", "")
HEIGEN_AI_TOKEN = os.getenv("HEIGEN_AI_TOKEN", "")

# Webhook Configuration
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL", "https://example.com")
WEBHOOK_PATH = f'/{TELEGRAM_TOKEN}'
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST", "0.0.0.0")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT", 8000))

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'app', 'data', 'media')
LOCALES_DIR = os.path.join(BASE_DIR, 'app', 'data', 'locales')

# Debug Mode
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
