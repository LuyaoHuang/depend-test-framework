from contextlib import contextmanager
import logging
import time

FMT = '%(asctime)s | %(levelname)-3s | {0} %(message)s'
FILE_FMT = '%(message)s'


def make_timing_logger(logger, precision=3, level=logging.INFO):
    @contextmanager
    def log_time(msg, *args):
        start_time = time.time()

        try:
            yield
        finally:
            message = "{} in %0.{}fs".format(msg, precision)
            duration = time.time() - start_time
            args = args + (duration,)
            logger.log(level, message, *args)

    return log_time


def make_prefix_logger(logger, prefix):
    def log_helper(msg, *args):
        with prefix_logger(logger, prefix):
            logger.info(msg, *args)

    return log_helper


def get_logger(name, level=logging.INFO, prefix=""):
    """
    Generate a logger for a module
    """
    logger = logging.getLogger(name)
    logger.propagate = False
    # logger.setLevel(level)
    formatter = logging.Formatter(FMT.format(prefix))

    console_handler = logging.StreamHandler()
    # console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # TODO: file put in config
    file_handler = logging.FileHandler('log.debug')
    # file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_file_logger(name, file_name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.propagate = False
    # logger.setLevel(level)
    formatter = logging.Formatter(FILE_FMT)

    # TODO: file put in config
    file_handler = logging.FileHandler(file_name, mode='w')
    # file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


@contextmanager
def prefix_logger(logger, prefix, level=logging.DEBUG, new_name=None):
    old_logger_fmt = logger.handlers[0].formatter._fmt

    new_fmt_list = old_logger_fmt.split()
    new_fmt_list.insert(-1, prefix)
    new_fmt = " ".join(new_fmt_list)
    if new_name:
        # TODO
        new_fmt = new_fmt.replace("%(name)-30s", "%-30s" % new_name)
    formatter = logging.Formatter(new_fmt)
    logger.handlers[0].setFormatter(formatter)
    try:
        yield
    finally:
        formatter = logging.Formatter(old_logger_fmt)
        logger.handlers[0].setFormatter(formatter)
