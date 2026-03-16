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

DATA_FILE = "data.json"

# ======================
# CARREGAR DADOS
# ======================

try:
with open(DATA_FILE, "r") as f:
data = json.load(f)
xp = data.get("xp", {})
coins = data.get("coins", {})
daily_cooldown = data.get("daily_cooldown", {})
except:
xp = {}
coins = {}
daily_cooldown = {}

start_time = time.time()

# ======================
# CARREGAR DADOS
# ======================

def save_data():
with open(DATA_FILE, "w") as f:
json.dump({
"xp": xp,
"coins": coins,
"daily_cooldown": daily_cooldown
}, f)

# ======================
# MENU
# ======================

MENU = f"""
╭━━━ 🌻 {BOT_NAME} BOT 🌻 ━━━╮

👋 Olá! Eu sou a {BOT_NAME}! ꒰ᐢ. .ᐢ꒱₊˚⊹
Use meus comandos abaixo:

━━━━━━━━━━━━━━━━

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

━━━━━━━━━━━━━━━━

🌸 Extras automáticos
✔ Welcome automático
✔ Goodbye automático
✔ Tempo no grupo

╰━━━━━━━━━━━━━━━╯
"""

# ======================
# START COM IMAGEM
# ======================
@bot.message_handler(commands=['start'])
def start(m):
    # URL da imagem que você quer enviar
    img_url = "https://i.postimg.cc/6QDLmktT/file-00000000104871f5ab38bc387c4c1435.png"
    
    # Envia a imagem
    try:
        bot.send_photo(m.chat.id, img_url, caption=MENU)
    except:
        # Caso dê algum erro no envio da imagem, envia só o menu
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
# XP AUTOMÁTICO
# ======================

@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def gain_xp(m):
user = str(m.from_user.id)
xp[user] = xp.get(user, 0) + 5
save_data()

# ======================
# PIN / UNPIN
# ======================

@bot.message_handler(commands=['pin'])
def pin(m):
if m.reply_to_message:
try:
bot.pin_chat_message(m.chat.id, m.reply_to_message.message_id)
bot.reply_to(m, "📌 Mensagem fixada!")
except:
bot.reply_to(m, "🚫 Não consegui fixar.")
else:
bot.reply_to(m, "💛 Responda a mensagem.")

@bot.message_handler(commands=['unpin'])
def unpin(m):
try:
bot.unpin_all_chat_messages(m.chat.id)
bot.reply_to(m, "📌 Mensagens desfixadas!")
except:
bot.reply_to(m, "🚫 Erro ao desfixar.")

# ======================
# LEVEL / RANK / COINS
# ======================

@bot.message_handler(commands=['level'])
def level(m):
user = str(m.from_user.id)
user_xp = xp.get(user, 0)
lvl = user_xp // 100
bot.reply_to(m, f"⭐ {m.from_user.first_name}\nXP: {user_xp}\nLevel: {lvl}")

@bot.message_handler(commands=['rank'])
def rank(m):
ranking = sorted(xp.items(), key=lambda x: x[1], reverse=True)
text = "🏆 Ranking\n\n"
for i, (user_id, points) in enumerate(ranking[:5], start=1):
try:
user_name = bot.get_chat_member(m.chat.id, int(user_id)).user.first_name
except:
user_name = str(user_id)
text += f"{i}. {user_name} - {points} XP\n"
bot.send_message(m.chat.id, text)

@bot.message_handler(commands=['saldo'])
def saldo(m):
user = str(m.from_user.id)
bot.reply_to(m, f"💰 Seu saldo: {coins.get(user, 0)} coins")

@bot.message_handler(commands=['daily'])
def daily(m):
user = str(m.from_user.id)
now = time.time()
week = 7 * 24 * 60 * 60
last = daily_cooldown.get(user, 0)
if now - last < week:
bot.reply_to(m, f"💛 Você já coletou seu daily semanal! Aguarde.")
return
reward = random.randint(50, 150)
coins[user] = coins.get(user, 0) + reward
daily_cooldown[user] = now
save_data()
bot.reply_to(m, f"💰 Você recebeu {reward} coins!\nSaldo atual: {coins[user]} coins")

