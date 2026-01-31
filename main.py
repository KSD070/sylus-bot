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
    return "Сайлус наблюдает.", 200

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(
        request.get_data().decode("utf-8")
    )
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda m: True)
def reply(message):
    bot.send_chat_action(message.chat.id, "typing")

    prompt = (
        CHARACTER_DESCRIPTION
        + "\n\nИгрок: "
        + message.text
        + "\nСайлус:"
    )

    try:
        start = time.time()

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.9,
                "max_tokens": 200,
            },
            timeout=30,
        )

        data = r.json()
        response = data["choices"][0]["message"]["content"]

        print(f"Ответ за {time.time() - start:.2f} сек")
        bot.reply_to(message, response)

    except Exception as e:
        print("ОШИБКА:", repr(e))
        bot.reply_to(
            message,
            "*красный глаз Сайлуса мерцает* Повтори."
        )

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://sylus-bot-pokf.onrender.com/{TELEGRAM_TOKEN}"
    )

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
