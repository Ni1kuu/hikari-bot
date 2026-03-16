import os
import telebot
import requests
import random
import time
import urllib.parse
import json
from telebot import types

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
last_xp = {}

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
# MENU / BOTÕES INLINE
# ======================

MENU = f"""
╭━━━ 🌼 {BOT_NAME} BOT 🌼 ━━━╮

🎮 *DIVERSÃO SFW & NSFW* 💛
💌 /gif → Gifs fofinhos de anime
😂 /meme → Memes divertidos
🔞 /waifunsfw → Waifu NSFW (privado)
💖 /waifugif → Waifu GIF animada
😈 /gifnsfw → GIF NSFW (privado)
🎵 /play → Tocar música do YouTube
🍑 /r34 → Conteúdo adulto (privado)
🖼 /danbooru → Imagens fofinhas do Danbooru

🔎 *PESQUISA* 🌟
🔗 /google → Buscar links
🖼 /image → Buscar imagens

👤 *PERFIL* 🌷
📸 /avatar → Ver foto de perfil
⭐ /level → Seu nível
🏆 /rank → Ranking de XP
💰 /saldo → Coins atuais
🪙 /coinflip → Cara ou coroa
🎁 /daily → Coletar prêmio diário

📌 *GRUPO* 🌈
📌 /pin → Fixar mensagem
❌ /unpin → Desfixar mensagens
🎲 /dado → Jogar dado
💕 /ship → Shipar pessoas fofinhas

🛡 *MODERAÇÃO* 🐾
🚫 /ban → Banir usuário
⚠️ /warn → Aviso de conduta
🔇 /mute → Mutar usuário
🔊 /unmute → Desmutar usuário
🧹 /limpar → Apagar mensagens
🚨 /antilink on/off → Ativar/Desativar antilink

╰━━━━━━━━━━━━━━━╯
"""

# ======================
# START / MENU INLINE
# ======================

