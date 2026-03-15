import os
import telebot
import requests
import random
import time
import urllib.parse

# ----------------------
# VARIÁVEIS
# ----------------------
TOKEN = os.getenv("BOT_TOKEN")
GIPHY_KEY = os.getenv("GIPHY_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

bot = telebot.TeleBot(TOKEN)

antilink = {}
warns = {}
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

🖼 PESQUISA
/google
/image

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

# ======================
# START
# ======================
@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, MENU)

# ======================
# PING
# ======================
@bot.message_handler(commands=['ping'])
def ping(m):
    start_ping = time.time()
    msg = bot.reply_to(m,"🏓 Pingando...")
    elapsed = int((time.time()-start_ping)*1000)
    bot.edit_message_text(f"🏓 Pong! {elapsed} ms", m.chat.id, msg.message_id)

# ======================
# PIN
# ======================
@bot.message_handler(commands=['pin'])
def pin(m):
    if m.reply_to_message:
        try:
            bot.pin_chat_message(m.chat.id,m.reply_to_message.message_id)
            bot.reply_to(m,"📌 Mensagem fixada!")
        except:
            bot.reply_to(m,"🚫 Não consegui fixar.")
    else:
        bot.reply_to(m,"💛 Responda a mensagem.")

# ======================
# UNPIN
# ======================
@bot.message_handler(commands=['unpin'])
def unpin(m):
    try:
        bot.unpin_all_chat_messages(m.chat.id)
        bot.reply_to(m,"📌 Mensagens desfixadas!")
    except:
        bot.reply_to(m,"🚫 Erro ao desfixar.")

# ======================
# WAIFU
# ======================
WAIFU_CATS = ["waifu","neko","shinobu","megumin","hug","pat","kiss","smile"]

@bot.message_handler(commands=['waifu','waifunsfw'])
def waifu(m):

    if m.text.startswith("/waifunsfw") and m.chat.type != "private":
        bot.reply_to(m,"🚫 NSFW só no privado.")
        return

    categoria = random.choice(WAIFU_CATS)

    if m.text.startswith("/waifunsfw"):
        url = f"https://api.waifu.pics/nsfw/{categoria}"
    else:
        url = f"https://api.waifu.pics/sfw/{categoria}"

    try:
        r = requests.get(url,timeout=10).json()
        bot.send_photo(m.chat.id,r["url"],caption=f"💛 Waifu ({categoria})")
    except:
        bot.reply_to(m,"💛 Erro ao pegar waifu.")

# ======================
# GIF
# ======================
@bot.message_handler(commands=['gif'])
def gif(m):

    args = m.text.split()
    termo = "anime " + " ".join(args[1:]) if len(args)>1 else "anime"

    try:
        r = requests.get(
            f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_KEY}&q={termo}&limit=25",
            timeout=10
        ).json()

        data = r.get("data",[])

        if not data:
            bot.reply_to(m,"💛 Nenhum GIF.")
            return

        bot.send_animation(m.chat.id,random.choice(data)["images"]["original"]["url"])

    except:
        bot.reply_to(m,"💛 Erro ao buscar GIF.")

# ======================
# MEME
# ======================
@bot.message_handler(commands=['meme'])
def meme(m):
    try:
        r = requests.get("https://meme-api.com/gimme",timeout=10).json()
        bot.send_photo(m.chat.id,r["url"],caption=r["title"])
    except:
        bot.reply_to(m,"💛 Não consegui pegar meme.")

# ======================
# USERINFO
# ======================
@bot.message_handler(commands=['userinfo'])
def userinfo(m):

    user = m.from_user

    msg = f"""🌻 USERINFO
Nome: {user.first_name}
Username: @{user.username if user.username else "Não possui"}
ID: {user.id}
Bot: {user.is_bot}"""

    bot.send_message(m.chat.id,msg)

# ======================
# AVATAR
# ======================
@bot.message_handler(commands=['avatar'])
def avatar(m):

    user = m.from_user
    photos = bot.get_user_profile_photos(user.id)

    if photos.total_count > 0:
        bot.send_photo(m.chat.id,photos.photos[0][0].file_id)
    else:
        bot.reply_to(m,"💛 Sem foto.")

# ======================
# BAN
# ======================
@bot.message_handler(commands=['ban'])
def ban(m):

    if not m.reply_to_message:
        bot.reply_to(m,"💛 Responda o usuário.")
        return

    user_id = m.reply_to_message.from_user.id

    try:
        bot.ban_chat_member(m.chat.id,user_id)
        bot.reply_to(m,"🚫 Usuário banido.")
    except:
        bot.reply_to(m,"💛 Não consegui banir.")

