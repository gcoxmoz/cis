import boto3
import json
import http.client

client_id_name = '/iam/cis/development/change_client_id'
client_secret_name = '/iam/cis/development/change_service_client_secret'
base_url = 'vkvtuvkdo4.execute-api.us-west-2.amazonaws.com'
client = boto3.client('ssm')

def get_secure_parameter(parameter_name):
    response = client.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']

def get_client_secret():
    return get_secure_parameter(client_secret_name)

def get_client_id():
    return get_secure_parameter(client_id_name)

def exchange_for_access_token():
    conn = http.client.HTTPSConnection("auth-dev.mozilla.auth0.com")
    payload_dict = dict(
        client_id=get_client_id(),
        client_secret=get_client_secret(),
        audience="https://api.sso.allizom.org",
        grant_type="client_credentials"
    )

    payload = json.dumps(payload_dict)
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    return data['access_token']

def test_api_is_alive():
    access_token = exchange_for_access_token()
    conn = http.client.HTTPSConnection(base_url)
    headers =  { 'authorization': "Bearer {}".format(access_token) }
    conn.request("GET", "/development/change/status?sequenceNumber=123456", headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    assert data['identity_vault'] is not None

def test_publishing_a_profile_it_should_be_accepted():
    from cis_profile import fake_profile
    u = fake_profile.FakeUser()
    json_payload = u.as_json()

    from cis_profile import WellKnown

    wk = WellKnown()

    print()

    import jsonschema
    import json
    jsonschema.validate(json.loads(json_payload), wk.get_schema())
    access_token = exchange_for_access_token()
    conn = http.client.HTTPSConnection(base_url)
    headers =  {
        'authorization': "Bearer {}".format(access_token),
        'Content-type': 'application/json'
    }
    conn.request("POST", "/development/change", json_payload, headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data)

if __name__== "__main__":
  print(test_api_is_alive())
  print(test_publishing_a_profile_it_should_be_accepted())
