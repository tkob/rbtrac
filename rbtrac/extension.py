# rbtrac Extension for Review Board.

from __future__ import unicode_literals

from django import forms
from django.conf import settings
from django.conf.urls import patterns, include
from django.contrib.auth.models import AnonymousUser, User
from djblets.siteconfig.forms import SiteSettingsForm
from djblets.siteconfig.models import SiteConfiguration
from reviewboard.accounts.backends import AuthBackend
from reviewboard.extensions.base import Extension
from reviewboard.extensions.hooks import AuthBackendHook
from trac.core import TracError
from trac.env import Environment
from trac.web.session import DetachedSession
import logging
import pycurl
import sys

class TracExtension(Extension):
    metadata = {
        'Name': 'rbtrac',
        'Summary': 'Authenticate users with their Trac account',
    }
    is_configurable = True

    def initialize(self):
        AuthBackendHook(self, TracAuthBackend)

class TracAuthSettingsForm(SiteSettingsForm):
    auth_tracauth_trac_login_url = forms.CharField(
        label="Trac login URL",
        help_text="e.g. http://localhost/trac/sandbox/login",
        required=True)

    auth_tracauth_trac_env_path = forms.CharField(
        label="Trac environment path",
        help_text="Path to the local Trac environment directory e.g. /var/trac/projects/sandbox",
        required=False)

    class Meta:
        title = "Trac Auth Backend Settings"

class TracAuthBackend(AuthBackend):
    backend_id = 'tkob_tracauth'
    name = 'Trac Authentication'
    settings_form = TracAuthSettingsForm

    def __init__(self, siteconfig=None):
        siteconfig = siteconfig or SiteConfiguration.objects.get_current()
        self.siteconfig = siteconfig

        self.env = None
        trac_env_path = siteconfig.get('auth_tracauth_trac_env_path')
        if trac_env_path != "":
            try:
                self.env = Environment(path=trac_env_path)
            except TracError, e:
                logging.error(e)

        self.login_url = str(siteconfig.get('auth_tracauth_trac_login_url'))
        self.curl = pycurl.Curl()

    def authenticate(self, username, password):
        logging.debug('authenticate: username=%s, login_url=%s'
                % (username, self.login_url))
        try:
            curl = self.curl
            curl.setopt(pycurl.URL, self.login_url)
            curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_ANY)
            curl.setopt(pycurl.USERPWD, str('%s:%s' % (username, password)))
            curl.perform()
            status = curl.getinfo(pycurl.HTTP_CODE)
            logging.debug("authenticate: status=%d" % status)
        except:
            logging.error(sys.exc_info())

        if status == 200:
            logging.debug('authenticate: username=%s, success' % username)
            return self.get_or_create_user(username)
        else:
            logging.debug('authenticate: username=%s, fail' % username)
            return None

    def get_or_create_user(self, username, request=None):
        user, is_new = User.objects.get_or_create(username=username)
        if is_new:
            user.set_unusable_password()
            user.save()

        if self.env != None:
            session = DetachedSession(env=self.env, sid=username)
            if "email" in session:
                user.email = session["email"]
                user.save()

        return user