@bot.message_handler(commands=['start'])
def start(m):
    video = "https://github.com/Ni1kuu/hikari-bot/raw/main/Cute_anime_fox_girl_standing_in_a_peaceful_Japanese_garden%2C_arms_open_in_a_welcoming_pose.____Animat_seed1530167038.mp4"

    # Mensagem fofinha do menu
    msg_text = f"""
🌼 Bem-vindo(a) ao {BOT_NAME}! 🌼

✨ Aqui você pode se divertir, explorar e interagir comigo!
💌 Escolha uma opção abaixo clicando nos botões:

👤 Perfil → Veja seus dados
🏓 Ping → Teste meu tempo de resposta
🖼 Waifu → Receba uma waifu fofinha
ℹ️ Info → Saiba mais sobre mim
📋 Menu → Todos meus comandos 

Divirta-se e aproveite! ꒰ᐢ. .ᐢ꒱₊˚⊹ 💖
""".strip()

    # Cria teclado inline com os 5 botões principais
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("👤 Perfil", callback_data="perfil"),
        types.InlineKeyboardButton("🏓 Ping", callback_data="ping"),
        types.InlineKeyboardButton("🖼 Waifu", callback_data="waifu"),
        types.InlineKeyboardButton("ℹ️ Info", callback_data="info"),
        types.InlineKeyboardButton("📋 Menu", callback_data="menu_completo")
    )

    # Envia o vídeo com a legenda e os botões INLINE na mesma mensagem
    bot.send_video(
        m.chat.id,
        video,
        caption=msg_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# ======================
# CALLBACK HANDLER
# ======================

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    cid = call.message.chat.id

    if call.data == "perfil":
        user = call.from_user
        msg = (
            f"🌼✨ *USERINFO* ✨🌼\n\n"
            f"👤 Nome: {user.first_name}\n"
            f"💌 Username: @{user.username if user.username else 'Não possui'}\n"
            f"🆔 ID: {user.id}\n"
        )
        bot.send_message(cid, msg, parse_mode="Markdown")

    elif call.data == "ping":
        start_ping = time.time()
        msg = bot.send_message(cid, "🏓 Pingando...")
        elapsed = int((time.time() - start_ping) * 1000)
        bot.edit_message_text(f"🏓 Pong! {elapsed} ms", cid, msg.message_id)

    elif call.data == "waifu":
        try:
            url = waifu_request("sfw", cid)
            bot.send_photo(cid, url)
        except:
            bot.send_message(cid, "💛 Erro ao pegar waifu")

    elif call.data == "info":
        uptime = int(time.time() - start_time)
        h = uptime // 3600
        m2 = (uptime % 3600) // 60
        s = uptime % 60
        bot.send_message(
            cid,
            f"🌻 {BOT_NAME}\nUptime: {h}h {m2}m {s}s\nVersão: {BOT_VERSION}\nCriador: {CREATOR}"
        )

    elif call.data == "menu_completo":
        bot.send_message(cid, MENU, parse_mode="Markdown")

    bot.answer_callback_query(call.id)

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
# XP AUTOMÁTICO
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

# ======================
# LEVEL
# ======================

@bot.message_handler(commands=['level'])
def level(m):
    user = str(m.from_user.id)
    user_xp = xp.get(user, 0)
    lvl = user_xp // 100
    bot.reply_to(m, f"⭐ {m.from_user.first_name}\nXP: {user_xp}\nLevel: {lvl}")

# Comando de teste para adicionar XP
@bot.message_handler(commands=['addxp'])
def addxp(m):
    user = str(m.from_user.id)
    xp[user] = xp.get(user, 0) + 50
    save_data()
    bot.reply_to(m,f"✅ 100 XP adicionados! Total: {xp[user]} XP")

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
# GIF / MEME
# ======================

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

@bot.message_handler(commands=['meme'])
def meme(m):
    try:
        r = requests.get("https://meme-api.com/gimme").json()
        bot.send_photo(m.chat.id,r["url"],caption=r["title"])
    except:
        bot.reply_to(m,"Erro ao pegar meme")

# ======================
# WAIFU (SFW / NSFW / GIFS)
# ======================

def waifu_request(endpoint, gif=False):
    """
    Retorna URL da waifu.
    endpoint: 'sfw' ou 'nsfw'
    gif: True para GIF, False para imagem
    """
    url = f"https://api.waifu.pics/{endpoint}/waifu"
    if gif:
        url += "/gif"
    r = requests.get(url, timeout=10).json()
    return r["url"]

# ----- WAIFU SFW IMAGEM -----
@bot.message_handler(commands=['waifu'])
def waifu(m):
    try:
        bot.send_photo(m.chat.id, waifu_request("sfw"), caption="💛 Uma waifu fofinha pra você!")
    except:
        bot.reply_to(m, "❌️ Erro ao pegar waifu")

# ----- WAIFU SFW GIF -----
@bot.message_handler(commands=['waifugif'])
def waifugif(m):
    try:
        bot.send_animation(m.chat.id, waifu_request("sfw", gif=True), caption="💛 Waifu GIF fofinha!")
    except:
        bot.reply_to(m, "❌️ Erro ao pegar GIF")

# ----- WAIFU NSFW IMAGEM -----
@bot.message_handler(commands=['waifunsfw'])
def waifunsfw(m):
    if m.chat.type != "private":
        bot.reply_to(m,"🚫 NSFW só no privado!")
        return
    try:
        bot.send_photo(m.chat.id, waifu_request("nsfw"), caption="Uma waifu sexy só pra você 😏🔞")
    except:
        bot.reply_to(m,"❌️ Erro ao pegar NSFW")

# ----- WAIFU NSFW GIF -----
@bot.message_handler(commands=['gifnsfw'])
def gifnsfw(m):
    if m.chat.type != "private":
        bot.reply_to(m, "🚫 NSFW só no privado!")
        return

    try:
        # Busca GIFs NSFW de forma pública (sem login)
        headers = {"User-Agent": "TelegramBot (by /u/seu_usuario)"}
        r = requests.get("https://api.redgifs.com/v2/gifs/search?search_text=nsfw&count=50", headers=headers, timeout=10)
        data = r.json()

        gifs = data.get("gifs", [])
        if not gifs:
            bot.reply_to(m, "❌ Nenhum GIF encontrado")
            return

        gif = random.choice(gifs)
        url = gif.get("urls", {}).get("hd") or gif.get("urls", {}).get("sd")
        if not url:
            bot.reply_to(m, "❌ Erro ao pegar GIF")
            return

        bot.send_animation(m.chat.id, url, caption="🔥 Sexy pra você 😏🔞")

    except Exception as e:
        print("Erro no /gifnsfw:", e)
        bot.reply_to(m, "❌ Não consegui pegar o GIF agora")

# ======================
# R34 NSFW
# ======================
@bot.message_handler(commands=['r34'])
def r34(m):
    if m.chat.type != "private":
        bot.reply_to(m, "🚫 NSFW só no privado!")
        return
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m, "💛 Use /r34 termo")
        return
    query = args[1].replace(" ", "_")  # query formatada
    try:
        url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={query}"
        r = requests.get(url, timeout=10).json()
        if not r:
            bot.reply_to(m,"💛 Nenhum resultado encontrado")
            return
        img = random.choice(r)["file_url"]
        bot.send_photo(m.chat.id, img, caption=f"🔞 {query}")
    except Exception as e:
        print("Erro no /r34:", e)
        bot.reply_to(m,"💛 Erro ao buscar imagens")

# ----- DANBOORU NSFW -----
@bot.message_handler(commands=['danbooru'])
def danbooru(m):
    if m.chat.type != "private":
        bot.reply_to(m,"🚫 NSFW só no privado!")
        return
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m,"💛 Use /danbooru termo")
        return
    query = args[1].replace(" ", "_")
    try:
        url = f"https://danbooru.donmai.us/posts.json?tags={query}&limit=50"
        r = requests.get(url, timeout=10).json()
        if not r:
            bot.reply_to(m,"💛 Nenhum resultado encontrado")
            return
        post = random.choice(r)
        img_url = post.get("file_url") or post.get("large_file_url")
        bot.send_photo(m.chat.id, img_url, caption=f"🔞 {query}")
    except Exception as e:
        print("Erro no /danbooru:", e)
        bot.reply_to(m,"💛 Erro ao buscar imagens Danbooru")

