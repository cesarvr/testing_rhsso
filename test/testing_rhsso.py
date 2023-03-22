from kcapi import OpenID, Keycloak
import unittest

class TestingRHSSO(unittest.TestCase):
    def setUp(self):
        # This could be environment variables.
        ENDPOINT = "https://sso-cvaldezr-dev.apps.sandbox-m3.1530.p1.openshiftapps.com"
        USER = "admin"
        PASSWORD = "admin"
        self.REALM = "frankfurt"

        token = OpenID.createAdminClient(USER, PASSWORD, url=ENDPOINT).getToken()
        self.kc = Keycloak(token, ENDPOINT)

    # To add a new test we just add a new method.
    def test_clients(self):
        client = self.kc.build('clients', self.REALM).findFirst({'key': 'clientId', 'value': 'MyClient'})
        self.assertTrue(client != [], "The client MyClient should exists.")
        self.assertFalse(client['publicClient'], "client MyClient should be a private client.")

    # This just fetch all the roles for the realm "Frankfurt" and makes sure the role offline_access is there.
    def test_roles(self):
        roles = self.kc.build('roles', self.REALM).findAll().resp().json()
        roles_by_name = map(lambda role: role['name'], roles)
        self.assertTrue('offline_access' in roles_by_name, "This instance should have a role offline_access.")


if __name__ == '__main__':
    unittest.main()
