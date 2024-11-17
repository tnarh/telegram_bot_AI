import os

from dotenv import load_dotenv

load_dotenv()

# Database and Redis
DATABASE = "sqlite+aiosqlite:///database.db"
REDIS_URL = os.getenv("REDIS_URL")

# Telegram Bot
TELEGRAM_CHANEL_ID = os.getenv("TELEGRAM_CHANEL_ID")
TELEGRAM_CHANEL_URL = os.getenv("TELEGRAM_CHANEL_URL", 'https://t.me/mersoft_ai_bot')  # https://t.me/maks_hero_live
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YKASSA_PAYMENT_TOKEN = os.getenv("YKASSA_PAYMENT_TOKEN")
STRIPE_PAYMENT_TOKEN = os.getenv("STRIPE_PAYMENT_TOKEN")
ADMIN_LIST = [5431876685, 7297304134, 438918925, 796204001]


# LeonardoAI
LEONARDO_AI_TOKEN = os.getenv("LEONARDO_AI_TOKEN")
# LumaAI
LUMA_API_TOKEN = os.getenv("LUMA_API_TOKEN")
# SunoAI
SUNO_COOKIE = os.getenv("SUNO_COOKIE")
# HeiGenAI
HEIGEN_AI_TOKEN = os.getenv("HEIGEN_AI_TOKEN")


# For WEBHOOK
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
WEBHOOK_PATH = f'/{TELEGRAM_TOKEN}'
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST", "0.0.0.0")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT", 8000))


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, 'app', 'data', 'media')
LOCALES_DIR = os.path.join(BASE_DIR, 'app', 'data', 'locales')

# Initialize Flask and Telegram Bot
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# Define a basic command handler (e.g., /start)
def start(update, context):
    update.message.reply_text("Hello! Your bot is running on Azure!")

dispatcher.add_handler(CommandHandler("start", start))

# Define webhook endpoint
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    app.run(host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

DEBUG = os.getenv('DEBUG')
