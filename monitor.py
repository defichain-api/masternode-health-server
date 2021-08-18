import requests
import json
import argparse
from datetime import datetime

def rpcquery(method, rpchost, rpcuser, rpcpassword, params = False):
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

    try:
        response = requests.post(rpchost, auth=(rpcuser, rpcpassword), headers = headers, data=json.dumps(data), timeout=1000)
        return response.json()['result']
    except requests.exceptions.RequestException as e:
        print("Request error: ", e)

    return False

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

def main():
    parser = argparse.ArgumentParser(description='DefiChain Masternode Monitor')
    parser.add_argument('--max-block-seconds', help='Alert if node did not try to calculate hash within max-block-seconds (default: 30 seconds)', default=30)
    parser.add_argument('--rpcuser', help='RPC username')
    parser.add_argument('--rpcpassword', help='RPC password')
    parser.add_argument('--rpchost', help='RPC host (default: http://localhost:8554)', default='http://localhost:8554')

    args = parser.parse_args()

    if args.rpcuser == None or args.rpcpassword == None:
        exit('Please specify rpcuser and rpcpassword argument')
    
    checkNodes = checkAreNodesMining(args.max_block_seconds, args.rpchost, args.rpcuser, args.rpcpassword)
    print(checkNodes)
    


if __name__ == "__main__":
    main()