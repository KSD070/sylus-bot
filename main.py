import os
import time
import requests
import telebot
from flask import Flask, request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

CHARACTER_DESCRIPTION = (
    "Ты — Сайлус, лидер Онихинуса. "
    "Говори ТОЛЬКО от его лица. "
    "Саркастичный, спокойный, опасный, но тёплый к Игроку. "
    "Никогда не выходи из роли."
)

@app.route("/", methods=["GET"])
def index():
    return "Сайлус наблюдает."

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(
        request.stream.read().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda m: True)
def reply(message):
    try:
        bot.send_chat_action(message.chat.id, "typing")

        prompt = f"{CHARACTER_DESCRIPTION}\n\nИгрок: {message.text}\nСайлус:"

        start = time.time()
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completion
