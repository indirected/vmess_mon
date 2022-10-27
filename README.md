
# Vmess Monitoring

This program is a user manager for v2fly vmess proxy


---

## Install

First you need to clone this repository:

`git clone https://github.com/indirected/vmess_mon $HOME/vmess_mon`

`cd ~/vmess_mon`

Run ```bash install.sh``` you will be asked for a Mongodb connection string and a discord webhook.

This will create two files `dbconstring` and `discord`

Then you need to edit `CONFIG.py` and set `server_ip` variable by replacing your server ip address or a domain name that resolves to your server ip address.

---

## Using the CLI

You can check a full manuall of application and each commands of the application with `-h` flag.

Run `python3 vmessmon.py -h`

```
usage: Vmess Manager [-h] [-U] [-R] {init,newuser,banuser,unbanuser,check,getvmess,stats} ...

optional arguments:
-h, --help            show this help message and exit
-U, --updateDB        Update the MongoDB after all operations
-R, --resetv2         Restart the v2ray Container

Commands:
Use <Command> -h for help

{init,newuser,banuser,unbanuser,check,getvmess,stats}
init                Create or restore server
newuser             Add User
banuser             Ban a User
unbanuser           Unban a User
check               Check for Traffic Overages and Concurrent Connections
getvmess            Print a user's vmess string
stats               Show user stats table

```

Run `python3 vmessmon.py init` to initialize application
Use `-h` at any stage to get help.

---

## Setting Up a Cronjob

For checking the vpn server in intervally you need to set a cronjob in your server

Run `crontab -e`

Place this at the end of the file:

`*/5 * * * * $HOME/vmess_mon/cron.sh >>$HOME/vmess_mon/cron.log 2>>$HOME/vmess_mon/cron.log`

This will set a cronjob that will runs each 5 munutes and checks the vmess logs.
