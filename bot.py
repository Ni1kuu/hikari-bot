import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Oi oi! Eu sou a Hikari 🌸✨")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Comandos disponíveis:\n/start\n/help\n/ping")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hikari está online! 💛")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("ping", ping))

print("Hikari está rodando!")

app.run_polling()
