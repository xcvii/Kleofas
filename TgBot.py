'''
Simple asynchronous Python wrapper for the Telegram Bot REST API
'''


from Types import Text


class NoResult(Exception):
    def __init__(self, message):
        self.message = message


class TgBot:
    def __init__(self, event_loop, token):
        import logging

        # config
        self.__logger = logging.getLogger('TgBot')
        self.__update_poll_period = 1
        self.__loop = event_loop
        self.__token = token
        self.__host = 'api.telegram.org'

        # state
        self.__last_update_id = None

        # start
        self.__loop.call_soon(self.__get_me)
        self.__loop.call_soon(self.__init_last_update_id)
        self.__keep_polling(self.__update_poll_period, self.__get_updates)


    def __keep_polling(self, period, callback):
        import functools

        def f():
            callback()
            self.__loop.call_later(
                    period,
                    functools.partial(self.__keep_polling, period, callback))

        self.__loop.call_soon(f)


    def __request(self, method, **params):
        import http.client
        import json
        import urllib.parse

        if params:
            query = "%s?%s" % (method, urllib.parse.urlencode(params))
        else:
            query = method

        self.__logger.debug("running query: https://%s/bot<token>/%s" % (self.__host, query))

        full_query = "/bot%s/%s" % (self.__token, query)

        conn = http.client.HTTPSConnection(self.__host)

        try:
            conn.request('GET', full_query)
        except ConnectionResetError as e:
            raise NoResult('Connection reset by peer')

        response = conn.getresponse()

        data = response.read()
        result_json = json.loads(data.decode('UTF-8'))

        try:
            if result_json['ok']:
                return result_json['result']
            else:
                raise NoResult(result_json['description'])
        except KeyError:
            raise NoResult('Unkown error')


    def __get_me(self):
        self.__logger.debug(self.__request('getMe'))


    def __get_username(self, user):
        name = user['first_name']
        if 'last_name' in user:
            name = "%s %s" % (name, user['last_name'])
        if 'username' in user:
            name = "%s (@%s)" % (name, user['username'])
        return name


    def handle_message(self, update_id, message):
        self.__logger.info("received message from %s (chat #%d): %s" % (
            self.__get_username(message['from']),
            message['chat']['id'],
            message['text'],
            ))


    def __init_last_update_id(self):
        updates = self.__request('getUpdates')
        if updates:
            self.__last_update_id = updates[-1]['update_id']
            self.__logger.debug("setting last update id to %d" % self.__last_update_id)


    def __get_updates(self):
        updates = self.__request('getUpdates', offset=(self.__last_update_id or 0) + 1)

        for update in updates:
            update_id = update['update_id']

            if self.__last_update_id is None or self.__last_update_id < update_id:
                if 'message' in update:
                    self.handle_message(update_id, update['message'])

                self.__last_update_id = update_id


    def send_text(self, chat_id, text):
        self.__logger.info("sending text (chat #%d): %s" % (chat_id, text))
        message = self.__request('sendMessage', chat_id=chat_id, text=text)
        return message


    def send(self, chat_id, message):
        if type(message) is Text:
            self.send_text(chat_id, message.text)


