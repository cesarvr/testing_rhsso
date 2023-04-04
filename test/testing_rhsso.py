import json

from test import data_loader
from kcapi import OpenID, Keycloak
import unittest, requests

ENDPOINT = "https://sso-cvaldezr-dev.apps.sandbox-m3.1530.p1.openshiftapps.com"
USER = "admin"
PASSWORD = "admin"
REALM = "frankfurt"

TEST_DATA_ROLES = '../data/roles.json'
TEST_DATA_CLIENT_SCOPE = '../data/cs.json'


def get_test_data(data):
    with open(data) as json_file:
        return json.load(json_file)


class TestingRHSSO(unittest.TestCase):
    def setUp(self):
        # This could be environment variables.
        token = OpenID.createAdminClient(USER, PASSWORD, url=ENDPOINT).getToken()
        self.kc = Keycloak(token, ENDPOINT)

        # data_loader.populating_rhsso_client_scope(self.kc, self, TEST_DATA_CLIENT_SCOPE)

    # To add a new test we just add a new method.
    def test_clients(self):
        client = self.kc.build('clients', REALM).findFirst({'key': 'clientId', 'value': 'MyClient'})
        self.assertTrue(client != [], "The client MyClient should exists.")
        self.assertFalse(client['publicClient'], "client MyClient should be a private client.")

    # This just fetch all the roles for the realm "Frankfurt" and makes sure the role offline_access is there.
    def test_roles(self):
        roles = self.kc.build('roles', REALM).findAll().resp().json()
        roles_by_name = map(lambda role: role['name'], roles)
        self.assertTrue('offline_access' in roles_by_name, "This instance should have a role offline_access.")

    def testing_prometheus_is_installed(self):
        response = requests.get(f'{ENDPOINT}/auth/realms/master/metrics')
        self.assertEqual(response.status_code, 200, 'Keycloak metric SPI is not available.')

    def testing_client_scope_mappings(self):
        cs_data = get_test_data(TEST_DATA_CLIENT_SCOPE)
        realm = cs_data['realm']
        cs = self.kc.build('client-scopes', realm)

        cache = {}
        claims = None
        attributes = None

        for im in cs_data['identityProviderMappers']:
            name = im['name']
            cs_name = im['identityProviderAlias']

            if 'claim' not in im['config'] or 'user.attribute' not in im['config']:
                continue

            claim = im['config']['claim']
            user_attr = im['config']['user.attribute']

            if cs_name not in cache:
                cs_obj = cs.find(cs_name)
                self.assertIsNotNone(cs_obj, f'We expect {cs_name} to be a client scope for realm {realm}')
                cache[cs_name] = cs_obj
                raw = cs_obj.all()['protocolMappers']

                claims = list(map(lambda mapper: mapper['config']['claim.name'], raw))
                attributes = list(map(lambda mapper: mapper['config']['user.attribute'], raw))

            self.assertTrue(claim in claims, f'Claim {claim} is expected to be in the scope {cs_name}')
            self.assertTrue(user_attr in attributes, f'Attribute {user_attr} is expected to be in the scope {cs_name}')

    def testing_roles(self):
        roles_data = get_test_data(TEST_DATA_ROLES)

        realm = roles_data['realm']
        roles_obj = self.kc.build('roles', realm).all()
        roles = map(lambda r: r.role['name'], roles_obj)

        roles = list(roles)

        for role in roles_data['roles']['realm']:
            self.assertTrue(role['name'] in roles, f'We expect role {role["name"]} to exist on {ENDPOINT}')

    def testing_that_themes_are_installed_successfully(self):
        self.CLIENT_NAME = 'test-themes'
        theme_client = {
            "enabled": True,
            "attributes": {},
            "redirectUris": [],
            "clientId": self.CLIENT_NAME,
            "protocol": "openid-connect",
            "directAccessGrantsEnabled": True
        }

        clients = self.kc.build('clients', REALM)
        client_creation_state = clients.create(theme_client).isOk()
        self.assertTrue(client_creation_state, f'Failed to create client {self.CLIENT_NAME}')


    def tearDown(self):
        # Teardown
        clients = self.kc.build('clients', REALM)
        client_resource = clients.findFirstByKV('clientID', self.CLIENT_NAME)
        clients.remove(client_resource['id'])


if __name__ == '__main__':
    unittest.main()
