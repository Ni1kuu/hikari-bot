import os
import telebot
import requests
import random
import time
import urllib.parse
import json
from telebot import types
from pymongo import MongoClient

# ======================
# VARIÁVEIS
# ======================
TOKEN = os.getenv("BOT_TOKEN")
GIPHY_KEY = os.getenv("GIPHY_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
MONGO_URI = os.getenv("MONGO_URI")

BOT_VERSION = "2.2.0"
CREATOR = "@ni1ckkj"
BOT_NAME = "Hikari"

bot = telebot.TeleBot(TOKEN)

antilink = {}
warns = {}
last_xp = {}

# ======================
# MONGODB
# ======================
client = MongoClient(MONGO_URI)
db = client["hikari_bot"]
users_collection = db["users"]

def get_user(user_id):
    user = users_collection.find_one({"_id": str(user_id)})
    if not user:
        user = {
            "_id": str(user_id),
            "xp": 0,
            "coins": 0,
            "first_seen": time.strftime("%d/%m/%Y %H:%M")
        }
        users_collection.insert_one(user)
    return user

def add_xp(user_id, amount):
    users_collection.update_one(
        {"_id": str(user_id)},
        {"$inc": {"xp": amount}},
        upsert=True
    )

def add_coins(user_id, amount):
    users_collection.update_one(
        {"_id": str(user_id)},
        {"$inc": {"coins": amount}},
        upsert=True
    )

start_time = time.time()

# ======================
# MENU
# ======================
MENU = f"""
╭━━━ 🌼 {BOT_NAME} BOT 🌼 ━━━╮
╭─ 🌸 Usuários ─╮
👤 /userinfo - Info de usuário
🧩 /level - Seu nível
🏆 /rank - Ranking XP
💰 /saldo - Ver coins
🎲 /dado - Jogar dado
💛 /ship - Shipar alguém (responder)
╰─────────────╯
╭─ 🌸 Diversão ─╮
🖼 /waifu - Waifu imagem
🔞 /waifunsfw - Waifu NSFW
🤣 /meme - Meme aleatório
🎵 /song <música> - Buscar no YouTube
🔍 /google <termo> - Buscar no Google
🖼 /image <termo> - Buscar imagem
🪙 /coinflip - Jogo de coinflip
╰─────────────╯
╭─ 🌸 Sistema ─╮
🏓 /ping - Ping do bot
📌 /pin - Fixar mensagem
📌 /unpin - Desfixar mensagem
╰─────────────╯
╭─ 🌸 Moderação ─╮
🚫 /ban - Banir (responder)
⚠️ /warn - Avisar (responder)
🔇 /mute - Mutar (responder)
🔊 /unmute - Desmutar (responder)
🧹 /limpar <quantidade> - Apagar mensagens
🚫 /antilink on/off - Ativar/Desativar
╰─────────────╯
"""

# ======================
# FUNÇÕES
# ======================
def waifu_request(endpoint):
    url = f"https://api.waifu.pics/{endpoint}/waifu"
    r = requests.get(url).json()
    return r.get("url")

def uptime_text():
    uptime = int(time.time() - start_time)
    h = uptime // 3600
    m = (uptime % 3600) // 60
    s = uptime % 60
    return f"{h}h {m}m {s}s"

# ======================
# START
# ======================
@bot.message_handler(commands=['start'])
def start(m):

    get_user(m.from_user.id)

    video = "https://github.com/Ni1kuu/hikari-bot/raw/main/Cute_anime_fox_girl_standing_in_a_peaceful_Japanese_garden%2C_arms_open_in_a_welcoming_pose.____Animat_seed1530167038.mp4"

    msg_text = f"""
🌼 Bem-vindo(a) ao {BOT_NAME}! 🌼
✨ Aqui você pode se divertir, explorar e interagir comigo!
💌 Clique em um botão abaixo:
Divirta-se e aproveite! ꒰ᐢ. .ᐢ꒱₊˚⊹💛
""".strip()

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("👤 Perfil", callback_data="perfil"),
        types.InlineKeyboardButton("🏓 Ping", callback_data="ping"),
        types.InlineKeyboardButton("🖼 Waifu", callback_data="waifu"),
        types.InlineKeyboardButton("ℹ️ Info", callback_data="info"),
        types.InlineKeyboardButton("📋 Menu", callback_data="menu_completo")
    )

    bot.send_video(m.chat.id, video, caption=msg_text, reply_markup=keyboard)

# ======================
# XP AUTOMÁTICO ESTILO HIKARI 🌸✨
# ======================
last_xp_time = {}
msg_count = {}

