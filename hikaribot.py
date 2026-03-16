import os
import telebot
import requests
import random
import time
import urllib.parse
import json

# ======================
# VARIÁVEIS
# ======================

TOKEN = os.getenv("BOT_TOKEN")
GIPHY_KEY = os.getenv("GIPHY_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

BOT_VERSION = "2.2.0"
CREATOR = "@ni1ckkj"
BOT_NAME = "Hikari"

bot = telebot.TeleBot(TOKEN)

antilink = {}
warns = {}
entradas = {}

DATA_FILE = "data.json"

# ======================
# CARREGAR DADOS
# ======================

xp = {}
coins = {}
daily_cooldown = {}

try:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        xp = data.get("xp", {})
        coins = data.get("coins", {})
        daily_cooldown = data.get("daily_cooldown", {})
except:
    pass

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "xp": xp,
            "coins": coins,
            "daily_cooldown": daily_cooldown
        }, f)

start_time = time.time()

# ======================
# MENU
# ======================

MENU = f"""
╭━━━ 🌻 {BOT_NAME} BOT 🌻 ━━━╮

⚙️ SISTEMA
/start • /ping • /info

🎮 DIVERSÃO
/gif • /meme • /waifu • /waifunsfw • /play • /waifugif • /gifnsfw

🔎 PESQUISA
/google • /image

👤 PERFIL
/userinfo • /avatar • /level • /rank • /saldo • /coinflip • /daily

📌 GRUPO
/pin • /unpin • /dado • /ship

🛡 MODERAÇÃO
/ban • /warn • /mute • /unmute • /limpar • /antilink on/off
"""

# ======================
# START
# ======================

@bot.message_handler(commands=['start'])
def start(m):
    img = "https://i.postimg.cc/6QDLmktT/file-00000000104871f5ab38bc387c4c1435.png"
    try:
        bot.send_photo(m.chat.id, img, caption=MENU)
    except:
        bot.send_message(m.chat.id, MENU)

# ======================
# PING
# ======================

@bot.message_handler(commands=['ping'])
def ping(m):
    start_ping = time.time()
    msg = bot.reply_to(m, "🏓 Pingando...")
    elapsed = int((time.time() - start_ping) * 1000)
    bot.edit_message_text(f"🏓 Pong! {elapsed} ms", m.chat.id, msg.message_id)

# ======================
# XP AUTOMÁTICO COM LEVEL UP
# ======================

last_xp = {}

@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def gain_xp(m):

    user = str(m.from_user.id)
    now = time.time()

    # Cooldown de 10 segundos
    if user in last_xp and now - last_xp[user] < 10:
        return

    last_xp[user] = now

    # XP atual e novo XP
    user_xp = xp.get(user, 0)
    xp[user] = user_xp + 5
    save_data()

    # Calcula level
    old_level = user_xp // 100
    new_level = xp[user] // 100

    # Se subiu de level
    if new_level > old_level:
        try:
            bot.send_message(
                m.chat.id,
                f"⭐ Parabéns {m.from_user.first_name}! Você subiu para o level {new_level}!"
            )
        except:
            pass

# ======================
# RANK
# ======================

