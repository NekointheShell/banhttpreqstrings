import logging, yaml, mmap, os, time
import banhttpreqstrings.ban as ban


log = logging.getLogger(__name__)

try: file = open('/etc/banhttpreqstrings/banhttpreqstrings.yaml')
except: raise Exception('Configuration file not found!')

config = yaml.safe_load(file)
file.close()

if 'banned_paths' in config: banned_paths = config['banned_paths']
else: raise Exception('banned_paths not specified in configuration file!')

if 'exempt_ips' in config: exempt_ips = config['exempt_ips']


def filesize0_edgecase(log_file_path):
    while os.path.getsize(log_file_path) == 0:
        time.sleep(1)


def tail(log_file_path, stop_threads):
    log.info('Tailing {}...'.format(log_file_path))

    file = open(log_file_path, 'r')
    if os.path.getsize(log_file_path) == 0: filesize0_edgecase(log_file_path)
    mmapped_file = mmap.mmap(file.fileno(), 0, access = mmap.ACCESS_READ)

    while not stop_threads.is_set():
        line = mmapped_file.readline().decode()
        if line != '' and line != '\n':
            for path in banned_paths:
                if path in line:
                    ip = line.split()[0]
                    if ip not in exempt_ips: ban.ban(ip)

    log.info('Closing {}...'.format(log_file_path))
    mmapped_file.close()
    file.close()
