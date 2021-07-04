from bot_core import BotCore


class Bot(BotCore):
    def command_start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Start.')
    
    def command_ping(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='pong')
