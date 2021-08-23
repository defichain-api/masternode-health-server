from masternode_health.monitor import rpcquery
from unittest import TestCase, mock
from requests.exceptions import HTTPError

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
            'result': { "test": "ok"}
        }

        mock_resp = self._mock_response(status=200, json_data=data)
        mock_post.return_value = mock_resp
        
        result = rpcquery('getminiginfo', '', '', '')
        self.assertEqual(result['result']['test'], 'ok')
    
    @mock.patch('masternode_health.monitor.requests.post')
    def test_rpcquery_failed(self, mock_post):
        mock_resp = self._mock_response(status=500, raise_for_status=HTTPError("rpcerror"))
        mock_post.return_value = mock_resp
        self.assertRaises(HTTPError, rpcquery, 'getmininginfo', '', '', '')

