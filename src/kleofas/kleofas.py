'''
'''


from _metadata import __project__, __version__

from tgbot import TgBot
from commandmanager import CommandManager, BadCommand

import functools
import re


class Kleofas(TgBot):
    def __init__(self, loop, token, owner, command_file):
        import logging

        self.__logger = logging.getLogger(__name__)

        TgBot.__init__(self, loop, token)
        self.__owner = re.sub('^@', '', owner) if owner is not None else None

        self.__command_manager = CommandManager(command_file)


    def handle_message(self, message):
        TgBot.handle_message(self, message)

        chat_id = message['chat']['id']

        if re.match('(?:hi|hello)[!.]?', message['text'], flags=re.I):
            self.send(chat_id, "Hi %s!" % message['from']['first_name'])

        if self.__owner is None or message['from']['username'] == self.__owner:
            if re.match('/.+', message['text']):
                try:
                    self.send(
                            chat_id,
                            functools.partial(self.__command_manager.run, message['text']))
                except BadCommand as b:
                    self.__logger.error(b.message)


