from masternode_health.monitor import rpcquery, checkAreNodesMining, reportJson, processNodeInfo, processServerStats, parse_args
from unittest import TestCase, mock
from requests.exceptions import HTTPError
from datetime import datetime


class ParserTest(TestCase):

    def test_all_arguments(self):
        args = parse_args(['--rpcuser', 'test', '--rpchost', 'host', '--rpcpassword', 'password', '--verbose', '--defi-path', 'path', '--api-key', 'key', '--max-block-seconds', '30'])

        self.assertEqual(args.rpcuser, 'test')
        self.assertEqual(args.rpchost, 'host')
        self.assertEqual(args.rpcpassword, 'password')
        self.assertTrue(args.verbose)
        self.assertEqual(args.defi_path, 'path')
        self.assertEqual(args.api_key, 'key')
        self.assertEqual(args.max_block_seconds, 30)

    def test_default_arguments(self):
        args = parse_args(['--rpcuser', 'test', '--rpcpassword', 'password', '--verbose', '--defi-path', 'path', '--api-key', 'key'])

        self.assertEqual(args.rpcuser, 'test')
        self.assertEqual(args.rpchost, 'http://localhost:8554')
        self.assertEqual(args.rpcpassword, 'password')
        self.assertTrue(args.verbose)
        self.assertEqual(args.defi_path, 'path')
        self.assertEqual(args.api_key, 'key')
        self.assertEqual(args.max_block_seconds, 30)

    def test_rpc_creds_missing(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args([])

        self.assertEqual(cm.exception.code, 'Please specify rpcuser and rpcpassword argument')

    def test_defi_path_missing(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['--rpcuser', 'test', '--rpcpassword', 'password'])

        self.assertEqual(cm.exception.code, 'Please specify defi-path argument')

    def test_apikey_missing(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args(['--rpcuser', 'test', '--rpcpassword', 'password', '--defi-path', 'path'])

        self.assertEqual(cm.exception.code, 'Please specify an api-key argument')


class HealthMonitorTest(TestCase):

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

    @mock.patch('masternode_health.monitor.requests.post')
    def test_rpcquery_ok(self, mock_post):
        data = {
            'result': {"test": "ok"}
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = rpcquery('getminiginfo', '', '', '')
        self.assertEqual(result['test'], 'ok')

    @mock.patch('masternode_health.monitor.requests.post')
    def test_rpcquery_with_param_ok(self, mock_post):
        data = {
            'result': {"test": "ok"}
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = rpcquery('getminiginfo', '', '', '', params={'id': 1})
        self.assertEqual(result['test'], 'ok')

    @mock.patch('masternode_health.monitor.requests.post')
    def test_rpcquery_failed(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("rpcerror"))
        mock_post.return_value = mock_resp
        self.assertRaises(HTTPError, rpcquery, 'getmininginfo', '', '', '')

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

        result = checkAreNodesMining(30, '', '', '')

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

        result = checkAreNodesMining(30, '', '', '')

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

        result = checkAreNodesMining(30, '', '', '')

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

        result = checkAreNodesMining(30, '', '', '')

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

        result = checkAreNodesMining(30, '', '', '')
        self.assertEqual(len(result), 0)

    @mock.patch('masternode_health.monitor.requests.post')
    def test_reportJson_ok(self, mock_post):
        data = {
            'result': {"message": "ok"}
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp

        result = reportJson('key', 'endpoint', {})
        self.assertEqual(result['message'], 'ok')

    @mock.patch('masternode_health.monitor.requests.post')
    def test_reportJson_failed(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("rpcerror"))
        mock_post.return_value = mock_resp
        self.assertRaises(HTTPError, reportJson, 'key', 'endpoint', {})

    @mock.patch('masternode_health.monitor.requests.post')
    def test_processNodeInfo_failed(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("rpcerror"))
        mock_post.return_value = mock_resp

        args = parse_args(['--rpcuser', 'test', '--rpcpassword', 'password', '--verbose', '--defi-path', 'path', '--api-key', 'key'])
        self.assertRaises(SystemExit, processNodeInfo, args)

    @mock.patch('masternode_health.monitor.requests.post')
    def test_processServerStats_failed(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("rpcerror"))
        mock_post.return_value = mock_resp

        args = parse_args(['--rpcuser', 'test', '--rpcpassword', 'password', '--verbose', '--defi-path', '/', '--api-key', 'key'])
        self.assertRaises(SystemExit, processServerStats, args)