@bot.message_handler(commands=['coinflip'])
def coinflip(m):
user = str(m.from_user.id)
if coins.get(user, 0) < 10:
bot.reply_to(m, "💛 Você precisa de 10 coins")
return
coins[user] -= 10
if random.choice([True, False]):
coins[user] += 20
resultado = f"🪙 Cara! Você ganhou 20 coins"
else:
resultado = f"🪙 Coroa! Você perdeu"
save_data()
bot.reply_to(m, f"{resultado}\nSaldo atual: {coins[user]} coins")

# ======================
# GIF / MEME
# ======================

@bot.message_handler(commands=['gif'])
def gif(m):

actions = {  
    "hug": "anime hug",  
    "kiss": "anime kiss",  
    "slap": "anime slap",  
    "pat": "anime headpat",  
    "dance": "anime dance"  
}  

args = m.text.split(maxsplit=1)  

if len(args) < 2:  
    query = "anime"  
else:  
    user_query = args[1].lower()  

    if user_query in actions:  
        query = actions[user_query]  
    else:  
        query = user_query  

try:  
    url = "https://api.giphy.com/v1/gifs/search"  
    params = {  
        "api_key": GIPHY_KEY,  
        "q": query,  
        "limit": 25,  
        "rating": "pg-13"  
    }  

    r = requests.get(url, params=params, timeout=10).json()  
    data = r.get("data", [])  

    if not data:  
        url = "https://api.giphy.com/v1/gifs/trending"  
        params = {  
            "api_key": GIPHY_KEY,  
            "limit": 25  
        }  

        r = requests.get(url, params=params, timeout=10).json()  
        data = r.get("data", [])  

    if not data:  
        bot.reply_to(m, "💛 Não encontrei nenhum GIF.")  
        return  

    gif_url = random.choice(data)["images"]["original"]["url"]  

    bot.send_animation(m.chat.id, gif_url)  

except Exception as e:  
    print("Erro no /gif:", e)  
    bot.reply_to(m, "💛 Erro ao buscar GIF.")

@bot.message_handler(commands=['meme'])
def meme(m):
try:
r = requests.get("https://meme-api.com/gimme", timeout=10).json()
bot.send_photo(m.chat.id, r["url"], caption=r["title"])
except:
bot.reply_to(m, "💛 Não consegui pegar meme.")

# ======================
# USERINFO / AVATAR
# ======================

@bot.message_handler(commands=['userinfo'])
def userinfo(m):
user = m.from_user
msg = f"""🌻 USERINFO

Nome: {user.first_name}
Username: @{user.username if user.username else "Não possui"}
ID: {user.id}
Bot: {user.is_bot}"""
bot.send_message(m.chat.id, msg)

@bot.message_handler(commands=['avatar'])
def avatar(m):
user = m.from_user
photos = bot.get_user_profile_photos(user.id)
if photos.total_count > 0:
bot.send_photo(m.chat.id, photos.photos[0][0].file_id)
else:
bot.reply_to(m, "💛 Sem foto.")

# ======================
# WAIFU IMAGEM (SFW)
# ======================

@bot.message_handler(commands=['waifu'])
def waifu(m):
try:
r = requests.get("https://api.waifu.pics/sfw/waifu", timeout=10).json()
bot.send_photo(m.chat.id, r["url"], caption="💛 Aqui está sua waifu!")
except:
bot.reply_to(m, "💛 Não consegui pegar a waifu!")

# ======================
# WAIFU GIF (SFW)
# ======================

@bot.message_handler(commands=['waifugif'])
def waifugif(m):
try:
r = requests.get("https://api.waifu.pics/sfw/waifu", timeout=10).json()
bot.send_animation(m.chat.id, r["url"], caption="💛 Aqui está sua waifu GIF!")
except:
bot.reply_to(m, "💛 Não consegui pegar o gif!")

# ======================
# WAIFU NSFW (IMAGEM)
# ======================

@bot.message_handler(commands=['waifunsfw'])
def waifunsfw(m):

if m.chat.type != "private":  
    bot.reply_to(m, "🚫 NSFW só no privado!")  
    return  

try:  
    r = requests.get("https://api.waifu.pics/nsfw/waifu", timeout=10).json()  
    bot.send_photo(m.chat.id, r["url"], caption="🔞 Waifu NSFW!")  
except:  
    bot.reply_to(m, "💛 Não consegui pegar a waifu NSFW!")

# ======================
# WAIFU NSFW GIF
# ======================

@bot.message_handler(commands=['gifnsfw'])
def gifnsfw(m):

