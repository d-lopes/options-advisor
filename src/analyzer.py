from datetime import datetime, date, timedelta
from enum import Enum
import logging
import pandas as pd

from yahoo_fin import stock_info as stocks, options as opts

from utils.highlighter import highlighter

class analyzer:

    class Filter:
        min_puts = None
        min_calls = None
        min_yield = None
        max_strike = None

        def __init__(self, min_puts = 0, min_calls = 0, min_yield = 0, max_strike  = 1000):
            self.min_puts = min_puts
            self.min_calls = min_calls
            self.min_yield = min_yield
            self.max_strike = max_strike

        @staticmethod
        def getDefaults():
            return analyzer.Filter(min_puts = 1000, min_calls = 1000, min_yield = 10, max_strike  = 40)

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
        ### additional fields (provided by yahoo_fin)
        VOLUME = 'Volume'
        CONTRACT_NAME = 'Contract Name'

    class Types(Enum):
        PUT = 'PUT'
        CALL = 'CALL'

    DATA_COLUMNS=[Fields.TICKER.value, Fields.TYPE.value, Fields.EXPIRATION_DATE.value, Fields.STRIKE.value, Fields.YIELD.value, Fields.CURRENT_PRICE.value,
                    Fields.DISTANCE.value, Fields.PREMIUM.value, Fields.BID.value, Fields.ASK.value, Fields.CALLS_CNT.value, Fields.PUTS_CNT.value,
                    Fields.IMPLIED_VOLATILITY.value, Fields.TAGS.value]

    logger = logging.getLogger('analyzer')

    @staticmethod
    def exp_date_from_contract_name(name:str, prefix:str):
        size = len(name)
        ticker_date_portion = name[:size-9]
        date_str = '20' + ticker_date_portion.replace(prefix, '', 1)
        return datetime.strptime(date_str, '%Y%m%d')

    @staticmethod
    def get_info(ticker: str, type: Types = Types.PUT, expiration_date: date = None, price:float = 0, filter:Filter = None):

        # get options
        options = pd.DataFrame()
        try:
            all_options = opts.get_options_chain(ticker, expiration_date)
        except ValueError as err:
            analyzer.logger.error('unable to retrieve data for symbol %s: %s', ticker, err)
            return pd.DataFrame(columns=analyzer.DATA_COLUMNS)

        put_options = all_options['puts']
        call_options = all_options['calls']

        # extract expiration dates
        put_options[analyzer.Fields.EXPIRATION_DATE.value] = put_options[analyzer.Fields.CONTRACT_NAME.value].transform(lambda name: analyzer.exp_date_from_contract_name(name, ticker))
        call_options[analyzer.Fields.EXPIRATION_DATE.value] = call_options[analyzer.Fields.CONTRACT_NAME.value].transform(lambda name: analyzer.exp_date_from_contract_name(name, ticker))

        # link PUTs and CALLs based on their strike price and expiration date
        if (type == analyzer.Types.PUT):
            options = pd.merge(put_options, call_options, how="left", on=[analyzer.Fields.STRIKE.value, analyzer.Fields.EXPIRATION_DATE.value], suffixes=("", "_merged"))
        elif (type == analyzer.Types.CALL):
            options = pd.merge(call_options, put_options, how="left", on=[analyzer.Fields.STRIKE.value, analyzer.Fields.EXPIRATION_DATE.value], suffixes=("", "_merged"))
        else:
            analyzer.logger.error('unknown type %s', type)

        # cosmetic changes: name columns properly
        options = options.rename(columns={'Last Price': analyzer.Fields.PREMIUM.value })
        if (type == analyzer.Types.PUT):
            options[analyzer.Fields.PUTS_CNT.value] = options[analyzer.Fields.OPEN_INTEREST.value]
            options = options.rename(columns={analyzer.Fields.OPEN_INTEREST.value + '_merged': analyzer.Fields.CALLS_CNT.value })
        elif (type == analyzer.Types.CALL):
            options[analyzer.Fields.CALLS_CNT.value] = options[analyzer.Fields.OPEN_INTEREST.value]
            options = options.rename(columns={analyzer.Fields.OPEN_INTEREST.value + '_merged': analyzer.Fields.PUTS_CNT.value })

        # get rid of invalid numeric values
        options = options[pd.to_numeric(options[analyzer.Fields.PUTS_CNT.value], errors='coerce').notnull()]
        options = options[pd.to_numeric(options[analyzer.Fields.CALLS_CNT.value], errors='coerce').notnull()]

        # transform data types in columns
        options = options.astype({analyzer.Fields.PUTS_CNT.value:'int', analyzer.Fields.CALLS_CNT.value:'int'})

        # calculate dynamic values
        options[analyzer.Fields.DIFFERENCE.value] = price - options[analyzer.Fields.STRIKE.value]
        options[analyzer.Fields.DISTANCE.value] = options[analyzer.Fields.DIFFERENCE.value] / price * 100

        transaction_cost = 2 * 3 / 100 # assumption 3 US$ per transaction (buy and sell of 100 shares)
        days_per_year = 365
        holding_period:timedelta = expiration_date - date.today()

        # yield = [ (premium - transaction costs) / strike ] / holding_period * 365 * 100
        options[analyzer.Fields.YIELD.value] = (options[analyzer.Fields.PREMIUM.value] - transaction_cost) / options[analyzer.Fields.STRIKE.value] / holding_period.days * days_per_year * 100

        # filter for relevant data
        relevant_options = options.loc[
                            (options[analyzer.Fields.PUTS_CNT.value] >= filter.min_puts) &
                            (options[analyzer.Fields.CALLS_CNT.value] >= filter.min_calls) &
                            (options[analyzer.Fields.YIELD.value] >= filter.min_yield) &
                            (options[analyzer.Fields.STRIKE.value] <= filter.max_strike),
                        [analyzer.Fields.CONTRACT_NAME.value, analyzer.Fields.STRIKE.value, analyzer.Fields.PREMIUM.value, analyzer.Fields.BID.value, analyzer.Fields.ASK.value,
                        analyzer.Fields.VOLUME.value,analyzer.Fields.OPEN_INTEREST.value, analyzer.Fields.IMPLIED_VOLATILITY.value, analyzer.Fields.EXPIRATION_DATE.value,
                        analyzer.Fields.CALLS_CNT.value, analyzer.Fields.PUTS_CNT.value, analyzer.Fields.DIFFERENCE.value, analyzer.Fields.DISTANCE.value, analyzer.Fields.YIELD.value]]

        # add additional "static" values
        relevant_options[analyzer.Fields.TICKER.value] = ticker
        relevant_options[analyzer.Fields.TYPE.value] = type.value
        relevant_options[analyzer.Fields.CURRENT_PRICE.value] = price

        # highlight aspects
        relevant_options[analyzer.Fields.TAGS.value] = relevant_options.apply(highlighter.determineTags, axis=1)

        return relevant_options[analyzer.DATA_COLUMNS]