@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def gain_xp(m):
    user_id = m.from_user.id
    now = time.time()

    # ⏳ Cooldown de 10s por usuário
    if user_id in last_xp_time and now - last_xp_time[user_id] < 10:
        return
    last_xp_time[user_id] = now

    # Contador de mensagens
    msg_count[user_id] = msg_count.get(user_id, 0) + 1

    # Só dá XP visível a cada 5 mensagens
    give_xp = False
    if msg_count[user_id] >= 5:
        give_xp = True
        msg_count[user_id] = 0

    # 🎯 XP base + bônus por tamanho da mensagem
    base_xp = random.randint(15, 25)  # XP maior
    bonus = len(m.text) // 15          # +1 XP a cada 15 caracteres
    xp_gain = base_xp + bonus

    # XP aleatório bônus kawaii (10% de chance)
    bonus_msg = ""
    if random.random() < 0.1:
        xp_gain += random.randint(20, 35)
        bonus_msg = "✨ Surpresinha de XP! ✨"

    # Adiciona XP ao usuário
    user_data = get_user(user_id)
    current_xp = user_data.get("xp", 0)
    current_level = current_xp // 100
    add_xp(user_id, xp_gain)
    user_data = get_user(user_id)
    new_xp = user_data.get("xp", 0)
    new_level = new_xp // 100

    # ⚡ Level Up Hikari Style
    if new_level > current_level:
        level_up_msgs = [
            f"🎉 Yay! {m.from_user.first_name} subiu para o **Level {new_level}**! 🌸",
            f"✨ Woohoo! Você está mais forte agora, {m.from_user.first_name}! **Level {new_level}** alcançado! 💖",
            f"💛 Olha só! {m.from_user.first_name} evoluiu! **Level {new_level}** desbloqueado! 🐾",
            f"🌟 Parabéns, {m.from_user.first_name}! Seu esforço rendeu frutos! **Level {new_level}**! 🎀"
        ]
        msg = random.choice(level_up_msgs)
        if bonus_msg:
            msg += f"\n{bonus_msg}"
        bot.send_message(m.chat.id, msg, parse_mode="Markdown")

    # Mensagem XP normal (só a cada 5 msgs)
    elif give_xp:
        xp_msg = f"💛 {m.from_user.first_name} ganhou {xp_gain} XP! Total: {new_xp} XP."
        if bonus_msg:
            xp_msg += f"\n{bonus_msg}"
        bot.send_message(m.chat.id, xp_msg)

