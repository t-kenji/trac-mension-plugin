"""Sample Wiki syntax extension plugin."""

import os
import pkg_resources
from genshi.builder import tag

from trac.core import *
from trac.wiki.api import IWikiSyntaxProvider

from autocomplete_provider.api import IStrategyAdapter

class Mention(Component):
    """
    Allows for mention
    """
    implements(IWikiSyntaxProvider, IStrategyAdapter)

    def __init__(self):
        self.users = []
        for user_data in self.env.get_known_users():
            self.users.append(user_data[0].encode())
        self.users.sort()

    # IStrategyAdapter methods

    def add_strategy(self):
        template = 'return value'

        try:
            from avatar.web_ui import AvatarProvider
            if self.env.is_component_enabled(AvatarProvider):
                template = 'return \'<img src="{}/avatar/\' + value + \'" style="vertical-align: text-bottom;" width="16" height="16" />\' + \'&nbsp;\' + value'.format(self.env.href())
        except:
            pass

        return {
            'id': 'mension',
            'match': '\B@(\w*)$',
            'candidates': self.users,
            'template': template,
            'replace': 'return "@" + value + " "',
            'index': 1
        }

    # IWikiSyntaxProvider methods

    def get_link_resolvers(self):
        return []

    def get_wiki_syntax(self):
        def create_mention(f, match, fullmatch):
            mention = match
            mention_syntax = tag.b(mention)
            return mention_syntax
        yield (r'\B(?P<mention>@[^ ]+)', create_mention)
