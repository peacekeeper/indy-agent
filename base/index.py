#!/usr/bin/env python3.6
from indy import pool, wallet
from indy.error import ErrorCode, IndyError
from aiohttp import web
from getpass import getpass
from src.utils import get_config, exit_handler, health_handler
from src.handler import http_handler
import logging, sys, yaml, json, time, asyncio, code, signal

# Globals
POOL_PROTOCOL_VERSION = 2
wallet_handle = None
pool_handle = None
port = None

# Configure Logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

config = get_config()


async def main():
    global pool_handle, wallet_handle, port
    # Get Wallet Key and Open Wallet
    wallet_key = getpass('Enter Wallet Key: ')
    wallet_config = json.dumps({"id": config['wallet']['name']})
    wallet_credentials = json.dumps({"key": wallet_key})
    wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
    
    # Open Pool
    try:
        await pool.set_protocol_version(POOL_PROTOCOL_VERSION)
        pool_handle = await pool.open_pool_ledger(config['pool']['name'], None)
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerTimeout:
            print("Pool Ledger timed out. Please check your pool config and try again")
            exit(1)

    # Configure Web Server Port
    port = config['agent']['port']

    # FIXME: Setup Active Modules
    #for mod in config['modules']['active']:


if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_handler)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    app = web.Application()
    app.add_routes([
        web.get('/', health_handler),
        web.post('/', http_handler)
    ])

    web.run_app(app, host='0.0.0.0', port=port)
