log = logging.getLogger(__name__)


def tail(log_file_path):
    log.info('Tailing {}...'.format(log_file_path))
