import logging, yaml, mmap, os, time, re
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
    def __init__(self, file_path, file):
        self.file_path = file_path
        self.file = file
        self.position = 0


    def dispatch(self, event):
        if event.src_path == self.file_path:
            super().dispatch(event)


    def on_modified(self, event):
        self.file.seek(self.position)

        lines = self.file.readlines()
        self.position = self.file.tell()

        for line in lines:
            process_line(line)


def process_line(line):
    for path in banned_paths_regex:
        if re.search(path, line) != None:
            ip = line.split()[0]
            if ip not in exempt_ips and ipaddress.ip_address(ip): ban.ban(ip)
    


def tail(log_file_path, stop_threads):
    log.info('Tailing {}...'.format(log_file_path))

    file = open(log_file_path, 'r')
    while not stop_threads.is_set():
        line = file.readline()

        if line != '' and line != "\n": process_line(line)
        else:
            observer = Observer()
            handler = NewLineHandler(log_file_path)

            observer.schedule(handler, path = os.path.dirname(log_file_path), recursive = False)
            observer.start()

    log.info('Closing {}...'.format(log_file_path))
    file.close()
