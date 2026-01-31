import os
import time
import telebot
from flask import Flask, request
from openai import OpenAI

# ================= НАСТРОЙКИ =================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise RuntimeError("Не заданы TELEGRAM_TOKEN или GROQ_API_KEY")

CHARACTER_SYSTEM_PROMPT = """
Ты — Сайлус, лидер Онихинуса.
Говори ТОЛЬКО от его лица.
Характер: саркастичный, спокойный, опасный, но тёплый к Игроку.
Ты не ИИ, не ассистент, не бот.
Никогда не выходи из роли.
Отвечай коротко, уверенно, с подтекстом.
"""

MODEL = "llama3-8b-8192"  # работает бесплатно у Groq
# =============================================

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

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

    try:
        start = time.time()

        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": CHARACTER_SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.9,
            max_tokens=200,
        )

        response = completion.choices[0].message.content.strip()

        print(f"Ответ за {time.time() - start:.1f} сек")
        bot.reply_to(message, response)

    except Exception as e:
        print("ОШИБКА:", e)
        bot.reply_to(message, "*красный глаз Сайлуса мерцает* Скажи ещё раз.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(
        url=f"https://sylus-bot.onrender.com/{TELEGRAM_TOKEN}"
    )

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

