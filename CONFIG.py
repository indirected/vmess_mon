import os

# Things you NEED to change
server_ip = 'put_server_ip_here'
container_name = 'vmon_v2ray'


logfile = 'logs.txt'
conf_file = 'config.json'
user_db_file = 'users.csv'
db_constring_file = 'dbconstring'
user_db_cols = ['username', 'is_active', 'ban_count', 'last_banned', 'traffic_used', 'max_traffic', 'max_concurrent', 'ban_reason']


max_bans = 3
ban_time_mins = 15
temp_ban_users_file = 'banned.json'

run_interval_min = 5


if not os.path.exists(conf_file):
    with open(conf_file, 'w') as fp:
        fp.write("{}")

if not os.path.exists(user_db_file):
    with open(user_db_file, 'w') as fp:
        fp.write(','.join(user_db_cols))

if not os.path.exists(temp_ban_users_file):
    with open(temp_ban_users_file, 'w') as fp:
        fp.write("{}")



vmess_template = {
    'add': server_ip,
    'aid': '0',
    'host': '',
    'id': 'uuid_here',
    'net': 'ws',
    'path': '/api',
    'port': 'port_here',
    'ps': 'server_name_here',
    'scy': 'auto',
    'sni': '',
    'tls': 'none',
    'type': '',
    'v': '2'
}