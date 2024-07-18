import telebot
from yt_dlp import YoutubeDL
import sqlite3
import os

bot = telebot.TeleBot('6673027330:AAHHhZdrAPIua6IsDnvFO7HqxXWDZZQKEv0')

# Database initialization
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)''')
conn.commit()

admin_id = 7126212094

def add_user(user_id):
    try:
        c.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    add_user(user_id)
    bot.reply_to(message, "Salom! Video havolasini yuboring.")

    if user_id == admin_id:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, )
        markup.add(telebot.types.KeyboardButton('Foydalanuvchilar soni'))
        markup.add(telebot.types.KeyboardButton('Habar yuborish'))
        bot.send_message(user_id, "Admin paneli", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Foydalanuvchilar soni' and message.chat.id == admin_id)
def send_user_count(message):
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    bot.reply_to(message, f"Botdan foydalanuvchilar soni: {user_count}")

@bot.message_handler(func=lambda message: message.text == 'Habar yuborish' and message.chat.id == admin_id)
def prompt_broadcast_message(message):
    msg = bot.reply_to(message, "Yuboriladigan habarni yozing:")
    bot.register_next_step_handler(msg, broadcast_message)

def broadcast_message(message):
    broadcast_text = message.text
    c.execute("SELECT user_id FROM users")
    user_ids = c.fetchall()
    for user_id in user_ids:
        try:
            bot.send_message(user_id[0], broadcast_text)
        except Exception as e:
            print(f"Xatolik yuz berdi foydalanuvchiga habar yuborishda: {user_id[0]} - {e}")
    bot.reply_to(message, "Habar barcha foydalanuvchilarga yuborildi!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    try:
        bot.reply_to(message, "Videoni yuklab olish jarayoni boshlandi...")

        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
            'proxy': ''  # Bu qator proksini olib tashlash uchun qo'shiladi
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info_dict)

        caption_text = "Videoni yuklab olish uchun botimiz: https://t.me/youtue_video_yukla_robot"

        with open(video_path, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption=caption_text)

        # Yuklab olingan video faylini o'chirish
        os.remove(video_path)

    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {str(e)}")

if __name__ == '__main__':
    print('Bot ishladi....')
    bot.infinity_polling()