if m.chat.type != "private":  
    bot.reply_to(m, "🚫 NSFW só no privado!")  
    return  

try:  
    r = requests.get("https://api.waifu.pics/nsfw/waifu", timeout=10).json()  
    bot.send_animation(m.chat.id, r["url"], caption="🔞 Waifu GIF NSFW!")  
except:  
    bot.reply_to(m, "💛 Não consegui pegar o gif NSFW!")

# ======================
# MODERAÇÃO
# ======================

@bot.message_handler(commands=['ban'])
def ban(m):
if not m.reply_to_message:
bot.reply_to(m, "💛 Responda o usuário.")
return
user_id = m.reply_to_message.from_user.id
try:
bot.ban_chat_member(m.chat.id, user_id)
bot.reply_to(m, "🚫 Usuário banido.")
except:
bot.reply_to(m, "💛 Não consegui banir.")

@bot.message_handler(commands=['warn'])
def warn(m):
if not m.reply_to_message:
bot.reply_to(m, "💛 Responda o usuário.")
return
user_id = m.reply_to_message.from_user.id
warns[user_id] = warns.get(user_id, 0) + 1
bot.reply_to(m, f"⚠️ Aviso para {m.reply_to_message.from_user.first_name}\nTotal: {warns[user_id]}")
if warns[user_id] >= 3:
try:
bot.ban_chat_member(m.chat.id, user_id)
bot.send_message(m.chat.id, "🚫 Banido por 3 avisos.")
except:
pass

@bot.message_handler(commands=['mute'])
def mute(m):
if not m.reply_to_message:
return
user_id = m.reply_to_message.from_user.id
try:
bot.restrict_chat_member(m.chat.id, user_id, can_send_messages=False)
bot.reply_to(m, "🔇 Mutado.")
except:
bot.reply_to(m, "💛 Não consegui mutar.")

@bot.message_handler(commands=['unmute'])
def unmute(m):
if not m.reply_to_message:
return
user_id = m.reply_to_message.from_user.id
try:
bot.restrict_chat_member(m.chat.id, user_id, can_send_messages=True)
bot.reply_to(m, "🔊 Desmutado.")
except:
bot.reply_to(m, "💛 Não consegui desmutar.")

@bot.message_handler(commands=['limpar'])
def limpar(m):
args = m.text.split()
if len(args) < 2:
bot.reply_to(m, "💛 Use: /limpar <quantidade>")
return
try:
n = int(args[1])
if n > 50:
n = 50
for i in range(n):
try:
bot.delete_message(m.chat.id, m.message_id - i)
except:
pass
bot.reply_to(m, f"🧹 {n} mensagens apagadas!")
except:
bot.reply_to(m, "💛 Número inválido.")

@bot.message_handler(commands=['antilink'])
def anti(m):
args = m.text.split()
if len(args) < 2:
return
if args[1].lower() == "on":
antilink[m.chat.id] = True
bot.reply_to(m, "🚫 Antilink ativado")
elif args[1].lower() == "off":
antilink[m.chat.id] = False
bot.reply_to(m, "✅ Antilink desativado")

# ======================
# GOOGLE / IMAGE
# ======================

@bot.message_handler(commands=['google'])
def google(m):
args = m.text.split(maxsplit=1)
if len(args) < 2:
bot.reply_to(m, "💛 Use: /google <termo>")
return
query = args[1]
params = {"q": query, "engine": "google", "api_key": SERPAPI_KEY}
try:
r = requests.get("https://serpapi.com/search", params=params, timeout=10).json()
resultados = r.get("organic_results", [])
if not resultados:
bot.reply_to(m, "💛 Nenhum resultado encontrado.")
return
msg = f"🔎 {query}\n\n"
for res in resultados[:3]:
msg += f"{res.get('title')}\n{res.get('link')}\n\n"
bot.send_message(m.chat.id, msg)
except:
bot.reply_to(m, "💛 Erro na busca.")

@bot.message_handler(commands=['image'])
def image(m):
args = m.text.split(maxsplit=1)
if len(args) < 2:
bot.reply_to(m, "💛 Use: /image <termo>")
return
query = args[1]
params = {"engine": "google_images", "q": query, "api_key": SERPAPI_KEY}
try:
r = requests.get("https://serpapi.com/search", params=params, timeout=10).json()
imgs = r.get("images_results", [])
if not imgs:
bot.reply_to(m, "💛 Nenhuma imagem encontrada.")
return
img = random.choice(imgs)
bot.send_photo(m.chat.id, img["original"], caption=query)
except:
bot.reply_to(m, "💛 Erro ao buscar imagem.")

