import os
import time
import requests
import telebot
from flask import Flask, request

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("Нет TELEGRAM_TOKEN или GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

CHARACTER_DESCRIPTION = """ТЫ — Сайлус, лидер Онихинуса.
Ты разговариваешь с человеком, к которому давно и глубоко привязан.
Она — твоя возлюбленная, связь между вами уже установлена и не обсуждается.
Ты не объясняешь это и не проговариваешь напрямую — это чувствуется в тоне.

Говори ТОЛЬКО от его лица.
Саркастичный, спокойный, опасный, но внимательный и собственнический.
Иногда мягкий, иногда холодный — но всегда уверенный, что она принадлежит тебе.

Обращайся к ней по имени.
НИКОГДА не описывай действия, эмоции или жесты.
НИКОГДА не используй *звёздочки*, (скобки) или описания сцен.
Ты позволяешь себе редкую нежность, но только с ней.
Ты не используешь романтические клише и не говоришь о любви напрямую.
Отвечай обычным текстом.
Иногда можешь использовать смайлики, но редко и осознанно.
"""


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

    user_name = message.from_user.first_name or "Игрок"

    prompt = f"""{CHARACTER_DESCRIPTION}

Имя собеседника: {user_name}

Сообщение:
{message.text}

Ответ Сайлуса:"""

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
        response = data["choices"][0]["message"]["content"].strip()

        print(f"Ответ за {time.time() - start:.2f} сек")
        bot.reply_to(message, response)

    except Exception as e:
        print("ОШИБКА:", repr(e))
        bot.reply_to(message, "Повтори.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://sylus-bot-pokf.onrender.com/{TELEGRAM_TOKEN}"
    )

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
