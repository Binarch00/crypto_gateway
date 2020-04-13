import mysql.connector
from settings import logger, DATABASE, CHAIN


class DataBase:

    def __init__(self):
        self.conn = mysql.connector.connect(
            user=DATABASE["user"], password=DATABASE["password"],
            host=DATABASE["host"], database=DATABASE["database"])

    def __del__(self):
        self.conn.close()

    def add_output(self, block, address, value, hash):
        try:
            cursor = self.conn.cursor()
            add_output = ("INSERT INTO address_outputs "
                           "(block, address, value, block_hash) "
                           "VALUES (%s, %s, %s, %s)")
            data = (block, address, value, hash)
            cursor.execute(add_output, data)
            self.conn.commit()
            cursor.close()
        except Exception as ex:
            logger.exception(ex)

    def delete_block_hash(self, block, hash):
        cursor = self.conn.cursor()
        del_query = ("DELETE FROM address_outputs "
                     "WHERE block=%s AND block_hash=%s")
        data = (block, hash)
        cursor.execute(del_query, data)
        self.conn.commit()
        cursor.close()

    def get_total_received(self, address, confirms=None):
        confirms = CHAIN["confirms"] if not confirms else confirms
        confirmed = self.get_last_block() - CHAIN["confirms"]
        query = ("SELECT SUM(IF(block <= %s, value, 0)) as confirmed, "
                 "SUM(IF(block > %s, value, 0)) as unconfirmed "
                 "FROM address_outputs "
                 "WHERE address=%s")
        data = (confirmed, confirmed, address)
        cursor = self.conn.cursor()
        cursor.execute(query, data)
        row = cursor.fetchone()
        result = [0.0, 0.0]
        if row and row[0] is not None:
            result[0] = float(row[0])
            result[1] = float(row[1])
        cursor.close()
        return result

    def get_block_hash(self, block):
        query = ("SELECT block_hash "
                 "FROM address_outputs "
                 "WHERE block=%s "
                 "LIMIT 1")
        data = (block, )
        cursor = self.conn.cursor()
        cursor.execute(query, data)
        row = cursor.fetchone()
        result = False
        if row and row[0]:
            result = row[0]
        cursor.close()
        return result

    def get_last_block(self):
        query = ("SELECT MAX(block) "
                 "FROM address_outputs")
        cursor = self.conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        result = 0
        if row and row[0]:
            result = row[0]
        cursor.close()
        return result

    def get_ipns(self, block):
        try:
            query = ("SELECT DISTINCT(i.address), i.max_confirms, i.url "
                     "FROM ipn i "
                     "JOIN address_outputs a "
                     "ON i.address=a.address "
                     "WHERE a.block BETWEEN %s AND %s + i.max_confirms "
                     )
            cursor = self.conn.cursor()
            cursor.execute(query, (block, block))
            data = cursor.fetchall()
            cursor.close()
            return data
        except Exception as ex:
            logger.exception(ex)

    def get_ipns_fails(self):
        try:
            query = ("SELECT DISTINCT(address), max_confirms, url "
                     "FROM ipn "
                     "WHERE status='fail' "
                     )
            cursor = self.conn.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            return data
        except Exception as ex:
            logger.exception(ex)

    def set_ipn_status(self, address, status):
        try:
            query = (
                "UPDATE ipn "
                "SET status=%s "
                "WHERE address=%s "
            )
            data = (status, address)
            cursor = self.conn.cursor()
            cursor.execute(query, data)
            self.conn.commit()
            cursor.close()
        except Exception as ex:
            logger.exception(ex)

    def get_ipn_status(self, address):
        try:
            query = (
                "SELECT status FROM ipn "
                "WHERE address=%s "
            )
            cursor = self.conn.cursor()
            cursor.execute(query, (address,))
            row = cursor.fetchone()
            result = 0
            if row and row[0]:
                result = row[0]
            cursor.close()
            return result
        except Exception as ex:
            logger.exception(ex)

    def add_ipn(self, address, url, type="btc", max_confirms=3):
        try:
            query = (
                "INSERT IGNORE INTO ipn "
                "(address, url, type, max_confirms) "
                "VALUES (%s, %s, %s, %s)"
            )
            data = (address, url, type, max_confirms)
            cursor = self.conn.cursor()
            cursor.execute(query, data)
            self.conn.commit()
            cursor.close()
            return True
        except Exception as ex:
            logger.exception(ex)
        return False

    def get_setting(self, name):
        query = ("SELECT value "
                 "FROM settings "
                 "WHERE name=%s "
                 "LIMIT 1")
        data = (name,)
        cursor = self.conn.cursor()
        cursor.execute(query, data)
        row = cursor.fetchone()
        result = None
        if row and row[0]:
            result = row[0]
        cursor.close()
        return result

    def set_setting(self, name, value):
        try:
            cursor = self.conn.cursor()
            add_output = ("INSERT INTO settings "
                          "(name, value) "
                          "VALUES (%s, %s) "
                          "ON DUPLICATE KEY UPDATE "
                          "value = VALUES(value)")
            data = (name, value)
            cursor.execute(add_output, data)
            self.conn.commit()
            cursor.close()
        except Exception as ex:
            logger.exception(ex)
