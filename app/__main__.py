from telegram.ext import Updater, CommandHandler

from config import TOKEN


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Start.")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()


