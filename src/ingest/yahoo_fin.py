import types
from datetime import date
from enum import Enum
import logging

from src.ingest.datasource import AbstractDataSource as datasource

from yahoo_fin import stock_info as stocks, options as opts

import pandas as pd

class YahooFinanceDataSource(datasource):

    NO_PUTS_INDICATOR = "There are no puts."
    NO_CALLS_INDICATOR = "There are no calls."

    put_options = None
    call_options = None

    logger = logging.getLogger('yahooFinanceDataSource')


    def __init__(self):
        datasource.__init__(self)
        

    def loadData(self, ticker: str = None, date: date = None):
    
        # reset internal store    
        self.put_options = pd.DataFrame(columns=datasource.DATA_FIELDS)
        self.call_options = pd.DataFrame(columns=datasource.DATA_FIELDS)

        # get options
        try:
            all_options = opts.get_options_chain(ticker=ticker, date=date, raw=True, headers=types.MappingProxyType({'User-agent': 'Mozilla/5.0'}))
        except ValueError as err:
            self.logger.error(f"unable to retrieve data for symbol {ticker}: {err}")
            return pd.DataFrame(columns=datasource.DATA_FIELDS)

        # guard: if no data for PUTs is returned then don't update internal store
        if (not all_options['puts'].empty):
            self.put_options = all_options['puts']
            # unfortunately, yahoo_fin does output that there are no calls in text form instead of an empty dataframe
            # here we are trying to fix this behaviour
            if (self.NO_PUTS_INDICATOR in self.put_options.values):
                self.put_options = pd.DataFrame(columns=datasource.DATA_FIELDS)
            

        # guard: if no data for CALLs is returned then don't update internal store
        if (not all_options['calls'].empty):
            self.call_options = all_options['calls']
            # unfortunately, yahoo_fin does output that there are no calls in text form instead of an empty dataframe
            # here we are trying to fix this behaviour
            if (self.NO_CALLS_INDICATOR in self.call_options.values):
                self.call_options = pd.DataFrame(columns=datasource.DATA_FIELDS)

    def getData(self, type: datasource.OptionTypes = datasource.OptionTypes.PUT):

        if (type == datasource.OptionTypes.PUT):
            return self.put_options

        if (type == datasource.OptionTypes.CALL):
            return self.call_options
            
        return pd.DataFrame(columns=datasource.DATA_FIELDS)
    
    
    def getLivePrice(self, ticker):
        return stocks.get_live_price(ticker=ticker)
