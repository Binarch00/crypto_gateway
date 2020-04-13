import pprint
import time
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import db
from settings import logger, RPC_NODE, CHAIN


class ChainData:

    RPC_USER = RPC_NODE["user"]
    RPC_PASSWORD = RPC_NODE["password"]
    RPC_SERVER = RPC_NODE["server"]
    RPC_PORT = RPC_NODE["port"]
    MIN_BLOCK = CHAIN["start_block"]
    MIN_CONFIRMS = CHAIN["confirms"]
    COIN = CHAIN["name"]

    def __init__(self):
        self.rpc_conn = AuthServiceProxy("http://%s:%s@%s:%s" % (
            self.RPC_USER, self.RPC_PASSWORD, self.RPC_SERVER, self.RPC_PORT))

    def get_blocks(self):
        resp = self.rpc_conn.getblockchaininfo()
        return resp["blocks"]

    def get_headers(self):
        resp = self.rpc_conn.getblockchaininfo()
        return resp["headers"]

    def get_blockhash(self, block):
        resp = self.rpc_conn.getblockhash(block)
        return resp

    def _get_blocktransactions(self, block):
        blockhash = self.get_blockhash(block)
        resp = self.rpc_conn.getblock(blockhash, 2)
        return resp["tx"], blockhash

    def getblock_out_balances(self, block):
        txs, blockhash = self._get_blocktransactions(block)
        balances = []
        for tx in txs:
            for iout in tx['vout']:
                if iout.get("scriptPubKey") and iout.get("scriptPubKey").get("addresses"):
                    balances.append((iout["scriptPubKey"]["addresses"][0], iout["value"]))
                    if len(iout["scriptPubKey"]["addresses"]) > 1:
                        logger.error("More than one address detected! block %s, addresses: %s" %
                                     (block, iout["scriptPubKey"]["addresses"]))
        return balances, blockhash


def check_block(block):
    """ Check if block hash remain the same.
        If hash change, delete and update all the related info.
    """
    chain = ChainData()
    ldb = db.DataBase()
    hash = ldb.get_block_hash(block)
    if chain.get_blockhash(block) != hash:
        if block and hash:
            logger.warning("Block %s change hash" % block)
        ldb.delete_block_hash(block, hash)
        balances, blockhash = chain.getblock_out_balances(block)
        for balance in balances:
            ldb.add_output(block, balance[0], balance[1], blockhash)


def clean_last_block():
    chain = ChainData()
    ldb = db.DataBase()

    block = ldb.get_last_block()
    hash = ldb.get_block_hash(block)
    logger.warning("Cleaning block %s, hash %s" % (block, hash))
    ldb.delete_block_hash(block, hash)


if __name__ == "__main__":
    clean_last_block()
    while True:
        try:
            chain = ChainData()
            ldb = db.DataBase()
            current_block = chain.get_blocks()
            last_db_block = ldb.get_last_block()

            if last_db_block < current_block:
                for block in range(
                        max(last_db_block - chain.MIN_CONFIRMS, chain.MIN_BLOCK),
                        max(chain.MIN_BLOCK, current_block) + 1, 1):
                    logger.debug("Processing block %s" % block)
                    check_block(block)
            else:
                logger.debug("Waiting new blocks!")
        except Exception as ex:
            print("Exc: %s" % ex)
            logger.exception(ex)
        time.sleep(5)
