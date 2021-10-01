import requests
import json
import argparse
import psutil
import sys
import multiprocessing
import subprocess
from datetime import datetime, timedelta
from os.path import expanduser, getsize
from hashlib import md5
from .version import __version__


class NodeMonitor:
    def __init__(self, args):
        self.defi_path = args.defi_path
        self.defi_conf = args.defi_conf
        self.verbose = args.verbose
        self.report = args.report
        self.max_block_seconds = args.max_block_seconds
        self.rpchost = args.rpchost
        self.api_key = args.api_key

        conf = self._readConfig()

        if 'rpcuser' not in conf or 'rpcpassword' not in conf:
            raise ValueError('Please define rpcuser and rpcpassword in your defi.conf')

        self.rpcuser = conf['rpcuser']
        self.rpcpassword = conf['rpcpassword']

    def _readConfig(self):
        conf = {}
        with open(self.defi_conf) as f:
            lines = f.read().splitlines()
            ignore = False

            for line in lines:
                var = line.split('=', 1)

                if len(var) == 1 and 'test' in var[0]:
                    ignore = True
                elif len(var) == 1 and 'main' in var[0]:
                    ignore = False

                if var[0] in ['rpcuser', 'rpcpassword', 'rpcport'] and not ignore:
                    conf[var[0]] = var[1]

        return conf

    def _rpcquery(self, method, params=False):
        '''
            Wrapper to run DefiChain RPC commands
        '''
        if not params:
            params = []
        else:
            params = [params]
        headers = {'Content-type': 'application/json'}
        data = {
            'jsonrpc': '1.0',
            'id': 'curltest',
            'method': method,
            'params': params
        }

        try:
            response = requests.post(self.rpchost, auth=(self.rpcuser, self.rpcpassword), headers=headers, data=json.dumps(data), timeout=1000)
            response.raise_for_status()

            data = response.json()

            if 'result' in data:
                return data['result']
            return data
        except requests.exceptions.ConnectionError:
            print("❌ Your defid process seems to be down or RPC server is not reachable!")
            self._uploadToApi('node-info', {"defid_running": False})
            raise SystemExit()

    def _uploadToApi(self, endpoint, data):
        headers = {'x-api-key': self.api_key}
        try:
            r = requests.post(f'https://api.defichain-masternode-health.com/v1/{endpoint}', headers=headers, json=data)
            r.raise_for_status()
            data = r.json()

            if self.verbose and self.report:
                print(f"✅ Sent report to masternode-health api with endpoint {endpoint}")

            if 'result' in data:
                return data['result']

            return data
        except requests.exceptions.HTTPError:
            raise SystemExit(f"❌ Could not send report to masternode-health api with endpoint {endpoint}")

    def _checkAreNodesMining(self):
        '''
            Returns a list of tuples (node_id, True|False) where the boolean defines if a block has successfully been checked within MAX_LASTBLOCK_SECONDS
        '''
        # Get mininginfo
        mininginfo = self._rpcquery('getmininginfo')
        retval = []

        for node in mininginfo['masternodes']:
            lastBlockTime = datetime.strptime(node['lastblockcreationattempt'], '%Y-%m-%dT%H:%M:%SZ')
            now = datetime.utcnow()
            timeDiff = now - lastBlockTime

            if timeDiff.total_seconds() > self.max_block_seconds:
                ret = False
            else:
                ret = True

            retval.append((node['id'], ret))

        return retval

    def _processNodeInfo(self):
        try:
            self.checkNodes = self._checkAreNodesMining()
            self.blockcount = self._rpcquery('getblockcount')
            self.bestblockhash = self._rpcquery('getbestblockhash')
            self.uptime = self._rpcquery('uptime')
            self.connectioncount = self._rpcquery('getconnectioncount')
            self.logSize = getsize(self.defi_path + '/debug.log') / 1024**2
            lines = subprocess.Popen([self.defi_path + '/defid', '--version'], stdout=subprocess.PIPE).communicate()[0]
            self.nodeVersion = lines.splitlines()[0].split(b' ')[-1].decode()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        except OSError:
            raise SystemExit(f"❌ Could not open {self.defi_path}/debug.log")

    def _processServerStats(self):
        self.loadavg = psutil.getloadavg()[1]
        vmem = psutil.virtual_memory()
        self.memUsed = vmem.used / 1024**3
        self.memTotal = vmem.total / 1024**3

        disk = psutil.disk_usage(self.defi_path)
        self.diskUsed = disk.used / 1024**3
        self.diskTotal = disk.total / 1024**3

        self.numCores = multiprocessing.cpu_count()

    def _drawProgressBar(self, percent, barLen=15):
        # percent float from 0 to 1.
        return "[{:<{}}] {:.0f}%".format('▰' * int(barLen * percent), barLen, percent * 100)

    def __repr__(self):
        server_info = [('Node Version:', self.nodeVersion), ('Uptime:', str(timedelta(seconds=self.uptime))), ('Local Block Height:', self.blockcount), ('Local Block Hash:', self.bestblockhash), ('Connection Count:', self.connectioncount)]
        for nodeId, online in self.checkNodes:
            server_info.append((f'Operator ..{nodeId[:3]}:', '✅' if online else '❌'))

        server_stats = [('System Load:', self._drawProgressBar(self.loadavg / (self.numCores * 1.5)), f' ({self.loadavg}/{(self.numCores * 1.5)})'), ('Memory Usage:', self._drawProgressBar(self.memUsed / self.memTotal), f' ({int(self.memUsed)}/{int(self.memTotal)} GB)'), ('Disk Usage:', self._drawProgressBar(self.diskUsed / self.diskTotal), f' ({int(self.diskUsed)}/{int(self.diskTotal)} GB)'), ('Log Size:', int(self.logSize), ' MB')]

        retval = '----- [ server stats ] -----\n'
        for stat in server_stats:
            retval += '{:<15s}{:<10s}\n'.format(stat[0], str(stat[1]) + stat[2])

        retval += '\n----- [ node info ] -----\n'
        for stat in server_info:
            retval += '{:<20s}{:<60s}\n'.format(stat[0], str(stat[1]))

        return retval

    def processNode(self):
        self._processNodeInfo()
        self._processServerStats()

        with open(self.defi_conf, 'rb') as f:
            self.confCheckSum = md5(f.read()).hexdigest()

    def sendReport(self):
        data_node_info = {
            'block_height_local': self.blockcount,
            'local_hash': self.bestblockhash,
            'node_uptime': self.uptime,
            'operator_status': list(map(lambda x: {'id': x[0], 'online': x[1]}, self.checkNodes)),
            'connection_count': self.connectioncount,
            'logsize': self.logSize,
            'config_checksum': self.confCheckSum,
            'node_version': self.nodeVersion
        }

        data_node_stats = {
            'load_avg': self.loadavg,
            'hdd_used': self.diskUsed,
            'hdd_total': self.diskTotal,
            'ram_used': self.memUsed,
            'ram_total': self.memTotal,
            'num_cores': self.numCores,
            'server_script_version': __version__
        }

        try:
            self._uploadToApi('node-info', data_node_info)
            self._uploadToApi('server-stats', data_node_stats)
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)


