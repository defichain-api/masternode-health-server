import requests
import json
import argparse
import psutil
from datetime import datetime


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
        "jsonrpc": "1.0",
        "id": "curltest",
        "method": method,
        "params": params
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
        lastBlockTime = datetime.strptime(node['lastblockcreationattempt'], "%Y-%m-%dT%H:%M:%SZ")
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


def main():
    parser = argparse.ArgumentParser(description='DefiChain Masternode Monitor')
    parser.add_argument('--max-block-seconds', help='Alert if node did not try to calculate hash within max-block-seconds (default: 30 seconds)', default=30)
    parser.add_argument('--rpcuser', help='RPC username')
    parser.add_argument('--rpcpassword', help='RPC password')
    parser.add_argument('--rpchost', help='RPC host (default: http://localhost:8554)', default='http://localhost:8554')
    parser.add_argument('--verbose', action='store_true', help='Prints stats to stdout')
    parser.add_argument('--defi-path', help='Path to your .defi folder. Example: /home/defi/.defi')
    parser.add_argument('--api-key', help='API Key')

    args = parser.parse_args()

    if args.rpcuser is None or args.rpcpassword is None:
        exit('Please specify rpcuser and rpcpassword argument')

    if args.defi_path is None:
        exit('Please specify defi-path argument')

    if args.api_key is None:
        exit('Please specify an api-key argument')

    try:
        checkNodes = checkAreNodesMining(args.max_block_seconds, args.rpchost, args.rpcuser, args.rpcpassword)
        blockcount = rpcquery('getblockcount', args.rpchost, args.rpcuser, args.rpcpassword)
        bestblockhash = rpcquery('getbestblockhash', args.rpchost, args.rpcuser, args.rpcpassword)
        uptime = rpcquery('uptime', args.rpchost, args.rpcuser, args.rpcpassword)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    loadavg = psutil.getloadavg()[1]
    vmem = psutil.virtual_memory()
    memUsed = vmem.used / 1024**3
    memTotal = vmem.total / 1024**3

    disk = psutil.disk_usage(args.defi_path)
    diskUsed = disk.used / 1024**3
    diskTotal = disk.total / 1024**3

    if args.verbose:
        print('############ mn server analysis ############')
        print('Load Average: {:.2f}\nMemory Total: {:.0f} GB\nMemory Used: {:.0f} GB\nDisk Total: {:.0f} GB\nDisk Used: {:.0f} GB'.format(loadavg, memTotal, memUsed, diskTotal, diskUsed))
        print('############ mn server analysis ############')
        print('############ mn node info ############')
        print('uptime: {:.0f}\nLocal block height: {:.0f}\nLocal block hash: {:s}'.format(uptime, blockcount, bestblockhash))
        for nodeId, online in checkNodes:
            print('Operator {:s}: {:s}\n'.format(nodeId, "Online" if online else "Offline!"))
        print('############ mn node info ############')

    data = {
        "load_avg": loadavg,
        "hdd_used": diskUsed,
        "hdd_total": diskTotal,
        "ram_used": memUsed,
        "ram_total": memTotal
    }

    data_node_info = {
        "block_height_local": blockcount,
        "local_hash": bestblockhash,
        "node_uptime": uptime
    }

    try:
        reportJson(args.api_key, 'server-stats', data)
        #reportJson(args.api_key, 'node-info', data_node_info)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
