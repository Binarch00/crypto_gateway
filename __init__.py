from settings import logger, CHAIN
import db
from pywallet import wallet
import pprint


def get_received(address):
    """ Main service function, that returns the total received balance.

    :returns a tuple with total received (confirmed, unconfirmed) balance from address
    """
    try:
        ldb = db.DataBase()
        return tuple(ldb.get_total_received(address))
    except Exception as ex:
        logger.exception(ex)


def get_deposit_address(user_id: int):
    """
    Given an int unique user id, return the public wallet address related
    :param user_id: User unique int id
    :return: The user address
    """
    user_addr = wallet.create_address(
        network="BTC", xpub=CHAIN['xpub_key'], child=user_id)
    return user_addr['address']


def get_user_received(user_id: int):
    """
    Return the user total received balance.
    :param user_id: User unique int id
    :return: total received balance.
    """
    address = get_deposit_address(user_id)
    return get_received(address)
