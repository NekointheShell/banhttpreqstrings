import logging, configparser, mmap
import banhttpreqstrings.ban as ban


log = logging.getLogger(__name__)

config = configparser.ConfigParser()
try: config.read('/etc/banhttpreqstrings/banhttpreqstrings.conf')
except: raise Exception('Configuration file not found!')

if config.has_option('banhttpreqstrings', 'banned_paths'):
    banned_paths = config.get('banhttpreqstrings', 'banned_paths')
else: raise Exception('banned_paths not specified in configuration file!')

if config.has_option('banhttpreqstrings', 'exempt_ips'):
    exempt_ips = config.get('banhttpreqstrings', 'exempt_ips')


def tail(log_file_path, stop_threads):
    log.info('Tailing {}...'.format(log_file_path))

    file = open(log_file_path, 'r')
    mmapped_file = mmap.mmap(file.fileno(), 0, access = mmap.ACCESS_READ)

    while not stop_threads.is_set()
        line = mmapped_file.readline()
        if line != '' and line != '\n':
            for path in banned_paths:
                if path in line:
                    ip = line.split()[0]
                    if ip not in exempt_ips: ban.ban(ip)

    log.info('Closing {}...'.format(log_file_path))
    mmapped_file.close()
    file.close()
