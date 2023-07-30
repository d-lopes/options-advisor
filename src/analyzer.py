from datetime import date
from enum import Enum
import logging
import pandas as pd

from src.utils.yahoo_fin_wrapper import YahooFinanceWrapper
from src.utils.highlighter import Highlighter
from src.utils.exp_date_extractor import ExpirationDateExtractor
from src.utils.dyn_value_calc import DynamicValueCalculator


class OptionsAnalyzer:

    class Filter:
        min_puts = None
        min_calls = None
        min_yield = None
        max_strike = None

        def __init__(self, min_puts=0, min_calls=0, min_yield=0, max_strike=1000):
            self.min_puts = min_puts
            self.min_calls = min_calls
            self.min_yield = min_yield
            self.max_strike = max_strike

        @staticmethod
        def getDefaults():
            return OptionsAnalyzer.Filter(min_puts=1000, min_calls=1000, min_yield=10, max_strike=100000)

    class Fields(Enum):
        TICKER = 'Ticker'
        TYPE = 'Type'
        EXPIRATION_DATE = 'Exp. Date'
        STRIKE = 'Strike'
        YIELD = 'Yield (p. a.)'
        CURRENT_PRICE = 'Current Price'
        DIFFERENCE = 'Difference'
        DISTANCE = 'Distance (%)'
        PREMIUM = 'Premium'
        BID = 'Bid'
        ASK = 'Ask'
        OPEN_INTEREST = 'Open Interest'
        CALLS_CNT = '# Open CALLs'
        PUTS_CNT = '# Open PUTs'
        IMPLIED_VOLATILITY = 'Implied Volatility'
        TAGS = 'Tags'
        # additional fields (provided by yahoo_fin)
        VOLUME = 'Volume'
        CONTRACT_NAME = 'Contract Name'

    class Types(Enum):
        PUT = 'PUT'
        CALL = 'CALL'

    DATA_COLUMNS = [Fields.TICKER.value, Fields.TYPE.value, Fields.EXPIRATION_DATE.value, Fields.STRIKE.value,
                    Fields.YIELD.value, Fields.CURRENT_PRICE.value, Fields.DISTANCE.value, Fields.PREMIUM.value,
                    Fields.BID.value, Fields.ASK.value, Fields.CALLS_CNT.value, Fields.PUTS_CNT.value,
                    Fields.IMPLIED_VOLATILITY.value, Fields.TAGS.value]

    logger = logging.getLogger('optionsAnalyzer')

    @staticmethod
    def get_info(ticker: str, type: Types = Types.PUT, expiration_date: date = None,
                 price: float = 0, filter: Filter = None, order_date: date = None):
        # get options
        try:
            all_options = YahooFinanceWrapper.get_options_chain(ticker, expiration_date)
        except ValueError as err:
            OptionsAnalyzer.logger.error('unable to retrieve data for symbol %s: %s', ticker, err)
            return pd.DataFrame(columns=OptionsAnalyzer.DATA_COLUMNS)

        put_options = all_options['puts']
        call_options = all_options['calls']

        # guard: if no data is returned then stop processing
        if (put_options.empty & call_options.empty):
            return pd.DataFrame(columns=OptionsAnalyzer.DATA_COLUMNS)

        # extract expiration dates
        col_name1 = OptionsAnalyzer.Fields.CONTRACT_NAME.value
        col_name2 = OptionsAnalyzer.Fields.EXPIRATION_DATE.value
        ede = ExpirationDateExtractor(ordinal=10, ticker=ticker, source=col_name1, target=col_name2)
        ede.process(put_options)
        ede.process(call_options)

        # link PUTs and CALLs based on their strike price and expiration date
        options = OptionsAnalyzer.link_puts_and_calls(type, put_options, call_options)

        # calculate dynamic values
        dvc = DynamicValueCalculator(ordinal=20, expiration_date=expiration_date, order_date=order_date, price=price)
        dvc.process(options)

        # filter for relevant data
        relevant_options = options.loc[
                            (options[OptionsAnalyzer.Fields.PUTS_CNT.value] >= filter.min_puts) &
                            (options[OptionsAnalyzer.Fields.CALLS_CNT.value] >= filter.min_calls) &
                            (options[OptionsAnalyzer.Fields.YIELD.value] >= filter.min_yield) &
                            (options[OptionsAnalyzer.Fields.STRIKE.value] <= filter.max_strike),
                            [OptionsAnalyzer.Fields.CONTRACT_NAME.value, OptionsAnalyzer.Fields.STRIKE.value,
                             OptionsAnalyzer.Fields.PREMIUM.value, OptionsAnalyzer.Fields.BID.value,
                             OptionsAnalyzer.Fields.ASK.value, OptionsAnalyzer.Fields.VOLUME.value,
                             OptionsAnalyzer.Fields.OPEN_INTEREST.value, OptionsAnalyzer.Fields.IMPLIED_VOLATILITY.value,
                             OptionsAnalyzer.Fields.EXPIRATION_DATE.value, OptionsAnalyzer.Fields.CALLS_CNT.value,
                             OptionsAnalyzer.Fields.PUTS_CNT.value, OptionsAnalyzer.Fields.DIFFERENCE.value,
                             OptionsAnalyzer.Fields.DISTANCE.value, OptionsAnalyzer.Fields.YIELD.value]]

        # add additional "static" values
        relevant_options[OptionsAnalyzer.Fields.TICKER.value] = ticker
        relevant_options[OptionsAnalyzer.Fields.TYPE.value] = type.value
        relevant_options[OptionsAnalyzer.Fields.CURRENT_PRICE.value] = price

        # highlight aspects
        relevant_options[OptionsAnalyzer.Fields.TAGS.value] = relevant_options.apply(Highlighter.determine_tags, axis=1)

        # reindex or clean data frame
        relevant_options = relevant_options.reset_index(drop=True)

        return relevant_options[OptionsAnalyzer.DATA_COLUMNS]

    @staticmethod
    def link_puts_and_calls(type, put_options, call_options):
        options = pd.DataFrame()

        merge_columns = [OptionsAnalyzer.Fields.STRIKE.value, OptionsAnalyzer.Fields.EXPIRATION_DATE.value]
        if (type == OptionsAnalyzer.Types.PUT):
            options = pd.merge(put_options, call_options, how="left", on=merge_columns, suffixes=("", "_merged"))
        elif (type == OptionsAnalyzer.Types.CALL):
            options = pd.merge(call_options, put_options, how="left", on=merge_columns, suffixes=("", "_merged"))
        else:
            raise ValueError(Exception('invalid type "' + type + '"'))

        # cosmetic changes: name columns properly
        options = options.rename(columns={'Last Price': OptionsAnalyzer.Fields.PREMIUM.value})
        open_interest_orig_column_name = OptionsAnalyzer.Fields.OPEN_INTEREST.value + '_merged'
        if (type == OptionsAnalyzer.Types.PUT):
            options[OptionsAnalyzer.Fields.PUTS_CNT.value] = options[OptionsAnalyzer.Fields.OPEN_INTEREST.value]
            options = options.rename(columns={open_interest_orig_column_name: OptionsAnalyzer.Fields.CALLS_CNT.value})
        elif (type == OptionsAnalyzer.Types.CALL):
            options[OptionsAnalyzer.Fields.CALLS_CNT.value] = options[OptionsAnalyzer.Fields.OPEN_INTEREST.value]
            options = options.rename(columns={open_interest_orig_column_name: OptionsAnalyzer.Fields.PUTS_CNT.value})

        # get rid of invalid numeric values
        options = options[pd.to_numeric(options[OptionsAnalyzer.Fields.PUTS_CNT.value], errors='coerce').notnull()]
        options = options[pd.to_numeric(options[OptionsAnalyzer.Fields.CALLS_CNT.value], errors='coerce').notnull()]

        # transform data types in columns
        options = options.astype({OptionsAnalyzer.Fields.PUTS_CNT.value: 'int', OptionsAnalyzer.Fields.CALLS_CNT.value: 'int'})
        return options

    @staticmethod
    def get_options(symbols=('BAC',), mode: Types = Types.PUT, year: int = 2023,
                    start_week: int = 1, end_week: int = 1, filter: Filter = None):

        data = pd.DataFrame(columns=OptionsAnalyzer.DATA_COLUMNS)

        for symbol in symbols:
            try:
                price = YahooFinanceWrapper.get_live_price(symbol)

                # if filter is given, calculate threshold for price too high (when strike + 20%)
                if (filter is not None):
                    priceTooHigh = price > filter.max_strike * 1.2
                else:
                    priceTooHigh = False

                # skip processing of underlying when live price is above acceptable value
                if (priceTooHigh):
                    OptionsAnalyzer.logger.warning('price of underlying %s is too high. Skipping this symbol!', symbol)
                    continue

            except AssertionError:
                OptionsAnalyzer.logger.error('unable to retrieve price for symbol %s.', symbol)
                continue

            data = OptionsAnalyzer._get_options_internal(mode, year, start_week, end_week, filter, data, symbol, price)

        return data

    @staticmethod
    def _get_options_internal(mode, year, start_week, end_week, filter, data, symbol, price):
        for week in range(start_week, end_week):
            expiration_date = date.fromisocalendar(year, week, 5)
            order_date = date.today()
            OptionsAnalyzer.logger.info("get data for %s with expiration date %d", symbol, expiration_date)

            try:
                more_data = OptionsAnalyzer.get_info(symbol, mode, expiration_date, price, filter, order_date)
            except KeyError:
                OptionsAnalyzer.logger.error('unable to analyze data for symbol %s. Continuing with next symbol!', symbol)
                continue
            data = pd.concat([data, more_data], ignore_index=True)

        # reindex for clean data frame
        data = data.reset_index(drop=True)

        return data
