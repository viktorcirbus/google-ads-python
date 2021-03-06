# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests the configuration helper module."""

import mock
import os
import yaml
from pyfakefs.fake_filesystem_unittest import TestCase as FileTestCase

from google.ads.google_ads import config

class ConfigTest(FileTestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.developer_token = 'abc123'
        self.client_id = 'client_id_123456789'
        self.client_secret = 'client_secret_987654321'
        self.refresh_token = 'refresh'
        self.login_customer_id = '1234567890'
        self.path_to_private_key_file = '/test/path/to/config.json'
        self.delegated_account = 'delegated@account.com'
        self.endpoint = 'www.testendpoint.com'

    def test_load_from_yaml_file(self):
        file_path = os.path.join(os.path.expanduser('~'), 'google-ads.yaml')
        self.fs.create_file(file_path, contents=yaml.safe_dump({
            'developer_token': self.developer_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token}))

        result = config.load_from_yaml_file()

        self.assertEqual(result['developer_token'], self.developer_token)
        self.assertEqual(result['client_id'], self.client_id)
        self.assertEqual(result['client_secret'], self.client_secret)
        self.assertEqual(result['refresh_token'], self.refresh_token)

    def test_load_from_yaml_file_missing_required_key(self):
        file_path = os.path.join(os.path.expanduser('~'), 'google-ads.yaml')
        # save a YAML file without a required developer_token key
        self.fs.create_file(file_path, contents=yaml.safe_dump({
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token}))

        self.assertRaises(
            ValueError,
            config.load_from_yaml_file)

    def test_load_from_yaml_file_with_path(self):
        custom_path = os.path.expanduser('/test/custom/path')
        file_path = os.path.join(custom_path, 'google-ads.yaml')
        self.fs.create_file(file_path, contents=yaml.safe_dump({
            'developer_token': self.developer_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token}))

        result = config.load_from_yaml_file(path=file_path)

        self.assertEqual(result['developer_token'], self.developer_token)
        self.assertEqual(result['client_id'], self.client_id)
        self.assertEqual(result['client_secret'], self.client_secret)
        self.assertEqual(result['refresh_token'], self.refresh_token)

    def test_load_from_yaml_file_login_cid_int(self):
        login_cid_int = 1234567890
        file_path = os.path.join(os.path.expanduser('~'), 'google-ads.yaml')
        self.fs.create_file(file_path, contents=yaml.safe_dump({
            'login_customer_id': login_cid_int,
            'developer_token': self.developer_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token}))

        result = config.load_from_yaml_file()

        self.assertEqual(result['developer_token'], self.developer_token)
        self.assertEqual(result['client_id'], self.client_id)
        self.assertEqual(result['client_secret'], self.client_secret)
        self.assertEqual(result['refresh_token'], self.refresh_token)

    def test_parse_yaml_document_to_dict(self):
        yaml_doc = ('client_id: {}\n'
                    'client_secret: {}\n'
                    'developer_token: {}\n'
                    'refresh_token: {}\n'.format(
                        self.client_id, self.client_secret,
                        self.developer_token, self.refresh_token))

        result = config.parse_yaml_document_to_dict(yaml_doc)

        self.assertEqual(result['developer_token'], self.developer_token)
        self.assertEqual(result['client_id'], self.client_id)
        self.assertEqual(result['client_secret'], self.client_secret)
        self.assertEqual(result['refresh_token'], self.refresh_token)

    def test_parse_yaml_document_to_dict_missing_required_key(self):
        # YAML document is missing the required developer_token key
        yaml_doc = ('client_id: {}\n'
                    'client_secret: {}\n'
                    'refresh_token: {}\n'.format(
                        self.client_id, self.client_secret,
                        self.developer_token, self.refresh_token))

        self.assertRaises(
            ValueError,
            config.parse_yaml_document_to_dict,
            yaml_doc)

    def test_load_from_dict(self):
        config_data = {
              'developer_token': self.developer_token,
              'client_id': self.client_id,
              'client_secret': self.client_secret,
              'refresh_token': self.refresh_token}
        self.assertEqual(config.load_from_dict(config_data), config_data)
    
    def test_load_from_dict_error(self):
        config_data = 111
        self.assertRaises(ValueError, config.load_from_dict, config_data)

    def test_load_from_env(self):
        environ = {
            'GOOGLE_ADS_DEVELOPER_TOKEN': self.developer_token,
            'GOOGLE_ADS_CLIENT_ID': self.client_id,
            'GOOGLE_ADS_CLIENT_SECRET': self.client_secret,
            'GOOGLE_ADS_REFRESH_TOKEN': self.refresh_token,
            'GOOGLE_ADS_LOGGING': '{"test": true}',
            'GOOGLE_ADS_ENDPOINT': self.endpoint,
            'GOOGLE_ADS_LOGIN_CUSTOMER_ID': self.login_customer_id,
            'GOOGLE_ADS_PATH_TO_PRIVATE_KEY_FILE':
                self.path_to_private_key_file,
            'GOOGLE_ADS_DELEGATED_ACCOUNT': self.delegated_account}

        with mock.patch('os.environ', environ):
            result = config.load_from_env()
            self.assertEqual(result, {
                'developer_token': self.developer_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
                'logging': {'test': True},
                'endpoint': self.endpoint,
                'login_customer_id': self.login_customer_id,
                'path_to_private_key_file': self.path_to_private_key_file,
                'delegated_account': self.delegated_account})

    def test_load_from_env_missing_required_key(self):
        # environ is missing required developer_token key
        environ = {
            'GOOGLE_ADS_CLIENT_ID': self.client_id,
            'GOOGLE_ADS_CLIENT_SECRET': self.client_secret,
            'GOOGLE_ADS_REFRESH_TOKEN': self.refresh_token,
            'GOOGLE_ADS_LOGGING': '{"test": true}',
            'GOOGLE_ADS_ENDPOINT': self.endpoint,
            'GOOGLE_ADS_LOGIN_CUSTOMER_ID': self.login_customer_id,
            'GOOGLE_ADS_PATH_TO_PRIVATE_KEY_FILE':
                self.path_to_private_key_file,
            'GOOGLE_ADS_DELEGATED_ACCOUNT': self.delegated_account}

        with mock.patch('os.environ', environ):
            self.assertRaises(
                ValueError,
                config.load_from_env)

    def test_validate_dict(self):
        config_data = {'invalid': 'config'}

        self.assertRaises(
            ValueError,
            config.validate_dict,
            config_data
        )

    def test_validate_dict(self):
        config_data = {key: 'test' for key in config._REQUIRED_KEYS}
        try:
            config.validate_dict(config_data)
        except ValueError as ex:
            self.fail('test_validate_dict failed unexpectedly: {}'.format(ex))

    def test_validate_dict_with_invalid_login_cid(self):
        config_data = {key: 'test' for key in config._REQUIRED_KEYS}
        config_data['login_customer_id'] = '123-456-5789'
        self.assertRaises(
            ValueError,
            config.validate_dict,
            config_data)

    def test_validate_dict_with_valid_login_cid(self):
        config_data = {key: 'test' for key in config._REQUIRED_KEYS}
        config_data['login_customer_id'] = '1234567893'
        try:
            config.validate_dict(config_data)
        except ValueError as ex:
            self.fail('test_validate_dict_with_login_cid failed unexpectedly: '
                      '{}'.format(ex))

    def test_validate_login_customer_id_invalid(self):
        self.assertRaises(
            ValueError,
            config.validate_login_customer_id,
            '123-456-7890')

    def test_validate_login_customer_id_too_short(self):
        self.assertRaises(
            ValueError,
            config.validate_login_customer_id,
            '123')

    def test_get_oauth2_installed_app_keys(self):
        self.assertEqual(config.get_oauth2_installed_app_keys(),
                         config._OAUTH2_INSTALLED_APP_KEYS)

    def test_get_oauth2_service_account_keys(self):
        self.assertEqual(config.get_oauth2_service_account_keys(),
                         config._OAUTH2_SERVICE_ACCOUNT_KEYS)

    def test_convert_login_customer_id_to_str_with_int(self):
        config_data = {'login_customer_id': 1234567890}
        expected = {'login_customer_id': '1234567890'}
        self.assertEqual(config.convert_login_customer_id_to_str(config_data),
                         expected)

    def test_parse_login_customer_id_with_str(self):
        config_data = {'login_customer_id': '1234567890'}
        self.assertEqual(config.convert_login_customer_id_to_str(config_data),
                         config_data)

    def test_parse_login_customer_id_with_none(self):
        config_data = {'not_login_customer_id': 1234567890}
        self.assertEqual(config.convert_login_customer_id_to_str(config_data),
                         config_data)
