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

BOT_VERSION = "2.5"
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
🎞 /waifugif - Waifu GIF
🔞 /waifunsfw - Waifu NSFW
🔞 /gifnsfw - GIF NSFW
🤣 /meme - Meme aleatório
🎵 /song <música> - Buscar no YouTube
🔍 /google <termo> - Buscar no Google
🖼 /image <termo> - Buscar imagem
🪙 /coinflip - Jogo de coinflip
╰─────────────╯
╭─ 🌸 Sistema ─╮
🏓 /ping - Ping do bot
💌 /avatar - Ver avatar
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
Divirta-se e aproveite! ꒰ᐢ. .ᐢ꒱₊˚⊹ 💖
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

        first_seen = user_data.get("first_seen", "Desconhecido")

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
            url = waifu_request("sfw")
            bot.send_photo(cid, url)
        except:
            bot.send_message(cid, "Erro ao pegar waifu")

    elif call.data == "info":
        bot.send_message(
            cid,
            f"{BOT_NAME}\nUptime: {uptime_text()}\nVersão: {BOT_VERSION}"
        )

    elif call.data == "menu_completo":
        bot.send_message(cid, MENU)

    bot.answer_callback_query(call.id)

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

@bot.message_handler(commands=['saldo'])
def saldo(m):
    user_data = get_user(m.from_user.id)
    coins_amt = user_data.get('coins', 0)
    msg = f"💛 Olá {m.from_user.first_name}! Seu saldo atual é: **{coins_amt} coins** 🪙\nContinue interagindo para ganhar mais!"
    bot.reply_to(m, msg, parse_mode="Markdown")


