from datetime import datetime, date
import pandas as pd
from yahoo_fin import stock_info as stocks, options as opts

from analyzer import analyzer

symbols = ['BAC']
mode = analyzer.Types.PUT
min_puts = 1000
min_calls = 1000
start_week_offset = 3
end_week_offset = start_week_offset + 4

# get possible expiration dates between start and end date
now = datetime.now() # current date and time
start_week = now.isocalendar().week + start_week_offset
end_week = start_week - start_week_offset + end_week_offset


data = pd.DataFrame(columns=analyzer.DATA_COLUMNS)

for symbol in symbols:
    price = stocks.get_live_price(symbol)
    for week in range(start_week, end_week):
        # expiration_date = datetime.strptime('2023 ' + str(week) + ' 5', '%Y %W %w') # always on friday
        expiration_date = date.fromisocalendar(2023, week, 5)
        print("get data for " + symbol + " with Date: " + expiration_date.strftime('%d/%m/%Y')  + " / Timestamp: " + str(int(pd.Timestamp(expiration_date).timestamp())))

        more_data = analyzer.get_info(ticker = symbol, type = mode, expiration_date = expiration_date, price = price, filter = [min_calls, min_puts])
        data = pd.concat([data, more_data], ignore_index=True)

print('Time: ' + now.strftime('%d/%m/%Y, %H:%M:%S'))
print('Options: ')
print(data)
