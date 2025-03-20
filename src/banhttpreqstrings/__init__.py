import logging, sys, os, threading, signal
from banhttpreqstrings import tail
from systemd import journal


log = logging.getLogger(__name__)
log.addHandler(journal.JournalHandler())
log.setLevel(logging.INFO)

config = configparser.ConfigParser()
try: config.read('/etc/banhttpreqstrings/banhttpreqstrings.conf')
except: shutdown(exception = 'Configuration file not found!')

threads = []
stop_threads = threading.Event()


def get_log_file_paths()
    if config.has_option('banhttpreqstrings', 'log_paths'):
        return config.get('banhttpreqstrings', 'log_paths')

    else: shutdown(exception = 'Nothing to monitor!')


def shutdown(exception = False):
    log.info('Shutting down...')
    stop_threads.set()
    for thread in threads: thread.join(timeout = 5)

    if threading.active_count() != 0: sys.exit(1)
    if exception:
        log.error(exception)
        sys.exit(1)

    sys.exit(0)


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
