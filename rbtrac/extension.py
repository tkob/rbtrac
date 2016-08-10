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
from trac.env import Environment
from trac.web.session import DetachedSession


class TracExtension(Extension):
    metadata = {
        'Name': 'rbtrac',
        'Summary': 'Authenticate users with their Trac account',
    }
    is_configurable = True

    def initialize(self):
        AuthBackendHook(self, TracAuthBackend)

class TracAuthSettingsForm(SiteSettingsForm):
    auth_tracauth_trac_env_path = forms.CharField(
        label="Trac environment path",
        help_text="Path to the local Trac environment directory",
        required=False)

    class Meta:
        title = "Trac Auth Backend Settings"

class TracAuthBackend(AuthBackend):
    backend_id = 'tkob_tracauth'
    name = 'Trac Authentication'
    settings_form = TracAuthSettingsForm

    def __init__(self):
        self.siteconfig = SiteConfiguration.objects.get_current()
        trac_env_path = self.siteconfig.get('auth_tracauth_trac_env_path')
        self.env = Environment(path=trac_env_path)

    def authenticate(self, username, password):
        # TODO: authenticate the user
        return self.get_or_create_user(username, password=password)

    def get_or_create_user(self, username, request=None, password=None):
        user, is_new = User.objects.get_or_create(username=username)
        if is_new:
            user.set_unusable_password()
            user.save()

        session = DetachedSession(env=self.env, sid=username)
        if "email" in session:
            user.email = session["email"]
            user.save()

        return user
