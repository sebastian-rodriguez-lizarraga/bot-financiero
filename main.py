from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ContextTypes, Application
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

# Configuración de Telegram
TOKEN = os.getenv("TOKEN")
BOT_USERNAME = "chinwen_bot"


async def start_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I'm a bot")

async def help_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I don't know how to help you")

async def custom_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command")

# Responses

async def reservasinternacionales_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    global message
    url = "https://api.estadisticasbcra.com/reservas"
    token = os.getenv("token")
    headers = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(url, headers = headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    if(response.status_code == 200):
        data = response.json()
        valor = data[len(data)-1]['v']
        fecha = data[len(data)-1]['d']
        await update.message.reply_text(f"Reservas Internacionales: {valor} Millones USD en la fecha: {fecha}")
    else:
        await update.message.reply_text(f"Error al obtener datos. Código de estado: {response.status_code}, Mensaje: {response.text}")



async def dolar_command(update: Update,context: ContextTypes.DEFAULT_TYPE):
    response = requests.get("https://dolarapi.com/v1/dolares")
    cotizaciones = response.json()
    message = ""
    for cotizacion in cotizaciones:
        for k, v in cotizacion.items():
            if k in ["nombre", "compra", "venta"]:
                if k != "nombre":
                    message +=f"{k}: {v}\n"
                if k == "venta":
                    message += "----------------------------\n"
                if k == "nombre":
                    message +=f"{v}\n"


    # Responder al usuario con el mensaje construido
    await update.message.reply_text(f"{message}")



def handle_response(text:str) -> str:
    text_lower = text.lower()
    print('User:', text)
    # Define algunos patrones de entrada para desencadenar respuestas específicas
    if 'hola' in text_lower:
        return "Hello there!"
    elif 'como estas' in text_lower or 'que onda' in text_lower:
        return "Hola, yo estoy bien, y ahora que me hablaste mejor. ¿Como estas?"
    elif 'chau' in text_lower or 'inutil' in text_lower:
        return "Chau! Anda con cuidado."
    # Si no coincide con ningún patrón específico, utiliza OpenAI GPT-3 para generar una respuesta
    elif 'te quiero' in text_lower:
        return 'Yo te quiero mas Mambru <3 '

async def handle_message(update: Update,context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type #private or group
    text: str = update.message.text
    print(f"Message from {update.message.chat.id}  in {message_type}: {text}")

    if message_type== 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
            await update.message.reply_text(handle_response(text))
        else:
            return
    else:
        response: str = handle_response(text)
        print('Bot:', response)
        await update.message.reply_text(response)

async def error(update: Update,context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == '__main__':
   app = Application.builder().token(TOKEN).build()

   #commands
   app.add_handler(CommandHandler('start', start_command))
   app.add_handler(CommandHandler('help', help_command))
   app.add_handler(CommandHandler('custom', custom_command))
   app.add_handler(CommandHandler('dolar', dolar_command))
   app.add_handler(CommandHandler('reservas', reservasinternacionales_command))
   #messages
   app.add_handler(MessageHandler(filters.TEXT, handle_message))
   app.add_error_handler(error)
   print('Polling...')
   app.run_polling(poll_interval=3) #3 seconds
