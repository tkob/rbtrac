# rbtrac

rbtrac is a [Review Board](https://www.reviewboard.org/) extension and provides the following features:

- Authenticate users with their [Trac](https://trac.edgewall.org/) account
- Pull email address from Trac database on login

# Prerequisites

Trac instance should be running on the same machine as Review Board.

# Installation

    sudo pip install 'git+https://github.com/tkob/rbtrac.git'

Login to Review Board as an admin user, follow [Admin Dashboard] -> [SYSTEM SETTINGS] -> [Authentication].

In [AUTHENTICATION SETTINGS], select [Trac Authentication] as [Authencication Method],
and enter [Trac login URL].

Also enter [Trac environment path] if you want to pull email addresses from the Trac database.
