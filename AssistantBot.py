from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os

from Finance.StockMarket import TickerManager

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
botApp = ApplicationBuilder().token(f"{bot_token}").build()

# Define los comandos del bot
@staticmethod
async def add_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        symbol = context.args[0].upper()
        manager = TickerManager()
        result = manager.add_ticker(symbol)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Por favor, proporciona un símbolo de ticker. Uso: /add <TICKER>")

@staticmethod
async def del_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        symbol = context.args[0].upper()
        manager = TickerManager()
        result = manager.del_ticker(symbol)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Por favor, proporciona un símbolo de ticker. Uso: /del <TICKER>")

@staticmethod
async def show_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        symbol = context.args[0].upper()
        manager = TickerManager()
        result = manager.show_ticker(symbol)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Por favor, proporciona un símbolo de ticker. Uso: /show <TICKER>")

@staticmethod
async def list_tickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manager = TickerManager()
    message = manager.list_tickers()
    await update.message.reply_text(message)

@staticmethod
async def add_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 3:
        symbol = context.args[0].upper()
        alert_type = context.args[1].lower()
        try:
            price = float(context.args[2])
            manager = TickerManager()
            result = manager.add_alert(symbol, alert_type, price)
            await update.message.reply_text(result)
        except ValueError:
            await update.message.reply_text("El precio debe ser un número válido. Uso: /addal <TICKER> <up/down> <PRICE>")
    else:
        await update.message.reply_text("Uso incorrecto. Uso: /addal <TICKER> <up/down> <PRICE>")

@staticmethod
async def del_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 2:
        symbol = context.args[0].upper()
        alert_type = context.args[1].lower()
        manager = TickerManager()
        result = manager.del_alert(symbol, alert_type)
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("Uso incorrecto. Uso: /delal <TICKER> <up/down/all>")

async def show_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manager = TickerManager()
    result = manager.show_alerts()
    await update.message.reply_text(result)

async def check_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manager = TickerManager()
    result = manager.check_alerts()
    await update.message.reply_text(result)

# Agrega los manejadores de comandos al bot
botApp.add_handler(CommandHandler("add", add_ticker))
botApp.add_handler(CommandHandler("del", del_ticker))
botApp.add_handler(CommandHandler("show", show_ticker))
botApp.add_handler(CommandHandler("list", list_tickers))
botApp.add_handler(CommandHandler("addal", add_alert))
botApp.add_handler(CommandHandler("delal", del_alert))
botApp.add_handler(CommandHandler("showal", show_alerts))
botApp.add_handler(CommandHandler("chkal", check_alerts))

botApp.run_polling(allowed_updates=Update.ALL_TYPES)