# ======================
# CALLBACKS
# ======================
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    cid = call.message.chat.id

    if call.data == "perfil":
        user = call.from_user
        user_id = str(user.id)
        user_data = get_user(user.id)

        xp = user_data.get("xp", 0)
        coins = user_data.get("coins", 0)
        level = xp // 100
        xp_next = (level + 1) * 100

        ranking = list(users_collection.find().sort("xp", -1))
        pos = next((i+1 for i, v in enumerate(ranking) if v["_id"] == user_id), "—")

        first_seen_raw = user_data.get("first_seen", None)
        if first_seen_raw:
            try:
                first_seen_struct = time.strptime(first_seen_raw, "%d/%m/%Y %H:%M")
                first_seen = time.strftime("%d.%m.%y %H:%M", first_seen_struct)
            except:
                first_seen = first_seen_raw
        else:
            first_seen = "Desconhecido"

        msg = f"""
╭━━━ 👤 PERFIL ━━━╮
👤 Nome: {user.first_name}
💌 Username: @{user.username if user.username else 'Não possui'}
🆔 ID: {user.id}

📅 Desde: {first_seen}

🏆 Level: {level}
✨ XP: {xp}/{xp_next}
💰 Coins: {coins}

🥇 Ranking: #{pos}
╰━━━━━━━━━━━━━━╯
"""
        bot.send_message(cid, msg)

    elif call.data == "ping":
        start_ping = time.time()
        msg_ping = bot.send_message(cid, "🏓 Pingando...")
        elapsed = int((time.time() - start_ping) * 1000)
        bot.edit_message_text(f"🏓 Pong! {elapsed} ms", cid, msg_ping.message_id)

    elif call.data == "waifu":
        try:
            user_id = call.from_user.id
            url = waifu_request("sfw")  # pega a waifu
            captions = [
                f"💛 Olha só que fofura, {call.from_user.first_name}! Uma waifu só pra você! 🌸",
                f"✨ Surpresa kawaii! Aqui vai uma waifu linda pra alegrar seu dia 💖",
                f"🌟 Um presentinho especial: waifu fresquinha para {call.from_user.first_name}! 🐾"
            ]
            bot.send_photo(cid, url, caption=random.choice(captions))

            xp_gain = random.randint(5, 15)
            coins_gain = random.randint(5, 20)
            add_xp(user_id, xp_gain)
            add_coins(user_id, coins_gain)
            bot.send_message(cid, f"💛 {call.from_user.first_name} ganhou {xp_gain} XP e {coins_gain} coins só por interagir com a waifu! 🌸")

        except Exception as e:
            bot.send_message(cid, f"❌️ Hmmm, não consegui pegar uma waifu agora 😢\n{e}")

    elif call.data == "info":
        try:
            msg = (
                f"🌼 **{BOT_NAME} Info** 🌼\n\n"
                f"⏱️ Uptime: {uptime_text()}\n"
                f"🛠️ Versão: {BOT_VERSION}\n"
                f"👤 Criador: {CREATOR}\n"
                f"💖 Divirta-se e interaja comigo!"
            )
            bot.send_message(cid, msg, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(cid, f"❌ Não consegui mostrar info 😢\n{e}")

    elif call.data == "menu_completo":
        bot.send_message(cid, MENU)

    bot.answer_callback_query(call.id)

# ======================
# PING
# ======================
@bot.message_handler(commands=['ping'])
def ping_command(m):
    start = time.time()
    msg = bot.send_message(m.chat.id, "🏓 Pingando...")
    elapsed = int((time.time() - start) * 1000)  # tempo em ms
    bot.edit_message_text(f"🏓 Pong! {elapsed} ms",
                          chat_id=m.chat.id,
                          message_id=msg.message_id)

# ======================
# LEVEL / RANK / ADDXP ESTILO HIKARI 🌸✨
# ======================

@bot.message_handler(commands=['level'])
def level(m):
    user_id = m.from_user.id
    user_data = get_user(user_id)
    user_xp = user_data.get("xp", 0)
    lvl = user_xp // 100
    next_level_xp = (lvl + 1) * 100
    xp_current = user_xp - (lvl * 100)
    xp_needed = next_level_xp - (lvl * 100)

    # Barra de XP: 10 blocos
    total_blocks = 10
    filled_blocks = int((xp_current / xp_needed) * total_blocks)
    empty_blocks = total_blocks - filled_blocks
    progress_bar = "💛" * filled_blocks + "▫️" * empty_blocks

    msg = (
        f"⭐ {m.from_user.first_name}\n"
        f"Level: {lvl}\n"
        f"XP: {xp_current}/{xp_needed}\n"
        f"{progress_bar}"
    )
    bot.reply_to(m, msg)


@bot.message_handler(commands=['rank'])
def rank(m):
    ranking = list(users_collection.find().sort("xp", -1))
    text = "🏆 Top 5 Hikari Friends\n\n"
    for i, user_data in enumerate(ranking[:5], start=1):
        try:
            member = bot.get_chat_member(m.chat.id, int(user_data["_id"]))
            name = member.user.first_name
        except:
            name = "Usuário"
        text += f"{i}. {name} - {user_data.get('xp',0)} XP\n"
    bot.send_message(m.chat.id, text)


@bot.message_handler(commands=['addxp'])
def addxp(m):
    user_id = m.from_user.id
    add_xp(user_id, 100)
    user_data = get_user(user_id)
    total_xp = user_data.get("xp",0)
    msg = (
        f"✨ Yeay! 100 XP adicionados para {m.from_user.first_name}! 💛\n"
        f"Total agora: {total_xp} XP."
    )
    bot.reply_to(m, msg)

# ======================
# COINS / DAILY / COINFLIP ESTILO HIKARI 🌸✨
# ======================

# 💰 Ver saldo
@bot.message_handler(commands=['saldo'])
def saldo(m):
    user_data = get_user(m.from_user.id)
    coins_amount = user_data.get("coins", 0)
    captions = [
        f"💛 {m.from_user.first_name}, você tem {coins_amount} coins fofinhos! 🌸",
        f"✨ Saldo atual: {coins_amount} coins 💖 Continue se divertindo!",
        f"🐾 Olha só! {m.from_user.first_name} possui {coins_amount} coins!"
    ]
    bot.reply_to(m, random.choice(captions))

# 🗓️ Daily coins
@bot.message_handler(commands=['daily'])
def daily(m):
    user_id = m.from_user.id
    user_data = get_user(user_id)
    now = time.time()
    cooldown = 86400  # 24h
    last = user_data.get("daily_cooldown", 0)

    if now - last < cooldown:
        remaining = int((cooldown - (now - last)) // 3600)
        bot.reply_to(m, f"⏳ Você já coletou hoje! Volte em {remaining}h 💛")
        return

    reward = random.randint(50, 150)
    add_coins(user_id, reward)
    users_collection.update_one({"_id": str(user_id)}, {"$set": {"daily_cooldown": now}})

    captions = [
        f"🌸 Yay! Você ganhou {reward} coins hoje! Continue assim 💖",
        f"💛 Dinheiro fofinho chegando! {reward} coins adicionados ao seu saldo 🌟",
        f"🐾 Daily coletado! {reward} coins para você, {m.from_user.first_name}!"
    ]
    bot.reply_to(m, random.choice(captions))

# 🪙 Coinflip estilo Hikari
@bot.message_handler(commands=['coinflip'])
def coinflip(m):
    user_id = m.from_user.id
    user_data = get_user(user_id)
    if user_data.get("coins",0) < 10:
        bot.reply_to(m,"🚫 Você precisa de pelo menos 10 coins para jogar!")
        return

    # Paga a aposta
    users_collection.update_one({"_id": str(user_id)}, {"$inc": {"coins": -10}})

    # Resultado do coinflip
    if random.choice([True, False]):
        add_coins(user_id, 20)
        result = f"🪙 Cara! Você ganhou 20 coins 👌🏻😎"
    else:
        result = f"🪙 Coroa! Que pena, você perdeu 🫵🏻😆"

    new_balance = get_user(user_id).get("coins",0)
    captions = [
        f"💛 {m.from_user.first_name}, {result}\nSaldo atual: {new_balance} coins 🌸",
        f"🌟 {result} Agora você tem {new_balance} coins 💖 Continue tentando!",
        f"🐾 Resultado do coinflip: {result}\n💛 Saldo atualizado: {new_balance}"
    ]
    bot.reply_to(m, random.choice(captions))

# ======================
# WAIFU / MEME / NSFW / DANBOORU COM RECOMPENSAS
# ======================

# Função para dar XP/Coins fofinho
def reward_user(user_id, xp_min=5, xp_max=15, coins_min=5, coins_max=20):
    xp_gain = random.randint(xp_min, xp_max)
    coins_gain = random.randint(coins_min, coins_max)
    add_xp(user_id, xp_gain)
    add_coins(user_id, coins_gain)
    return xp_gain, coins_gain

# Waifu SFW
@bot.message_handler(commands=['waifu'])
def waifu(m):
    try:
        user_id = m.from_user.id
        url = waifu_request("sfw")
        captions = [
            f"💛 Olha só que fofura, {m.from_user.first_name}! Uma waifu só pra você! 🌸",
            f"✨ Surpresa kawaii! Aqui vai uma waifu linda pra alegrar seu dia 💖",
            f"🌟 Um presentinho especial: waifu fresquinha para {m.from_user.first_name}! 🐾"
        ]
        bot.send_photo(m.chat.id, url, caption=random.choice(captions))
        
        # 💛 Recompensa
        xp_gain, coins_gain = reward_user(user_id)
        bot.send_message(m.chat.id, f"💛 {m.from_user.first_name} ganhou {xp_gain} XP e {coins_gain} coins só por interagir com a waifu! 🌸")

    except:
        bot.reply_to(m, "❌️ Hmmm, não consegui pegar uma waifu agora 😢")

# Waifu NSFW
@bot.message_handler(commands=['waifunsfw'])
def waifunsfw(m):
    if m.chat.type != "private":
        bot.reply_to(m, "🚫 NSFW só no privado! 😉")
        return
    try:
        user_id = m.from_user.id
        url = waifu_request("nsfw")
        captions = [
            f"🔥 Hey {m.from_user.first_name}, uma waifu sexy só pra você 😏",
            f"🔞 Surpresa safadinha! Curta com moderação 😈"
        ]
        bot.send_photo(m.chat.id, url, caption=random.choice(captions))
        
        xp_gain, coins_gain = reward_user(user_id, xp_min=10, xp_max=25, coins_min=10, coins_max=30)
        bot.send_message(m.chat.id, f"🔥 {m.from_user.first_name} ganhou {xp_gain} XP e {coins_gain} coins! 😏")

    except:
        bot.reply_to(m, "❌️ Não consegui pegar NSFW agora 😢")

# Meme
@bot.message_handler(commands=['meme'])
def meme(m):
    try:
        user_id = m.from_user.id
        r = requests.get("https://meme-api.com/gimme").json()
        captions = [
            f"🤣 Meme fresquinho pra você, {m.from_user.first_name}!\n{r['title']}",
            f"🌸 Risadas garantidas! {r['title']}",
        ]
        bot.send_photo(m.chat.id, r["url"], caption=random.choice(captions))
        
        xp_gain, coins_gain = reward_user(user_id)
        bot.send_message(m.chat.id, f"💛 {m.from_user.first_name} ganhou {xp_gain} XP e {coins_gain} coins só por rir um pouco! 😄")

    except:
        bot.reply_to(m, "❌ Erro ao pegar meme 😢")

# Danbooru
@bot.message_handler(commands=['danbooru'])
def danbooru(m):
    if m.chat.type != "private":
        bot.reply_to(m,"🚫 NSFW só no privado! 😉")
        return
    user_id = m.from_user.id
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m,"🔞 Use /danbooru termo")
        return
    query = args[1].replace(" ","_")
    try:
        r = requests.get(f"https://danbooru.donmai.us/posts.json?tags={query}&limit=50", timeout=10).json()
        if not r:
            bot.reply_to(m,"❌️ Nenhum resultado encontrado 😢")
            return
        post = random.choice(r)
        img_url = post.get("file_url") or post.get("large_file_url")
        captions = [
            f"🔥 {m.from_user.first_name}, olha que imagem Danbooru pra você 😏",
            f"🔞 Curta com moderação! {m.from_user.first_name}, aqui está o que você pediu 😉"
        ]
        bot.send_photo(m.chat.id, img_url, caption=random.choice(captions))
        
        # Recompensa NSFW
        xp_gain, coins_gain = reward_user(user_id, xp_min=15, xp_max=30, coins_min=15, coins_max=40)
        bot.send_message(m.chat.id, f"🔥 {m.from_user.first_name} ganhou {xp_gain} XP e {coins_gain} coins! 😏")

    except:
        bot.reply_to(m,"❌️ Erro ao buscar imagens Danbooru 😢")

# ======================
# GOOGLE / IMAGE / YOUTUBE PLAY 
# ======================

# Google Search
@bot.message_handler(commands=['google'])
def google(m):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m, "🔎 Use /google termo")
        return
    query = args[1]
    params = {"q": query, "engine": "google", "api_key": SERPAPI_KEY}
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=10).json()
        results = r.get("organic_results", [])
        if not results:
            bot.reply_to(m, f"❌ Nenhum resultado encontrado para '{query}' 😢")
            return
        msg = f"🔎 *Resultados para:* {query}\n\n"
        for res in results[:3]:
            msg += f"💛 {res['title']}\n🔗 {res['link']}\n\n"
        bot.send_message(m.chat.id, msg, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(m, f"❌ Erro na busca 😢\n{e}")


# Image Search
@bot.message_handler(commands=['image'])
def image(m):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m, "🖼️ Use /image termo")
        return
    query = args[1]
    params = {"engine": "google_images", "q": query, "api_key": SERPAPI_KEY}
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=10).json()
        imgs = r.get("images_results", [])
        if not imgs:
            bot.reply_to(m, f"❌ Nenhuma imagem encontrada para '{query}' 😢")
            return
        img = random.choice(imgs)
        captions = [
            f"💛 Olha só essa imagem de {query}! 🌸",
            f"✨ {m.from_user.first_name}, achei isso sobre {query} 😍",
            f"🌟 Aqui está a imagem que você pediu: {query} 💖"
        ]
        bot.send_photo(m.chat.id, img["original"], caption=random.choice(captions))
    except Exception as e:
        bot.reply_to(m, f"❌ Erro ao buscar imagem 😢\n{e}")


