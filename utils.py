import re
import pandas as pd
import numpy as np
import json
import datetime
import subprocess
from pymongo import MongoClient
import uuid
import CONFIG


with open(CONFIG.conf_file, 'r') as fp:
    v2ray_conf = json.load(fp)

with open(CONFIG.temp_ban_users_file, 'r') as fp:
    banned_users_dict = json.load(fp)


user_db = pd.read_csv(CONFIG.user_db_file, index_col='username')



def _parse_logs(logs: str):
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


def _update_user_db():
    user_db.to_csv(CONFIG.user_db_file)

def _update_json_config(config: dict, file: str):
    with open(file, 'w') as fp:
        json.dump(config, fp, indent=4)


def _add_user_to_conf(config: dict, userdict: dict):
        config['inbounds'][0]['settings']['clients'].append(userdict)
        _update_json_config(config, CONFIG.conf_file)

def _get_cli_dict_from_config(config:dict, username: str):
    for cli in config['inbounds'][0]['settings']['clients']:
        if cli['email'] == username:
            return cli

def _remove_user_from_conf(config: dict, cli: dict):
    config['inbounds'][0]['settings']['clients'].remove(cli)
    _update_json_config(config, CONFIG.conf_file)



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
        _update_user_db()
        _add_user_to_conf(v2ray_conf, userdict)
        print(f"User <{username}> Added!")


def remove_user(config: dict, username: str):
    cur_users =  [cli['email'] for cli in config['inbounds'][0]['settings']['clients']]
    if username not in cur_users:
        print("User Does Not Exists! No changes Made")
        return
    else:
        cli_dict = _get_cli_dict_from_config(v2ray_conf, username)
        _remove_user_from_conf(config, username)
        user_db.loc[username, ['is_active', 'ban_reason']] = [False, 'manual']
        _update_user_db()
        banned_users_dict[username] = cli_dict
        _update_json_config(banned_users_dict, CONFIG.temp_ban_users_file)
        print(f"User <{username}> Removed!")


def check_concurrent():
    user_ips = _parse_logs(logs)
    print(user_ips)
    for k, v in user_ips.items():
        if user_db.loc[k, 'max_concurrent'] > 0 and len(v) > user_db.loc[k, 'max_concurrent']:
            print(f"User <{k}> is koskesh")

            # Enter Banning procedure
            if user_db.loc[k, 'is_active'] == True:
                cli_dict = _get_cli_dict_from_config(v2ray_conf, k)
                _remove_user_from_conf(v2ray_conf, cli_dict)

                banned_users_dict[k] = cli_dict
                _update_json_config(banned_users_dict, CONFIG.temp_ban_users_file)

                user_db.loc[k, 'ban_count'] += 1
                user_db.loc[k, ['is_active', 'last_banned', 'ban_reason']] = [
                    False,
                    datetime.datetime.now(),
                    f'concurrent ({len(v)})'
                ]
                _update_user_db()


def unban_user(username: str):
    if username not in banned_users_dict:
        print("User is not Banned")
        return

    cli_dict = banned_users_dict[username]
    banned_users_dict.pop(username)
    _update_json_config(banned_users_dict, CONFIG.temp_ban_users_file)

    _add_user_to_conf(v2ray_conf, cli_dict)

    user_db.loc[username, 'is_active'] = True
    _update_user_db()


def check_for_unban():
    for banned_user in list(banned_users_dict.keys()):
        if user_db.loc[banned_user, 'ban_count'] <= CONFIG.max_bans:
            if datetime.datetime.strptime(user_db.loc[banned_user, 'last_banned'], '%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(minutes=CONFIG.ban_time_mins) < datetime.datetime.now():
                if 'concurrent' in user_db.loc[banned_user, 'ban_reason']:
                    unban_user(banned_user)
                    print(f"User <{banned_user}> Unbanned by time")


def _user_db_tomongo():
    userdb_dict = {'server_name': v2ray_conf['server_name']}
    userdb_dict['data'] = user_db.to_dict()
    return userdb_dict


def update_mongo():
    with open(CONFIG.db_constring_file, 'r') as fp:
        constr = fp.readline()
    client = MongoClient(constr)
    
    server_name = v2ray_conf['server_name']
    server_names = client.vmess.v2ray_config.find({}, {'server_name': 1})
    server_names = [i['server_name'] for i in server_names]

    if server_name not in server_names:
        print(f"Server <{server_name}> Does not Exist in Mongo! Init first")
        return -1
    else:
        client.vmess.v2ray_config.replace_one({'server_name': server_name}, v2ray_conf)
        client.vmess.user_dbs.replace_one({'server_name': server_name}, _user_db_tomongo())
        client.vmess.banned.replace_one({'server_name': server_name}, {
            'server_name': server_name,
            'banned_dict': banned_users_dict
        })
        print("MongoDB Updated!")
    client.close()
    return 0


def init_server(server_name, new_port: int=None):
    with open(CONFIG.db_constring_file, 'r') as fp:
        constr = fp.readline()
    client = MongoClient(constr)

    server_names = client.vmess.v2ray_config.find({}, {'server_name': 1})
    server_names = [i['server_name'] for i in server_names]
    global v2ray_conf
    if server_name in server_names:
        # Exists - Download stuff
        new_conf = client.vmess.v2ray_config.find_one({"server_name": server_name}, projection={'_id': 0})
        # global v2ray_conf
        v2ray_conf = new_conf
        v2ray_conf['inbounds'][0]["port"] = int(new_port)
        _update_json_config(v2ray_conf, CONFIG.conf_file)

        new_userdb = client.vmess.user_dbs.find_one({"server_name": server_name})
        global user_db
        user_db = pd.DataFrame(new_userdb['data'])
        _update_user_db()

        new_banned = client.vmess.banned.find_one({"server_name": server_name})
        global banned_users_dict
        banned_users_dict = new_banned['banned_dict']
        _update_json_config(banned_users_dict, CONFIG.temp_ban_users_file)
        print(f"Server <{server_name}> Recovered!")
        
    else:
        # Does Not Exist - Create New
        new_conf = client.vmess.v2ray_config.find_one({"server_name": "init"}, projection={'_id': 0})
        new_conf['server_name'] = server_name
        admin_cli = new_conf['inbounds'][0]['settings']['clients'][0]
        admin_uname = admin_cli['email']
        admin_uuid = str(uuid.uuid4())
        admin_cli['id'] = admin_uuid
        
        user_db.loc[admin_uname] = [True, 0, "", 0.0, -1.0, -1.0, ""]

        # global v2ray_conf
        v2ray_conf = new_conf
        v2ray_conf['inbounds'][0]["port"] = int(new_port)
        _update_json_config(v2ray_conf, CONFIG.conf_file)
        _update_user_db()

        client.vmess.v2ray_config.insert_one(v2ray_conf)
        client.vmess.user_dbs.insert_one(_user_db_tomongo())
        client.vmess.banned.insert_one({
            'server_name': v2ray_conf['server_name'],
            'banned_dict': banned_users_dict
        })
        print(f"Server <{server_name}> Created!")
    client.close()
    return 0




if __name__ == '__main__':
    res = subprocess.run(['docker', 'logs', '--since', f'{CONFIG.run_interval_min}m', CONFIG.container_name], capture_output=True, text=True)
    logs = res.stdout.split('\n')
    check_for_unban()
    check_concurrent()