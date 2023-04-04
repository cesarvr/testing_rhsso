import json, random

from test import data_loader
from kcapi import OpenID, Keycloak
import unittest, requests
import test.helper

ENDPOINT = "https://sso-cvaldezr-dev.apps.sandbox-m3.1530.p1.openshiftapps.com"
USER = "admin"
PASSWORD = "admin"
REALM = "frankfurt"

class Themes:
    def __init__(self, kc):
        self.kc = kc
        self.installed_themes = self.load()

    def load(self):
        headers = {
            'Content-type': 'application/json',
            'Authorization': 'Bearer ' + self.kc.token.get_token()
        }

        response = requests.get(f'{ENDPOINT}/auth/admin/serverinfo', headers=headers)
        info = response.json()
        return info['themes']

    # This function find a particular theme inside RHSSO
    def lookup_theme(self, theme_name, section='login'):
        for theme in self.installed_themes[section]:
            if theme['name'] == theme_name:
              return theme


        return None


class TestingThemes(unittest.TestCase):
    def setUp(self):
        # This could be environment variables.
        token = OpenID.createAdminClient(USER, PASSWORD, url=ENDPOINT).getToken()
        self.kc = Keycloak(token, ENDPOINT)
        self.themes = ['dtag', 'dtag-supplier', 'gfnw', 'gfnw-supplier']

    def testing_themes_are_installed(self):
        rhsso_themes = Themes(self.kc)
        for theme in self.themes:
            theme_info_login = rhsso_themes.lookup_theme(theme, section='login')
            self.assertIsNotNone(theme_info_login, f'Theme {theme} not found.')
            self.assertListEqual(theme_info_login['locales'], ['en', 'de', 'ru'], f"Locales do not match with [en, de, ru]")


    def testing_that_themes_are_deployed_successfully(self):
        for theme in self.themes:
            client_id = test.helper.create_client_for_theme(theme, self.kc, self.assertTrue, REALM)
            login_url = f'{ENDPOINT}/auth/realms/{REALM}/protocol/openid-connect/auth?client_id={client_id}&redirect_uri=https://theme-testing.org&response_type=code&scope=openid&nonce=7aeca9d7-d74c-46ee-806a-2a5ca171d7bc&code_challenge=7OOGYjgwoh9Mn_JRjDKBQP9wV6NdNBvxb2-B41XIDgc&code_challenge_method=S256'
            resp = requests.get(login_url)
            self.assertEqual(200, resp.status_code, "We expect a 200 indicating successful deployment of the theme.")

    def tearDown(self):
        for theme in self.themes:
            test.helper.remove_client_for_theme(theme, self.kc, self.assertTrue, REALM)

if __name__ == '__main__':
    unittest.main()
