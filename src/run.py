import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from datetime import datetime, timedelta
import time
import humanize

from enum import Enum
import logging
import argparse
import json

from src.analyzer import OptionsAnalyzer
from src.ingest.yahoo_fin import YahooFinanceDataSource
from src.ingest.yoptions import YOptionDataSource
from src.utils.opts_tbl_filter import OptionsTableFilter
from src.utils.exp_date_generator import ExpiryDateGenerator

logger = logging.getLogger('main')
logging.basicConfig(level=logging.INFO, format='%(message)s')


class Format(Enum):
    CSV = 'CSV'
    XLSX = 'XLSX'


if __name__ == '__main__':

    # Start timer
    start_time = time.time()

    parser = argparse.ArgumentParser(description='gathers data about stock options')
    parser.add_argument('-i', dest='input_file', help='an input file defining the settings to scan for options',
                        type=str, required=True)
    parser.add_argument('-ds', dest='datasource', help='yahoofin (default) or yoptions', type=str, 
                        default='yahoofin')
    parser.add_argument('-mode', dest='mode', help='PUT (default) or CALL', type=OptionsAnalyzer.Types, 
                        default=OptionsAnalyzer.Types.PUT)
    parser.add_argument('-ms', dest='max_strike', help='filter for maximum acceptable strike (Default = 60)',
                        type=float, default=60)
    parser.add_argument('-mp', dest='min_puts', help='filter for minium available interest in PUTs (Default = 1000)',
                        type=int, default=1000)
    parser.add_argument('-mc', dest='min_calls', help='filter for minium available interest in CALLs (Default = 1000)',
                        type=int, default=1000)
    parser.add_argument('-mv', dest='min_volume', help='filter for minium available volume (Default = 100)',
                        type=int, default=100)
    parser.add_argument('-my', dest='min_yield', help='filter for minimum acceptable yield (Default = 10)',
                        type=float, default=10)
    parser.add_argument('-mn', dest='moneyness', help='filter for the moneyness: OTM (default), ITM or ATM',
                        type=OptionsTableFilter.Moneyness, default=OptionsTableFilter.Moneyness.OUT)
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
    current_week = now.strftime("%W")
    current_year = now.year
    start_week = int(current_week) + args.start_week_offset
    start_year = current_year
    end_week = start_week - args.start_week_offset + args.end_week_offset
    
    # fix possible overflow at the end of the year 
    if start_week > 52:
        start_week = start_week - 52
        start_year = current_year + 1
    if end_week > 52:
        end_week = end_week - 52
        end_year = current_year + 1
    else:
        end_year = current_year

    print("\n")
    logger.info(f"searching for {args.mode.value} options between calendar weeks {start_week}/{start_year} - {end_week}/{end_year}")

    # Opening input file in JSON format to retrieve the watchlist
    with open(args.input_file) as file:
        file_data = json.load(file)
        symbols = file_data['watchlist']
        count = len(symbols)

    filter = OptionsTableFilter.FilterOptions(min_puts=args.min_puts, min_calls=args.min_calls, min_volume=args.min_volume,
                                              min_yield=args.min_yield, max_strike=args.max_strike, moneyness=args.moneyness)

    datasource = YahooFinanceDataSource()
    if (args.datasource == 'yoptions'):
        datasource = YOptionDataSource()
    analyzer = OptionsAnalyzer(datasource)
    expiry_dates = ExpiryDateGenerator.getDates(start_week_offset=args.start_week_offset,
                                                end_week_offset=args.end_week_offset)
    data = analyzer.get_options(symbols, args.mode, expiry_dates, filter)
    rows = len(data.index)

    # End timer and calculate elapsed time
    end_time = time.time()
    elapsed_time: timedelta = end_time - start_time

    print("\n-------- SUMMARY ---------")
    logger.info(f"finished run on: {now.strftime('%d/%m/%Y, %H:%M:%S')}")
    logger.info(f"started scan at: {humanize.naturaltime(elapsed_time)} (took {elapsed_time:.2f} seconds overall)")
    logger.info(f"scanned {count} underlyings: {symbols}")
    logger.info(f"applied filter: {filter}")
    logger.info(f"found options: {rows}")

    # write results to disk
    if ((args.output_path is not None) & (rows > 0)):
        format: Format = args.output_format
        if (Format.XLSX == format):
            data.to_excel(args.output_path)
        else:
            data.to_csv(args.output_path)
        logger.info(f"results written to disk: {args.output_path}")
    else:
        logger.info("results:")
        print("\n")
        print(data)

    print("\n")
