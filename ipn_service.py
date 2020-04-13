import asyncio
import random
import time

import requests

from settings import logger, IPN_AUTH, TESTING
import db


IPN_WORKERS = 10


async def worker(queue):
    ldb = None
    try:
        if not ldb:
            ldb = db.DataBase()
        address, max_confirms, url = await queue.get()
        confirmed, unconfirmed = ldb.get_total_received(address, confirms=max_confirms)
        data = {
            "address": address,
            "confirmed": confirmed,
            "unconfirmed": unconfirmed,
            "ipn_auth": IPN_AUTH
        }
        resp = requests.post(url=url, data=data)
        if resp.ok and resp.json() == data:
            ldb.set_ipn_status(address, 'done')
        else:
            ldb.set_ipn_status(address, 'fail')
            logger.error("IPN confirmation failed! data: {}".format(data))
        queue.task_done()
        if TESTING:
            return data
    except Exception as ex:
        logger.exception(ex)


async def main():
    queue = asyncio.Queue()

    tasks = []
    for i in range(IPN_WORKERS):
        task = asyncio.create_task(worker(queue))
        tasks.append(task)

    ldb = db.DataBase()
    ipn_sync_block = int(ldb.get_setting("ipn_sync_block"))
    while True:
        last_block = ldb.get_last_block()
        logger.warning("last_block: %s" % last_block)
        if last_block > ipn_sync_block:
            for block in range(ipn_sync_block + 1, last_block + 1, 1):
                logger.warning("active block: %s" % block)
                for row in ldb.get_ipns(block) or []:
                    queue.put_nowait(row)
                ldb.set_setting("ipn_sync_block", block)
                ipn_sync_block = block
        # waiting for next block usually each 10 minutes for BTC
        await asyncio.sleep(10)
        # code for unittests
        if TESTING:
            return None
        # check for missing workers
        for task in tasks:
            if task.done():
                tasks.remove(task)
                tasks.append(asyncio.create_task(worker(queue)))



if __name__ == "__main__":
    asyncio.run(main())
