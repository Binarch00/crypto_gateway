# Crypto IPN Service
Free standalone Crypto Instant Payment Notification service.

###### Features:
* http api to query a BTC address total confirmed and unconfirmed balance.
* http api to subscribe for IPN notifications for specific bitcoin address.
* Bitcoin IPN service to notify with http requests about new incoming deposits.

Required services:
* mysql database
* bitcoind

## Install

1. Install coin daemon and use this config:

        server=1
        rpcuser=<change username here>
        rpcpassword=<change passw here>
        rpcport=8332
        prune=1
        rpcconnect=127.0.0.1
    1.1. Prune all old blocks `bitcoin-cli pruneblockchain 573503`
    
    1.2. Other option is set `prune=700` wait for sync and remove the option
    
2. Create a mysql database and adjust db.DataBase database server info and credentials.

3. At database create the tables described at file `DDL.sql`

4. Install python3.5 or greater

5. Setup  python virtualenv and install requirements 

        pip install -r requirements.txt
6. Adjust service settings at `settings.py` file.

7. Run service `chain_sync.py` and add a watchdog to verify it runs all the time.

8. After blockchain synchronization, run the IPN notification service `ipn_service.py`

9. Run or deploy http api service located at `crypto_gateway/web_api.py`
```shell script
PYTHONPATH=./ python ./crypto_gateway/web_api.py
```

## Usage

##### How get the total BTC received by an specific address

    from crypto_gateway import get_received
    confirmed, unconfirmed = get_received("btc-address-here")

##### How get the total BTC received by an specific user id

This feature assume that you can easy relate one unique integer id to each user.

    from crypto_gateway import get_user_received
    confirmed, unconfirmed = get_user_received(1010)

The address are generated usign the `settings.CHAIN['xpub_key']` public key.

#### IPN http api

###### How get the total BTC received by an specific address

Do a http POST or GET request to api server url `/btc` using the form 
field `address` for specify the BTC address.

The server response result will be a json like below:
```json
{
        "confirmed": 0.1,
        "unconfirmed": 0.2
}
``` 

###### How subscribe a BTC address and URL to receive IPN notifications about BTC deposits.

Do a http POST or GET request to api server url `/btc_ipn` using the below form fields:
* **address** BTC address to watch about incoming deposits.
* **url** URL to receive the IPN notifications about incoming deposits.
* **max_confirms** Maximum amount of block confirms to consider confirmed a deposit.

The server response will be a plain text string `success` or `fail`

###### How process IPN notifications

At subscribed URL will arrive a HTTP POST request with below fields:

* **address** The BTC address that receive a new deposit.
* **confirmed** Total historical confirmed balance for the 
address, including the new deposit amount.
* **unconfirmed** Total unconfirmed balance for the address.

> Note: IPN will send total net amount received. Client should track address 
>previous deposits to calculate  new amount deposit.

To confirm that IPN was received the IPN receiver response should
 be a json with same received fields.
 
 ```json
{
    "address": "1LT...",
    "confirmed": "0.01",
    "unconfirmed": "0.0"
}
```

If this confirmation is not sent properly, the IPN will arrive forever.

At unusual situations, if block-chain need sync many blocks, the IPN receiver 
could be receiving multiple IPN for each delayed block not parsed, concurrently.
IPN receiver should be able to handle those unusual cases.

.