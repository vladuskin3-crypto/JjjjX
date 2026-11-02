import telebot
import requests
import re

# Вставьте сюда ваш токен от @BotFather
API_TOKEN = '9198275284:AAFi5njhpgHjBBkp_RcuWLzSMgmEy8i4mKE'

bot = telebot.TeleBot(API_TOKEN)

# Регулярные выражения для поиска JWT и хэшей
JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*")
GENERIC_KEY_PATTERN = re.compile(r"[a-f0-9]{32,64}")

def scan_text_for_tokens(text: str) -> list:
    found = []
    if not text:
        return found
    jwts = JWT_PATTERN.findall(text)
    if jwts:
        found.extend([f"JWT: {j}" for j in jwts])
    keys = GENERIC_KEY_PATTERN.findall(text)
    if keys:
        found.extend([f"Хэш/Ключ: {k}" for k in keys])
    return found

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "👋 Бот запущен на чистом коде без сложных библиотек!\n\n"
        "Используйте команду: /scan https://example.com"
    )

@bot.message_handler(commands=['scan'])
def scan_site(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "⚠️ Укажите URL. Пример: /scan https://example.com")
        return
        
    target_url = args[1].strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    status_msg = bot.reply_to(message, f"🔍 Сканирую код страницы {target_url}...")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(target_url, headers=headers, timeout=15)
        
        tokens = scan_text_for_tokens(response.text)
        for key, value in response.headers.items():
            tokens.extend(scan_text_for_tokens(value))
            
        report = f"📋 Результаты анализа для: {target_url}\n\n"
        if tokens:
            report += "⚠️ Обнаружены потенциальные токены/ключи (первые 5):\n"
            for t in list(set(tokens))[:5]:
                report += f"• {t[:100]}\n"
        else:
            report += "✅ Чувствительных токенов в открытом коде и заголовках страницы не найдено."
            
    except Exception as e:
        report = f"❌ Ошибка при запросе к сайту: {str(e)}"
        
    bot.delete_message(message.chat.id, status_msg.message_id)
    bot.send_message(message.chat.id, report)

print("[*] Бот успешно запущен на легкой библиотеке!")
bot.infinity_polling()