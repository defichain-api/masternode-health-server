from masternode_health.monitor import NodeMonitor, parse_args
from unittest import TestCase, mock
from requests.exceptions import HTTPError
from datetime import datetime
from os.path import expanduser
import hashlib


class ParserTest(TestCase):

    def test_all_arguments(self):
        args = parse_args(['--rpchost', 'host', '--verbose', '--defi-path', 'path', '--defi-conf', 'conf', '--api-key', 'key', '--max-block-seconds', '30', '--report'])

        self.assertEqual(args.rpchost, 'host')
        self.assertTrue(args.verbose)
        self.assertTrue(args.report)
        self.assertEqual(args.defi_path, 'path')
        self.assertEqual(args.defi_conf, 'conf')
        self.assertEqual(args.api_key, 'key')
        self.assertEqual(args.max_block_seconds, 30)

    def test_default_arguments(self):
        args = parse_args(['--api-key', 'key'])
        home = expanduser("~")

        self.assertEqual(args.rpchost, 'http://localhost:8554')
        self.assertEqual(args.defi_path, home + '/.defi')
        self.assertEqual(args.defi_conf, home + '/.defi/defi.conf')
        self.assertEqual(args.max_block_seconds, 30)

    def test_apikey_missing(self):
        with self.assertRaises(SystemExit):
            parse_args([])

    def test_apikey_missing_but_verbose(self):
        args = parse_args(['--verbose'])
        self.assertTrue(args.verbose)

    def test_apikey_missing_but_verbose_and_report(self):
        with self.assertRaises(SystemExit):
            parse_args(['--verbose', '--report'])

    def test_version(self):
        with self.assertRaises(SystemExit):
            parse_args(['--api-key', 'bla', '--verison'])