@bot.message_handler(commands=['daily'])
def daily(m):
    user_id = m.from_user.id
    user_data = get_user(user_id)
    now = time.time()
    cooldown = 86400  # 24h
    last = user_data.get("daily_cooldown", 0)
    
    if now - last < cooldown:
        remaining = int((cooldown - (now - last)) // 3600)
        bot.reply_to(m, f"⏳ Você já coletou hoje! Volte em ~{remaining}h para pegar de novo.")
        return

    reward = random.randint(75, 200)  # valor mais divertido
    add_coins(user_id, reward)
    users_collection.update_one({"_id": str(user_id)}, {"$set": {"daily_cooldown": now}})
    
    messages = [
        f"✨ Yay! Você ganhou {reward} coins hoje! 💛 Continue firme, {m.from_user.first_name}!",
        f"💖 Moedinhas fresquinhas: {reward} coins! Aproveite seu dia! 🌸",
        f"🌟 Daily coletado! {m.from_user.first_name}, {reward} coins chegaram para você! 🪙",
    ]
    bot.reply_to(m, random.choice(messages))


@bot.message_handler(commands=['coinflip'])
def coinflip(m):
    user_id = m.from_user.id
    user_data = get_user(user_id)
    coins_amt = user_data.get('coins', 0)
    
    if coins_amt < 10:
        bot.reply_to(m, "🚫 Ops! Você precisa de pelo menos 10 coins para jogar.")
        return

    # Retira 10 coins
    users_collection.update_one({"_id": str(user_id)}, {"$inc": {"coins": -10}})

    # Resultado do coinflip
    win = random.choice([True, False])
    if win:
        reward = random.randint(15, 30)
        add_coins(user_id, reward)
        result_msg = f"🪙 Cara! Você ganhou {reward} coins 😎👌🏻"
    else:
        result_msg = "🪙 Coroa! Você perdeu 🫵🏻😆"

    user_data = get_user(user_id)
    new_balance = user_data.get("coins",0)
    
    # Mensagens estilo Hikari
    messages = [
        f"{result_msg}\n💛 Saldo atual: {new_balance} coins",
        f"🎲 Que emoção! {result_msg}\n💖 Agora você tem {new_balance} coins",
        f"🌸 Coinflip resultado: {result_msg}\n✨ Total de coins: {new_balance}"
    ]
    bot.reply_to(m, random.choice(messages))

# ======================
# WAIFU / GIF / MEME / NSFW / DANBOORU ESTILO HIKARI 🌸✨ COM RECOMPENSAS
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

# Waifu GIF
@bot.message_handler(commands=['waifugif'])
def waifugif(m):
    try:
        user_id = m.from_user.id
        url = waifu_request("sfw", gif=True)
        captions = [
            f"💛 Waifu GIF fofinha pra você! {m.from_user.first_name}, olha que charme! 🌸",
            f"✨ GIF fresquinho chegando! Que lindinha 😍",
        ]
        bot.send_animation(m.chat.id, url, caption=random.choice(captions))
        
        xp_gain, coins_gain = reward_user(user_id)
        bot.send_message(m.chat.id, f"💛 {m.from_user.first_name} ganhou {xp_gain} XP e {coins_gain} coins! 🌸")

    except:
        bot.reply_to(m, "❌️ Erro ao pegar GIF fofinho 😢")

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
            f"🔞 Surpresa safadinha! Curta com moderação 😘"
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

# GIF
@bot.message_handler(commands=['gif'])
def gif(m):
    user_id = m.from_user.id
    query = "anime"
    args = m.text.split(maxsplit=1)
    if len(args) > 1:
        query = args[1]
    try:
        url = "https://api.giphy.com/v1/gifs/search"
        params = {"api_key": GIPHY_KEY,"q": query,"limit": 25}
        r = requests.get(url,params=params).json()
        data = r.get("data",[])
        if not data:
            bot.reply_to(m,"❌ Nenhum gif encontrado 😢")
            return
        gif_url = random.choice(data)["images"]["original"]["url"]
        bot.send_animation(m.chat.id,gif_url, caption=f"✨ GIF {query} fresquinho!")

        xp_gain, coins_gain = reward_user(user_id)
        bot.send_message(m.chat.id, f"💛 {m.from_user.first_name} ganhou {xp_gain} XP e {coins_gain} coins! 🌸")

    except:
        bot.reply_to(m,"❌ Erro ao buscar gif 😢")

# ======================
# DANBOORU / GIF NSFW COM RECOMPENSAS 🌸✨
# ======================

# GIF NSFW
@bot.message_handler(commands=['gifnsfw'])
def gifnsfw(m):
    if m.chat.type != "private":
        bot.reply_to(m, "🚫 NSFW só no privado! 😉")
        return
    user_id = m.from_user.id
    try:
        headers = {"User-Agent": "TelegramBot"}
        r = requests.get("https://api.redgifs.com/v2/gifs/search?search_text=nsfw&count=50", headers=headers, timeout=10).json()
        gifs = r.get("gifs", [])
        if not gifs:
            bot.reply_to(m, "❌ Nenhum GIF encontrado 😢")
            return
        gif = random.choice(gifs)
        url = gif.get("urls", {}).get("hd") or gif.get("urls", {}).get("sd")
        if not url:
            bot.reply_to(m, "❌ Erro ao pegar GIF 😢")
            return
        captions = [
            f"🔥 Hey {m.from_user.first_name}, um GIF sexy só pra você 😏",
            f"🔞 Surpresinha safadinha! Curta com moderação 😉"
        ]
        bot.send_animation(m.chat.id, url, caption=random.choice(captions))
        
        # Recompensa maior por NSFW
        xp_gain, coins_gain = reward_user(user_id, xp_min=15, xp_max=30, coins_min=15, coins_max=40)
        bot.send_message(m.chat.id, f"🔥 {m.from_user.first_name} ganhou {xp_gain} XP e {coins_gain} coins! 😏")

    except:
        bot.reply_to(m, "❌ Não consegui pegar o GIF agora 😢")


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
@bot.message_handler(commands=['google'])
def google(m):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m,"Use /google termo")
        return
    query = args[1]
    params = {"q": query,"engine":"google","api_key":SERPAPI_KEY}
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=10).json()
        results = r.get("organic_results",[])
        if not results:
            bot.reply_to(m,"Nenhum resultado encontrado")
            return
        msg = f"🔎 {query}\n\n"
        for res in results[:3]:
            msg += f"{res['title']}\n{res['link']}\n\n"
        bot.send_message(m.chat.id,msg)
    except:
        bot.reply_to(m,"Erro na busca")