# ======================
# PLAY (YouTube)
# ======================

@bot.message_handler(commands=['play'])
def play(message):
args = message.text.split(maxsplit=1)
if len(args) < 2:
bot.reply_to(message, "💛 Use:\n/play nome da música")
return

query = args[1]  
url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={urllib.parse.quote_plus(query)}&key={YOUTUBE_KEY}&maxResults=1&type=video"  
try:  
    r = requests.get(url, timeout=10).json()  
    items = r.get("items", [])  
    if not items:  
        bot.reply_to(message, "💛 Música não encontrada.")  
        return  
    video = items[0]  
    title = video["snippet"]["title"]  
    channel = video["snippet"]["channelTitle"]  
    vid = video["id"]["videoId"]  
    bot.send_message(message.chat.id, f"🎵 {title}\n📺 {channel}\nhttps://youtu.be/{vid}")  
except Exception as e:  
    print("Erro no /play:", e)  
    bot.reply_to(message, "💛 Erro ao buscar música.")

# ======================
# DADO / SHIP
# ======================

@bot.message_handler(commands=['dado'])
def dado(m):
bot.reply_to(m, f"🎲 Resultado: {random.randint(1, 6)}")

@bot.message_handler(commands=['ship'])
def ship(m):
if not m.reply_to_message:
return
score = random.randint(1, 100)
user1 = m.from_user.first_name
user2 = m.reply_to_message.from_user.first_name
bot.send_message(m.chat.id, f"💕 {user1} + {user2}\nCompatibilidade: {score}%")

# ======================
# INFO (BOT)
# ======================

@bot.message_handler(commands=['info'])
def info(m):
uptime = int(time.time() - start_time)
h = uptime // 3600
m2 = (uptime % 3600) // 60
s = uptime % 60
msg = (
f"╭━━━━━━━━━━━━━━━\n"
f"🌻 {BOT_NAME} BOT 🌻\n"
f"╰━━━━━━━━━━━━━━━\n"
f"🤖 Nome: {BOT_NAME}\n"
f"⏱ Uptime: {h}h {m2}m {s}s\n"
f"👤 Criador: {CREATOR}\n"
f"🛠 Versão: {BOT_VERSION}"
)
bot.send_message(m.chat.id, msg)

# ======================
# ANTILINK GLOBAL
# ======================

@bot.message_handler(func=lambda m: True)
def global_handler(m):
if m.text and antilink.get(m.chat.id):
if "http" in m.text or "t.me" in m.text:
try:
bot.delete_message(m.chat.id, m.message_id)
bot.ban_chat_member(m.chat.id, m.from_user.id)
bot.send_message(m.chat.id, "🚫 Link proibido!")
return
except:
pass

# ======================
# WELCOME / GOODBYE
# ======================

@bot.message_handler(content_types=['new_chat_members'])
def welcome(m):
membros = bot.get_chat_members_count(m.chat.id)
hora = time.strftime("%H:%M")
for user in m.new_chat_members:
nome = user.first_name
entradas[user.id] = time.time()
mensagem = f"""
🌸 Bem-vindo ao grupo!

👤 Usuário: {nome}
👥 Membro nº: {membros}
🕒 Entrou às: {hora}

💛 Aproveite o grupo!
"""
try:
bot.send_photo(m.chat.id, "https://i.imgur.com/9XnK8YB.jpeg", caption=mensagem)
except:
bot.send_message(m.chat.id, mensagem)

@bot.message_handler(content_types=['left_chat_member'])
def goodbye(m):
user = m.left_chat_member
if user:
hora = time.strftime("%H:%M")
mensagem = f"""
🌸 Alguém saiu do grupo.

👤 Usuário: {user.first_name}
🕒 Saiu às: {hora}

💛 Até logo!
"""
try:
bot.send_photo(m.chat.id, "https://i.imgur.com/9XnK8YB.jpeg", caption=mensagem)
except:
bot.send_message(m.chat.id, mensagem)

# ======================
# INICIAR BOT
# ======================

bot.polling(none_stop=True)