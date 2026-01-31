import os
import time
import requests
from flask import Flask, request
import telebot

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN не найден")

if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY не найден")

BOT_URL = f"https://sylus-bot-pokf.onrender.com/{TELEGRAM_TOKEN}"

bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
app = Flask(__name__)

MODEL = "llama3-70b-8192"  # НЕ ТРОГАТЬ

SYSTEM_PROMPT = (
    "Ты — Сайлус. Холодный, язвительный, умный, с оттенком угрозы. "
    "Говоришь кратко, с сарказмом, иногда пугающе. "
    "Никогда не повторяй одну и ту же фразу дважды."
)

@app.route("/", methods=["GET"])
def index():
    return "ok", 200

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "ok", 200


@bot.message_handler(content_types=["text"])
def handle_message(message):
    user_text = message.text.strip()
    chat_id = message.chat.id

    start_time = time.time()
    pr
