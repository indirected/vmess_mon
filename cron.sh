#!/usr/bin/bash
# echo "hello"
# PATH= $PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
# pwd
python3 vmessman.py -U -R check

# Usage:
# Put this in crontab -e
# */5 * * * * /root/vmess_mon/cron.sh >>/root/vmess_mon/cron.log 2>>/root/vmess_mon/cron.log