# ======================
# WARN
# ======================
@bot.message_handler(commands=['warn'])
def warn(m):

    if not m.reply_to_message:
        bot.reply_to(m,"💛 Responda o usuário.")
        return

    user_id = m.reply_to_message.from_user.id

    warns[user_id] = warns.get(user_id,0)+1

    bot.reply_to(
        m,
        f"⚠️ Aviso para {m.reply_to_message.from_user.first_name}\nTotal: {warns[user_id]}"
    )

    if warns[user_id] >= 3:
        try:
            bot.ban_chat_member(m.chat.id,user_id)
            bot.send_message(m.chat.id,"🚫 Banido por 3 avisos.")
        except:
            pass

# ======================
# MUTE
# ======================
@bot.message_handler(commands=['mute'])
def mute(m):

    if not m.reply_to_message:
        return

    user_id = m.reply_to_message.from_user.id

    try:
        bot.restrict_chat_member(m.chat.id,user_id,can_send_messages=False)
        bot.reply_to(m,"🔇 Mutado.")
    except:
        bot.reply_to(m,"💛 Não consegui mutar.")

# ======================
# UNMUTE
# ======================
@bot.message_handler(commands=['unmute'])
def unmute(m):

    if not m.reply_to_message:
        return

    user_id = m.reply_to_message.from_user.id

    try:
        bot.restrict_chat_member(m.chat.id,user_id,can_send_messages=True)
        bot.reply_to(m,"🔊 Desmutado.")
    except:
        bot.reply_to(m,"💛 Não consegui desmutar.")

# ======================
# LIMPAR
# ======================
@bot.message_handler(commands=['limpar'])
def limpar(m):

    args = m.text.split()

    if len(args)<2:
        return

    quantidade = int(args[1])

    for i in range(quantidade):
        try:
            bot.delete_message(m.chat.id,m.message_id-i)
        except:
            pass

# ======================
# ANTILINK
# ======================
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

# ======================
# GOOGLE
# ======================
@bot.message_handler(commands=['google'])
def google(m):

    args = m.text.split(maxsplit=1)

    if len(args)<2:
        return

    query = args[1]

    params={
        "q":query,
        "engine":"google",
        "api_key":SERPAPI_KEY
    }

    try:
        r=requests.get("https://serpapi.com/search",params=params,timeout=10).json()

        resultados=r.get("organic_results",[])

        msg=f"🔎 {query}\n\n"

        for res in resultados[:3]:
            msg+=f"{res.get('title')}\n{res.get('link')}\n\n"

        bot.send_message(m.chat.id,msg)

    except:
        bot.reply_to(m,"💛 Erro na busca.")

# ======================
# IMAGE
# ======================
@bot.message_handler(commands=['image'])
def image(m):

    args = m.text.split(maxsplit=1)

    if len(args)<2:
        return

    query=args[1]

    params={
        "engine":"google_images",
        "q":query,
        "api_key":SERPAPI_KEY
    }

    try:

        r=requests.get("https://serpapi.com/search",params=params,timeout=10).json()

        imgs=r.get("images_results",[])

        if not imgs:
            bot.reply_to(m,"💛 Nenhuma imagem.")
            return

        img=random.choice(imgs)

        bot.send_photo(m.chat.id,img["original"],caption=query)

    except:
        bot.reply_to(m,"💛 Erro ao buscar imagem.")

# ======================
# PLAY
# ======================
@bot.message_handler(commands=['play'])
def play(m):

    args = m.text.split(maxsplit=1)

    if len(args)<2:
        return

    query=args[1]

    url=f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={urllib.parse.quote_plus(query)}&key={YOUTUBE_KEY}&maxResults=1&type=video"

    try:
        r=requests.get(url,timeout=10).json()

        video=r["items"][0]

        title=video["snippet"]["title"]
        channel=video["snippet"]["channelTitle"]
        vid=video["id"]["videoId"]

        bot.send_message(
            m.chat.id,
            f"🎵 {title}\n📺 {channel}\nhttps://youtu.be/{vid}"
        )

    except:
        bot.reply_to(m,"💛 Música não encontrada.")

# ======================
# INFO
# ======================
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

# ======================
# HANDLER GLOBAL
# ======================
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
# INICIAR BOT
# ======================
print("🌻 HikariBot iniciado!")
bot.infinity_polling(none_stop=True,skip_pending=True)