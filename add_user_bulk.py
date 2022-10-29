import pandas as pd
import subprocess

users_file = pd.read_csv('./users-bulk.csv', index_col=0)

error_file = pd.DataFrame([], columns=users_file.columns)

for user,row in users_file.iterrows():
    # error_file.loc[user] = row
    cmd_result = subprocess.run(
        [
        'python3',
        'vmessmon.py',
        'newuser',
        '--username',
        str(user),
        '--alterid',
        str(row['alterid']),
        '--level',
        str(row['level']),
        '--traffic',
        str(row['max_traffic']),
        '--concurrent',
        str(row['max_concurrent'])
        ],
        capture_output=True,
        text=True
    )

    splitted_output = cmd_result.stdout.splitlines()

    if len(splitted_output) == 3:
        vmess = splitted_output[2]
        users_file.loc[user, 'vmess'] = vmess
        print(f'user {user} created successflly')
    else:
        print(f'error occured when creating user {user}')  
        error_file.loc[user] = row
        error_file.loc[user, 'error_message'] = cmd_result.stdout


# update the mongodb 
update_cmd_result = subprocess.run(
    [
        'python3',
        'vmessmon.py',
        '-U',
        '-R'
    ]
)

# todo: check if update cmd failed or not

# write results in disk 
users_file.to_csv('./create-users-bulk-result.csv')
error_file.to_csv('./create-users-bulk-error.csv')

print("DONE")