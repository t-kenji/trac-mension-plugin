from distutils.core import setup
from setuptools import find_packages

version='0.2'

setup(
    name='TracMentionPlugin',
    url='https://github.com/t-kenji/trac-mention-plugin',
    long_description='Mention plugin for trac',
    author='t-kenji',
    author_email='protect.2501@gmail.com',
    version=version,
    license = 'BSD', # the same as Trac

    install_requires = [
        'Trac >= 1.2',
        'TracAutocompletePlugin',
    ],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    package_data = {
        'tracmention': [
            'htdocs/css/*.css',
        ]
    },
    entry_points = {
        'trac.plugins': [
            'mention = tracmention'
        ]
    }
)
