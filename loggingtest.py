import logging


logging.basicConfig(level=logging.debug, filename="log.log", filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    1 / 0
except ZeroDivisionError:
    logging.debug('zerodiveisionerror')