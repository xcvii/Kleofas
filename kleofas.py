#!/usr/bin/env python3


'''
Personal Telegram bot
'''


import TgBot
import logging
import re


logging.basicConfig(format='%(asctime)-12s %(thread)d %(name)s %(levelname)s: %(message)s',
        level=logging.INFO)


class Kleofas(TgBot.TgBot):
    def __init__(self, token, owner):
        TgBot.TgBot.__init__(self, token)
        self.__owner = re.sub('^@', '', owner) if owner is not None else None

    def handle_message(self, update_id, message):
        TgBot.TgBot.handle_message(self, update_id, message)

        chat_id = message['chat']['id']

        if re.match('(?:hi|hello)[!.]?', message['text'], flags=re.I):
            self.send_message(chat_id, "Hi %s!" % message['from']['first_name'])

        if self.__owner is None or message['from']['username'] == self.__owner:
            if message['text'].lower() == 'xyzzy':
                self.send_message(chat_id, 'Nothing happens.')


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

    parser = argparse.ArgumentParser(description=__doc__, fromfile_prefix_chars='@')
    parser.add_argument('--token',  required=True, help='Telegram bot token')
    parser.add_argument('--owner', help='Only respond to this user id when specified')
    parser.add_argument('--no-owner', dest='owner', action='store_const', const=None)

    rc_file = os.path.expanduser(os.getenv('KLEOFASRC') or '~/.kleofasrc')
    args = parser.parse_args(parse_rcfile(rc_file) + sys.argv[1:])

    censored_args = { k: '...' if k == 'token' else vars(args)[k] for k in vars(args) }
    logging.info("running with options: %s" % censored_args)

    kleofas = Kleofas(token=args.token, owner=args.owner)

    try:
        kleofas.start()
    except KeyboardInterrupt:
        pass
    finally:
        logging.warn('Shutting down...')
        kleofas.stop()


if __name__ == '__main__':
    main()


