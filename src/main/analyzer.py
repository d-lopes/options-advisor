from datetime import datetime, date, timedelta
from enum import Enum
import logging
import pandas as pd

from yahoo_fin import stock_info as stocks, options as opts

from src.main.utils.highlighter import Highlighter

# introduced to being able to mock out the actual calls to Yahoo Finance (done by yahoo_fin module)
class YahooFinanceWrapper:

    @staticmethod
    def get_options_chain(ticker, date = None, raw = True, headers = {'User-agent': 'Mozilla/5.0'}):
        return opts.get_options_chain(ticker=ticker, date=date, raw=raw, headers=headers)

class Analyzer:

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
            return Analyzer.Filter(min_puts = 1000, min_calls = 1000, min_yield = 10, max_strike  = 40)

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
            all_options = YahooFinanceWrapper.get_options_chain(ticker, expiration_date)
        except ValueError as err:
            Analyzer.logger.error('unable to retrieve data for symbol %s: %s', ticker, err)
            return pd.DataFrame(columns=Analyzer.DATA_COLUMNS)

        put_options = all_options['puts']
        call_options = all_options['calls']

        # guard: if no data is returned then stop processing
        if (put_options.empty & call_options.empty):
             return pd.DataFrame(columns=Analyzer.DATA_COLUMNS)

        # extract expiration dates
        put_options[Analyzer.Fields.EXPIRATION_DATE.value] = put_options[Analyzer.Fields.CONTRACT_NAME.value].transform(lambda name: Analyzer.exp_date_from_contract_name(name, ticker))
        call_options[Analyzer.Fields.EXPIRATION_DATE.value] = call_options[Analyzer.Fields.CONTRACT_NAME.value].transform(lambda name: Analyzer.exp_date_from_contract_name(name, ticker))

        # link PUTs and CALLs based on their strike price and expiration date
        if (type == Analyzer.Types.PUT):
            options = pd.merge(put_options, call_options, how="left", on=[Analyzer.Fields.STRIKE.value, Analyzer.Fields.EXPIRATION_DATE.value], suffixes=("", "_merged"))
        elif (type == Analyzer.Types.CALL):
            options = pd.merge(call_options, put_options, how="left", on=[Analyzer.Fields.STRIKE.value, Analyzer.Fields.EXPIRATION_DATE.value], suffixes=("", "_merged"))
        else:
            Analyzer.logger.error('unknown type %s', type)

        # cosmetic changes: name columns properly
        options = options.rename(columns={'Last Price': Analyzer.Fields.PREMIUM.value })
        if (type == Analyzer.Types.PUT):
            options[Analyzer.Fields.PUTS_CNT.value] = options[Analyzer.Fields.OPEN_INTEREST.value]
            options = options.rename(columns={Analyzer.Fields.OPEN_INTEREST.value + '_merged': Analyzer.Fields.CALLS_CNT.value })
        elif (type == Analyzer.Types.CALL):
            options[Analyzer.Fields.CALLS_CNT.value] = options[Analyzer.Fields.OPEN_INTEREST.value]
            options = options.rename(columns={Analyzer.Fields.OPEN_INTEREST.value + '_merged': Analyzer.Fields.PUTS_CNT.value })

        # get rid of invalid numeric values
        options = options[pd.to_numeric(options[Analyzer.Fields.PUTS_CNT.value], errors='coerce').notnull()]
        options = options[pd.to_numeric(options[Analyzer.Fields.CALLS_CNT.value], errors='coerce').notnull()]

        # transform data types in columns
        options = options.astype({Analyzer.Fields.PUTS_CNT.value:'int', Analyzer.Fields.CALLS_CNT.value:'int'})

        # calculate dynamic values
        options[Analyzer.Fields.DIFFERENCE.value] = price - options[Analyzer.Fields.STRIKE.value]
        options[Analyzer.Fields.DISTANCE.value] = options[Analyzer.Fields.DIFFERENCE.value] / price * 100

        transaction_cost = 2 * 3 / 100 # assumption 3 US$ per transaction (buy and sell of 100 shares)
        days_per_year = 365
        holding_period:timedelta = expiration_date - date.today()

        # yield = [ (premium - transaction costs) / strike ] / holding_period * 365 * 100
        options[Analyzer.Fields.YIELD.value] = (options[Analyzer.Fields.PREMIUM.value] - transaction_cost) / options[Analyzer.Fields.STRIKE.value] / holding_period.days * days_per_year * 100

        # filter for relevant data
        relevant_options = options.loc[
                            (options[Analyzer.Fields.PUTS_CNT.value] >= filter.min_puts) &
                            (options[Analyzer.Fields.CALLS_CNT.value] >= filter.min_calls) &
                            (options[Analyzer.Fields.YIELD.value] >= filter.min_yield) &
                            (options[Analyzer.Fields.STRIKE.value] <= filter.max_strike),
                        [Analyzer.Fields.CONTRACT_NAME.value, Analyzer.Fields.STRIKE.value, Analyzer.Fields.PREMIUM.value, Analyzer.Fields.BID.value, Analyzer.Fields.ASK.value,
                        Analyzer.Fields.VOLUME.value,Analyzer.Fields.OPEN_INTEREST.value, Analyzer.Fields.IMPLIED_VOLATILITY.value, Analyzer.Fields.EXPIRATION_DATE.value,
                        Analyzer.Fields.CALLS_CNT.value, Analyzer.Fields.PUTS_CNT.value, Analyzer.Fields.DIFFERENCE.value, Analyzer.Fields.DISTANCE.value, Analyzer.Fields.YIELD.value]]

        # add additional "static" values
        relevant_options[Analyzer.Fields.TICKER.value] = ticker
        relevant_options[Analyzer.Fields.TYPE.value] = type.value
        relevant_options[Analyzer.Fields.CURRENT_PRICE.value] = price

        # highlight aspects
        relevant_options[Analyzer.Fields.TAGS.value] = relevant_options.apply(Highlighter.determineTags, axis=1)

        return relevant_options[Analyzer.DATA_COLUMNS]