@bot.message_handler(commands=['image'])
def image(m):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m,"Use /image termo")
        return
    query = args[1]
    params = {"engine":"google_images","q":query,"api_key":SERPAPI_KEY}
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=10).json()
        imgs = r.get("images_results",[])
        if not imgs:
            bot.reply_to(m,"Nenhuma imagem encontrada")
            return
        img = random.choice(imgs)
        bot.send_photo(m.chat.id,img["original"], caption=query)
    except:
        bot.reply_to(m,"Erro ao buscar imagem")

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
            bot.reply_to(m, "❌ Nenhum resultado encontrado")
            return

        video = items[0]
        title = video["snippet"]["title"]
        channel = video["snippet"]["channelTitle"]
        vid = video["id"]["videoId"]
        thumb = video["snippet"]["thumbnails"]["high"]["url"]
        video_url = f"https://youtu.be/{vid}"

        caption = f"🎵 *{title}*\n📺 {channel}\n🔗 [Assistir/Download]({video_url})"
        bot.send_photo(m.chat.id, thumb, caption=caption, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(m, f"❌ Erro ao buscar música\n{e}")

# ======================
# DADO / SHIP
# ======================
@bot.message_handler(commands=['dado'])
def dado(m):
    bot.reply_to(m,f"🎲 {random.randint(1,6)}")

@bot.message_handler(commands=['ship'])
def ship(m):
    if not m.reply_to_message:
        bot.reply_to(m,"💭 Responda alguém para shippar")
        return
    score = random.randint(1,100)
    user1 = m.from_user.first_name
    user2 = m.reply_to_message.from_user.first_name
    bot.send_message(m.chat.id,f"💕 {user1} + {user2}\nCompatibilidade: {score}%")

# ======================
# USERINFO / AVATAR
# ======================
@bot.message_handler(commands=['userinfo'])
def userinfo(m):
    user = m.from_user
    user_id = str(user.id)

    # Pega os dados do usuário do MongoDB
    user_data = get_user(user_id)

    xp = user_data.get("xp", 0)
    coins = user_data.get("coins", 0)
    first_seen = user_data.get("first_seen", "Desconhecido")

    level = xp // 100
    xp_next = (level + 1) * 100

    # Ranking
    ranking = list(users_collection.find().sort("xp", -1))
    pos = next((i + 1 for i, v in enumerate(ranking) if v["_id"] == user_id), "—")

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
    bot.reply_to(m, msg)

# ======================
# AVATAR COMPLETO
# ======================
@bot.message_handler(commands=['avatar'])
def avatar(m):
    # Define o usuário alvo: se for resposta, pega o usuário respondido, senão o próprio
    if m.reply_to_message:
        user = m.reply_to_message.from_user
    else:
        user = m.from_user

    # Pega as fotos de perfil do usuário
    photos = bot.get_user_profile_photos(user.id)

    if photos.total_count > 0:
        # Seleciona a foto mais recente
        file_id = photos.photos[0][-1].file_id

        captions = [
            f"✨ Aqui está a foto de perfil de {user.first_name}! 🌸 Olha só que fofura!",
            f"🖼 Olha quem apareceu! É o perfil de {user.first_name} 🌟 Muito estiloso(a)!",
            f"👀 Dê uma olhadinha no perfil de {user.first_name}! 🔥",
            f"📸 Foto fresquinha de {user.first_name}! Que charme 😎",
        ]
        caption = random.choice(captions)
        bot.send_photo(m.chat.id, file_id, caption=caption)

    else:
        # Se não tiver foto, mostra a foto do bot ou grupo
        try:
            bot_photo = bot.get_user_profile_photos(bot.get_me().id)
            if bot_photo.total_count > 0:
                file_id = bot_photo.photos[0][-1].file_id
                bot.send_photo(m.chat.id, file_id, caption="😅 Este usuário não tem foto, mas olha a minha!")
            else:
                bot.reply_to(m, "❌️ Usuário sem foto de perfil e eu também não tenho 😭")
        except:
            bot.reply_to(m, "❌️ Usuário sem foto de perfil e não consegui pegar a minha 😭")

# ======================
# PIN / UNPIN MENSAGEM
# ======================
@bot.message_handler(commands=['pin'])
def pin(m):
    if not m.reply_to_message:
        bot.reply_to(m, "📋 Responda a uma mensagem para fixar.")
        return
    try:
        bot.pin_chat_message(m.chat.id, m.reply_to_message.message_id)
        bot.reply_to(m, "📌 Mensagem fixada!")
    except:
        bot.reply_to(m, "❌️ Não consegui fixar a mensagem.")

@bot.message_handler(commands=['unpin'])
def unpin(m):
    try:
        bot.unpin_chat_message(m.chat.id)
        bot.reply_to(m, "📌 Mensagem desfixada!")
    except:
        bot.reply_to(m, "❌️ Não consegui desfixar a mensagem.")

# ======================
# MODERAÇÃO (BAN / WARN / MUTE / UNMUTE / LIMPAR / ANTILINK)
# ======================
@bot.message_handler(commands=['ban'])
def ban(m):
    if not m.reply_to_message:
        bot.reply_to(m,"💛 Responda alguém para banir")
        return
    try:
        bot.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
        bot.reply_to(m,"🚫 Usuário banido")
    except:
        bot.reply_to(m,"💛 Não consegui banir")

@bot.message_handler(commands=['warn'])
def warn(m):
    if not m.reply_to_message:
        bot.reply_to(m,"💛 Responda alguém para avisar")
        return
    uid = m.reply_to_message.from_user.id
    warns[uid] = warns.get(uid,0) + 1
    bot.reply_to(m,f"⚠️ Aviso para {m.reply_to_message.from_user.first_name}\nTotal: {warns[uid]}")
    if warns[uid] >= 3:
        try:
            bot.ban_chat_member(m.chat.id, uid)
            bot.send_message(m.chat.id,"🚫 Banido por 3 avisos")
        except:
            pass

@bot.message_handler(commands=['mute'])
def mute(m):
    if not m.reply_to_message:
        return
    try:
        bot.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id, can_send_messages=False)
        bot.reply_to(m,"🔇 Mutado")
    except:
        bot.reply_to(m,"💛 Não consegui mutar")

