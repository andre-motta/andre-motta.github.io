#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

AUTHOR = 'Andre Lustosa'
SITENAME = 'Andre Lustosa'
SITEURL = ''

PATH = 'content'
THEME = 'themes/minimal'

TIMEZONE = 'America/New_York'
DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ('GitHub', 'https://github.com/andre-motta'),
    ('Google Scholar', 'https://scholar.google.com/citations?user=lQwnqkwAAAAJ&hl=en&oi=ao'),
    ('LinkedIn', 'https://www.linkedin.com/in/andre-motta/'),
    ('tongs', 'https://tongs.tools'),
    ('Claude Fleet Monitor', 'https://github.com/andre-motta/claude-fleet-monitor'),
)

# Social widget
SOCIAL = (
    ('GitHub', 'https://github.com/andre-motta'),
    ('LinkedIn', 'https://www.linkedin.com/in/andre-motta/'),
)

DEFAULT_PAGINATION = 10

# URL/Save as patterns
ARTICLE_URL = 'blog/{date:%Y}/{slug}.html'
ARTICLE_SAVE_AS = 'blog/{date:%Y}/{slug}.html'
PAGE_URL = '{slug}.html'
PAGE_SAVE_AS = '{slug}.html'

# Static paths
STATIC_PATHS = ['images', 'extra']

# Extra files to copy to output root
EXTRA_PATH_METADATA = {
    'extra/CNAME': {'path': 'CNAME'},
}

# Menu items
MENUITEMS = (
    ('Home', '/'),
    ('About', '/about.html'),
    ('Archive', '/archives.html'),
    ('CV', '/extra/Andre_Motta_Resume.pdf'),
)

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# Author metadata
AUTHOR_EMAIL = 'alustosa@redhat.com'
AUTHOR_BIO = 'Principal Software Engineer @ Red Hat, Ecosystems'
AUTHOR_TAGLINE = 'Building AI infrastructure for every accelerator.'

CURRENT_YEAR = datetime.datetime.now().year

# Site metadata
SITE_DESCRIPTION = 'Personal website and blog of Andre Lustosa, Principal Software Engineer at Red Hat Ecosystems'
