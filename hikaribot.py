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
# XP AUTOMÁTICO
# ======================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def gain_xp(m):
    add_xp(m.from_user.id, 5)

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
# XP / LEVEL / RANK
# ======================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def gain_xp(m):
    user = str(m.from_user.id)
    now = time.time()
    if user in last_xp and now - last_xp[user] < 10:
        return
    last_xp[user] = now
    xp[user] = xp.get(user, 0) + 5
    save_data()

@bot.message_handler(commands=['level'])
def level(m):
    user = str(m.from_user.id)
    user_xp = xp.get(user, 0)
    lvl = user_xp // 100
    bot.reply_to(m, f"⭐ {m.from_user.first_name}\nXP: {user_xp}\nLevel: {lvl}")

@bot.message_handler(commands=['addxp'])
def addxp(m):
    user = str(m.from_user.id)
    xp[user] = xp.get(user, 0) + 100
    save_data()
    bot.reply_to(m,f"✅ 100 XP adicionados! Total: {xp[user]} XP")

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
# COINS / DAILY / COINFLIP
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

@bot.message_handler(commands=['coinflip'])
def coinflip(m):
    user = str(m.from_user.id)
    if coins.get(user,0) < 10:
        bot.reply_to(m,"🚫 Você precisa de 10 coins")
        return
    coins[user] -= 10
    if random.choice([True,False]):
        coins[user] += 20
        result = "🪙 Cara! Você ganhou 😎👌🏻"
    else:
        result = "🪙 Coroa! Você perdeu 🫵🏻😆"
    save_data()
    bot.reply_to(m,f"{result}\nSaldo: {coins[user]}")

# ======================
# WAIFU / GIF / MEME / NSFW / DANBOORU
# ======================
# Waifu SFW
@bot.message_handler(commands=['waifu'])
def waifu(m):
    try:
        bot.send_photo(m.chat.id, waifu_request("sfw"), caption="💛 Uma waifu fofinha pra você!")
    except:
        bot.reply_to(m, "❌️ Erro ao pegar waifu")

# Waifu GIF
@bot.message_handler(commands=['waifugif'])
def waifugif(m):
    try:
        bot.send_animation(m.chat.id, waifu_request("sfw", gif=True), caption="💛 Waifu GIF fofinha!")
    except:
        bot.reply_to(m, "❌️ Erro ao pegar GIF")

# Waifu NSFW
@bot.message_handler(commands=['waifunsfw'])
def waifunsfw(m):
    if m.chat.type != "private":
        bot.reply_to(m,"🚫 NSFW só no privado!")
        return
    try:
        bot.send_photo(m.chat.id, waifu_request("nsfw"), caption="🔞 Uma waifu sexy 😏")
    except:
        bot.reply_to(m,"❌️ Erro ao pegar NSFW")

# GIF NSFW
@bot.message_handler(commands=['gifnsfw'])
def gifnsfw(m):
    if m.chat.type != "private":
        bot.reply_to(m, "🚫 NSFW só no privado!")
        return
    try:
        headers = {"User-Agent": "TelegramBot"}
        r = requests.get("https://api.redgifs.com/v2/gifs/search?search_text=nsfw&count=50", headers=headers, timeout=10).json()
        gifs = r.get("gifs", [])
        if not gifs:
            bot.reply_to(m, "❌ Nenhum GIF encontrado")
            return
        gif = random.choice(gifs)
        url = gif.get("urls", {}).get("hd") or gif.get("urls", {}).get("sd")
        if not url:
            bot.reply_to(m, "❌ Erro ao pegar GIF")
            return
        bot.send_animation(m.chat.id, url, caption="🔥 Sexy pra você 😏🔞")
    except:
        bot.reply_to(m, "❌ Não consegui pegar o GIF agora")

# Meme
@bot.message_handler(commands=['meme'])
def meme(m):
    try:
        r = requests.get("https://meme-api.com/gimme").json()
        bot.send_photo(m.chat.id, r["url"], caption=r["title"])
    except:
        bot.reply_to(m,"Erro ao pegar meme")

# GIF
@bot.message_handler(commands=['gif'])
def gif(m):
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
            bot.reply_to(m,"Nenhum gif encontrado")
            return
        gif_url = random.choice(data)["images"]["original"]["url"]
        bot.send_animation(m.chat.id,gif_url)
    except:
        bot.reply_to(m,"Erro ao buscar gif")

# Danbooru
@bot.message_handler(commands=['danbooru'])
def danbooru(m):
    if m.chat.type != "private":
        bot.reply_to(m,"🚫 NSFW só no privado!")
        return
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m,"🔞 Use /danbooru termo")
        return
    query = args[1].replace(" ","_")
    try:
        r = requests.get(f"https://danbooru.donmai.us/posts.json?tags={query}&limit=50", timeout=10).json()
        if not r:
            bot.reply_to(m,"❌️ Nenhum resultado encontrado")
            return
        post = random.choice(r)
        img_url = post.get("file_url") or post.get("large_file_url")
        bot.send_photo(m.chat.id, img_url, caption=f"🔞 {query}")
    except:
        bot.reply_to(m,"❌️ Erro ao buscar imagens Danbooru")

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
    # Se responder a alguém, pega os dados dessa pessoa
    if m.reply_to_message:
        user = m.reply_to_message.from_user
    else:
        user = m.from_user

    msg = (
        f"✨️🌼 USERINFO 🌼✨️\n\n"
        f"Nome: {user.first_name}\n"
        f"Username: @{user.username if user.username else 'Não possui'}\n"
        f"ID: {user.id}\n"
        f"Bot: {user.is_bot}"
    )
    bot.send_message(m.chat.id, msg)

# ======================
# AVATAR
# ======================
@bot.message_handler(commands=['avatar'])
def avatar(m):
    if m.reply_to_message:
        user = m.reply_to_message.from_user
    else:
        user = m.from_user

    photos = bot.get_user_profile_photos(user.id)
    if photos.total_count > 0:
        bot.send_photo(m.chat.id, photos.photos[0][-1].file_id)
    else:
        bot.reply_to(m, "❌️ Usuário sem foto de perfil")

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