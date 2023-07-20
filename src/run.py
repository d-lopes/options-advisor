from datetime import datetime, date
import pandas as pd
import logging

from yahoo_fin import stock_info as stocks, options as opts

from analyzer import analyzer

symbols = ['CVX', 'AMZN', 'P911', 'NKE', 'TSM', 'LPX', 'OXY', 'KR', 'KHC', 'BAC', 'ALLY', 'PARA', 'ECV', 'STNE', 'PFE', 'CSX', 'BEPC']
mode = analyzer.Types.PUT
min_puts = 1000
min_calls = 1000
start_week_offset = 3
end_week_offset = start_week_offset + 4

# get possible expiration dates between start and end date
now = datetime.now() # current date and time
start_week = now.isocalendar().week + start_week_offset
end_week = start_week - start_week_offset + end_week_offset
logger = logging.getLogger('main')

data = pd.DataFrame(columns=analyzer.DATA_COLUMNS)

for symbol in symbols:
    try:
        price = stocks.get_live_price(symbol)
    except AssertionError:
        logger.error('unable to retrieve data for symbol  %s. Continuing with next symbol!', symbol)
        continue

    for week in range(start_week, end_week):
        expiration_date = date.fromisocalendar(2023, week, 5)
        logger.info("get data for %s with expiration date %d", symbol, expiration_date)

        try:
            more_data = analyzer.get_info(ticker = symbol, type = mode, expiration_date = expiration_date, price = price, filter = [min_calls, min_puts])
        except KeyError:
            logger.error('unable to analyze data for symbol  %s. Continuing with next symbol!', symbol)
            continue
        data = pd.concat([data, more_data], ignore_index=True)

print('Time: ' + now.strftime('%d/%m/%Y, %H:%M:%S'))
print('Options: ')
print(data)
