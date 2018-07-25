# -*- coding: utf-8 -*-
"""Sample Wiki syntax extension plugin."""

import os
import pkg_resources
from genshi.builder import tag

from trac.core import *
from trac.wiki.api import IWikiSyntaxProvider

from tracautocomplete.api import IWikiAutocompleteProvider

class Mention(Component):
    """
    Allows for mention
    """
    implements(IWikiSyntaxProvider, IWikiAutocompleteProvider)

    # IWikiAutocompleteProvider

    def add_strategy(self):
        users = [{'value': name, 'label': nickname, 'email': email} \
                 for name, nickname, email in self.env.get_known_users()]

        template = 'return item.value'
        try:
            from avatar.backend import AvatarBackend
            from avatar.web_ui import AvatarProvider
            if self.env.is_component_enabled(AvatarProvider):
                backend = AvatarBackend(self.env, self.config)
                backend.clear_auth_data()
                for user in users:
                    backend.collect_author(user['value'])
                backend.lookup_author_data()
                for user in users:
                    user['icon'] = backend.generate_avatar(user['value'], 'icon', '30').render()

                template = 'return item.icon + " " + item.value'
        except:
            pass

        return {
            'id': 'mension',
            'match': '\B@(\w*)$',
            'source': users,
            'template': template,
            'replace': 'return "@" + item.value + " "',
            'index': 1,
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
