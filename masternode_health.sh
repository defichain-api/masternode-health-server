#!/usr/bin/env bash

# README
# ------
#
# This script is designed to be a passive DeFiChain master node monitoring solution.
# It will examine the state of your server and alert the DefiChain Masternode Health API.
# More details and specifics can be found in the README.md of the GIT
# repo linked below.
#
# Bugs or suggestions? Open issue or submit a pull request to
# https://github.com/defichain-api/masternode-health-server
#
#
# CONFIG
# ------
#
# To run this script, you need to setup your user and server keys.
# more information how to setup: https://docs.defichain-masternode-health.com/
#
SERVER_ID="00000000-0000-0000-0000-000000000000"
USER_API_KEY="00000000-0000-0000-0000-000000000000"

DEBUG_LOG_PATH=".defi/debug.log"

######################################################################
# DO NOT CHANGE ANYTHING UNDERNEATH!
######################################################################
check_package_installed() {
    if [ $(dpkg-query -W -f='${Status}' $1 2>/dev/null | grep -c "ok installed") -eq 0 ];
    then
      echo you need to install $1 first to use this script.
      exit 0;
    else
        echo $1 is installed
    fi
}
check_package_installed curl
check_package_installed jq


REPORT_SEND=false
VERBOSE=true

while [ "$#" -gt 0 ]; do
    case $1 in
        -r|--report) REPORT_SEND=true ;;
        -v|--verbose) VERBOSE=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

API_VERSION="1"
API_DOMAIN="https://api.defichain-masternode-health.com"

######################################################################
# Call DFI Signal API
######################################################################
report_json () {
    curl -X POST --silent \
        -H "X-SERVER-ID: $SERVER_ID" \
        -H "X-API-KEY: $USER_API_KEY" \
        -d "$2" \
        "$API_DOMAIN/v$API_VERSION/$1" > /dev/null
}

###########################################
# Check for local chain split in debug.log
###########################################
LOCAL_SPLIT_FOUND_IN_DEBUG_LOG=false
if [ -f ${DEBUG_LOG_PATH} ]; then
  if [ $(tail -n 20 ${DEBUG_LOG_PATH} | grep -m 1 "proof of stake failed") ]; then
    LOCAL_SPLIT_FOUND_IN_DEBUG_LOG=true
  fi
fi

###########################################
# report values to DFI Signal Server
###########################################
# CPU
CPU_LOAD=`LANG=C LC_ALL=C uptime | grep "load average" | awk '{print $(NF-2) $(NF-1) $NF}'`

# RAM
FREE_DATA=`free -m | grep Mem`
RAM_USED=`echo $FREE_DATA | cut -f3 -d' '`
RAM_TOTAL=`echo $FREE_DATA | cut -f2 -d' '`

# HDD
HDD_TOTAL=`df -lh | awk '{if ($6 == "/") { print $2 }}'`
HDD_USED=`df -lh | awk '{if ($6 == "/") { print $3 }}'`
if [ "$VERBOSE" = true ] ; then
    echo "############ mn server analysis ############"
    echo CPU_LOAD: $CPU_LOAD
    echo RAM Used: "$RAM_USED"
    echo RAM Total: "$RAM_TOTAL"
    echo HDD Used: "$HDD_USED"
    echo HDD Total: "$HDD_TOTAL"
    echo "############ mn server analysis ############"
fi
if [ "$REPORT_SEND" = true ] ; then
    report_json "server-stats" "{\"cpu\": \"$CPU_LOAD\",
    \"hdd_used\": \"$HDD_USED\",
    \"hdd_total\": \"$HDD_TOTAL\",
    \"ram_used\": \"$RAM_USED\",
    \"ram_total\": \"$RAM_TOTAL\"}"
fi

# local data
DEFI_CONNECTIONCOUNT=`$(.defi/defi-cli getconnectioncount)`
NODE_UPTIME=`$(.defi/defi-cli uptime)`
BLOCK_HEIGHT=`$(.defi/defi-cli getblockcount)`
LOCAL_HASH=`$(.defi/defi-cli getblockhash $BLOCK_HEIGHT)`
if [ -f ${DEBUG_LOG_PATH} ]; then
    LOG_SIZE=$(stat -c %s ${DEBUG_LOG_PATH})
else
    LOG_SIZE="n/a"
fi

# main net data
MAIN_NET_BLOCK_HEIGHT=$(/usr/bin/curl -s https://api.defichain.io/v1/getblockcount | /usr/bin/jq -r '.data')
MAIN_NET_BLOCK_HASH=$(/usr/bin/curl -s https://mainnet-api.defichain.io/api/DFI/mainnet/block/${MAIN_NET_BLOCK_HEIGHT} | /usr/bin/jq -r '.hash')
BLOCK_DIFF=$(MAIN_NET_BLOCK_HEIGHT-BLOCK_HEIGHT)

if [ "$VERBOSE" = true ] ; then
    echo "############ blockchain analysis ############"
    echo current connections count: $DEFI_CONNECTIONCOUNT
    echo block diff: "$BLOCK_DIFF"
    echo node uptime: "$NODE_UPTIME"
    echo local block height: "$BLOCK_HEIGHT"
    echo main net block height: "$MAIN_NET_BLOCK_HEIGHT"
    echo local hash: "$LOCAL_HASH"
    echo main net block hash: "$MAIN_NET_BLOCK_HASH"
    echo log size: "$LOG_SIZE"
    echo "############ blockchain analysis ############"
fi
if [ "$REPORT_SEND" = true ] ; then
    report_json "block-info" "{\"connectioncount\": \"$DEFI_CONNECTIONCOUNT\",
    \"node_uptime\": \"$NODE_UPTIME\",
    \"block_diff\": \"$BLOCK_DIFF\",
    \"block_height_local\": \"$BLOCK_HEIGHT\",
    \"main_net_block_height\": \"$MAIN_NET_BLOCK_HEIGHT\",
    \"local_hash\": \"$LOCAL_HASH\",
    \"main_net_block_hash\": \"$MAIN_NET_BLOCK_HASH\",
    \"local_split_found\": $LOCAL_SPLIT_FOUND_IN_DEBUG_LOG,
    \"logsize\": \"$LOG_SIZE\"}"
fi

exit 0
