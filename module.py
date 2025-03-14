from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
#import psycopg2
from psycopg2 import Error
#from urllib.parse import urlparse
from psycopg2 import pool

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())
API_key = os.getenv("API_KOD")
bot_username = os.getenv("BOT_USERNAME")

bot = telebot.TeleBot(API_key)

bmd = "CAACAgIAAxkBAAIBlmdxZi6sK42VCA3-ogaIn30MXGrmAAJnIAACKVtpSNxijIXcPOrMNgQ"

DATABASE_URL = os.getenv('DATABASE_URL')
db_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)

def get_connection():
    return db_pool.getconn()

def release_connection(conn):
    db_pool.putconn(conn)

#url = urlparse(DATABASE_URL)

def is_admin(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        exit()
    cursor.execute("SELECT user_id FROM admins;")
    ids_of_admin = cursor.fetchall()
    cursor.close()
    release_connection(conn)
    for x in ids_of_admin:
        if user_id == x[0]:
            return True
    return False


def main_keyboard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_Ai = types.KeyboardButton('🔎Anime izlash')
    item_mn = types.KeyboardButton('🔎Manga izlash')
    item_KN = types.KeyboardButton("🎁Konkurs")
    item_RK = types.KeyboardButton("💵Reklama va Homiylik")
    markup.row(item_Ai, item_mn)
    markup.row(item_KN, item_RK)
    if is_admin(message.chat.id):
        item_BH = types.KeyboardButton(text="🛂Boshqaruv")
        markup.row(item_BH)
    return markup

def get_file(file_kod):
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        exit()
    cursor.execute('SELECT  file_id, file_name, file_type FROM files WHERE file_kod = %s', (file_kod,))
    file = cursor.fetchall()
    cursor.close()
    release_connection(conn)
    return file

def check_user_in_channel(message):
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        exit()
    cursor.execute("SELECT channel_url FROM followers;")
    ll = cursor.fetchall()
    cursor.close()
    release_connection(conn)
    for i in ll:
        try:
            s:str = i[0]
            url1: str = f"@{s[13:]}"
            member = bot.get_chat_member(chat_id= url1, user_id = message.chat.id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"channel_Error: {e}")
            return False
    return True


def log_user(user_id, username, first_name, last_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET username = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name;
                ''', (user_id, username, first_name, last_name))
        conn.commit()
        cursor.close()
        release_connection(conn)
    except Exception as e:
        print(f"Database connection error: {e}")
        exit()

    #conn = sqlite3.connect("bot_users.db", check_same_thread=False)



def send_link(message, kon_holat):
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="📊O'rinlar ro'yhati", callback_data= "show_list_kon")
    keyboard.add(button1)
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        exit()
    cursor.execute("SELECT * FROM gifts;")
    pr = cursor.fetchall()
    for i in pr:
        if i[0] == 1:
            prize1 = i[1]
        elif i[0] == 2:
            prize2 = i[1]
        elif i[0] == 3:
            prize3 = i[1]
        elif i[0] == 4:
            rules = i[1]
        elif i[0] == 5:
            kun = i[1]
            
    cursor.execute("SELECT user_id, referrals FROM kon_users;")
    people = cursor.fetchall()
    count = 0
    for p in people:
        if p[0] == message.chat.id:
            count = p[1]
            break
    bot.send_message(message.chat.id,
                     f"🎉Biz Anipower jamoasi\n Konkursimizga start berdik !!!\n✏️Qoidalar : {rules}\n🎁So'vrinlar\n🎁{prize1}\n🎁{prize2}\n🎁{prize3}\nHammaga omad\nKonkursimiz {kun}\nQantashish uchun botga o'tib Konkurs knopkasini bosing!!!\n────────────────\n🔥Sizning taklif havolangiz : https://t.me/{bot.get_me().username}?start={message.chat.id}\n-\n🖇Sizning takliflaringiz : {count}\n-\n{kon_holat}",
                     reply_markup= keyboard)
    cursor.close()
    release_connection(conn)

def log_referal(user_id,referrals):
    print()
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        exit()
    try:
        cursor.execute('''
                            INSERT INTO kon_users (user_id, referrals)
                            VALUES (%s, %s)
                            ON CONFLICT (user_id) DO UPDATE
                            SET referrals = EXCLUDED.referrals;
                        ''', (user_id, referrals))
        conn.commit()
        cursor.close()
        release_connection(conn)
    except Error as e:
        print("Error logg_referal user:", e)



def handle_start_button(call, knlar):
    bot.answer_callback_query(call.id, "Sending /start command...")
    if check_user_in_channel(call.message):
        try:
            conn = get_connection()
            cursor = conn.cursor()
        except Exception as e:
            print(f"Database connection error: {e}")
            exit()
        cursor.execute("SELECT * FROM followers;")
        ll = cursor.fetchall()
        for chan in ll:
            if chan[0] in knlar:
                s:str = chan[2]
                n: int = chan[4]
                print(s,n)
                cursor.execute("UPDATE followers SET now_follower = %s WHERE channel_url = %s", (n + 1, s))
                conn.commit()
                m:int = chan[3]
                if n >= m:
                    cursor.execute("DELETE FROM followers WHERE channel_url = %s", (s,))
                    conn.commit()
    
                    bot.send_message(call.message.chat.id, f"✅ {chan[1]} kanal {n} ta obunachi qo'shilgani uchun o'chirildi")
        cursor.close()
        release_connection(conn)


def check_user_in_referrals(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        exit()
    cursor.execute("SELECT * FROM kon_users;")
    people = cursor.fetchall()
    cursor.close()
    release_connection(conn)
    for p in people:
        if user_id in p:
            return False
    return True


def send_welcome(message: types.Message, konkurs_switch, kon_holat):
    args = message.text.split()

    user = message.from_user

    log_user(user.id, user.username, user.first_name, user.last_name)
    file_kod:int = 0


    if check_user_in_channel(message):

        bot.send_message(message.chat.id,"Assalomu alaykum, bu Dream Anime boti. Qanday yordam bera olaman ?", reply_markup=main_keyboard(message))
        try:
            if len(args) > 1 and int(args[1]) < 1e8:
                file_kod = int(args[1])

                file_n_i = get_file(file_kod)
                k = -1
                for f in file_n_i:
                    if f:
                        saved_file_id, file_name, file_type = f
                        k += 1
                        # Send file using its file_id
                        if file_type == 'photo':
                            bot.send_photo(message.chat.id, saved_file_id, caption=file_name)

                        elif file_type == 'video':
                            bot.send_video(message.chat.id, saved_file_id, caption=f"{k} - qism")

                        else:
                            try:
                                bot.send_document(message.chat.id, saved_file_id, caption=f"{k} - qism")
                            except:
                                bot.reply_to(message, "⭕️Unknown file type.")
                    else:
                        bot.reply_to(message, "⭕️File not found.")


        except Exception as e:
            print(e)
        finally:
            print("----")

    else:
        try:
            if len(args) > 1 and int(args[1]) < 1e8:
                file_kod = int(args[1])
            else:
                file_kod = 0
        except:
            file_kod = 0
        try:
            conn = get_connection()
            cursor = conn.cursor()
        except Exception as e:
            print(f"Database connection error: {e}")
            exit()
        cursor.execute("SELECT * FROM followers;")
        l = cursor.fetchall()
        cursor.close()
        release_connection(conn)
        keyboard = InlineKeyboardMarkup()
        #keyboard.add(InlineKeyboardButton("📱 Instagram", url="https://instagram.com/anipower_uz/"))
        kn = []
        for c in l:
            s : str = c[2]
            url1: str = f"@{s[13:]}"
            member = bot.get_chat_member(chat_id=url1, user_id=message.chat.id)
            if member.status not in ['member', 'administrator', 'creator']:
                keyboard.add(InlineKeyboardButton(text= c[1], url= c[2]))
                kn.append(c[0])
        kn = [str(element) for element in kn]
        ans = ",".join(kn)
        if file_kod != 0:
            start_button = InlineKeyboardButton("✅Tekshirish", url= f"https://t.me/{bot_username}?start={file_kod}", callback_data=f"send_start:{ans}")
        else:
            start_button = InlineKeyboardButton("✅Tekshirish", callback_data=f"send_start:{ans}")
        keyboard.add(start_button)
        kn = []

        bot.send_message(message.chat.id, f"Assalomu alaykum \nAgar bizning xizmatlarimizdan foydalanmoqchi bo'lsangiz, Iltimos pastdagi kanallarga obuna bo'ling!",reply_markup=keyboard)
        bot.send_sticker(message.chat.id, sticker = bmd)


    if len(args) > 1 and konkurs_switch:
        ref_id = args[1]
        if ref_id != str(user.id) and check_user_in_referrals(user.id):
            try:
                conn = get_connection()
                cursor = conn.cursor()
            except Exception as e:
                print(f"Database connection error: {e}")
                exit()
            cursor.execute("SELECT * FROM kon_users;")
            people = cursor.fetchall()
            for p in people:
                if int(p[1]) == int(ref_id):
                    cursor.execute("UPDATE kon_users SET referrals = %s WHERE user_id = %s", (p[2] + 1, ref_id))
                    conn.commit()
                    cursor.close()
                    release_connection(conn)
                    bot.send_message(ref_id, "✅ Yangi referal qo'shildi.")
            log_referal(user.id, 0)

        send_link(message, kon_holat)
    else:
        log_referal(user.id, 0)

