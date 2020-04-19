"""Tests for certbot_dns_corenetworks.dns_corenetworks."""

import unittest

import mock
from certbot import errors
from certbot.compat import os
from certbot.plugins import dns_test_common
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

API_USER = "my_user"
API_PASSWORD = "secure"


class AuthenticatorTest(test_util.TempDirTestCase, dns_test_common.BaseAuthenticatorTest):
    """Test for Hetzner DNS Authenticator."""

    def setUp(self):
        from certbot_dns_corenetworks.dns_corenetworks import Authenticator

        super(AuthenticatorTest, self).setUp()

        path = os.path.join(self.tempdir, "file.ini")
        dns_test_common.write({
            "corenetworks_username": API_USER,
            "corenetworks_password": API_PASSWORD
        }, path)

        self.config = mock.MagicMock(
            corenetworks_credentials=path, corenetworks_propagation_seconds=0
        )  # don't wait during tests

        self.auth = Authenticator(self.config, "corenetworks")

        self.mock_client = mock.MagicMock()
        # _get_corenetworks_client | pylint: disable=protected-access
        self.auth._get_corenetworks_client = mock.MagicMock(return_value=self.mock_client)

    def test_perform(self):
        self.auth.perform([self.achall])

        expected = [
            mock.call.add_txt_record(DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY, mock.ANY)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_cleanup(self):
        # _attempt_cleanup | pylint: disable=protected-access
        self.auth.nameCache["_acme-challenge." + DOMAIN] = "_acme-challenge." + DOMAIN
        self.auth._attempt_cleanup = True
        self.auth.cleanup([self.achall])

        expected = [mock.call.del_txt_record(DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY)]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_creds(self):
        dns_test_common.write({
            "corenetworks_username": API_USER,
            "corenetworks_password": API_PASSWORD
        }, self.config.corenetworks_credentials)
        self.auth.perform([self.achall])

        expected = [
            mock.call.add_txt_record(DOMAIN, "_acme-challenge." + DOMAIN, mock.ANY, mock.ANY)
        ]
        self.assertEqual(expected, self.mock_client.mock_calls)

    def test_no_creds(self):
        dns_test_common.write({}, self.config.corenetworks_credentials)
        self.assertRaises(errors.PluginError, self.auth.perform, [self.achall])

    def test_missing_user_or_password(self):
        dns_test_common.write({"corenetworks_username": API_USER},
                              self.config.corenetworks_credentials)
        self.assertRaises(errors.PluginError, self.auth.perform, [self.achall])

        dns_test_common.write({"corenetworks_password": API_PASSWORD},
                              self.config.corenetworks_credentials)
        self.assertRaises(errors.PluginError, self.auth.perform, [self.achall])


if __name__ == "__main__":
    unittest.main()
