import unittest
import asyncio
from unittest.mock import patch, Mock
import settings
settings.TESTING = True
import db
import ipn_service
import requests
from settings import IPN_AUTH


class TestIPNService(unittest.TestCase):

    def setUp(self) -> None:
        db.DATABASE["database"] = "btc_ipn_test"
        self.ldb = db.DataBase()
        self.ldb.set_setting("ipn_sync_block", 0)

    def tearDown(self) -> None:
        self.ldb.delete_block_hash(2, "hash-test")
        self.ldb.delete_block_hash(5, "hash-test")
        self.ldb.delete_block_hash(6, "hash-test")
        self.ldb.delete_block_hash(8, "hash-test")
        self.ldb.set_setting("ipn_sync_block", 0)

    def test_ipn(self):
        self.ldb.add_output(2, "test-add", 1.1, "hash-test")
        self.ldb.add_output(5, "test-add", 2.2, "hash-test")
        self.ldb.add_output(8, "test-add2", 2.2, "hash-test")
        self.ldb.add_ipn("test-add", "http://test.com", type="btc", max_confirms=3)
        data = {
            "address": "test-add",
            "confirmed": 3.3,
            "unconfirmed": 0,
            "ipn_auth": IPN_AUTH
        }

        attrs = {'json.return_value': data}
        mk = Mock(ok=True, **attrs)
        with patch.object(requests, 'post', return_value=mk) as mock_method:
            asyncio.run(ipn_service.main())
            mock_method.assert_called_with(data=data, url='http://test.com')
            self.assertEqual(self.ldb.get_ipn_status("test-add"), "done")

    def test_ipn_fail(self):
        self.ldb.add_output(2, "test-add", 1.1, "hash-test")
        self.ldb.add_output(5, "test-add", 2.2, "hash-test")
        self.ldb.add_output(8, "test-add2", 2.2, "hash-test")
        self.ldb.add_ipn("test-add", "http://test.com", type="btc", max_confirms=3)
        data = {
            "address": "test-add",
            "confirmed": 3.3,
            "unconfirmed": 0,
            "ipn_auth": IPN_AUTH
        }

        attrs = {'json.return_value': None}
        mk = Mock(ok=True, **attrs)
        with patch.object(requests, 'post', return_value=mk) as mock_method:
            asyncio.run(ipn_service.main())
            mock_method.assert_called_with(data=data, url='http://test.com')
            self.assertEqual(self.ldb.get_ipn_status("test-add"), "fail")

    def test_ipn_unconfirmed(self):
        self.ldb.add_output(2, "test-add", 1.1, "hash-test")
        self.ldb.add_ipn("test-add", "http://test.com", type="btc", max_confirms=3)
        data = {
            "address": "test-add",
            "confirmed": 0,
            "unconfirmed": 1.1,
            "ipn_auth": IPN_AUTH
        }

        attrs = {'json.return_value': data}
        mk = Mock(ok=True, **attrs)
        with patch.object(requests, 'post', return_value=mk) as mock_method:
            asyncio.run(ipn_service.main())
            mock_method.assert_called_with(data=data, url='http://test.com')
            self.assertEqual(self.ldb.get_ipn_status("test-add"), "done")


class TestDb(unittest.TestCase):

    def setUp(self):
        db.DATABASE["database"] = "btc_ipn_test"
        self.ldb = db.DataBase()
        self.ldb.delete_block_hash(2, "hash-test")
        self.ldb.delete_block_hash(5, "hash-test")
        self.ldb.delete_block_hash(6, "hash-test")
        self.ldb.delete_block_hash(8, "hash-test")

    def tearDown(self):
        self.ldb.delete_block_hash(2, "hash-test")
        self.ldb.delete_block_hash(5, "hash-test")
        self.ldb.delete_block_hash(6, "hash-test")
        self.ldb.delete_block_hash(8, "hash-test")

    def test_add_output(self):
        self.ldb.add_output(2, "test-add", 1.1, "hash-test")
        self.ldb.add_output(2, "test-add", 2.2, "hash-test")
        self.assertEqual(self.ldb.get_total_received("test-add"), [0, 3.3])

        self.ldb.add_output(5, "test-add", 7.5, "hash-test")
        self.ldb.add_output(6, "test-add", 0.5, "hash-test")
        self.assertEqual(self.ldb.get_total_received("test-add"), [3.3, 8])

    def test_delete_block_hash(self):
        self.ldb.add_output(2, "test-add", 1.1, "hash-test")
        self.ldb.add_output(2, "test-add", 2.2, "hash-test")
        self.assertEqual(self.ldb.get_total_received("test-add"), [0, 3.3])
        self.ldb.delete_block_hash(2, "hash-test")
        self.assertEqual(self.ldb.get_total_received("test-add"), [0, 0])
        self.assertEqual(self.ldb.get_total_received("test-add1"), [0, 0])

    def test_get_block_hash(self):
        self.ldb.add_output(2, "test-add", 1.1, "hash-test")
        self.ldb.add_output(2, "test-add", 2.2, "hash-test")
        self.assertEqual(self.ldb.get_block_hash(2), "hash-test")
        self.assertEqual(self.ldb.get_block_hash(1), False)

    def test_settings(self):
        self.ldb.set_setting("test", "123")
        assert self.ldb.get_setting("test") == "123"
        self.ldb.set_setting("test", 55)
        self.assertEqual(self.ldb.get_setting("test"), '55')


if __name__ == '__main__':
    unittest.main()
