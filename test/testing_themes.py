import json, random

from test import data_loader
from kcapi import OpenID, Keycloak
import unittest, requests

ENDPOINT = "https://sso-cvaldezr-dev.apps.sandbox-m3.1530.p1.openshiftapps.com"
USER = "admin"
PASSWORD = "admin"
REALM = "frankfurt"


def create_user(kc, is_true):
    batman_password = 'lalelilulo'
    batman = {"enabled": 'true',
              "attributes": {},
              "username": "batman",
              "firstName": "Bruce",
              "lastName": "Wayne",
              "emailVerified": ""
              }

    users = kc.build('users', REALM)
    state_user_creation = users.create(batman)
    state_user_creds_update = users.update_credentials(batman['username'], batman_password, False).isOk()

    is_true(state_user_creds_update and state_user_creation,
            f'Failed to setup the user and credentials for realm {REALM}, make sure that SSO is up and running.')


def create_client_for_theme(theme, kc, is_true):
    client_id = f'client-{theme}'
    theme_client = {
        "enabled": True,
        "attributes": {
            "login_theme": theme,
        },
        "publicClient": True,
        "redirectUris": ['*'],
        "clientId": client_id,
        "protocol": "openid-connect",
        "directAccessGrantsEnabled": True
    }

    clients = kc.build('clients', REALM)
    client_creation_state = clients.create(theme_client).isOk()
    is_true(client_creation_state, f'Failed to create client {client_id}')

    return client_id


def remove_client_for_theme(theme, kc, is_true):
    client_id = f'client-{theme}'
    clients = kc.build('clients', REALM)
    client_resource = clients.findFirstByKV('clientId', client_id)
    if client_resource:
        state = clients.remove(client_resource['id']).isOk()
        is_true(state, f'Failed to delete client {client_id}')



class TestingThemes(unittest.TestCase):
    def setUp(self):
        # This could be environment variables.
        token = OpenID.createAdminClient(USER, PASSWORD, url=ENDPOINT).getToken()
        self.kc = Keycloak(token, ENDPOINT)
        self.themes = ['dtag', 'dtag-supplier', 'gfnw', 'gfnw-supplier']

    def testing_that_themes_are_deployed_successfully(self):
        # https://sso-cvaldezr-dev.apps.sandbox-m3.1530.p1.openshiftapps.com/auth/realms/frankfurt/protocol/openid-connect/auth?client_id=account-console&redirect_uri=https%3A%2F%2Fsso-cvaldezr-dev.apps.sandbox-m3.1530.p1.openshiftapps.com%2Fauth%2Frealms%2Ffrankfurt%2Faccount%2F%23%2F&state=0800f7d8-a495-4f9b-9b4f-cbca56fe01d1&response_mode=fragment&response_type=code&scope=openid&nonce=d8c91b81-5bd5-45f6-81e9-72b116d080c1&code_challenge=SJRDAVOwVu3yF0RXyuqABYKS690EcscHY03u0GXP3Lc&code_challenge_method=S256

        for theme in self.themes:
            client_id = create_client_for_theme(theme, self.kc, self.assertTrue)
            login_url = f'{ENDPOINT}/auth/realms/{REALM}/protocol/openid-connect/auth?client_id={client_id}&redirect_uri=https://theme-testing.org&response_type=code&scope=openid&nonce=7aeca9d7-d74c-46ee-806a-2a5ca171d7bc&code_challenge=7OOGYjgwoh9Mn_JRjDKBQP9wV6NdNBvxb2-B41XIDgc&code_challenge_method=S256'
            resp = requests.get(login_url)
            self.assertEqual(200, resp.status_code, "We expect a 200 indicating successful deployment of the theme.")


    def tearDown(self):
        for theme in self.themes:
            remove_client_for_theme(theme, self.kc, self.assertTrue)

if __name__ == '__main__':
    unittest.main()
