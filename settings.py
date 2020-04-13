import logging

TESTING = False

DATABASE = {
    "user": 'root',
    "password": '1234567*',
    "host": '127.0.0.1',
    "database": "btc_ipn"
}

RPC_NODE = {
    "user": "OIDSAHdiasdiosudhasdjoasidjoaiqweoirof",
    "password": "sldkfhsooiAHOIDoIHJSOAKlsdjAOSIDao",
    "server": "127.0.0.1",
    "port": 8332
}

CHAIN = {
    "name": "btc",
    "confirms": 3,
    "start_block": 10,  # set this value to a recent block after chain sync and prune is completed.
    "xpub_key": "xpub661MyMwAqRbcEf6HK5WHdbCjz1QYyqAK6SXmfYcNVbYYr33CZndih7tjYgCd"
                "C54cJ8f2v8DLJNnVhTKqgWbg2s5v1BdBfysF8Ki9QuKGmm2"
}

IPN_AUTH = "IPN-Auth1"

LOGS = {
    "level": logging.DEBUG,
    "file": "ipn_service.log",
    "format": '%(asctime)s - %(filename)s - Line %(lineno)d - %(levelname)s - %(message)s'
}


def setup_logger():
    # create logger
    logger = logging.getLogger('main')
    logger.setLevel(LOGS['level'])
    # create console handler and set level to debug
    ch = logging.FileHandler(LOGS['file'])
    ch.setLevel(LOGS['level'])
    # create formatter
    formatter = logging.Formatter(LOGS['format'])
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


logger = setup_logger()
