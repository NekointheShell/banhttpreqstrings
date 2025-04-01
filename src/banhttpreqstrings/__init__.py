import logging, yaml, threading, sys, signal, os, time
import banhttpreqstrings.tail as tail
from systemd import journal


log = logging.getLogger(__name__)
log.addHandler(journal.JournalHandler())
log.setLevel(logging.INFO)

try: file = open('/etc/banhttpreqstrings/banhttpreqstrings.yaml', 'r')
except: raise Exception('Configuration file not found!')

config = yaml.safe_load(file)
file.close()

if 'log_file_paths' in config: log_file_paths = config['log_file_paths']
else: raise Exception('log_file_paths not specified in configuration file!')

stop_threads = threading.Event()


def shutdown():
    log.info('Shutting down...')
    stop_threads.set()

    for thread in threading.enumerate():
        if thread is not threading.main_thread():
            thread.join()

    if threading.active_count() != 1: sys.exit('Threads did not stop in time!')
    sys.exit()


def sigterm(signal, frame):
    shutdown()


def exception_handler(exception_type, exception_value, exception_traceback):
    log.error('{}: {}'.format(exception_type.__name__, exception_value))
    exit_code = 2
    shutdown()


def main():
    log.info('Starting service...')
    signal.signal(signal.SIGTERM, sigterm)

    try:
        os.system('iptables -N banhttpreqstrings')
        os.system('iptables -A INPUT -j banhttpreqstrings')
    except: pass

    for log_file_path in log_file_paths:
        thread = threading.Thread(target = tail.tail, args = (log_file_path, stop_threads))
        thread.start()

    while True: time.sleep(1)


if __name__ == '__main__': main()