def parse_args(args):
    home = expanduser("~")
    parser = argparse.ArgumentParser(description='DefiChain Masternode Monitor')
    parser.add_argument('--max-block-seconds', help='Alert if node did not try to calculate hash within max-block-seconds (default: 30 seconds)', default=30, type=int)
    parser.add_argument('--rpchost', help='RPC host (default: http://localhost:8554)', default='http://localhost:8554')
    parser.add_argument('--verbose', action='store_true', help='Prints stats to stdout')
    parser.add_argument('--report', action='store_true', help='Force sending report when using in combination with --verbose')
    parser.add_argument('--defi-path', help='Path to your .defi folder. Default: ~/.defi', default=f"{home}/.defi")
    parser.add_argument('--defi-conf', help='Path to your defi.conf. Default: ~/.defi/defi.conf', default=f"{home}/.defi/defi.conf")
    parser.add_argument('--api-key', help='API Key')
    parser.add_argument('--version', help='Returns masternode-health version', action='store_true')

    args = parser.parse_args(args)

    if args.version:
        raise SystemExit(f'Version: {__version__}')

    if (args.api_key is None and not args.verbose) or (args.api_key is None and args.verbose and args.report):
        raise SystemExit('Please specify an api-key argument')

    return args


def main():
    args = parse_args(sys.argv[1:])

    nodeMonitor = NodeMonitor(args)
    nodeMonitor.processNode()

    if args.verbose:
        print(nodeMonitor)

    if (args.verbose and args.report) or not args.verbose:
        nodeMonitor.sendReport()


if __name__ == '__main__':
    main()
