from datetime import datetime
import logging
import argparse

from src.analyzer import OptionsAnalyzer as Analyzer

# only NYSE listed stocks are possible
# BEPC and LPX caused issues. thus they were removed from the list of symbols below
symbols = ['CVX', 'AMZN', 'NKE', 'TSM', 'LPX', 'OXY', 'KR', 'KHC', 'BAC', 'ALLY', 'PARA', 'STNE', 'PFE', 'CSX']
logger = logging.getLogger('main')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='gathers data about stock options')
    parser.add_argument('-mode', dest='mode', help='PUT or CALL', type=Analyzer.Types, default=Analyzer.Types.PUT)
    parser.add_argument('-strike', dest='max_strike', help='filter for maximum acceptable strike', type=float, default=60)
    parser.add_argument('-mp', dest='min_puts', help='filter for minium available puts', type=int, default=1000)
    parser.add_argument('-mc', dest='min_calls', help='filter for minium available calls', type=int, default=1000)
    parser.add_argument('-my', dest='min_yield', help='filter for minimum acceptable yield', type=float, default=10)
    parser.add_argument('-swo', dest='start_week_offset', help='Offset from current week to start searching for expiry dates',
                        type=int, default=3)
    parser.add_argument('-ewo', dest='end_week_offset', help='Offset from current week to end searching for expiry dates',
                        type=int, default=7)
    args = parser.parse_args()

    # determine investing period
    now = datetime.now()    # current date and time
    start_week = now.isocalendar().week + args.start_week_offset
    end_week = start_week - args.start_week_offset + args.end_week_offset

    filter = Analyzer.Filter(args.min_puts, args.min_calls, args.min_yield, args.max_strike)
    data = Analyzer.get_options(symbols, args.mode, 2023, start_week, end_week, filter)

    print(f"\n\nTime: {now.strftime('%d/%m/%Y, %H:%M:%S')}\n")
    print(f"applied Filter: {filter}\n")
    print("found Opportunities:\n")
    print(data)
