'''example command file
'''


def cmd_xyzzy():
    '''Say the magic word'''

    import time
    time.sleep(3)
    return 'Nothing happens.'


def cmd_fortune():
    '''"Print a random, hopefully interesting, adage"'''

    import subprocess
    return subprocess.check_output(['fortune'])

