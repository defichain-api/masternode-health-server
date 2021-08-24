[![codecov](https://codecov.io/gh/defichain-api/masternode-health-server/branch/master/graph/badge.svg?token=WWRB5IZN7A)](https://codecov.io/gh/defichain-api/masternode-health-server)


# DFI Signal Server Sync
This script is designed to be a DeFiChain master node monitoring solution for DFI Signal Bot.

# Installation

- copy this repo on your server - e.g. with `git clone https://github.com/defichain-api/masternode-health-server.git defichain_masternode_health defichain_masternode_health`
- Ensure curl and jq are installed in `/usr/bin/`
- Run the script from the home directory that contains the `.defi` folder (same user than running the masternode)
- get your API KEY and Server ID from the API - take a look at the [documentation](https://docs.defichain-masternode-health.com/) and copy them to the script

To run this script, I recommend a cronjob.

To add it to your crontab, use 

```
crontab -l | { cat; echo "*/15 * * * * ~/defichain_masternode_health/masternode_health.sh"; } | crontab -
```

Important:
The API only accepts requests every 15min!

# Upgrade to the current release

```
cd defichain_masternode_health
git pull
```

# Bugs or suggestions?
Open issue or submit a pull request to
[https://github.com/defichain-api/masternode-health-server](https://github.com/defichain-api/masternode-health-server)

# License
MIT
