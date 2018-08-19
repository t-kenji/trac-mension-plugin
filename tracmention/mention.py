# -*- coding: utf-8 -*-
"""Mention Wiki syntax extension plugin."""

import os
import itertools

from trac.core import *
from trac.web.api import IRequestFilter
from trac.web.chrome import (
    ITemplateStreamFilter, ITemplateProvider,
    add_stylesheet
)
from trac.wiki.api import IWikiSyntaxProvider
from genshi.builder import tag
from genshi.filters.transform import Transformer, START, TEXT

from tracautocomplete.api import IWikiAutocompleteProvider

class MentionModule(Component):
    """
    Allows for mention
    """

    implements(IRequestFilter,
               IWikiSyntaxProvider,
               IWikiAutocompleteProvider,
               ITemplateProvider,
               ITemplateStreamFilter,
    )

    # IWikiAutocompleteProvider methods

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

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if template in ('ticket.html',):
            add_stylesheet(req, 'tracmention/css/mention.css')

        return template, data, content_type

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        from pkg_resources import resource_filename

        return [('tracmention', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return []

    # ITemplateStreamFilter methods

    def filter_stream(self, req, method, filename, stream, data):
        if not req.path_info.startswith('/ticket'):
            return stream

        author = req.authname
        if len(author) == 0:
            return stream

        def _find_change(stream):
            kind0, data0, pos0 = stream[0]
            class0 = data0[1].get('class')

            for kind, data, pos in stream:
                if (kind in TEXT) and ('@' + author in data):
                    self.env.log.info('data: {}'.format(data0))
                    return itertools.chain([(kind0,
                                             (data0[0], data0[1] | [('class', class0 + ' to-me')]),
                                             pos0)], stream[1:])
            return stream

        xpath = '//div[@id="changelog"]/div'
        stream |= Transformer(xpath).filter(_find_change)
        return stream
