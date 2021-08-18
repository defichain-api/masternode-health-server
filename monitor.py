import requests
import json
import argparse
from datetime import datetime

MAX_LASTBLOCK_SECONDS = 30

def rpcquery(method, params = False):
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
        response = requests.post('http://localhost:8554', auth=('user', 'password'), headers = headers, data=json.dumps(data), timeout=1000)
        return response.json()['result']
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("Request error: ", e)

    return False

def checkAreNodesMining():
    '''
        Returns a list of tuples (node_id, True|False) where the boolean defines if a block has successfully been checked within MAX_LASTBLOCK_SECONDS
    '''
    # Get mininginfo
    mininginfo = rpcquery('getmininginfo')
    retval = []

    for node in mininginfo['masternodes']:
        lastBlockTime = datetime.strptime(node['lastblockcreationattempt'], "%Y-%m-%dT%H:%M:%SZ")
        now = datetime.utcnow()
        timeDiff = now - lastBlockTime
        
        if timeDiff.total_seconds() > MAX_LASTBLOCK_SECONDS:
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

    checkNodes = checkAreNodesMining()
    print(checkNodes)
    


if __name__ == "__main__":
    main()