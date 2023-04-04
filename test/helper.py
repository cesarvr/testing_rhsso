
def create_user(kc, is_true, REALM='frankfurt'):
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


def create_client_for_theme(theme, kc, is_true, REALM='frankfurt'):
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


def remove_client_for_theme(theme, kc, is_true, REALM='frankfurt'):
    client_id = f'client-{theme}'
    clients = kc.build('clients', REALM)
    client_resource = clients.findFirstByKV('clientId', client_id)
    if client_resource:
        state = clients.remove(client_resource['id']).isOk()
        is_true(state, f'Failed to delete client {client_id}')

