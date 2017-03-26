'''
'''


class BadCommand(Exception):
    def __init__(self, message):
        self.message = message


class CommandManager:
    def __init__(self):
        self.__builtins = {
            'version': ('Kleofas, Personal Telegram Bot, ' +
                        'version 20170319.0, written by Endre Tamas SAJO ' +
                        '(endre.t.sajo@gmail.com)'),
            'help':    self.__show_help,
        }

        self.__commands = self.__builtins


    def __show_help(self):
        return ("Available commands: %s" %
                    ', '.join(sorted(["/%s" % key for key in self.__commands])))


    def run(self, command_line):
        import re

        if not re.match('/.+', command_line):
            raise BadCommand('Commands need to start with a slash')

        tokens = re.sub('^/', '', command_line).split()

        if tokens:
            command_word = tokens[0]
            args = tokens[1:]

            if command_word in self.__commands:
                command = self.__commands[command_word]

                try:
                    if callable(command):
                        if args:
                            return command(*args)
                        else:
                            return command()
                    else:
                        return command
                except Exception as e:
                    raise BadCommand(str(e))
            else:
                raise BadCommand("Unknown command: %s" % command_word)
        else:
            raise BadCommand("Could not parse command line: %s" % command_line)