@bot.message_handler(commands=['unmute'])
def unmute(m):
    if not m.reply_to_message:
        return
    try:
        bot.restrict_chat_member(m.chat.id, m.reply_to_message.from_user.id, can_send_messages=True)
        bot.reply_to(m,"🔊 Desmutado")
    except:
        bot.reply_to(m,"❌️ Não consegui desmutar")

@bot.message_handler(commands=['limpar'])
def limpar(m):
    args = m.text.split()
    if len(args) < 2:
        bot.reply_to(m,"🧹 Use: /limpar <quantidade>")
        return
    try:
        n = min(int(args[1]),50)
        for i in range(n):
            try:
                bot.delete_message(m.chat.id,m.message_id-i)
            except:
                pass
        bot.reply_to(m,f"🧹 {n} mensagens apagadas")
    except:
        bot.reply_to(m,"❌️ Número inválido")

@bot.message_handler(commands=['antilink'])
def antilink_cmd(m):
    args = m.text.split()
    if len(args) < 2:
        return
    if args[1].lower() == "on":
        antilink[m.chat.id] = True
        bot.reply_to(m,"🚫 Antilink ativado")
    elif args[1].lower() == "off":
        antilink[m.chat.id] = False
        bot.reply_to(m,"✅ Antilink desativado")

# ======================
# GLOBAL HANDLER (ANTILINK)
# ======================
@bot.message_handler(func=lambda m: True)
def global_handler(m):
    if m.text and antilink.get(m.chat.id):
        if "http" in m.text or "t.me" in m.text:
            try:
                bot.delete_message(m.chat.id,m.message_id)
                bot.ban_chat_member(m.chat.id,m.from_user.id)
                bot.send_message(m.chat.id,"🚫 Link proibido!")
            except:
                pass

# ======================
# WELCOME / GOODBYE
# ======================
@bot.message_handler(content_types=['new_chat_members'])
def welcome(m):
    for user in m.new_chat_members:
        hora = time.strftime("%H:%M")
        msg = f"🌼 Bem-vindo {user.first_name}!\n🕒 Entrou às: {hora}"
        try:
            bot.send_photo(m.chat.id,"https://i.imgur.com/9XnK8YB.jpeg",caption=msg)
        except:
            bot.send_message(m.chat.id,msg)

@bot.message_handler(content_types=['left_chat_member'])
def goodbye(m):
    user = m.left_chat_member
    if user:
        hora = time.strftime("%H:%M")
        msg = f"🌼 {user.first_name} saiu do grupo às {hora}"
        try:
            bot.send_photo(m.chat.id,"https://i.imgur.com/9XnK8YB.jpeg",caption=msg)
        except:
            bot.send_message(m.chat.id,msg)

# ======================
# INICIAR BOT
# ======================
print(f"{BOT_NAME} iniciado...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)