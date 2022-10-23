import argparse
import sys
import subprocess
import utils
import CONFIG


parser = argparse.ArgumentParser(
    prog="Vmess Manager",
    description="",
    add_help=True
)
parser.add_argument(
    "-U", "--updateDB", 
    help="Update the MongoDB after all operations",
    action='store_true'
)
parser.add_argument(
    "-R", "--resetv2", 
    help="Restart the v2ray Container",
    action='store_true'
)

subparser = parser.add_subparsers(title="Commands", description="Use <Command> -h for help", dest='command')

init_parser = subparser.add_parser("init", help="Create or restore server")
init_parser.add_argument(
    "--name",
    help="Server Name. If the server config Exists Online, The Configs Are Restored; Else, Creates New Server",
    required=True
)
init_parser.add_argument(
    "-p", "--port",
    help="Server Port. Defaults to 752 for new servers",
    default=None
)


newu_parser = subparser.add_parser("newuser", help="Add User")
newu_parser.add_argument(
    "--username",
    help="New User's username",
    required=True
)
newu_parser.add_argument(
    "--alterid",
    help="New User's alterID",
    default=0,
    type=int
)
newu_parser.add_argument(
    "--level",
    help="New User's level",
    default=1,
    type=int
)
newu_parser.add_argument(
    "--traffic",
    help="New User's Allowed Traffic",
    default=10,
    type=int
)
newu_parser.add_argument(
    "--concurrent",
    help="New User's Allowed Concurrent Connections",
    default=2,
    type=int
)

ban_parser = subparser.add_parser("banuser", help="Ban a User")
ban_parser.add_argument(
    "--username",
    help="username to Ban",
    required=True
)

unban_parser = subparser.add_parser("unbanuser", help="Unban a User")
unban_parser.add_argument(
    "--username",
    help="username to Unban",
    required=True
)

check_parser = subparser.add_parser("check", help="Check for Traffic Overages and Concurrent Connections")

# init_parser = subparser.add_parser("init", help="Create or restore server")

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)


args = parser.parse_args()

print(args)

if __name__ == "__main__":
    if args.command == 'init':
        utils.init_server(args.name, args.port)
    elif args.command == 'newuser':
        utils.new_user(args.username, args.alterid, args.level, args.concurrent, args.traffic)
    elif args.command == 'banuser':
        utils.remove_user(args.username)
    elif args.command == 'unbanuser':
        utils.unban_user(args.username)
    elif args.command == 'check':
        res = subprocess.run(['docker', 'logs', '--since', f'{CONFIG.run_interval_min}m', CONFIG.container_name], capture_output=True, text=True)
        logs = res.stdout.split('\n')
        utils.check_concurrent(logs)

        res = subprocess.run(['docker', 'exec', CONFIG.container_name, 'v2ray', 'api', 'stats', '-server=127.0.0.1:10085', '-json'], capture_output=True, text=True)
        logs = res.stdout
        stats = utils.parse_usage(logs)
        utils.update_traffics(stats)
        utils.check_overages()

        utils.check_for_unban()
    
    if args.updateDB and args.command != 'init':
        utils.update_mongo()
    
    if args.resetv2:
        subprocess.run(['docker-compose', 'restart'])