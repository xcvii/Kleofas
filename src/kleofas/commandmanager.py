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
            'version': "%s %s" % (__project__, __version__),
            'help':    self.__show_help,
        }

        self.__commands = self.__builtins

        if command_file is not None:
            commands = SourceFileLoader('commands', command_file).load_module()

            cmd_pattern = re.compile('cmd_(\w+)')
            for attr in dir(commands):
                match = cmd_pattern.match(attr)
                if match:
                    command = match.group(1)
                    command_fun = getattr(commands, attr)

                    self.__logger.info("adding custom command '/%s'" % command)
                    self.__commands[command] = command_fun


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


