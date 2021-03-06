'''Simple asynchronous Python wrapper for the Telegram Bot REST API
'''


from _metadata import __project__, __version__

import asyncio


class NoResult(Exception):
    def __init__(self, message):
        self.message = message


class TgBot:
    def __init__(self, loop, token, max_workers=1):
        import aiohttp
        import logging
        import concurrent.futures

        # config
        self.__logger = logging.getLogger(__name__)
        self.__loop = loop
        self.__token = token
        self.__host = 'api.telegram.org'
        self.__http_session = aiohttp.ClientSession(loop=loop)
        self.__update_poll_period = 1
        self.__executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

        # state
        self.__last_update_id = None


    def __del__(self):
        self.__http_session.close()


    @asyncio.coroutine
    def start(self):
        yield from self.__get_me()
        yield from self.__init_last_update_id()

        while True:
            yield from self.__get_updates()
            yield from asyncio.sleep(self.__update_poll_period, loop=self.__loop)


    @asyncio.coroutine
    def __request(self, verb, **params):
        import json
        import urllib.parse

        self.__logger.debug("running query: %s %s" % (verb, params))

        url = "https://%s/bot%s/%s" % (self.__host, self.__token, verb)

        try:
            response = yield from self.__http_session.get(url, params=params)
        except:
            import sys
            raise NoResult(str(sys.exc_info()[1]))

        data = yield from response.read()

        try:
            result_json = json.loads(data.decode('UTF-8'))
        except:
            import sys
            raise NoResult(str(sys.exc_info()[1]))

        try:
            if result_json['ok']:
                return result_json['result']
            else:
                raise NoResult(result_json['description'])
        except KeyError:
            raise NoResult('Unkown error')


    @asyncio.coroutine
    def __get_me(self):
        result = yield from self.__request('getMe')
        self.__logger.debug(result)


    def __get_username(self, user):
        name = user['first_name']
        if 'last_name' in user:
            name = "%s %s" % (name, user['last_name'])
        if 'username' in user:
            name = "%s (@%s)" % (name, user['username'])
        return name


    def handle_message(self, message):
        self.__logger.info("received message from %s (chat #%d): %s" % (
            self.__get_username(message['from']),
            message['chat']['id'],
            message['text'],
            ))


    @asyncio.coroutine
    def __init_last_update_id(self):
        updates = yield from self.__request('getUpdates')
        if updates:
            self.__last_update_id = updates[-1]['update_id']
            self.__logger.debug("setting last update id to %d" % self.__last_update_id)


    @asyncio.coroutine
    def __get_updates(self):
        import functools

        offset = (self.__last_update_id or 0) + 1
        updates = yield from self.__request('getUpdates', offset=offset)

        for update in updates:
            update_id = update['update_id']

            if self.__last_update_id is None or self.__last_update_id < update_id:
                if 'message' in update:
                    self.__loop.call_soon(
                            functools.partial(self.handle_message, update['message']))

                self.__last_update_id = update_id


    @asyncio.coroutine
    def __send_text(self, chat_id, message):
        self.__logger.info("sending text (chat #%d): %s" % (chat_id, message))
        message = yield from self.__request('sendMessage', chat_id=chat_id, text=message)
        return message


    @asyncio.coroutine
    def __send_typing(self, chat_id):
        yield from self.__request('sendChatAction', chat_id=chat_id, action='typing')


    @asyncio.coroutine
    def __send(self, chat_id, message_object):
        if callable(message_object):
            try:
                typing = yield from self.__send_typing(chat_id)
                if not typing:
                    self.__logger.warning('failed to set typing status')

                message = yield from self.__loop.run_in_executor(self.__executor, message_object)
            except:
                import sys
                self.__logger.error(str(sys.exc_info()[1]))
                return
        else:
            message = message_object

        try:
            content_type = message.content_type()
        except AttributeError:
            content_type = 'text/plain'

        if content_type == 'text/plain':
            yield from self.__send_text(chat_id, message)


    def send(self, chat_id, message_object):
        asyncio.async(self.__send(chat_id, message_object))