# YouTube Play
@bot.message_handler(commands=['song'])
def play(m):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m, "⏸️ Use /song <nome da música>")
        return
    query = args[1]
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={urllib.parse.quote_plus(query)}&key={YOUTUBE_KEY}&maxResults=1&type=video"
    try:
        r = requests.get(url, timeout=10).json()
        items = r.get("items", [])
        if not items:
            bot.reply_to(m, f"❌ Nenhum resultado encontrado para '{query}' 😢")
            return

        video = items[0]
        title = video["snippet"]["title"]
        channel = video["snippet"]["channelTitle"]
        vid = video["id"]["videoId"]
        thumb = video["snippet"]["thumbnails"]["high"]["url"]
        video_url = f"https://youtu.be/{vid}"

        captions = [
            f"🎵 *{title}*\n📺 {channel}\n🔗 [Assistir/Download]({video_url})",
            f"💛 Música fresquinha pra você, {m.from_user.first_name}!\n🎶 {title} - {channel}\n🔗 [Link]({video_url})"
        ]
        bot.send_photo(m.chat.id, thumb, caption=random.choice(captions), parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(m, f"❌ Erro ao buscar música 😢\n{e}")

# ======================
# DADO / SHIP ESTILO HIKARI 🌸✨
# ======================

# 🎲 Dado fofinho
@bot.message_handler(commands=['dado'])
def dado(m):
    roll = random.randint(1, 6)
    captions = [
        f"🎲 {m.from_user.first_name} rolou o dado e saiu: *{roll}* 🌸",
        f"✨ Olha só! {m.from_user.first_name} tirou {roll} no dado 💛",
        f"💖 Yay! Número sorteado: *{roll}* para {m.from_user.first_name}!"
    ]
    bot.reply_to(m, random.choice(captions), parse_mode="Markdown")

# 💕 Ship Hikari Style
@bot.message_handler(commands=['ship'])
def ship(m):
    if not m.reply_to_message:
        bot.reply_to(m,"💭 Responda alguém para shippar")
        return
    score = random.randint(1, 100)
    user1 = m.from_user.first_name
    user2 = m.reply_to_message.from_user.first_name

    # Mensagens fofas de compatibilidade
    if score > 90:
        msg = f"🌟 Incrível! {user1} + {user2} = {score}% compatibilidade 💛💖"
    elif score > 70:
        msg = f"💛 Bem combinados! {user1} + {user2} = {score}%"
    elif score > 40:
        msg = f"💭 Hmmm... {user1} + {user2} = {score}% compatibilidade 🌸"
    else:
        msg = f"😅 Meio difícil, {user1} + {user2} = {score}% 😆"

    bot.send_message(m.chat.id, msg)

# ======================
# USERINFO ESTILO HIKARI 🌸✨
# ======================
@bot.message_handler(commands=['userinfo'])
def userinfo(m):
    user = m.from_user
    user_id = str(user.id)

    # Pega os dados do MongoDB
    user_data = get_user(user_id)
    xp = user_data.get("xp", 0)
    coins = user_data.get("coins", 0)
    first_seen = user_data.get("first_seen", "Desconhecido")
    
    level = xp // 100
    xp_next = (level + 1) * 100
    xp_in_level = xp % 100

    # Ranking
    ranking = list(users_collection.find().sort("xp", -1))
    pos = next((i + 1 for i, v in enumerate(ranking) if v["_id"] == user_id), "—")

    # Barra de XP estilo Hikari
    total_blocks = 10
    filled_blocks = int((xp_in_level / 100) * total_blocks)
    empty_blocks = total_blocks - filled_blocks
    xp_bar = "💛" * filled_blocks + "▫️" * empty_blocks

    # Mensagens Hikari fofinhas
    captions = [
        f"🌸 Olha só quem está brilhando! {user.first_name} 🌟",
        f"💖 Perfil fofinho de {user.first_name}! Continue arrasando!",
        f"🐾 Yay! {user.first_name}, você está progredindo muito!",
        f"✨ Confira o perfil de {user.first_name}! Que charme!"
    ]
    caption = random.choice(captions)

    # Pega a foto do usuário ou do bot como fallback
    photos = bot.get_user_profile_photos(user.id)
    if photos.total_count > 0:
        file_id = photos.photos[0][-1].file_id
        bot.send_photo(
            m.chat.id, 
            file_id, 
            caption=f"{caption}\n\n"
                    f"👤 Nome: {user.first_name}\n"
                    f"💌 Username: @{user.username if user.username else 'Não possui'}\n"
                    f"🆔 ID: {user.id}\n"
                    f"📅 Desde: {first_seen}\n\n"
                    f"🏆 Level: {level}\n"
                    f"✨ XP: [{xp_bar}] {xp_in_level}/{100}\n"
                    f"💰 Coins: {coins}\n"
                    f"🥇 Ranking: #{pos}",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            m.chat.id,
            f"{caption}\n\n"
            f"👤 Nome: {user.first_name}\n"
            f"💌 Username: @{user.username if user.username else 'Não possui'}\n"
            f"🆔 ID: {user.id}\n"
            f"📅 Desde: {first_seen}\n\n"
            f"🏆 Level: {level}\n"
            f"✨ XP: [{xp_bar}] {xp_in_level}/{100}\n"
            f"💰 Coins: {coins}\n"
            f"🥇 Ranking: #{pos}",
            parse_mode="Markdown"
        )

# ======================
# PIN / UNPIN MENSAGEM
# ======================
@bot.message_handler(commands=['pin'])
def pin(m):
    if not m.reply_to_message:
        bot.reply_to(m, "📋 Responda a uma mensagem para fixar.")
        return
    try:
        # URL do GIF hospedado no GitHub (raw)
        gif_url = "https://github.com/Ni1kuu/hikari-bot/raw/main/PinDown.io_%40blackirisblog_1773786904.gif"

        # Pega o texto da mensagem original
        original_text = m.reply_to_message.text or "📎 Sem texto"

        # Legenda melhorada
        caption = (
            f"📌 *Mensagem fofinha fixada!* 💛\n"
            f"💌 Quem fixou: {m.from_user.first_name}\n\n"
            f"📝 Conteúdo:\n{original_text}"
        )

        # Envia o GIF com a legenda
        bot.send_animation(
            chat_id=m.chat.id,
            animation=gif_url,
            caption=caption,
            parse_mode="Markdown"
        )

        # Tenta fixar a mensagem original
        bot.pin_chat_message(m.chat.id, m.reply_to_message.message_id)

    except Exception as e:
        bot.reply_to(m, f"❌ Ops! Não consegui desfixar a mensagem 😢.\nErro: {e}")

# 📌 UNPIN
@bot.message_handler(commands=['unpin'])
def unpin(m):
    try:
        # Se respondeu a uma mensagem, desfixa ela
        if m.reply_to_message:
            bot.unpin_chat_message(m.chat.id, message_id=m.reply_to_message.message_id)
            bot.reply_to(m, f"🔓 Mensagem desfixada com sucesso! 💛")
        else:
            # Senão, desfixa a última mensagem fixada
            bot.unpin_chat_message(m.chat.id)
            bot.reply_to(m, f"🔓 Última mensagem desfixada com sucesso! 💛")
    except Exception as e:
        bot.reply_to(m, f"❌ Ops! Não consegui desfixar a mensagem 😢\nErro: {e}")

# 🗑 UNPINALL
@bot.message_handler(commands=['unpinall'])
def unpin_all(m):
    try:
        bot.unpin_all_chat_messages(m.chat.id)
        bot.reply_to(m, f"🔓 Todas as mensagens fixadas foram desfixadas com amor! 🌼💛")
    except Exception as e:
        bot.reply_to(m, f"❌ Ops! Não consegui desfixar todas as mensagens 😢\nErro: {e}")

# ======================
# MODERAÇÃO KAWAII HIKARI 🌸✨
# ======================

# 🚫 BAN
@bot.message_handler(commands=['ban'])
def ban(m):
    if not m.reply_to_message:
        bot.reply_to(m, "💛 Responda alguém para banir fofinho! ✨")
        return
    try:
        target = m.reply_to_message.from_user
        bot.ban_chat_member(m.chat.id, target.id)
        bot.reply_to(m, f"🚫 Putz! {target.first_name} foi banido! 💨\nNão se preocupe, Hikari cuida do grupo 🌸")
    except Exception as e:
        bot.reply_to(m, f"💛 Ops! Não consegui banir {target.first_name} 😢\nErro: {e}")


# ⚠️ WARN
@bot.message_handler(commands=['warn'])
def warn(m):
    if not m.reply_to_message:
        bot.reply_to(m, "💛 Responda alguém para avisar fofinho! ✨")
        return
    uid = m.reply_to_message.from_user.id
    target_name = m.reply_to_message.from_user.first_name
    warns[uid] = warns.get(uid, 0) + 1
    total_warns = warns[uid]

    bot.reply_to(m, f"⚠️ {target_name}, você recebeu um aviso!\nTotal de avisos: {total_warns} 💛")

    if total_warns >= 3:
        try:
            bot.ban_chat_member(m.chat.id, uid)
            bot.send_message(m.chat.id, f"🚫 {target_name} foi banido por acumular 3 avisos! 💨\nHikari não deixa bagunça no grupo 🌸")
            warns[uid] = 0  # Resetar avisos após ban
        except Exception as e:
            bot.send_message(m.chat.id, f"💛 Não consegui banir {target_name} 😢\nErro: {e}")


# 🔇 MUTE
@bot.message_handler(commands=['mute'])
def mute(m):
    if not m.reply_to_message:
        bot.reply_to(m, "💛 Responda alguém para mutar! 🤫")
        return
    try:
        target = m.reply_to_message.from_user
        bot.restrict_chat_member(m.chat.id, target.id, can_send_messages=False)
        bot.reply_to(m, f"🔇 Shhh! {target.first_name} foi mutado com carinho 🌸")
    except Exception as e:
        bot.reply_to(m, f"💛 Não consegui mutar {target.first_name} 😢\nErro: {e}")


# 🔊 UNMUTE
@bot.message_handler(commands=['unmute'])
def unmute(m):
    if not m.reply_to_message:
        bot.reply_to(m, "💛 Responda alguém para desmutar! 🎶")
        return
    try:
        target = m.reply_to_message.from_user
        bot.restrict_chat_member(m.chat.id, target.id, can_send_messages=True)
        bot.reply_to(m, f"🔊 Yay! {target.first_name} foi desmutado! 🌸 Volte a conversar 🥰")
    except Exception as e:
        bot.reply_to(m, f"❌️ Ops! Não consegui desmutar {target.first_name} 😢\nErro: {e}")


# 🧹 LIMPAR MENSAGENS
@bot.message_handler(commands=['limpar'])
def limpar(m):
    args = m.text.split()
    if len(args) < 2:
        bot.reply_to(m, "🧹 Use: /limpar <quantidade> (máx 50) 🌸")
        return
    try:
        n = min(int(args[1]), 50)
        for i in range(n):
            try:
                bot.delete_message(m.chat.id, m.message_id - i)
            except:
                pass
        bot.reply_to(m, f"🧹 {n} mensagens apagadas com amor! 💛✨")
    except ValueError:
        bot.reply_to(m, "❌️ Número inválido 😢")


# 🚫 ANTILINK
@bot.message_handler(commands=['antilink'])
def antilink_cmd(m):
    args = m.text.split()
    if len(args) < 2:
        bot.reply_to(m, "💡 Use: /antilink on ou /antilink off 🌸")
        return

    if args[1].lower() == "on":
        antilink[m.chat.id] = True
        bot.reply_to(m, "🚫 Antilink ativado! Hikari protegerá o grupo de links indesejados 💛✨")
    elif args[1].lower() == "off":
        antilink[m.chat.id] = False
        bot.reply_to(m, "✅ Antilink desativado! Agora links são permitidos 😉🌸")
    else:
        bot.reply_to(m, "💡 Comando inválido! Use /antilink on ou /antilink off 😅")

# ======================
# GLOBAL HANDLER (ANTILINK) 🌸
# ======================
ANTILINK_GIF = "https://forum.treeofsavior.com/uploads/default/original/3X/b/6/b6486d06486a05685b50e01a3c83e44a17b9ba42.gif"

@bot.message_handler(func=lambda m: True)
def global_handler(m):
    if not m.text:
        return

    if antilink.get(m.chat.id):
        forbidden = ["http://", "https://", "t.me/"]
        if any(f in m.text.lower() for f in forbidden):
            try:
                # deleta a mensagem com link
                bot.delete_message(m.chat.id, m.message_id)

                # tenta banir o usuário
                bot.ban_chat_member(m.chat.id, m.from_user.id)

                # envia o GIF com legenda cute
                bot.send_animation(
                    m.chat.id,
                    ANTILINK_GIF,
                    caption=(
                        f"🚫 Oops! {m.from_user.first_name}, links não são permitidos 🌸\n"
                        "Hikari protege o grupo! 💛"
                    )
                )

            except Exception as e:
                print(f"Erro no antilink: {e}")

# ======================
# WELCOME / GOODBYE
# ======================
@bot.message_handler(content_types=['new_chat_members'])
def welcome(m):
    for user in m.new_chat_members:
        hora = time.strftime("%d.%m.%y %H:%M")  # Data e hora completas
        msg = f"🌼 Bem-vindo {user.first_name}!\n🕒 Entrou em: {hora}"
        try:
            bot.send_animation(
                m.chat.id,
                "https://media.tenor.com/pt-BR/view/welcome-new-members-senko-san-cute-anime-welcome-gif-26050520.gif",
                caption=msg
            )
        except:
            bot.send_message(m.chat.id, msg)

@bot.message_handler(content_types=['left_chat_member'])
def goodbye(m):
    user = m.left_chat_member
    if user:
        hora = time.strftime("%d.%m.%y %H:%M")  # Data e hora completas
        msg = f"🌼 {user.first_name} saiu do grupo em: {hora}"
        try:
            bot.send_animation(
                m.chat.id,
                "https://media.tenor.com/pt-BR/view/anime-roka-shibasaki-%E6%9F%B4%E5%B4%8E-%E8%8A%A6%E8%8A%B1-gif-13007334342926281309.gif",
                caption=msg
            )
        except:
            bot.send_message(m.chat.id, msg)

# ======================
# INICIAR BOT
# ======================
bot.remove_webhook()
print(f"🤖 {BOT_NAME} iniciado com sucesso! Rodando polling...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)