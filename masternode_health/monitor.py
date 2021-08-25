import requests
import json
import argparse
import psutil
import sys
from datetime import datetime, timedelta


def rpcquery(method, rpchost, rpcuser, rpcpassword, params=False):
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

    response = requests.post(rpchost, auth=(rpcuser, rpcpassword), headers=headers, data=json.dumps(data), timeout=1000)
    response.raise_for_status()

    data = response.json()

    if 'result' in data:
        return data['result']
    return data


def checkAreNodesMining(max_lastblock_seconds, rpchost, rpcuser, rpcpassword):
    '''
        Returns a list of tuples (node_id, True|False) where the boolean defines if a block has successfully been checked within MAX_LASTBLOCK_SECONDS
    '''
    # Get mininginfo
    mininginfo = rpcquery('getmininginfo', rpchost, rpcuser, rpcpassword)
    retval = []

    for node in mininginfo['masternodes']:
        lastBlockTime = datetime.strptime(node['lastblockcreationattempt'], '%Y-%m-%dT%H:%M:%SZ')
        now = datetime.utcnow()
        timeDiff = now - lastBlockTime

        if timeDiff.total_seconds() > max_lastblock_seconds:
            ret = False
        else:
            ret = True

        retval.append((node['id'], ret))

    return retval


def reportJson(key, endpoint, data):
    headers = {'x-api-key': key}
    r = requests.post(f'https://api.defichain-masternode-health.com/v1/{endpoint}', headers=headers, json=data)
    r.raise_for_status()

    data = r.json()
    if 'result' in data:
        return data['result']

    return data


def processNodeInfo(args):
    try:
        checkNodes = checkAreNodesMining(args.max_block_seconds, args.rpchost, args.rpcuser, args.rpcpassword)
        blockcount = rpcquery('getblockcount', args.rpchost, args.rpcuser, args.rpcpassword)
        bestblockhash = rpcquery('getbestblockhash', args.rpchost, args.rpcuser, args.rpcpassword)
        uptime = rpcquery('uptime', args.rpchost, args.rpcuser, args.rpcpassword)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    server_info = [('Uptime:', str(timedelta(seconds=uptime))), ('Local Block Height:', blockcount), ('Local Block Hash:', bestblockhash)]
    for nodeId, online in checkNodes:
        server_info.append((f'Operator ..{nodeId[:3]}:', 'Online' if online else 'Offline!'))

    data_node_info = {
        'block_height_local': blockcount,
        'local_hash': bestblockhash,
        'node_uptime': uptime,
        'operator_status': list(map(lambda x: {'id': x[0], 'online': x[1]}, checkNodes))
    }

    try:
        reportJson(args.api_key, 'node-info', data_node_info)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return server_info


def processServerStats(args):
    loadavg = psutil.getloadavg()[1]
    vmem = psutil.virtual_memory()
    memUsed = vmem.used / 1024**3
    memTotal = vmem.total / 1024**3

    disk = psutil.disk_usage(args.defi_path)
    diskUsed = disk.used / 1024**3
    diskTotal = disk.total / 1024**3

    server_stats = [('Load Average:', loadavg, '   '), ('Memory Total:', int(memTotal), ' GB'), ('Memory Used:', int(memUsed), ' GB'), ('Disk Total:', int(diskTotal), ' GB'), ('Disk Used:', int(diskUsed), ' GB')]
    data = {
        'load_avg': loadavg,
        'hdd_used': diskUsed,
        'hdd_total': diskTotal,
        'ram_used': memUsed,
        'ram_total': memTotal
    }

    try:
        reportJson(args.api_key, 'server-stats', data)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    return server_stats


def parse_args(args):
    parser = argparse.ArgumentParser(description='DefiChain Masternode Monitor')
    parser.add_argument('--max-block-seconds', help='Alert if node did not try to calculate hash within max-block-seconds (default: 30 seconds)', default=30, type=int)
    parser.add_argument('--rpcuser', help='RPC username')
    parser.add_argument('--rpcpassword', help='RPC password')
    parser.add_argument('--rpchost', help='RPC host (default: http://localhost:8554)', default='http://localhost:8554')
    parser.add_argument('--verbose', action='store_true', help='Prints stats to stdout')
    parser.add_argument('--defi-path', help='Path to your .defi folder. Example: /home/defi/.defi')
    parser.add_argument('--api-key', help='API Key')

    args = parser.parse_args(args)

    if args.rpcuser is None or args.rpcpassword is None:
        raise SystemExit('Please specify rpcuser and rpcpassword argument', )

    if args.defi_path is None:
        raise SystemExit('Please specify defi-path argument')

    if args.api_key is None:
        raise SystemExit('Please specify an api-key argument')

    return args


def main():
    args = parse_args(sys.argv[1:])

    server_stats = processServerStats(args)
    server_info = processNodeInfo(args)

    if args.verbose:
        print('----- [ server stats ] -----')
        for stat in server_stats:
            print('{:<15s}{:>10s}'.format(stat[0], str(stat[1]) + stat[2]))

        print('\n----- [ node info ] -----')
        for stat in server_info:
            print('{:<20s}{:<60s}'.format(stat[0], str(stat[1])))
