'''Parse and execute slash commands
'''


from _metadata import __project__, __version__


class BadCommand(Exception):
    def __init__(self, message):
        self.message = message


class CommandManager:
    def __init__(self, command_file):
        from importlib.machinery import SourceFileLoader
        import logging
        import re

        self.__logger = logging.getLogger(__name__)

        self.__builtins = {
            'help':    { 'action': self.__show_help,
                         'help': 'Show this help' },
            'version': { 'action': "%s %s" % (__project__, __version__),
                         'help': 'Show version' },
        }

        self.__commands = self.__builtins

        if command_file is not None:
            commands = SourceFileLoader('commands', command_file).load_module()

            cmd_pattern = re.compile('cmd_(\w+)')
            for attr in dir(commands):
                match = cmd_pattern.match(attr)
                if match:
                    command  = match.group(1)
                    function = getattr(commands, attr)

                    self.__logger.info("adding custom command '/%s'" % command)
                    self.__commands[command] = { 'action': function, 'help': function.__doc__ }


    def __show_help(self):
        return ("Available commands:\n%s" %
                '\n'.join(sorted(["\t/%s: %s" % (key, self.__commands[key]['help'])
                        for key in self.__commands])))


    def run(self, command_line):
        import re

        if not re.match('/.+', command_line):
            raise BadCommand('Commands need to start with a slash')

        tokens = re.sub('^/', '', command_line).split()

        if tokens:
            command_word = tokens[0]
            args = tokens[1:]

            if command_word in self.__commands:
                action = self.__commands[command_word]['action']

                try:
                    if callable(action):
                        if args:
                            return action(*args)
                        else:
                            return action()
                    else:
                        return action
                except Exception as e:
                    raise BadCommand(str(e))
            else:
                raise BadCommand("Unknown command: %s" % command_word)
        else:
            raise BadCommand("Could not parse command line: %s" % command_line)


