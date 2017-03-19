#!/usr/bin/env python3


'''
Personal Telegram bot
'''


from TgBot import TgBot
from CommandManager import CommandManager, BadCommand
from Types import Text

import logging
import re


logging.basicConfig(format='%(asctime)-12s %(name)s %(levelname)s: %(message)s',
        level=logging.INFO)


class Kleofas(TgBot):
    def __init__(self, event_loop, token, owner):
        TgBot.__init__(self, event_loop, token)
        self.__owner = re.sub('^@', '', owner) if owner is not None else None

        self.__command_manager = CommandManager()

    def handle_message(self, message):
        TgBot.handle_message(self, message)

        chat_id = message['chat']['id']

        if re.match('(?:hi|hello)[!.]?', message['text'], flags=re.I):
            self.send(chat_id, Text("Hi %s!" % message['from']['first_name']))

        if self.__owner is None or message['from']['username'] == self.__owner:
            if re.match('/.+', message['text']):
                try:
                    self.send(chat_id, self.__command_manager.run(message['text']))
                except BadCommand as b:
                    logging.error(b.message)

            elif message['text'].lower() == 'xyzzy':
                self.send(chat_id, Text('Nothing happens.'))


def parse_rcfile(path):
    try:
        with open(path, 'r') as fh:
            logging.info("getting extra flags from %s" % path)
            return list(fh.read().split())
    except FileNotFoundError:
        return list()


def main():
    import argparse
    import os
    import os.path
    import sys
    import asyncio

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--token',  required=True, help='Telegram bot token')
    parser.add_argument('--owner', help='Only respond to this user id when specified')
    parser.add_argument('--no-owner', dest='owner', action='store_const', const=None)

    rc_file = os.path.expanduser(os.getenv('KLEOFASRC') or '~/.kleofasrc')
    args = parser.parse_args(parse_rcfile(rc_file) + sys.argv[1:])

    censored_args = { k: '...' if k == 'token' else vars(args)[k] for k in vars(args) }
    logging.info("running with options: %s" % censored_args)

    event_loop = asyncio.get_event_loop()

    kleofas = Kleofas(event_loop=event_loop, token=args.token, owner=args.owner)

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.warn('Stopping event loop...')
        event_loop.stop()


if __name__ == '__main__':
    main()