class HealthMonitorTest(TestCase):

    @mock.patch('masternode_health.monitor.open', mock.mock_open(read_data='rpcuser=user\nrpcpassword=password\n'))
    def setUp(self):
        args = parse_args(['--rpchost', 'host', '--verbose', '--api-key', 'key', '--max-block-seconds', '35', '--report', '--defi-path', '/'])
        self.nm = NodeMonitor(args)
        self.home = expanduser("~")

    def _mock_response(
            self,
            status=200,
            content="CONTENT",
            json_data=None,
            raise_for_status=None):
        """
        since we typically test a bunch of different
        requests calls for a service, we are going to do
        a lot of mock responses, so its usually a good idea
        to have a helper function that builds these things
        """
        mock_resp = mock.Mock()
        # mock raise_for_status call w/optional error
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        # set status code and content
        mock_resp.status_code = status
        mock_resp.content = content
        # add json data if provided
        if json_data:
            mock_resp.json = mock.Mock(
                return_value=json_data
            )
        return mock_resp

    @mock.patch('masternode_health.monitor.open', mock.mock_open(read_data=''))
    def test_rpc_creds_missing(self):
        args = parse_args(['--api-key', 'key'])
        self.assertRaises(ValueError, NodeMonitor, args)

    @mock.patch('masternode_health.monitor.open', mock.mock_open(read_data='[test]\nrpcuser=user\nrpcpassword=password\n'))
    def test_rpc_creds_in_test_fails(self):
        args = parse_args(['--api-key', 'key'])
        self.assertRaises(ValueError, NodeMonitor, args)

    @mock.patch('masternode_health.monitor.open', mock.mock_open(read_data='[test]\nrpcuser=bla\nrpcpassword=bla\n[main]\nrpcuser=user\nrpcpassword=password\n'))
    def test_rpc_creds_in_test_and_main_ok(self):
        args = parse_args(['--api-key', 'key'])
        nm = NodeMonitor(args)
        self.assertEqual(nm.rpcuser, 'user')
        self.assertEqual(nm.rpcpassword, 'password')

    @mock.patch('masternode_health.monitor.open', mock.mock_open(read_data='rpcuser=user\nrpcpassword=pass=word\n'))
    def test_rpc_creds_in_test_and_have_equal_sign(self):
        args = parse_args(['--api-key', 'key'])
        nm = NodeMonitor(args)
        self.assertEqual(nm.rpcuser, 'user')
        self.assertEqual(nm.rpcpassword, 'pass=word')

    @mock.patch('masternode_health.monitor.open', mock.mock_open(read_data='rpcuser=user\nrpcpassword=password\n'))
    def test_NodeMonitor_init(self):
        self.assertEqual(self.nm.defi_path, '/')
        self.assertEqual(self.nm.defi_conf, self.home + '/.defi/defi.conf')
        self.assertTrue(self.nm.verbose)
        self.assertTrue(self.nm.report)
        self.assertEqual(self.nm.max_block_seconds, 35)
        self.assertEqual(self.nm.api_key, 'key')
        self.assertEqual(self.nm.rpchost, 'host')
        self.assertEqual(self.nm.rpcuser, 'user')
        self.assertEqual(self.nm.rpcpassword, 'password')

    @mock.patch('masternode_health.monitor.requests.post')
    def test_rpcquery_ok(self, mock_post):
        data = {
            'result': {"test": "ok"}
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = self.nm._rpcquery('getminiginfo')
        self.assertEqual(result['test'], 'ok')

    @mock.patch('masternode_health.monitor.requests.post')
    def test_rpcquery_with_param_ok(self, mock_post):
        data = {
            'result': {"test": "ok"}
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = self.nm._rpcquery('getminiginfo', params={'id': 1})
        self.assertEqual(result['test'], 'ok')

    @mock.patch('masternode_health.monitor.requests.post')
    def test_rpcquery_failed(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("rpcerror"))
        mock_post.return_value = mock_resp
        self.assertRaises(HTTPError, self.nm._rpcquery, 'getmininginfo')

    @mock.patch('masternode_health.monitor.requests.post')
    def test_checkAreNodesMining_single_mn_fails(self, mock_post):
        data = {
            "masternodes": [
                {
                    "id": "8cb09568143d7bae6822a7a78f91cb907c23fd12dcf986d4d2c8de89457edf87",
                    "lastblockcreationattempt": "2021-08-23T19:48:21Z",
                },
            ],
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = self.nm._checkAreNodesMining()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], '8cb09568143d7bae6822a7a78f91cb907c23fd12dcf986d4d2c8de89457edf87')
        self.assertEqual(result[0][1], False)

    @mock.patch('masternode_health.monitor.requests.post')
    def test_checkAreNodesMining_single_mn_ok(self, mock_post):
        datenow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        data = {
            "masternodes": [
                {
                    "id": "8cb09568143d7bae6822a7a78f91cb907c23fd12dcf986d4d2c8de89457edf87",
                    "lastblockcreationattempt": datenow,
                },
            ],
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = self.nm._checkAreNodesMining()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], '8cb09568143d7bae6822a7a78f91cb907c23fd12dcf986d4d2c8de89457edf87')
        self.assertEqual(result[0][1], True)

    @mock.patch('masternode_health.monitor.requests.post')
    def test_checkAreNodesMining_multiple_mn_ok(self, mock_post):
        datenow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        data = {
            "masternodes": [
                {
                    "id": "8cb09568143d7bae6822a7a78f91cb907c23fd12dcf986d4d2c8de89457edf87",
                    "lastblockcreationattempt": datenow,
                },
                {
                    "id": "2ceb7c9c3bea0bd0e5e4199eca5d0b797d79a0077a9108951faecf715e1e1a57",
                    "lastblockcreationattempt": datenow,
                }
            ],
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = self.nm._checkAreNodesMining()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], '8cb09568143d7bae6822a7a78f91cb907c23fd12dcf986d4d2c8de89457edf87')
        self.assertEqual(result[0][1], True)
        self.assertEqual(result[1][0], '2ceb7c9c3bea0bd0e5e4199eca5d0b797d79a0077a9108951faecf715e1e1a57')
        self.assertEqual(result[1][1], True)

    @mock.patch('masternode_health.monitor.requests.post')
    def test_checkAreNodesMining_multiple_mn_one_ok(self, mock_post):
        datenow = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        data = {
            "masternodes": [
                {
                    "id": "8cb09568143d7bae6822a7a78f91cb907c23fd12dcf986d4d2c8de89457edf87",
                    "lastblockcreationattempt": datenow,
                },
                {
                    "id": "2ceb7c9c3bea0bd0e5e4199eca5d0b797d79a0077a9108951faecf715e1e1a57",
                    "lastblockcreationattempt": "2021-08-23T19:48:21Z",
                }
            ],
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = self.nm._checkAreNodesMining()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], '8cb09568143d7bae6822a7a78f91cb907c23fd12dcf986d4d2c8de89457edf87')
        self.assertEqual(result[0][1], True)
        self.assertEqual(result[1][0], '2ceb7c9c3bea0bd0e5e4199eca5d0b797d79a0077a9108951faecf715e1e1a57')
        self.assertEqual(result[1][1], False)

    @mock.patch('masternode_health.monitor.requests.post')
    def test_checkAreNodesMining_empty_ok(self, mock_post):
        data = {
            "masternodes": [],
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = self.nm._checkAreNodesMining()
        self.assertEqual(len(result), 0)

    @mock.patch('masternode_health.monitor.requests.post')
    def test_uploadToApi_ok(self, mock_post):
        data = {
            'result': {"message": "ok"}
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = self.nm._uploadToApi('endpoint', {})
        self.assertEqual(result['message'], 'ok')

    @mock.patch('masternode_health.monitor.requests.post')
    def test_uploadToApi_ok_without_result(self, mock_post):
        data = {"message": "ok"}

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = self.nm._uploadToApi('endpoint', {})
        self.assertEqual(result['message'], 'ok')

    @mock.patch('masternode_health.monitor.requests.post')
    def test_uploadToApi_failed(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("rpcerror"))
        mock_post.return_value = mock_resp
        self.assertRaises(SystemExit, self.nm._uploadToApi, 'endpoint', {})

    @mock.patch('masternode_health.monitor.requests.post')
    def test_processNodeInfo_failed(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("rpcerror"))
        mock_post.return_value = mock_resp

        self.assertRaises(SystemExit, self.nm._processNodeInfo)

    @mock.patch('masternode_health.monitor.requests.post')
    def test_processNodeInfo_no_debuglog(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=OSError("No debug log"))
        mock_post.return_value = mock_resp

        self.assertRaises(SystemExit, self.nm._processNodeInfo)

    def test_processServerStats_ok(self):
        self.nm._processServerStats()
        self.assertGreater(self.nm.loadavg, 0)
        self.assertGreater(self.nm.memUsed, 0)
        self.assertGreater(self.nm.memTotal, 0)
        self.assertGreater(self.nm.diskUsed, 0)
        self.assertGreater(self.nm.diskTotal, 0)

    @mock.patch('masternode_health.monitor.requests.post')
    def test_processNode_fail(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("rpcerror"))
        mock_post.return_value = mock_resp

        self.assertRaises(SystemExit, self.nm.processNode)

    def test_toString(self):
        self.nm.uptime = 0
        self.nm.blockcount = 0
        self.nm.bestblockhash = "best"
        self.nm.connectioncount = 0
        self.nm.checkNodes = [('server', True)]
        self.nm.loadavg = 0
        self.nm.memTotal = 5
        self.nm.memUsed = 2
        self.nm.diskTotal = 5
        self.nm.diskUsed = 2
        self.nm.logSize = 0
        self.nm.nodeVersion = "1"
        self.nm.numCores = 10
        ret = self.nm.__repr__()
        self.assertEqual(hashlib.md5(ret.encode('utf-8')).hexdigest(), 'd28564cfe5e1cbb0eb2d4f3adda1b5c1')

    def test_drawProgressBar(self):
        progress = self.nm._drawProgressBar(0.5)
        self.assertEqual(progress, '[▰▰▰▰▰▰▰        ] 50%')
