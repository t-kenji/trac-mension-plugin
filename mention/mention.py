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
        return {
            'id': 'mension',
            'match': '/\B@(\w*)$/',
            'candidates': self.users,
            'template': 'function(mension) { return mension; }',
            'replace': 'function(mension) { return "@" + mension + " "; }',
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
        yield (r"(?P<mention>@[^ ]+)", create_mention)
