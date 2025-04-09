import logging, yaml, mmap, os, time, re, ipaddress
import banhttpreqstrings.ban as ban
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


log = logging.getLogger(__name__)

try: file = open('/etc/banhttpreqstrings/banhttpreqstrings.yaml')
except: raise Exception('Configuration file not found!')

config = yaml.safe_load(file)
file.close()

if 'banned_paths' in config: banned_paths = config['banned_paths']
else: raise Exception('banned_paths not specified in configuration file!')

if 'exempt_ips' in config: exempt_ips = config['exempt_ips']

banned_paths_regex = []
for path in banned_paths:
    path_compiled = re.compile(path)
    banned_paths_regex.append(path_compiled)



class NewLineHandler(FileSystemEventHandler):
    def __init__(self, file_path, file, position):
        self.file_path = file_path
        self.file = file
        self.position = position


    def dispatch(self, event):
        if event.src_path == self.file_path:
            super().dispatch(event)


    def on_modified(self, event):
        if self.position > os.fstat(self.file.fileno()).st_size:
            self.position = 0
            log.info('{} truncated.'.format(self.file_path))

        self.file.seek(self.position)

        lines = self.file.readlines()
        self.position = self.file.tell()

        for line in lines:
            process_line(line)


    def on_exit(self, event):
        self.file.close()


def process_line(line):
    if line == '' or line == "\n": return

    for path in banned_paths_regex:
        match = re.search(path, line)
        if match != None:
            ip = line.split()[0]
            if ipaddress.ip_address(ip):
                if ip not in exempt_ips:
                    log.info('Matched "{}" from {}'.format(match.group(), ip))
                    ban.ban(ip)
                else:
                    log.info('IP exempted: {}'.format(ip))
    

def tail(log_file_path, stop_threads):
    log.info('Tailing {}...'.format(log_file_path))

    file = open(log_file_path, 'r')
    for line in file.readlines(): process_line(line)

    observer = Observer()
    handler = NewLineHandler(log_file_path, file, file.tell())
    observer.schedule(handler, path = os.path.dirname(log_file_path), recursive = False)
    observer.start()

    while not stop_threads.is_set():
        time.sleep(1)

    observer.stop()
    observer.join()
    log.info('Closing {}...'.format(log_file_path))
    file.close()
