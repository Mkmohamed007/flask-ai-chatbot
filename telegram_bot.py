import telebot
import requests

# 🔹 Replace with your Telegram Bot Token
TELEGRAM_BOT_TOKEN = "7624616543:AAEXQz1yLhNrgh4oOZmf5sUN4HyqmGldICo"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 🔹 Replace with your Flask API URL
FLASK_API_URL = "https://flask-ai-chatbot-c1zz.onrender.com/chat"

# 🔹 Function to send message to Flask AI Chatbot
def get_ai_response(user_prompt):
    try:
        response = requests.post(FLASK_API_URL, json={"prompt": user_prompt})
        data = response.json()
        
        if data.get("success"):
            return data.get("response")
        else:
            return "❌ خطأ في النظام، حاول لاحقاً."
    except requests.exceptions.RequestException as e:
        return f"❌ خطأ في الاتصال بالسيرفر: {e}"
    except Exception as e:
        return f"❌ خطأ غير متوقع: {e}"

# 🔹 Handle Messages in Telegram Bot
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text  # Get user message

    # Show "Typing..." animation in Telegram
    bot.send_chat_action(message.chat.id, 'typing')

    ai_reply = get_ai_response(user_text)  # Get AI response from Flask
    bot.send_message(message.chat.id, ai_reply)  # Send response back

# 🔹 Start the bot
print("🤖 Telegram Bot is running...")
bot.polling()
