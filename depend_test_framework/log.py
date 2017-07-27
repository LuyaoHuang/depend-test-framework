from contextlib import contextmanager
import logging
import time

FMT = '%(asctime)s | %(levelname)-3s | %(name)-10s | {0} %(message)s'

def make_timing_logger(logger, precision=3, level=logging.DEBUG):
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
    logger.setLevel(level)
    formatter = logging.Formatter(FMT.format(prefix))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # TODO: file put in config
    file_handler = logging.FileHandler('log.debug')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

@contextmanager
def prefix_logger(logger, prefix, level=logging.DEBUG):
    old_logger_fmt = logger.handlers[0].formatter._fmt

    new_fmt_list = old_logger_fmt.split()
    new_fmt_list.insert(-1, prefix)
    new_fmt = " ".join(new_fmt_list)
    formatter = logging.Formatter(new_fmt)
    logger.handlers[0].setFormatter(formatter)
    try:
        yield
    finally:
        formatter = logging.Formatter(old_logger_fmt)
        logger.handlers[0].setFormatter(formatter)
