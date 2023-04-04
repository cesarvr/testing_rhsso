import json


def get_test_data(TEST_DATA):
    with open(TEST_DATA) as json_file:
        return json.load(json_file)


def populating_rhsso_roles(kc, test, TEST_DATA):
    roles_data = get_test_data(TEST_DATA)

    realm = roles_data['realm']
    realm_creation = kc.admin().create({"enabled": "true", "id": realm, "realm": realm}).response.status_code
    roles_api = kc.build('roles', realm)
    test.assertTrue(realm_creation == 201 or realm_creation == 409, 'Realm should be created')

    print('loading test data')
    for role in roles_data['roles']['realm']:
        state = roles_api.create(role).response.status_code
        test.assertTrue(state == 201 or state == 409, 'Role should be created')

    print('loading test data: done')


def populating_rhsso_client_scope(kc, test, TEST_DATA):
    cs_data = get_test_data(TEST_DATA)
    cache = {}
    realm = cs_data['realm']
    realm_creation = kc.admin().create({"enabled": "true", "id": realm, "realm": realm}).response.status_code

    test.assertTrue(realm_creation == 201 or realm_creation == 409, 'Realm should be created')
    cs_api = kc.build('client-scopes', realm)

    new_mapper_skeleton = lambda name, claim, user: {"protocol":"openid-connect","config":{"id.token.claim":"true","access.token.claim":"true","userinfo.token.claim":"true","multivalued":"","aggregate.attrs":"","user.attribute":user,"claim.name":claim},"name":name,"protocolMapper":"oidc-usermodel-attribute-mapper"}

    new_client_scope_proto = lambda name: {"attributes":
        {
            "display.on.consent.screen": "true",
            "include.in.token.scope": "true"
        },
        "name": name,
        "protocol": "openid-connect"
    }

    for im in cs_data['identityProviderMappers']:
        cs_name = im['identityProviderAlias']

        name = im['name']
        if 'claim' not in im['config'] or 'user.attribute' not in im['config']:
            continue

        claim = im['config']['claim']
        user_attr = im['config']['user.attribute']

        if cs_name not in cache:
            status = cs_api.create(new_client_scope_proto(cs_name)).response.status_code
            test.assertTrue(status == 201 or status == 409, f'Client Scope should be created, status received {status}')
            cs_obj = cs_api.find(cs_name)
            cache[cs_name] = cs_obj

        cs_obj = cache[cs_name]
        state = cs_obj.add_mapper(new_mapper_skeleton(name, claim, user_attr))


def depopulating_rhsso(kc, test, TEST_DATA):
    roles_data = get_test_data(TEST_DATA)

    realm = roles_data['realm']
    realm_removal = kc.admin().remove(realm).isOk()
    test.assertTrue(realm_removal, 'Realm should be removed')
