import os

logfile = 'logs.txt'
conf_file = 'config.json'
user_db_file = 'users.csv'
user_db_cols = ['username', 'is_active', 'ban_count', 'last_banned', 'traffic_used', 'max_traffic', 'max_concurrent', 'ban_reason']


max_bans = 3
ban_time_mins = 15
temp_ban_users_file = 'banned.json'

run_interval_min = 5

container_name = 'vmess_v2ray_1'

if not os.path.exists(user_db_file):
    with open(user_db_file, 'w') as fp:
        fp.write(','.join(user_db_cols))

if not os.path.exists(temp_ban_users_file):
    with open(temp_ban_users_file, 'w') as fp:
        fp.write("{}")