#!/usr/bin/env python3


'''
Personal Telegram bot
'''


from TgBot import TgBot
from CommandManager import CommandManager, BadCommand

import logging
import re


logging.basicConfig(format='%(asctime)-12s %(levelname)-5s %(name)s: %(message)s',
        level=logging.INFO)


class Kleofas(TgBot):
    def __init__(self, loop, token, owner, command_file):
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
                    self.send(chat_id, self.__command_manager.run(message['text']))
                except BadCommand as b:
                    logging.error(b.message)


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
    parser.add_argument('--command-file', help='')

    rc_file = os.path.expanduser(os.getenv('KLEOFASRC') or '~/.kleofasrc')
    args = parser.parse_args(parse_rcfile(rc_file) + sys.argv[1:])

    censored_args = { k: '...' if k == 'token' else vars(args)[k] for k in vars(args) }
    logging.info("running with options: %s" % censored_args)

    loop = asyncio.get_event_loop()

    kleofas = Kleofas(loop=loop, token=args.token, owner=args.owner,
            command_file=args.command_file)

    try:
        loop.run_until_complete(kleofas.start())
    except KeyboardInterrupt:
        loop.stop()
    finally:
        logging.info('Stopping event loop...')
        loop.close()


if __name__ == '__main__':
    main()


