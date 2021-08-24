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
    return response.json()


def checkAreNodesMining(max_lastblock_seconds, rpchost, rpcuser, rpcpassword):
    '''
        Returns a list of tuples (node_id, True|False) where the boolean defines if a block has successfully been checked within MAX_LASTBLOCK_SECONDS
    '''
    # Get mininginfo
    mininginfo = rpcquery('getmininginfo', rpchost, rpcuser, rpcpassword)
    retval = []

    for node in mininginfo['masternodes']['result']:
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
    headers = {'X-API-KEY': key}
    r = requests.post(f'https://api.defichain-masternode-health.com/v1/{endpoint}', headers=headers, json=data)
    r.raise_for_status()

    print(r.json())

    print(r.request.body)
    print(r.request.headers)
    print(r.request.url)
    print(r.response.body)

    if r.status_code != requests.codes.ok:
        print(f"Request error with return code {r.status_code}")


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

    checkNodes = checkAreNodesMining(args.max_block_seconds, args.rpchost, args.rpcuser, args.rpcpassword)
    print(checkNodes)

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

    data = {
        "cpu": loadavg,
        "hdd_used": diskUsed,
        "hdd_total": diskTotal,
        "ram_used": memUsed,
        "ram_total": memTotal
    }

    reportJson(args.api_key, 'server-stats', data)
