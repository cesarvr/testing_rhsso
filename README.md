Just a quick example on how to test a particular RHSSO instance with [Python unittest](https://docs.python.org/3/library/unittest.html) library. 

## Dependencies

- **Python 3**
- **KCAPI**: 
  Make sure you have installed the Keycloak API (kcapi). 

  ```sh 
  pip install kcapi
  ```

## What Does It Test

This example tests the following: 

- There is a realm called ``frankfurt`` and insider this realm there is:
  - A general role called ``offline_access`` (Almost always succeed because is a role created by RHSSO)
  - A client named ``MyClient`` exists and is not public. 

## Configuration 
To test it make sure to spin up a RHSSO in the cloud via ([Openshift Online](https://www.redhat.com/en/technologies/cloud-computing/openshift/try-it)). 
Once you got it running change go to the test file inside the test folder and change [these parameters](https://github.com/cesarvr/testing_rhsso/blob/main/test/testing_rhsso.py#L7-L10) to target your deployment:

```python
   def setUp(self):
        # This could be environment variables.
        ENDPOINT = "https://sso-cvaldezr-dev.apps.sandbox-m3.1530.p1.openshiftapps.com"
        USER = "admin"
        PASSWORD = "admin"
        self.REALM = "frankfurt"
```

Where ``ENDPOINT`` is the URL of your running RHSSO instance and ``self.REALM`` allow you to check for the same conditions but in other realms. 

> Disclaimer: these tests only work with HTTPS at the moment. 



## Running the tests 

To run the test you just need to get into the project root folder and run: 

```sh
python3 -m unittest discover test -v
```

![running_tests](https://user-images.githubusercontent.com/3899337/226871925-0c01ac6b-fa07-4684-9fc6-b813e167340e.gif)
