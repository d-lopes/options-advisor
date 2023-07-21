from datetime import datetime, date
import pandas as pd
import logging

from yahoo_fin import stock_info as stocks, options as opts

from src.main.analyzer import Analyzer

# for Testing purposes: 
symbols = ['AMZN']

# only NYSE listed stocks are possible
# BEPC and LPX caused issues. thus they were removed from the list of symbols below
# symbols = ['CVX', 'AMZN', 'NKE', 'TSM', 'LPX', 'OXY', 'KR', 'KHC', 'BAC', 'ALLY', 'PARA', 'STNE', 'PFE', 'CSX']

mode = Analyzer.Types.PUT
default_filter = Analyzer.Filter.getDefaults()
default_filter.max_strike = 40
start_week_offset = 3
end_week_offset = start_week_offset + 4

# get possible expiration dates between start and end date
now = datetime.now() # current date and time
start_week = now.isocalendar().week + start_week_offset
end_week = start_week - start_week_offset + end_week_offset
logger = logging.getLogger('main')

data = pd.DataFrame(columns=Analyzer.DATA_COLUMNS)

if __name__ == '__main__':
    for symbol in symbols:
        try:
            price = stocks.get_live_price(symbol)
            # skip processing of underlying when live price + 20% is above acceptable strike
            if (price > default_filter.max_strike * 1.2):
                logger.warning('price of underlying %s too high. Skipping this symbol!', symbol)
                continue
        except AssertionError:
            logger.error('unable to retrieve data for symbol %s. Skipping this symbol!', symbol)
            continue

        for week in range(start_week, end_week):
            expiration_date = date.fromisocalendar(2023, week, 5)
            logger.info("get data for %s with expiration date %d", symbol, expiration_date)

            #try:
            more_data = Analyzer.get_info(symbol, mode, expiration_date, price, default_filter)
            #except KeyError:
            #    logger.error('unable to analyze data for symbol  %s. Continuing with next symbol!', symbol)
            #    continue
            data = pd.concat([data, more_data], ignore_index=True)

    print('Time: ' + now.strftime('%d/%m/%Y, %H:%M:%S'))
    print('Options: ')
    print(data)
