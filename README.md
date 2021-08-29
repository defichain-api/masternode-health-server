[![Tests](https://github.com/defichain-api/masternode-health-server/actions/workflows/package.yml/badge.svg?branch=master)](https://github.com/defichain-api/masternode-health-server/actions/workflows/package.yml) [![codecov](https://codecov.io/gh/defichain-api/masternode-health-server/branch/master/graph/badge.svg?token=WWRB5IZN7A)](https://codecov.io/gh/defichain-api/masternode-health-server) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.md)




# Masternode Health Server

This script is designed for collecting server & DeFiChain node information of your system and send them to the [DeFiChain Masternode Health API](https://github.com/defichain-api/masternode-health).

For a closed look in it's functionality there's a [detailled documentation](https://docs.defichain-masternode-health.com/).

# Installation

- Install pip3 (pip from python v3. Some operating systems just name it ```pip```)
- Run ```pip3 install masterhode-health```

Make sure you set ```rpcuser=xxx``` and ```rpcpassword=xxx``` in your defi.conf
You can choose the username and password by yourself. 

**Hint:** restart your node after updating your defi.conf
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
usage: masternode-health [-h] [--max-block-seconds MAX_BLOCK_SECONDS] [--rpchost RPCHOST] [--verbose] [--report] [--defi-path DEFI_PATH] [--defi-conf DEFI_CONF] [--api-key API_KEY] [--version]

DefiChain Masternode Monitor

optional arguments:
  -h, --help            show this help message and exit
  --max-block-seconds MAX_BLOCK_SECONDS
                        Alert if node did not try to calculate hash within max-block-seconds (default: 30 seconds)
  --rpchost RPCHOST     RPC host (default: http://localhost:8554)
  --verbose             Prints stats to stdout
  --report              Force sending report when using in combination with --verbose
  --defi-path DEFI_PATH
                        Path to your .defi folder. Default: ~/.defi
  --defi-conf DEFI_CONF
                        Path to your defi.conf. Default: ~/.defi/defi.conf
  --api-key API_KEY     API Key
  --version             Returns masternode-health version
```

You can manually run it with

```
$ masternode-health --verbose --report --api-key=your-api-key

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
- your-api-key: make an educated guess ;)

# Run automatically with a cron job

Add calling Masternode Health into your crontab to check every 10 minutes.

First, open up a text editor to edit your crontab with:

```
crontab -e
```

Add the following line to run it every 10 minutes: (Masternode Health won't accept any higher frequency than every 10 minutes)

```
*/10 * * * * ~/.local/bin/masternode-health --rpcuser rpc-username --rpcpassword rpc-password --defi-path /home/system-user/.defi --api-key=your-api-key
```

**Warning:** The API allows only 1 call to each endpoint every 300 seconds. Don't let the cron run more often than every 5 minutes!

Please don't forget to replace the following parts with your own:
- rpc-username: your RPC username
- rpc-password: your RPC password
- system-user: the local username you're running on your machine
- your-api-key: make an educated guess ;)

# Verbose

To take a look at the collected data, you can use the `--verbose` argument.
With this argument, no data is sent to the API. To force sending the data and viewing the verbose output use the `--report` argument in parallel.

# Bugs or suggestions?
Open issue or submit a pull request to
[https://github.com/defichain-api/masternode-health-server](https://github.com/defichain-api/masternode-health-server)

# Buy me a coffee
@sandrich implemented this tool alone. Want to give him a small thank you? His coffee cash box (in DFI) is:
**df1qvzdgd85m67eym95l0jxrdn6aue5cjthpg78r4z**

# License
MIT
