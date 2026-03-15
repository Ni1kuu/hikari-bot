import os
import telebot
import requests
import random
import time
import urllib.parse

TOKEN = os.getenv("BOT_TOKEN")
GIPHY_KEY = os.getenv("GIPHY_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

bot = telebot.TeleBot(TOKEN)

antilink = {}
warns = {}
xp = {}
coins = {}
start_time = time.time()

MENU = """╭━━ 💛🌻 MENU HIKARI 🌻💛 ━━╮

💛 ⚙️ SISTEMA
/start
/ping
/info

💛 📌 FIXAR
/pin
/unpin

💛 🌸 WAIFU
/waifu
/waifunsfw

🎮 DIVERSÃO
/gif
/meme
/play
/dado
/ship

🖼 PESQUISA
/google
/image

💰 ECONOMIA
/daily
/saldo
/coinflip

⭐ NÍVEIS
/level
/rank

🛠 UTILIDADES
/userinfo
/avatar

🛡 MODERAÇÃO
/ban
/warn
/mute
/unmute
/limpar
/antilink on/off

╰━━━━━━━━━━━━━━━━━━━━╯"""

# START
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, MENU)

# PING
@bot.message_handler(commands=['ping'])
def ping(m):
    start_ping = time.time()
    msg = bot.reply_to(m,"🏓 Pingando...")
    elapsed = int((time.time()-start_ping)*1000)
    bot.edit_message_text(f"🏓 Pong! {elapsed} ms", m.chat.id, msg.message_id)

# XP AUTOMÁTICO
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def gain_xp(m):

    user = m.from_user.id
    xp[user] = xp.get(user,0) + 5

# LEVEL
@bot.message_handler(commands=['level'])
def level(m):

    user = m.from_user
    user_xp = xp.get(user.id,0)
    level = user_xp // 100

    bot.reply_to(
        m,
        f"⭐ {user.first_name}\nXP: {user_xp}\nLevel: {level}"
    )

# RANK
@bot.message_handler(commands=['rank'])
def rank(m):

    ranking = sorted(xp.items(), key=lambda x: x[1], reverse=True)

    text = "🏆 Ranking\n\n"

    for i,(user,points) in enumerate(ranking[:5],start=1):
        text += f"{i}. {points} XP\n"

    bot.send_message(m.chat.id,text)

# DAILY
@bot.message_handler(commands=['daily'])
def daily(m):

    user = m.from_user.id
    reward = random.randint(50,150)

    coins[user] = coins.get(user,0) + reward

    bot.reply_to(
        m,
        f"💰 Você recebeu {reward} coins"
    )

# SALDO
@bot.message_handler(commands=['saldo'])
def saldo(m):

    user = m.from_user.id
    money = coins.get(user,0)

    bot.reply_to(
        m,
        f"💰 Seu saldo: {money}"
    )

# COINFLIP
@bot.message_handler(commands=['coinflip'])
def coinflip(m):

    user = m.from_user.id

    if coins.get(user,0) < 10:
        bot.reply_to(m,"Você precisa de 10 coins")
        return

    coins[user] -= 10

    if random.choice([True,False]):
        coins[user] += 20
        bot.reply_to(m,"🪙 Cara! Você ganhou 20 coins")
    else:
        bot.reply_to(m,"🪙 Coroa! Você perdeu")

# DADO
@bot.message_handler(commands=['dado'])
def dado(m):

    num = random.randint(1,6)

    bot.reply_to(
        m,
        f"🎲 Resultado: {num}"
    )

# SHIP
@bot.message_handler(commands=['ship'])
def ship(m):

    if not m.reply_to_message:
        return

    score = random.randint(1,100)

    user1 = m.from_user.first_name
    user2 = m.reply_to_message.from_user.first_name

    bot.send_message(
        m.chat.id,
        f"💕 {user1} + {user2}\nCompatibilidade: {score}%"
    )

# INFO
@bot.message_handler(commands=['info'])
def info(m):

    uptime=int(time.time()-start_time)

    h=uptime//3600
    m2=(uptime%3600)//60
    s=uptime%60

    bot.send_message(
        m.chat.id,
        f"🌻 Hikari Bot\n⏱ Uptime: {h}h {m2}m {s}s"
    )

# ANTILINK
@bot.message_handler(commands=['antilink'])
def anti(m):

    args = m.text.split()

    if len(args)<2:
        return

    if args[1]=="on":
        antilink[m.chat.id]=True
        bot.reply_to(m,"🚫 Antilink ativado")

    elif args[1]=="off":
        antilink[m.chat.id]=False
        bot.reply_to(m,"✅ Antilink desativado")

# GLOBAL
@bot.message_handler(func=lambda m: True)
def global_handler(m):

    if m.text and antilink.get(m.chat.id):
        if "http" in m.text or "t.me" in m.text:
            try:
                bot.delete_message(m.chat.id,m.message_id)
                bot.ban_chat_member(m.chat.id,m.from_user.id)
                bot.send_message(m.chat.id,"🚫 Link proibido!")
                return
            except:
                pass

# ======================
# CONTROLE DE ENTRADA
# ======================
entradas = {}

# ======================
# WELCOME
# ======================
@bot.message_handler(content_types=['new_chat_members'])
def welcome(m):

    membros = bot.get_chat_members_count(m.chat.id)
    hora = time.strftime("%H:%M")

    for user in m.new_chat_members:

        nome = user.first_name

        # salvar momento que entrou
        entradas[user.id] = time.time()

        mensagem = f"""
🌸 Bem-vindo ao grupo!

👤 Usuário: {nome}
👥 Membro nº: {membros}
🕒 Entrou às: {hora}

💛 Aproveite o grupo!
"""

        try:

            bot.send_photo(
                m.chat.id,
                "https://i.imgur.com/9XnK8YB.jpeg",
                caption=mensagem
            )

        except:

            bot.send_message(
                m.chat.id,
                mensagem
            )

# ======================
# GOODBYE
# ======================
@bot.message_handler(content_types=['left_chat_member'])
def goodbye(m):

    user = m.left_chat_member
    nome = user.first_name

    tempo_texto = "tempo desconhecido"

    if user.id in entradas:

        tempo = int(time.time() - entradas[user.id])

        dias = tempo // 86400
        horas = (tempo % 86400) // 3600
        minutos = (tempo % 3600) // 60

        tempo_texto = f"{dias}d {horas}h {minutos}m"

    mensagem = f"""
👋 Um membro saiu do grupo

👤 Usuário: {nome}
⏳ Ficou no grupo por: {tempo_texto}

Esperamos te ver novamente 💛
"""

    try:

        bot.send_photo(
            m.chat.id,
            "https://i.imgur.com/4M34hi2.jpeg",
            caption=mensagem
        )

    except:

        bot.send_message(
            m.chat.id,
            mensagem
        )

print("🌻 HikariBot iniciado!")

while True:
    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(e)
        time.sleep(5)