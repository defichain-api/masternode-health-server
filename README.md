# DFI Signal Server Sync
This script is designed to be a DeFiChain master node monitoring solution for DFI Signal Bot.

# Installation

- copy this repo on your server - e.g. with `git clone git@github.com:adrian-schnell/dfi_signal_server.git dfi_signal_server`
- Ensure curl and jq are installed in `/usr/bin/`
- Run the script from the home directory that contains the `.defi` folder (same user than running the masternode)
- get your API KEY and Server ID from the [DFI Signal Bot](https://t.me/DFI_Signal_bot) and copy them to the script

To run this script, I recommend a cronjob.

To add it to your crontab, use 

```
crontab -l | { cat; echo "*/30 * * * * ~/dfi_signal_server/dfi_signal_sync.sh"; } | crontab -
```

Important:
The API only accepts requests every 15min!

# Bugs or suggestions?
Open issue or submit a pull request to
[https://github.com/adrian-schnell/dfi_signal_server](https://github.com/adrian-schnell/dfi_signal_server)
