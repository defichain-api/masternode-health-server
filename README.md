[![codecov](https://codecov.io/gh/defichain-api/masternode-health-server/branch/master/graph/badge.svg?token=WWRB5IZN7A)](https://codecov.io/gh/defichain-api/masternode-health-server)


# DFI Signal Server Sync
This script is designed to be a DeFiChain master node monitoring solution for DFI Signal Bot.

# Installation

- Install pip3 (pip from python v3. Some operating systems just name it ```pip```)
- Run ```pip3 install masterhode-health```

# Upgrade to the current release

```
pip3 install --upgrade masternode-health
```

# Usage

```
masternode-health --help
usage: masternode-health [-h] [--max-block-seconds MAX_BLOCK_SECONDS] [--rpcuser RPCUSER] [--rpcpassword RPCPASSWORD] [--rpchost RPCHOST] [--verbose] [--defi-path DEFI_PATH]
                         [--api-key API_KEY]

DefiChain Masternode Monitor

optional arguments:
  -h, --help            show this help message and exit
  --max-block-seconds MAX_BLOCK_SECONDS
                        Alert if node did not try to calculate hash within max-block-seconds (default: 30 seconds)
  --rpcuser RPCUSER     RPC username
  --rpcpassword RPCPASSWORD
                        RPC password
  --rpchost RPCHOST     RPC host (default: http://localhost:8554)
  --verbose             Prints stats to stdout
  --defi-path DEFI_PATH
                        Path to your .defi folder. Example: /home/defi/.defi
  --api-key API_KEY     API Key
```

You can manually run it with

```
masternode-health --rpcuser user --rpcpassword password --defi-path /home/user/.defi --verbose --api-key=xxx

############ mn server analysis ############
Load Average: 0.14
Memory Total: 126 GB
Memory Used: 3 GB
Disk Total: 933 GB
Disk Used: 53 GB
############ mn server analysis ############
############ mn node info ############
uptime: 2 days, 21:00:11
Local block height: 1131809
Local block hash: 4737d0f0633275a102142b37feb6ab6bf2ed3ab83ca58962a410ca70d6b089c7
Operator xxx: Online
Operator yyy: Online
############ mn node info ############
```

Add into crontab to check every 5 minutes

```
*/5 * * * * masternode-health --rpcuser user --rpcpassword password --defi-path /home/user/.defi --api-key=xxx
```

# Bugs or suggestions?
Open issue or submit a pull request to
[https://github.com/defichain-api/masternode-health-server](https://github.com/defichain-api/masternode-health-server)

# License
MIT
