import logging


def setup_log(conf):
    """TODO"""
    log_file_name = conf['logging']['filename']
    logging.basicConfig(level=logging.DEBUG, filename=log_file_name, filemode='w')
