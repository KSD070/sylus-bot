import telebot
from transformers import pipeline
from flask import Flask, request
import os
import time

# ===== НАСТРОЙКИ =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN не задан")

CHARACTER_DESCRIPTION = """ТЫ — Сайлус, лидер Онихинуса.
Говори ТОЛЬКО от его лица.
Саркастичный, спокойный, опасный, но тёплый к Игроку.
Никогда не выходи из роли.
"""

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# ====================

print("Загружаю модель...")
generator = pipeline(
    "text-generation",
    model=MODEL_NAME,
    max_new_tokens=120
)
print("Модель загружена")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Сайлус наблюдает."

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda m: True)
def reply(message):
    bot.send_chat_action(message.chat.id, "typing")

    prompt = f"""{CHARACTER_DESCRIPTION}

Человек: {message.text}
Сайлус:"""

    try:
        result = generator(prompt)[0]["generated_text"]
        response = result.split("Сайлус:")[-1].strip()
        bot.reply_to(message, response[:500])
    except Exception as e:
        print("ОШИБКА:", e)
        bot.reply_to(message, "…")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://sylus-bot.onrender.com/{TELEGRAM_TOKEN}"
    )

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

