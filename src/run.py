from datetime import datetime
from enum import Enum
import logging
import argparse
import json

from IPython.display import display

from src.analyzer import OptionsAnalyzer as Analyzer
from src.utils.filter_opts import FilterOptions

logger = logging.getLogger('main')
logging.basicConfig()
logger.setLevel(logging.INFO)


class Format(Enum):
    CSV = 'CSV'
    XLSX = 'XLSX'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='gathers data about stock options')
    parser.add_argument('-i', dest='input_file', help='an input file defining the settings to scan for options',
                        type=str, required=True)
    parser.add_argument('-mode', dest='mode', help='PUT (default) or CALL', type=Analyzer.Types, default=Analyzer.Types.PUT)
    parser.add_argument('-ms', dest='max_strike', help='filter for maximum acceptable strike (Default = 60)',
                        type=float, default=60)
    parser.add_argument('-mp', dest='min_puts', help='filter for minium available puts (Default = 1000)',
                        type=int, default=1000)
    parser.add_argument('-mc', dest='min_calls', help='filter for minium available calls (Default = 1000)',
                        type=int, default=1000)
    parser.add_argument('-my', dest='min_yield', help='filter for minimum acceptable yield (Default = 10)',
                        type=float, default=10)
    parser.add_argument('-swo', dest='start_week_offset', help='offset from current week to start searching for ' +
                        'expiry dates (Default = 3)', type=int, default=3)
    parser.add_argument('-ewo', dest='end_week_offset', help='offset from current week to end searching for ' +
                        'expiry dates (Default = 7)', type=int, default=7)
    parser.add_argument('-o', dest='output_path', help='destination to write the result to. ' +
                        'If empty, then no data is written to disk. Instead it is printed on screen (Default = None)',
                        type=str, default=None)
    parser.add_argument('-f', dest='output_format', help='CSV (default) or XLSX (requires python module openpyxl)',
                        type=Format, default=Format.CSV)
    args = parser.parse_args()

    # determine investing period
    now = datetime.now()    # current date and time
    start_week = now.isocalendar().week + args.start_week_offset
    end_week = start_week - args.start_week_offset + args.end_week_offset

    # Opening input file in JSON format to retrieve the watchlist
    with open(args.input_file) as file:
        file_data = json.load(file)
        symbols = file_data['watchlist']

    filter = FilterOptions(args.min_puts, args.min_calls, args.min_yield, args.max_strike)
    data = Analyzer.get_options(symbols, args.mode, 2023, start_week, end_week, filter)
    rows = data.__len__()

    print("\n")
    logger.info(f"- Time: {now.strftime('%d/%m/%Y, %H:%M:%S')}")
    logger.info(f"- scanned underlyings: {symbols}")
    logger.info(f"- applied Filter: {filter}")
    logger.info(f"- found: {rows}")

    # write results to disk
    if ((args.output_path is not None) & (rows > 0)):
        format: Format = args.output_format
        if (Format.XLSX == format):
            data.to_excel(args.output_path)
        else:
            data.to_csv(args.output_path)
        logger.info(f"- results written to disk: {args.output_path}")
    else:
        logger.info("- Results:")
        print("\n")
        display(data)

    print("\n")
