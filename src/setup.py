from setuptools import setup, find_packages


def get_attr(path, attr):
    import re

    pattern = re.compile(r"%s\s*=\s*['\"]([^'\"]+)['\"]" % attr)
    with open(path, 'r') as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                return match.group(1)

    raise Exception("attribute not found: %s" % attr)


setup(
    name         = get_attr('kleofas/_metadata.py', '__project__'),
    version      = get_attr('kleofas/_metadata.py', '__version__'),
    author       = get_attr('kleofas/_metadata.py', '__author__'),
    author_email = get_attr('kleofas/_metadata.py', '__email__'),

    packages     = find_packages(),
    entry_points = { 'console_scripts': [ 'kleofas = kleofas.__main__:main' ] },
)


