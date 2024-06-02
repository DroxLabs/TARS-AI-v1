import logging


formatter = logging.Formatter("[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
                              "%Y-%m-%d %H:%M:%S")


def setup_logger(name, log_file, mode='a', level=logging.INFO):
    """To set up as many loggers as you want"""

    handler = logging.FileHandler(log_file, mode)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
