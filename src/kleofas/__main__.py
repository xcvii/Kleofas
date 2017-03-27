'''Project entry point
'''


from _metadata import __project__, __version__

from kleofas import Kleofas

import logging
import sys


logging.basicConfig(format='%(asctime)-12s %(levelname)-5s %(name)s: %(message)s',
        level=logging.INFO)


def __parse_rcfile(path):
    try:
        with open(path, 'r') as fh:
            return list(fh.read().split())
    except sys.FileNotFoundError:
        return list()


def main():
    import argparse
    import os
    import os.path
    import asyncio

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--token',  required=True, help='Telegram bot token')
    parser.add_argument('--owner', help='Only respond to this user id when specified')
    parser.add_argument('--no-owner', dest='owner', action='store_const', const=None)
    parser.add_argument('--command-file', metavar='PATH', help='Specify a python file with global \
            cmd_* functions to be used as custom commands')

    rc_file = os.path.expanduser(os.getenv('KLEOFASRC') or '~/.kleofasrc')
    args = parser.parse_args(__parse_rcfile(rc_file) + sys.argv[1:])

    logging.info("running %s version %s" % (__project__, __version__))
    logging.info("getting extra flags from %s" % rc_file)

    censored_args = { k: '...' if k == 'token' else vars(args)[k] for k in vars(args) }
    logging.info("using options: %s" % censored_args)

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

