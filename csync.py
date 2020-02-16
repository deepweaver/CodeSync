#!python 
import os, sys 
import argparse 
from time import sleep
import getpass
import json 

cwd = os.getcwd()
head, tail = os.path.split(cwd)
if sys.version_info[0] < 3: input = raw_input 



def parse_args():
    parser = argparse.ArgumentParser(description="This command will sync this folder to your vps")
    parser.add_argument('--push', action='store_true', help='pick one from --push, --pull, --sync')
    parser.add_argument('--pull', action='store_true', help='pick one from --push, --pull, --sync')
    parser.add_argument('--sync', action='store_true', help='pick one from --push, --pull, --sync')
    parser.add_argument('-c', '--config', dest="config_file", default='$HOME/.config/csync.json', help='xxx.json({"Host":...,"User":...,"Passwd":...')
    parser.add_argument('-s', '--server', dest='server', help='User@Host')
    parser.add_argument('-k', '--key', dest='identity_file', default='$HOME/.ssh/id_rsa', help='identity file')
    parser.add_argument('-f', '--folder', dest='server_folder', default='$HOME', help='base folder on server')
    parser.add_argument('-ig', '--ignore', dest='ignore_file', default=".gitignore", help="file such as .ignore or .gitignore(default)")
    parser.add_argument('-i', '--interval', default='never', dest="sync_interval", help="measured by seconds")
    parser.add_argument('--push_then_pull', action='store_false')
    parser.add_argument('--pull_then_push', action='store_false')
    args = parser.parse_args()
    return args 




cfg = {
    'Host': '',
    'User': '',
    'Passwd': '',
    'Ignore': '',
    'Key': ''
}

def get_ignore_exclude():
    # cwd = os.getcwd()
    
    # print(head, tail)
    exclude = ' '
    if os.path.isfile(cfg['Ignore']):
        ignore_file = os.path.join(cwd, cfg['Ignore']) 
        
        if os.path.isfile(ignore_file):
            with open(ignore_file, 'r') as f:
                file = f.read().strip().split('\n')
                for exfile in file:
                    exclude += "--exclude '{}' ".format(exfile)
    return exclude    

def get_server_address(folder='~/'):
    return cfg['User'] + '@' + cfg['Host'] + ':' + folder 

def get_command_from_source2target(exclude, source, target):
    if cfg.get('Passwd', False):
        return "sshpass -p {} rsync -av {} {} {} --delete".format(cfg['Passwd'], exclude, source, target)
    elif cfg['Key']:
        pass 
def push2server():
    
    exclude = get_ignore_exclude()
    address = get_server_address()
    print("pushing from {} to {}".format(cwd, address))
    command = "sshpass -p {} rsync -av {} {} {} --delete".format(cfg['Passwd'], exclude, cwd, address)
    os.system(command)

def pullfserver():
    print("IMPORTANT: specify folder by naming your current folder as the same one on your host server. \nOtherwise it won't work!")
    exclude = get_ignore_exclude()
    address = get_server_address(folder='~/'+tail+'/')
    print("pulling from {} to {}".format(address, cwd))
    command = "sshpass -p {} rsync -av {} {} {} --delete".format(cfg['passwd'], exclude, address, cwd)
    os.system(command)


def ask_passwd(args):
    cfg['Passwd'] = getpass.getpass("Enter your password for server {}: ".format(cfg['User'] + '@' + cfg['Host']))

def args_examine(args):
    global cfg 
    if [args.push, args.pull, args.sync].count(True) != 1:
        raise ValueError("ERROR: You should choose one and only one action from 'push, pull or sync'")
    else:
        if args.push:
            args.choice = 'push'
        elif args.pull:
            args.choice = 'pull'
        else:
            args.choice = 'sync'
    if args.server:
        try:
            cfg['User'], cfg['Host'] = args.server.split('@')
        except ValueError:
            print("-s should be something like xxx@xxx.xxx.xxx.xxx")
    elif args.config_file:
        
        with open(os.environ['HOME'] + args.config_file[5:], 'r') as f:
            cfg = json.load(f)
    if args.ignore_file:
        cfg['Ignore'] = args.ignore_file 
    if args.identity_file:
        cfg['Key'] = args.identity_file 
    # print(cfg)
        
def cfg_examine(args):
    if cfg.get('Passwd', False):
        if cfg.get('Key', False) cfg['Key']:
            ask_passwd(args)
    if (not cfg.get('Passwd', False) and not cfg.get('Key', False)) or not cfg.get('User', False) or not cfg.get('Host', False):
        raise Exception("cfg file fail, please try again") 

def sync_action(args, interval=None):
    wording = {'push':'to', 'pull':'from', 'sync':'with'}
    if input("You sure you want to {} folder [{}] {} {}? Y(default)/N  ".format(args.choice, tail, wording[args.choice], get_server_address())).lower() == 'n':
        exit()
    while True:
        if args.push:
            push2server()
        elif args.pull:
            pullfserver()
        elif args.sync:
            if args.pull_then_push:
                pullfserver()
                push2server()
            else:
                push2server()
                pullfserver()
        if interval is not None:
            sleep(interval)
        else:
            break 

if __name__ == '__main__':

    args = parse_args()
    # print(os.environ['HOME'])
    # exit()
    
    args_examine(args)
    print(cfg)
    cfg_examine(args)

    if args.sync_interval.strip().lower() == 'never':
        sync_action(args, interval=None)
    elif args.sync_interval.strip().isdigit():
        sync_action(args, interval=int(args.sync_interval))








