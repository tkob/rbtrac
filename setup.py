from __future__ import unicode_literals

from reviewboard.extensions.packaging import setup


PACKAGE = "rbtrac"
VERSION = "0.1"

setup(
    name=PACKAGE,
    version=VERSION,
    description="Authenticate users with their Trac account",
    author="tkob",
    packages=["rbtrac"],
    entry_points={
        'reviewboard.extensions':
            '%s = rbtrac.extension:TracExtension' % PACKAGE,
    },
    package_data={
        b'rbtrac': [
            'templates/rbtrac/*.txt',
            'templates/rbtrac/*.html',
        ],
    }
)