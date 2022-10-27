
# Vmess Monitoring

This program is a user manager for v2fly vmess proxy



## install instructure

First you need to clone this repository:

`git clone https://github.com/indirected/vmess_mon $HOME/vmess_mon`

`cd vmess_mon`

Run ```bash install.sh``` you will be asked for a Mongodb connection string and a discord webhook.

This will create two files `dbconstring` and `discord`

Then you need to edit `CONFIG.py` and set `server_ip` variable by replacing your server ip address or a domain name that resolves your server ip address with `put_server_ip_here`

Now you are all setup.

Run `python3 vmessmon.py init` to initialize application
## Setting up a cronjob

For checking the vpn server in intervally you need to set a cronjob in your server

Run `crontab -e`

Place this at the end of the file:

`*/5 * * * * $HOME/vmess_mon/cron.sh >>$HOME/vmess_mon/cron.log 2>>$HOME/vmess_mon/cron.log`

This will set a cronjob that will runs each 5 munutes and checks the vmess logs.


## Using the CLI

You can check a full manuall of application and each commands of the application with `-h` flag.

Run `python3 vmessmon.py -h`