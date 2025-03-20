import logging, configparser, threading, sys, signal, os
import banhttpreqstrings.tail as tail
from systemd import journal


log = logging.getLogger(__name__)
log.addHandler(journal.JournalHandler())
log.setLevel(logging.INFO)

config = configparser.ConfigParser()
try: config.read('/etc/banhttpreqstrings/banhttpreqstrings.conf')
except: raise Exception('Configuration file not found!')

threads = []
stop_threads = threading.Event()

exit_code = 0


def get_log_file_paths()
    if config.has_option('banhttpreqstrings', 'log_paths'):
        return config.get('banhttpreqstrings', 'log_paths')

    else: raise Exception('log_paths not specified in configuration file!')


def shutdown():
    log.info('Shutting down...')
    stop_threads.set()
    for thread in threads: thread.join(timeout = 5)
    if threading.active_count() != 0: exit_code = 1

    sys.exit(exit_code)


def exception_handler(exception_type, exception_value, exception_traceback):
    log.error('{}: {}'.format(exception_type.__name__, exception_value))
    exit_code = 2
    shutdown()


def main():
    log.info('Starting service...')
    signal.signal(signal.SIGTERM, shutdown)

    try: os.system('iptables -N banhttpreqstrings')
    except: pass

    log_file_paths = get_log_file_paths()
    for log_file_path in log_file_paths:
        thread = threading.Thread(target = tail.tail, args = (log_file_path,))
        thread.start()
        threads.append(thread)


if __name__ == '__main__': main()
