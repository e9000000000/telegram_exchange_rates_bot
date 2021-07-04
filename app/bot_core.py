import inspect

from telegram.ext import Updater, CommandHandler


class BotCore():
    command_prefix = 'command_'

    def __init__(self, token: str):
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        self._update_commands_list()

    def run(self):
        self.updater.start_polling()

    def _update_commands_list(self):
        for function_name, function in inspect.getmembers(type(self), inspect.isfunction):
            if function_name.startswith(self.command_prefix):
                command = function_name[len(self.command_prefix):]
                self._add_command(command, function)

    def _add_command(self, command: str, on_execute):
        def function(*args):
            return on_execute(self, *args)
        handler = CommandHandler(command, function)
        self.dispatcher.add_handler(handler)
