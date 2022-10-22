import re
import pandas as pd
import numpy as np
import json
import datetime
import subprocess
import CONFIG

# with open(CONFIG.logfile, 'r') as fp:
#     logs=fp.readlines()

with open(CONFIG.conf_file, 'r') as fp:
    v2ray_conf = json.load(fp)

with open(CONFIG.temp_ban_users_file, 'r') as fp:
    banned_users_dict = json.load(fp)


user_db = pd.read_csv(CONFIG.user_db_file, index_col='username')


def parse_logs(logs: str):
    logs_array = [i.split() for i in logs]
    users = [cli['email'] for cli in v2ray_conf['inbounds'][0]['settings']['clients']]

    user_ips = {u: [] for u in users}
    for line_array in logs_array:
        if len(line_array) >= 8:
            ip = re.search("^([0-9]+\.){3}([0-9]+)", line_array[2])
            if ip is not None and line_array[3] == "accepted":
                # print((line_array[-1], ip.group()))
                # break
                user_ips[line_array[-1]].append(ip.group())

    for k, v in user_ips.items():
        user_ips[k] = np.unique(v).tolist()
    
    return user_ips


def update_user_db():
    user_db.to_csv(CONFIG.user_db_file)

def update_json_config(config: dict, file: str):
    with open(file, 'w') as fp:
        json.dump(config, fp, indent=4)


def add_user_to_conf(config: dict, userdict: dict):
        config['inbounds'][0]['settings']['clients'].append(userdict)
        update_json_config(config, CONFIG.conf_file)

def get_cli_dict_from_config(config:dict, username: str):
    for cli in config['inbounds'][0]['settings']['clients']:
        if cli['email'] == username:
            return cli

def remove_user_from_conf(config: dict, cli: dict):
    config['inbounds'][0]['settings']['clients'].remove(cli)
    update_json_config(config, CONFIG.conf_file)



def new_user(username: str, uuid: str, alterid: int, level: int, max_concurrent: int, max_traffic: int):
    cur_users =  [cli['email'] for cli in v2ray_conf['inbounds'][0]['settings']['clients']]
    if username in cur_users:
        print("User Already Exists! No changes Made")
        return
    else:
        userdict = {
            "id": uuid,
            "level": level,
            "alterId": alterid,
            "email": username
        }
        user_db.loc[username] = [True, 0, "", 0, max_traffic, max_concurrent, ""]
        update_user_db()
        add_user_to_conf(v2ray_conf, userdict)
        print(f"User <{username}> Added!")


def remove_user(config: dict, username: str):
    cur_users =  [cli['email'] for cli in config['inbounds'][0]['settings']['clients']]
    if username not in cur_users:
        print("User Does Not Exists! No changes Made")
        return
    else:
        remove_user_from_conf(config, username)
        user_db.loc[username, ['is_active', 'ban_reason']] = [False, 'manual']
        update_user_db()
        print(f"User <{username}> Removed!")


def check_concurrent():
    user_ips = parse_logs(logs)
    print(user_ips)
    for k, v in user_ips.items():
        if user_db.loc[k, 'max_concurrent'] > 0 and len(v) > user_db.loc[k, 'max_concurrent']:
            print(f"User <{k}> is koskesh")

            # Enter Banning procedure
            if user_db.loc[k, 'ban_count'] < CONFIG.max_bans and user_db.loc[k, 'is_active'] == True:
                cli_dict = get_cli_dict_from_config(v2ray_conf, k)
                remove_user_from_conf(v2ray_conf, cli_dict)

                banned_users_dict[k] = cli_dict
                update_json_config(banned_users_dict, CONFIG.temp_ban_users_file)

                user_db.loc[k, 'ban_count'] += 1
                user_db.loc[k, ['is_active', 'last_banned', 'ban_reason']] = [
                    False,
                    datetime.datetime.now(),
                    f'concurrent ({len(v)})'
                ]
                update_user_db()


def unban_user(username: str):
    if username not in banned_users_dict:
        print("User is not Banned")
        return

    cli_dict = banned_users_dict[username]
    banned_users_dict.pop(username)
    update_json_config(banned_users_dict, CONFIG.temp_ban_users_file)

    add_user_to_conf(v2ray_conf, cli_dict)

    user_db.loc[username, 'is_active'] = True
    update_user_db()


def check_for_unban():
    for banned_user in list(banned_users_dict.keys()):
        if user_db.loc[banned_user, 'ban_count'] <= CONFIG.max_bans:
            if datetime.datetime.strptime(user_db.loc[banned_user, 'last_banned'], '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(minutes=CONFIG.ban_time_mins) < datetime.datetime.now():
                if 'concurrent' in user_db.loc[banned_user, 'ban_reason']:
                    unban_user(banned_user)
                    print(f"User <{banned_user}> Unbanned by time")



if __name__ == '__main__':
    res = subprocess.run(['docker', 'logs', '--since', f'{CONFIG.run_interval_min}m', CONFIG.container_name], capture_output=True, text=True)
    logs = res.stdout.split('\n')
    check_for_unban()
    check_concurrent()