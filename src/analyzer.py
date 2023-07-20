from datetime import datetime, date
import pandas as pd
from yahoo_fin import stock_info as stocks, options as opts
from enum import Enum

from utils.highlighter import highlighter

class analyzer:

    class Fields(Enum):
        TICKER = 'Ticker'
        TYPE = 'Type'
        EXPIRATION_DATE = 'Exp. Date'
        STRIKE = 'Strike'
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

    DATA_COLUMNS=[Fields.TICKER.value, Fields.TYPE.value, Fields.EXPIRATION_DATE.value, Fields.STRIKE.value, Fields.CURRENT_PRICE.value, Fields.DISTANCE.value, 
                  Fields.PREMIUM.value, Fields.BID.value, Fields.ASK.value, Fields.CALLS_CNT.value, Fields.PUTS_CNT.value, Fields.IMPLIED_VOLATILITY.value, 
                  Fields.TAGS.value]

    @staticmethod
    def exp_date_from_contract_name(name, prefix):
        size = len(name)
        ticker_date_portion = name[:size-9]
        date_str = '20' + ticker_date_portion.replace(prefix, '', 1)
        return datetime.strptime(date_str, '%Y%m%d')

    @staticmethod
    def get_info(ticker, type = Types.PUT, expiration_date = None, price = 0, filter = [0,0]):

        # get options
        options = pd.DataFrame()
        all_options = opts.get_options_chain(ticker, expiration_date)
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
            print("ERROR: unknown type " + type + "!")

        # cosmetic changes: name columns properly
        options = options.rename(columns={'Last Price': analyzer.Fields.PREMIUM.value })
        if (type == analyzer.Types.PUT):
            options[analyzer.Fields.PUTS_CNT.value] = options[analyzer.Fields.OPEN_INTEREST.value]
            options = options.rename(columns={analyzer.Fields.OPEN_INTEREST.value + '_merged': analyzer.Fields.CALLS_CNT.value })
        elif (type == analyzer.Types.CALL):
            options[analyzer.Fields.CALLS_CNT.value] = options[analyzer.Fields.OPEN_INTEREST.value]
            options = options.rename(columns={analyzer.Fields.OPEN_INTEREST.value + '_merged': analyzer.Fields.PUTS_CNT.value })

        #print(options)

        # get rid of invalid numeric values
        options = options[pd.to_numeric(options[analyzer.Fields.PUTS_CNT.value], errors='coerce').notnull()]
        options = options[pd.to_numeric(options[analyzer.Fields.CALLS_CNT.value], errors='coerce').notnull()]

        # transform data types in columns
        options = options.astype({analyzer.Fields.PUTS_CNT.value:'int', analyzer.Fields.CALLS_CNT.value:'int'})

        # filter for relevant data
        relevant_options = options.loc[(options[analyzer.Fields.PUTS_CNT.value] >= filter[0]) & (options[analyzer.Fields.CALLS_CNT.value] >= filter[1]),
                        [analyzer.Fields.CONTRACT_NAME.value, analyzer.Fields.STRIKE.value, analyzer.Fields.PREMIUM.value, analyzer.Fields.BID.value, analyzer.Fields.ASK.value,
                        analyzer.Fields.VOLUME.value,analyzer.Fields.OPEN_INTEREST.value, analyzer.Fields.IMPLIED_VOLATILITY.value, analyzer.Fields.EXPIRATION_DATE.value,
                        analyzer.Fields.CALLS_CNT.value, analyzer.Fields.PUTS_CNT.value]]

        # add additional an calculated values
        relevant_options[analyzer.Fields.TICKER.value] = ticker
        relevant_options[analyzer.Fields.TYPE.value] = type.value
        relevant_options[analyzer.Fields.CURRENT_PRICE.value] = price
        relevant_options[analyzer.Fields.DIFFERENCE.value] = relevant_options[analyzer.Fields.CURRENT_PRICE.value] - relevant_options[analyzer.Fields.STRIKE.value]
        relevant_options[analyzer.Fields.DISTANCE.value] = relevant_options[analyzer.Fields.DIFFERENCE.value] / relevant_options[analyzer.Fields.CURRENT_PRICE.value] * 100

        # highlight aspects
        relevant_options[analyzer.Fields.TAGS.value] = relevant_options.apply(highlighter.determine, axis=1)

        return relevant_options[analyzer.DATA_COLUMNS]