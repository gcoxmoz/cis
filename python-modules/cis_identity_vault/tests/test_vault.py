import os
import subprocess
import time
from moto import mock_dynamodb2


@mock_dynamodb2
class TestVault(object):
    def test_crud_it_should_succeed(self):
        from cis_identity_vault import vault
        v = vault.IdentityVault()
        os.environ['CIS_ENVIRONMENT'] = 'purple'
        os.environ['CIS_REGION_NAME'] = 'us-east-1'
        os.environ['DEFAULT_AWS_REGION'] = 'us-east-1'
        v.connect()
        result = v.find_or_create()
        assert result is not None
        result = v.destroy()
        assert result['ResponseMetadata']['HTTPStatusCode'] == 200


class TestVaultDynalite(object):
    def setup_class(self):
        dynalite_port = '9567'
        self.dynaliteprocess = subprocess.Popen(['dynalite', '--port', dynalite_port], preexec_fn=os.setsid)

    def test_create_using_dynalite(self):
        os.environ['CIS_ENVIRONMENT'] = 'local'
        os.environ['CIS_DYNALITE_PORT'] = '9567'
        os.environ['CIS_REGION_NAME'] = 'us-east-1'
        from cis_identity_vault import vault
        v = vault.IdentityVault()
        v.connect()
        result = v.find_or_create()
        assert result is not None
        result = v.find_or_create()
        assert result is not None

    def teardown_class(self):
        os.killpg(os.getpgid(self.dynaliteprocess.pid), 15)