@bot.message_handler(commands=['rank'])
def rank(m):
    ranking = sorted(xp.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 Ranking\n\n"

    for i, (user_id, points) in enumerate(ranking[:5], start=1):
        try:
            member = bot.get_chat_member(m.chat.id, int(user_id))
            name = member.user.first_name
        except:
            name = "Usuário"
        text += f"{i}. {name} - {points} XP\n"

    bot.send_message(m.chat.id, text)

# ======================
# COINS
# ======================

@bot.message_handler(commands=['saldo'])
def saldo(m):
    user = str(m.from_user.id)
    bot.reply_to(m, f"💰 Saldo: {coins.get(user,0)} coins")

@bot.message_handler(commands=['daily'])
def daily(m):

    user = str(m.from_user.id)
    now = time.time()

    cooldown = 86400
    last = daily_cooldown.get(user,0)

    if now - last < cooldown:
        bot.reply_to(m,"⏳ Você já coletou hoje.")
        return

    reward = random.randint(50,150)

    coins[user] = coins.get(user,0) + reward
    daily_cooldown[user] = now

    save_data()

    bot.reply_to(m,f"💰 Você ganhou {reward} coins!")

# ======================
# COINFLIP
# ======================

@bot.message_handler(commands=['coinflip'])
def coinflip(m):

    user = str(m.from_user.id)

    if coins.get(user,0) < 10:
        bot.reply_to(m,"💛 Você precisa de 10 coins")
        return

    coins[user] -= 10

    if random.choice([True,False]):
        coins[user] += 20
        result = "🪙 Cara! Você ganhou"
    else:
        result = "🪙 Coroa! Você perdeu"

    save_data()

    bot.reply_to(m,f"{result}\nSaldo: {coins[user]}")

# ======================
# GIF
# ======================

@bot.message_handler(commands=['gif'])
def gif(m):

    query = "anime"

    args = m.text.split(maxsplit=1)
    if len(args) > 1:
        query = args[1]

    try:

        url = "https://api.giphy.com/v1/gifs/search"

        params = {
            "api_key": GIPHY_KEY,
            "q": query,
            "limit": 25
        }

        r = requests.get(url,params=params).json()

        data = r.get("data",[])

        if not data:
            bot.reply_to(m,"Nenhum gif encontrado")
            return

        gif_url = random.choice(data)["images"]["original"]["url"]

        bot.send_animation(m.chat.id,gif_url)

    except:
        bot.reply_to(m,"Erro ao buscar gif")

# ======================
# MEME
# ======================

@bot.message_handler(commands=['meme'])
def meme(m):

    try:
        r = requests.get("https://meme-api.com/gimme").json()

        bot.send_photo(
            m.chat.id,
            r["url"],
            caption=r["title"]
        )

    except:
        bot.reply_to(m,"Erro ao pegar meme")

# ======================
# WAIFU
# ======================

@bot.message_handler(commands=['waifu'])
def waifu(m):

    try:

        r = requests.get(
            "https://api.waifu.pics/sfw/waifu"
        ).json()

        bot.send_photo(
            m.chat.id,
            r["url"]
        )

    except:
        bot.reply_to(m,"Erro")

@bot.message_handler(commands=['waifugif'])
def waifugif(m):

    try:
        r = requests.get(
            "https://api.waifu.pics/sfw/waifu"
        ).json()

        bot.send_animation(
            m.chat.id,
            r["url"],
            caption="💛 Waifu GIF!"
        )

    except:
        bot.reply_to(m,"Erro ao pegar gif")

@bot.message_handler(commands=['waifunsfw'])
def waifunsfw(m):

    if m.chat.type != "private":
        bot.reply_to(m,"🚫 NSFW só no privado!")
        return

    try:
        r = requests.get(
            "https://api.waifu.pics/nsfw/waifu"
        ).json()

        bot.send_photo(
            m.chat.id,
            r["url"],
            caption="🔞 Waifu NSFW"
        )

    except:
        bot.reply_to(m,"Erro ao pegar waifu")

@bot.message_handler(commands=['gifnsfw'])
def gifnsfw(m):

    if m.chat.type != "private":
        bot.reply_to(m,"🚫 NSFW só no privado!")
        return

    try:
        r = requests.get(
            "https://api.waifu.pics/nsfw/waifu"
        ).json()

        bot.send_animation(
            m.chat.id,
            r["url"],
            caption="🔞 Waifu GIF NSFW"
        )

    except:
        bot.reply_to(m,"Erro ao pegar gif")

# ======================
# GOOGLE
# ======================

@bot.message_handler(commands=['google'])
def google(m):

    args = m.text.split(maxsplit=1)

    if len(args) < 2:
        bot.reply_to(m,"Use /google termo")
        return

    query = args[1]

    params = {
        "q": query,
        "engine": "google",
        "api_key": SERPAPI_KEY
    }

    r = requests.get(
        "https://serpapi.com/search",
        params=params
    ).json()

    results = r.get("organic_results",[])

    msg = f"🔎 {query}\n\n"

    for res in results[:3]:
    title = res.get("title","Sem título")
    link = res.get("link","")

    msg += f"{title}\n{link}\n\n"

    bot.send_message(m.chat.id,msg)

# ======================
# PLAY
# ======================

@bot.message_handler(commands=['play'])
def play(m):

    args = m.text.split(maxsplit=1)

    if len(args) < 2:
        bot.reply_to(m,"Use /play musica")
        return

    query = args[1]

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={urllib.parse.quote_plus(query)}&key={YOUTUBE_KEY}&maxResults=1&type=video"

    r = requests.get(url).json()

    items = r.get("items",[])

    if not items:
        bot.reply_to(m,"Não encontrado")
        return

    video = items[0]

    title = video["snippet"]["title"]
    channel = video["snippet"]["channelTitle"]
    vid = video["id"]["videoId"]

    bot.send_message(
        m.chat.id,
        f"🎵 {title}\n📺 {channel}\nhttps://youtu.be/{vid}"
    )

# ======================
# DADO
# ======================

@bot.message_handler(commands=['dado'])
def dado(m):
    bot.reply_to(m,f"🎲 {random.randint(1,6)}")

# ======================
# SHIP
# ======================

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

# ======================
# INFO
# ======================

@bot.message_handler(commands=['info'])
def info(m):

    uptime = int(time.time() - start_time)

    h = uptime // 3600
    m2 = (uptime % 3600) // 60
    s = uptime % 60

    msg = f"""
🌻 {BOT_NAME}

Uptime: {h}h {m2}m {s}s
Versão: {BOT_VERSION}
Criador: {CREATOR}
"""

    bot.send_message(m.chat.id,msg)

# ======================
# POLLING
# ======================

print("Hikari iniciado...")

bot.infinity_polling(timeout=60, long_polling_timeout=60)