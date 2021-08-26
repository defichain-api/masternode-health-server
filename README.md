[![Tests](https://github.com/defichain-api/masternode-health-server/actions/workflows/package.yml/badge.svg?branch=master)](https://github.com/defichain-api/masternode-health-server/actions/workflows/package.yml) [![codecov](https://codecov.io/gh/defichain-api/masternode-health-server/branch/master/graph/badge.svg?token=WWRB5IZN7A)](https://codecov.io/gh/defichain-api/masternode-health-server) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)




# Masternode Health Server

This script is designed for collecting server & DeFiChain node information of your system and send them to the [DeFiChain Masternode Health API](https://github.com/defichain-api/masternode-health).

For a closed look in it's functionality there's a [detailled documentation](https://docs.defichain-masternode-health.com/).

# Installation

- Install pip3 (pip from python v3. Some operating systems just name it ```pip```)
- Run ```pip3 install masterhode-health```

# Upgrade to the current release

```
pip3 install --upgrade masternode-health
```

# Create API key

This scripts needs a DeFiChain Masternode Health API key. Take a look at the [documentation](https://docs.defichain-masternode-health.com/#get-an-api-key).

## tl;dr:

Open up a new tab in your browser, paste in that URL

```
https://api.defichain-masternode-health.com/setup/api_key
```

You'll get something like this:

```
{"message":"API key generated","api_key":"537e13a8-d027-45db-8f51-92b5219b203f"}
```

The part after ```"api_key":"``` (```537e13a8-d027-45db-8f51-92b5219b203f```) is your API key. Copy it (without ```"}```), store it in a safe place like your password manager and close that browser tab because you don't need it anymore.

# Usage

## Prerequisites
You can either run masternode-health by calling it with it's relative path in your user's directory:

```
~/.local/bin/masternode-health --help
```

OR you can create a symlink for making the ```masternode-health``` command accessible from anywhere on your system. The following command requires sudo rights.

```
sudo ln -sf ~/.local/bin/masternode-health /usr/local/bin/masternode-health
```


## Running Masternode Health

To keep it simple, the following examples do not contain the relative path like described above.

```
$ masternode-health --help
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
$ masternode-health --rpcuser rpc-username --rpcpassword rpc-password --defi-path /home/system-user/.defi --verbose --api-key=your-api-key

----- [ server stats ] -----
Load Average:     0.13   
Memory Total:      125 GB
Memory Used:         3 GB
Disk Total:        933 GB
Disk Used:          53 GB

----- [ node info ] -----
Uptime:             4 days, 1:54:14                                             
Local Block Height: 1135336                                                     
Local Block Hash:   844b3007709ced3828d5ec49174523b118b7ce7ebd75d2aafb0a27d8fc50d17e
Operator ..xzy:     Online                                                      
Operator ..oyx:     Online
```

Please don't forget to replace the following parts with your own:
- rpc-username: your RPC username
- rpc-password: your RPC password
- system-user: the local username you're running on your machine
- your-api-key: make an educated guess ;)

# Run automatically with a cron job

Add calling Masternode Health into your crontab to check every  minutes.

First, open up a text editor to edit your crontab with:

```
crontab -e
```

Add the following line to run it every 10 minutes: (Masternode Health won't accept any higher frequency than every 10 minutes)

```
*/10 * * * * ~/.local/bin/masternode-health --rpcuser rpc-username --rpcpassword rpc-password --defi-path /home/system-user/.defi --api-key=your-api-key
```

Please don't forget to replace the following parts with your own:
- rpc-username: your RPC username
- rpc-password: your RPC password
- system-user: the local username you're running on your machine
- your-api-key: make an educated guess ;)

# Bugs or suggestions?
Open issue or submit a pull request to
[https://github.com/defichain-api/masternode-health-server](https://github.com/defichain-api/masternode-health-server)

# License
MIT
