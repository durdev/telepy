import os
import asyncio
from datetime import datetime
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk import SynchronizationListener
from metaapi_cloud_sdk.metaapi.models import MetatraderTick, MetatraderSymbolPrice
from typing import List
import postgres_db
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('METAAPI_TOKEN')
domain = 'agiliumtrade.agiliumtrade.ai'
account_id = os.getenv('METAAPI_ACCOUNT_ID')

class QuoteListener(SynchronizationListener):
    async def on_symbol_price_updated(self, instance_index: int, price: MetatraderSymbolPrice):
        postgres_db.update_or_create_symbol(price['symbol'], price['bid'], price['ask'])

async def stream_quotes():
    api = MetaApi(token, {'domain': domain})

    try:
        account = await api.metatrader_account_api.get_account(account_id)

        if account.connection_status != 'CONNECTED':
            await account.wait_connected()

        connection = account.get_streaming_connection()

        quote_listener = QuoteListener()
        connection.add_synchronization_listener(quote_listener)

        await connection.connect()
        await connection.wait_synchronized()

        await subscribe_symbols(10, connection)

        while True:
            await asyncio.sleep(1)
    except Exception as err:
        print(api.format_error(err))

async def subscribe_symbols(interval_seconds: int, connection):
    """
    An asynchronous function that runs a task periodically.
    """
    while True:
        symbols = postgres_db.get_symbols()

        to_add_symbols = set(symbols) - set(connection.subscribed_symbols)

        for symbol in symbols:
            if symbol in to_add_symbols:
                print(f"Subscribing to market data for symbol: {symbol}")
                await connection.subscribe_to_market_data(symbol, [{'type': 'quotes'}])

        to_remove_symbols = set(connection.subscribed_symbols) - set(symbols)

        for symbol in connection.subscribed_symbols:
            if symbol in to_remove_symbols:
                print(f"Unsubscribing from market data for symbol: {symbol}")
                await connection.unsubscribe_from_market_data(symbol, [{'type': 'quotes'}])

        await asyncio.sleep(interval_seconds)

asyncio.run(stream_quotes())

