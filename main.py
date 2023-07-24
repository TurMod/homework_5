import asyncio
import aiohttp
import json
import sys
import platform

from datetime import datetime, timedelta
from aiohttp.client_exceptions import ClientConnectorError
from json.decoder import JSONDecodeError


async def get_currency(link: str, date: str, session) -> None:
    async with session.get(link + date) as response:
        return await response.json()


async def get_date(days: int):
    for day in range(0, days):
        date = datetime.now() - timedelta(days=day)
        date = date.strftime('%d.%m.%Y')
        yield date


async def normalize(currencies_info: dict):
    date = currencies_info.get('date')
    currencies_needed = ('EUR', 'USD')
    currencies_list = list(filter(
        lambda currency: currency.get('currency') in currencies_needed,
        currencies_info.get('exchangeRate')
    ))
    currencies_dict = {date: {}}

    for currency in currencies_list:
        currency_name = currency.get('currency')
        sale = currency.get('saleRateNB')
        purchase = currency.get('purchaseRateNB')
        currencies_dict[date][currency_name] = {'sale': sale, 'purchase': purchase}

    return currencies_dict


async def main():
    try:
        days = int(sys.argv[1])
    except (IndexError, ValueError):
        days = 1

    if days < 1:
        days = 1
    elif days > 10:
        days = 10

    link = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='

    async with aiohttp.ClientSession() as session:
        tasks = [get_currency(link, date, session) async for date in get_date(days)]
        result = await asyncio.gather(*tasks)

    tasks = [normalize(currencies_info) for currencies_info in result]
    normalize_data = await asyncio.gather(*tasks)
    print(json.dumps(normalize_data, indent=4))


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except (ClientConnectorError, ConnectionError):
        print('Connection failed!')
    except TypeError:
        print('No processing data found!')
    except (JSONDecodeError, KeyError, AttributeError):
        print('Unable to process data!')
    except OSError:
        print('Not enough file descriptors due to a large number of tasks!')
    except MemoryError:
        print('Insufficient memory due to a large volume of data!')
    except:
        print('Unexpected error!')
