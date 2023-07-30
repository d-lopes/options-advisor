from datetime import datetime
import logging

from src.analyzer import OptionsAnalyzer as Analyzer

# only NYSE listed stocks are possible
# BEPC and LPX caused issues. thus they were removed from the list of symbols below
symbols = ['CVX', 'AMZN', 'NKE', 'TSM', 'LPX', 'OXY', 'KR', 'KHC', 'BAC', 'ALLY', 'PARA', 'STNE', 'PFE', 'CSX']

mode = Analyzer.Types.PUT
default_filter = Analyzer.Filter.getDefaults()
default_filter.max_strike = 40
start_week_offset = 3
end_week_offset = start_week_offset + 4

# get possible expiration dates between start and end date
now = datetime.now()    # current date and time
start_week = now.isocalendar().week + start_week_offset
end_week = start_week - start_week_offset + end_week_offset
logger = logging.getLogger('main')

if __name__ == '__main__':
    data = Analyzer.get_options(symbols, mode, 2023, start_week, end_week, default_filter)

    print('Time: ' + now.strftime('%d/%m/%Y, %H:%M:%S'))
    print('Options: ')
    print(data)
