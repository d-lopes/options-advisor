from datetime import date
from enum import Enum
import logging
import pandas as pd

from alive_progress import alive_bar

from src.utils.yahoo_fin_wrapper import YahooFinanceWrapper
from src.utils.highlighter import Highlighter
from src.utils.exp_date_extractor import ExpirationDateExtractor
from src.utils.dyn_value_calc import DynamicValueCalculator
from src.utils.opts_tbl_filter import OptionsTableFilter


class OptionsAnalyzer:

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
        CALLS_CNT = '# Open Interest (CALLs)'
        PUTS_CNT = '# Open Interest (PUTs)'
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
                    Fields.BID.value, Fields.ASK.value, Fields.CALLS_CNT.value, Fields.PUTS_CNT.value, Fields.VOLUME.value,
                    Fields.IMPLIED_VOLATILITY.value, Fields.TAGS.value]

    logger = logging.getLogger('optionsAnalyzer')

    @staticmethod
    def get_info(ticker: str, type: Types = Types.PUT, expiration_date: date = None,
                 price: float = 0, filter: OptionsTableFilter.FilterOptions = None, order_date: date = None):
        # get options
        try:
            all_options = YahooFinanceWrapper.get_options_chain(ticker, expiration_date)
        except ValueError as err:
            OptionsAnalyzer.logger.error(f"unable to retrieve data for symbol {ticker}: {err}")
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
        put_options = ede.process(put_options)
        call_options = ede.process(call_options)

        # link PUTs and CALLs based on their strike price and expiration date
        options = OptionsAnalyzer.link_puts_and_calls(type, put_options, call_options)

        # calculate dynamic values
        dvc = DynamicValueCalculator(ordinal=20, expiration_date=expiration_date, order_date=order_date, price=price)
        options = dvc.process(options)

        # filter for relevant data
        otf = OptionsTableFilter(ordinal=30, type=type, filter=filter)
        relevant_options = otf.process(options)

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

        merge_columns = [OptionsAnalyzer.Fields.STRIKE.value, OptionsAnalyzer.Fields.EXPIRATION_DATE.value]
        if (type == OptionsAnalyzer.Types.PUT):
            options = pd.merge(put_options, call_options, how="left", on=merge_columns, suffixes=("", "_merged"))
        elif (type == OptionsAnalyzer.Types.CALL):
            options = pd.merge(call_options, put_options, how="left", on=merge_columns, suffixes=("", "_merged"))
        else:
            raise ValueError(Exception(f"invalid type '{type}'"))

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
        options = options[pd.to_numeric(options[OptionsAnalyzer.Fields.VOLUME.value], errors='coerce').notnull()]

        # transform data types in columns
        options = options.astype({
            OptionsAnalyzer.Fields.PUTS_CNT.value: 'int',
            OptionsAnalyzer.Fields.CALLS_CNT.value: 'int',
            OptionsAnalyzer.Fields.VOLUME.value: 'int'
        })

        return options

    @staticmethod
    def get_options(symbols=('BAC',), mode: Types = Types.PUT, year: int = 2023,
                    start_week: int = 1, end_week: int = 1, filter: OptionsTableFilter.FilterOptions = None):

        data = pd.DataFrame(columns=OptionsAnalyzer.DATA_COLUMNS)

        total_steps = len(symbols) * (end_week - start_week)
        with alive_bar(total_steps) as bar:
            for symbol in symbols:
                try:
                    OptionsAnalyzer.logger.debug(f"loading data for {symbol} ...")
                    price = YahooFinanceWrapper.get_live_price(symbol)

                    # if filter is given, calculate threshold for price too high (when strike + 20%)
                    if (filter is not None):
                        price_too_high = price > filter.max_strike * 1.2
                    else:
                        price_too_high = False

                    # skip processing of underlying when live price is above acceptable value
                    if price_too_high:
                        OptionsAnalyzer.logger.warning(f"price of underlying {symbol} is too high. Skipping this symbol!")
                        bar(4, skipped=True)
                        continue

                except AssertionError:
                    OptionsAnalyzer.logger.error(f"unable to retrieve price for symbol {symbol}.")
                    bar(4, skipped=True)
                    continue
                except KeyError:
                    OptionsAnalyzer.logger.error(f"unable to retrieve price for symbol {symbol}.")
                    bar(4, skipped=True)
                    continue

                data = OptionsAnalyzer._get_options_internal(mode, year, start_week, end_week, filter, data, symbol, price,
                                                             bar)

        return data

    @staticmethod
    def _get_options_internal(mode, year, start_week, end_week, filter, data, symbol, price, bar):
        for week in range(start_week, end_week):
            expiration_date = date.fromisocalendar(year, week, 5)
            order_date = date.today()
            OptionsAnalyzer.logger.debug(f"get data for {symbol} with expiration date {expiration_date}")

            try:
                more_data = OptionsAnalyzer.get_info(symbol, mode, expiration_date, price, filter, order_date)
            except KeyError:
                OptionsAnalyzer.logger.error(f"unable to analyze data for symbol {symbol}. Continuing with next symbol!")
                bar(skipped=True)
                continue
            data = pd.concat([data, more_data], ignore_index=True)

            # update progress bar
            bar()

        # reindex for clean data frame
        data = data.reset_index(drop=True)

        return data
