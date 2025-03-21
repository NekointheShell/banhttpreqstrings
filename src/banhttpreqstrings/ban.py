import logging, yaml, os, mmap, fcntl, ipaddress


log = logging.getLogger(__name__)


try: file = open('/etc/banhttpreqstrings/banhttpreqstrings.yaml', 'r')
except: raise Exception('Configuration file not found!')

config = yaml.safe_load(file)
file.close()

if 'ban_file_path' in config: ban_file_path = config['ban_file_path']
else: raise Exception('ban_file_path not specified in configuration file!')


def is_banned(ip):
    if not os.path.exists(ban_file_path): return False

    file = open(ban_file_path, 'r')
    mmapped_file = mmap.mmap(file.fileno(), 0, access = mmap.ACCESS_READ)

    if ip in mmapped_file.read().decode().rstrip(): return True
    return False


def save_ban(ip):
    file = open(ban_file_path, 'a+')
    fcntl.flock(file.fileno(), fcntl.LOCK_EX)

    file.write("{}\n".format(ip))

    fcntl.flock(file.fileno(), fcntl.LOCK_UN)
    file.close()


def ban(ip):
    if not ipaddress.ip_address(ip): raise Exception('Command injection attempt detected!')

    if not is_banned(ip):
        log.info('Banning {}...'.format(ip))
        save_ban(ip)
        os.system('iptables -A ban_noncreative -s {} -j DROP'.format(ip))