# ======================
# GOOGLE / IMAGE
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

# ======================
# PLAY (YouTube)
# ======================

@bot.message_handler(commands=['play'])
def play(m):
    args = m.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(m,"Use /play nome da música")
        return
    query = args[1]
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={urllib.parse.quote_plus(query)}&key={YOUTUBE_KEY}&maxResults=1&type=video"
    try:
        r = requests.get(url, timeout=10).json()
        items = r.get("items",[])
        if not items:
            bot.reply_to(m,"Não encontrado")
            return
        video = items[0]
        title = video["snippet"]["title"]
        channel = video["snippet"]["channelTitle"]
        vid = video["id"]["videoId"]
        bot.send_message(m.chat.id,f"🎵 {title}\n📺 {channel}\nhttps://youtu.be/{vid}")
    except:
        bot.reply_to(m,"Erro ao buscar música")

# ======================
# DADO / SHIP
# ======================

@bot.message_handler(commands=['dado'])
def dado(m):
    bot.reply_to(m,f"🎲 {random.randint(1,6)}")

@bot.message_handler(commands=['ship'])
def ship(m):
    if not m.reply_to_message:
        bot.reply_to(m,"💛 Responda alguém para shippar")
        return
    score = random.randint(1,100)
    user1 = m.from_user.first_name
    user2 = m.reply_to_message.from_user.first_name
    bot.send_message(m.chat.id,f"💕 {user1} + {user2}\nCompatibilidade: {score}%")

# ======================
# INFO
# ======================

@bot.message_handler(commands=['info'])
def info(m):
    uptime = int(time.time() - start_time)
    h = uptime // 3600
    m2 = (uptime % 3600) // 60
    s = uptime % 60
    msg = f"🌻 {BOT_NAME}\nUptime: {h}h {m2}m {s}s\nVersão: {BOT_VERSION}\nCriador: {CREATOR}"
    bot.send_message(m.chat.id,msg)

# ======================
# USERINFO
# ======================
@bot.message_handler(commands=['userinfo'])
def userinfo(m):
    # Se responder a alguém, pega os dados dessa pessoa
    if m.reply_to_message:
        user = m.reply_to_message.from_user
    else:
        user = m.from_user

    msg = (
        f"🌻 USERINFO 🌻\n\n"
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
    # Se responder a alguém, pega a foto dessa pessoa
    if m.reply_to_message:
        user = m.reply_to_message.from_user
    else:
        user = m.from_user

    photos = bot.get_user_profile_photos(user.id)
    if photos.total_count > 0:
        # Pega a primeira foto (mais recente)
        bot.send_photo(m.chat.id, photos.photos[0][0].file_id)
    else:
        bot.reply_to(m, "💛 Usuário sem foto de perfil")

# ======================
# PIN / UNPIN (ADM)
# ======================

@bot.message_handler(commands=['pin'])
def pin(m):
    if not m.reply_to_message:
        bot.reply_to(m,"💛 Responda a mensagem para fixar")
        return
    try:
        bot.pin_chat_message(m.chat.id, m.reply_to_message.message_id, disable_notification=False)
        bot.reply_to(m,"📌 Mensagem fixada!")
    except:
        bot.reply_to(m,"🚫 Não consegui fixar")

@bot.message_handler(commands=['unpin'])
def unpin(m):
    try:
        bot.unpin_all_chat_messages(m.chat.id)
        bot.reply_to(m,"📌 Todas as mensagens desfixadas!")
    except:
        bot.reply_to(m,"🚫 Não consegui desfixar")

# ======================
# MODERAÇÃO (ADM)
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
        bot.reply_to(m,"💛 Não consegui desmutar")

@bot.message_handler(commands=['limpar'])
def limpar(m):
    args = m.text.split()
    if len(args) < 2:
        bot.reply_to(m,"💛 Use: /limpar <quantidade>")
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
        bot.reply_to(m,"💛 Número inválido")

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
        msg = f"🌸 Bem-vindo {user.first_name}!\n🕒 Entrou às: {hora}"
        try:
            bot.send_photo(m.chat.id,"https://i.imgur.com/9XnK8YB.jpeg",caption=msg)
        except:
            bot.send_message(m.chat.id,msg)

@bot.message_handler(content_types=['left_chat_member'])
def goodbye(m):
    user = m.left_chat_member
    if user:
        hora = time.strftime("%H:%M")
        msg = f"🌸 {user.first_name} saiu do grupo às {hora}"
        try:
            bot.send_photo(m.chat.id,"https://i.imgur.com/9XnK8YB.jpeg",caption=msg)
        except:
            bot.send_message(m.chat.id,msg)

# ======================
# INICIAR BOT
# ======================

print("Hikari iniciado...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)