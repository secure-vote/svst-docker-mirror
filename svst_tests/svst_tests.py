import logging

import datetime

logging.basicConfig(level=logging.INFO)

import time
import json
import socket
import sys, os
from pprint import pprint

import psycopg2

import bitcoin
from bitcoinrpc.authproxy import AuthServiceProxy, EncodeDecimal, JSONRPCException


def fancy_log(title, thing):
    print()
    print("########" * 2 + "#" * len(title))
    print("####### %s #######" % title)
    print("########" * 2 + "#" * len(title))
    print()
    pprint(thing, indent=2)
    print()


magic_bytes = os.getenv('MAGICBYTES')
dbname = os.getenv('POSTGRES_DB')
dbhost = os.getenv('POSTGRES_HOST')
NUM_PALLETS = int(os.getenv('NUM_PALLETS', 20))
fancy_log("Environment Variables", {k: os.getenv(k) for k in os.environ.keys()})


while True:  # continuously attempt to do this until they are up
    try:
        try:
            bitcoind = AuthServiceProxy("http://%s:%s@bitcoind:8332" % (os.getenv('RPCUSER'), os.getenv('RPCPASSWORD')))
            bitcoind.getinfo()  # try to connect in some way
        except socket.gaierror:
            bitcoind = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (os.getenv('RPCUSER'), os.getenv('RPCPASSWORD')))
            bitcoind.getinfo()

        dbhost_ip = socket.gethostbyname(dbhost)
        sqlconn = psycopg2.connect(database=dbname, host=dbhost_ip,
                                   user=os.getenv('POSTGRES_USER'))

    except (socket.gaierror, JSONRPCException, psycopg2.OperationalError) as e:
        logging.info("Sleeping 5; Unable to connect to Bitcoind or Postgres: %s" % e)
        time.sleep(5)
    else:
        break


def run_query(sql_query):
    cur = sqlconn.cursor()
    cur.execute(sql_query)
    rows = [[a if type(a) is not memoryview else bytes(a) for a in row] for row in cur.fetchall()]
    return list(rows)


last_scrape_n = 0
def do_test_round():
    global last_scrape_n
    # first confirm everything and generate coins
    bitcoind.generate(128)
    fancy_log("Bitcoin Getinfo", bitcoind.getinfo())

    # wait for scraper to register some things
    all_scrapes = run_query("SELECT * FROM null_data")
    fancy_log("Last Scrape", [] if len(all_scrapes) == 0 else all_scrapes[-1])
    assert len(all_scrapes) >= last_scrape_n
    last_scrape_n = len(all_scrapes)
    for id, prefix, txid, nd, ht, btime, bhash in all_scrapes:
        assert nd[:len(magic_bytes)] == magic_bytes.encode()
        assert len(nd) == 40

    # now check pallet header download





ROUND_TIME_SEC = 2.0
NUM_ROUNDS = max(NUM_PALLETS * 3, 20)
for round_n in range(NUM_ROUNDS):
    r_start = time.time()
    fancy_log("Round %d / %d" % (round_n + 1, NUM_ROUNDS), {'time': time.time(), 'date': repr(datetime.datetime.now())})
    do_test_round()
    time.sleep(max(ROUND_TIME_SEC - time.time() + r_start, 0))

    if last_scrape_n == NUM_PALLETS:
        break

assert last_scrape_n == NUM_PALLETS
