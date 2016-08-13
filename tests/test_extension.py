# vim: set fileencoding=utf-8 :

from django.conf import settings
settings.configure()

import unittest
import pycurl
from rbtrac.extension import TracAuthBackend, TracEnvFactory
from trac.core import TracError

class TestTracAuthBackend(unittest.TestCase):
    def test_init_trac_login_url(self):
        '''
        login_url property is set from auth_tracauth_trac_login_url

        '''
        sut = TracAuthBackend(
                siteconfig={
                    'auth_tracauth_trac_env_path': '',
                    'auth_tracauth_trac_login_url': 'http://localhost/trac/login',
                    }
                )
        self.assertEqual(sut.login_url, 'http://localhost/trac/login')

    def test_init_trac_env_path_is_empty(self):
        '''
        env property will be None if auth_tracauth_trac_env_path is emoty

        '''
        sut = TracAuthBackend(
                siteconfig={
                    'auth_tracauth_trac_env_path': '',
                    'auth_tracauth_trac_login_url': 'http://localhost/trac/login',
                    }
                )
        self.assertEqual(sut.env, None)


    def test_init_trac_env_path_is_invalid(self):
        '''
        env property will be None if auth_tracauth_trac_env_path is invalid

        '''
        class RaisingEnvFactory(TracEnvFactory):
            def create(self, path):
                raise TracError('invalid url')
        sut = TracAuthBackend(
                siteconfig={
                    'auth_tracauth_trac_env_path': '/invalid',
                    'auth_tracauth_trac_login_url': 'http://localhost/trac/login',
                    },
                env_factory=RaisingEnvFactory(),
                )
        self.assertEqual(sut.env, None)


    def test_authenticate_fail(self):
        '''
        authenticate returns None if authentication fails

        '''
        class MockCurl():
            def setopt(self, a, b):
                pass
            def perform(self):
                pass
            def getinfo(self, x):
                if x == pycurl.HTTP_CODE:
                    return 401
                raise Error()
        sut = TracAuthBackend(
                siteconfig={
                    'auth_tracauth_trac_env_path': '',
                    'auth_tracauth_trac_login_url': 'http://localhost/trac/login',
                    }
                )
        sut.curl = MockCurl()
        actual = sut.authenticate("admin", "secret")
        self.assertEqual(actual, None)

    def test_authenticate_error(self):
        '''
        authenticate returns None if authentication not completed bacause of
        an error

        '''
        class MockCurl():
            def setopt(self, a, b):
                pass
            def perform(self):
                raise Exception()
            def getinfo(self, x):
                return 200
        sut = TracAuthBackend(
                siteconfig={
                    'auth_tracauth_trac_env_path': '',
                    'auth_tracauth_trac_login_url': 'http://localhost/trac/login',
                    }
                )
        sut.curl = MockCurl()
        actual = sut.authenticate("admin", "secret")
        self.assertEqual(actual, None)

    class MockUser():
        def set_unusable_password(self):
            pass
        def save(self):
            pass

    class MockCurl():
        def setopt(self, a, b):
            pass
        def perform(self):
            pass
        def getinfo(self, x):
            return 200

    def test_authenticate_success(self):
        '''
        authenticate returns a user if authentication succeeded

        '''
        sut = TracAuthBackend(
                siteconfig={
                    'auth_tracauth_trac_env_path': '',
                    'auth_tracauth_trac_login_url': 'http://localhost/trac/login',
                    }
                )
        sut.curl = self.MockCurl()
        class MockUser():
            def set_unusable_password(self):
                pass
            def save(self):
                pass
        mock_user = MockUser()
        def _get_or_create(username):
            return mock_user, False
        sut._get_or_create = _get_or_create
        actual = sut.authenticate("admin", "secret")
        self.assertEqual(actual, mock_user)

    def test_authenticate_pull_email(self):
        '''
        if the session attribute contains an email address,
        email property of the user is set to the email address

        '''
        class MockEnvFactory(TracEnvFactory):
            def create(self, path):
                return {}
        sut = TracAuthBackend(
                siteconfig={
                    'auth_tracauth_trac_env_path': '/',
                    'auth_tracauth_trac_login_url': 'http://localhost/trac/login',
                    },
                env_factory=MockEnvFactory(),
                )
        sut.curl = self.MockCurl()
        mock_user = self.MockUser()
        def _get_or_create(username):
            return mock_user, False
        sut._get_or_create = _get_or_create
        def _create_session(username):
            return {'email': 'postmaster@example.com'}
        sut._create_session = _create_session
        sut.authenticate("admin", "secret")
        self.assertEqual(mock_user.email, 'postmaster@example.com')
