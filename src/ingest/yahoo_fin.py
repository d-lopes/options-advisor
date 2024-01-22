import types
from datetime import date
from enum import Enum
import logging

from src.ingest.datasource import AbstractDataSource as datasource

from yahoo_fin import stock_info as stocks, options as opts

import pandas as pd

class YahooFinanceDataSource(datasource):

    EMPTY_VALUE = pd.DataFrame(columns=datasource.DATA_FIELDS) 

    put_options = None
    call_options = None

    logger = logging.getLogger('yahooFinanceDataSource')


    def __init__(self):
        datasource.__init__(self)
        

    def loadData(self, ticker: str = None, date: date = None):
    
        # reset internal store    
        self.put_options = self.EMPTY_VALUE
        self.call_options = self.EMPTY_VALUE

        # get options
        try:
            all_options = opts.get_options_chain(ticker=ticker, date=date, raw=True, headers=types.MappingProxyType({'User-agent': 'Mozilla/5.0'}))
        except ValueError as err:
            self.logger.error(f"unable to retrieve data for symbol {ticker}: {err}")
            return self.EMPTY_VALUE

        # guard: if no data for PUTs is returned then don't update internal store
        if (not all_options['puts'].empty):
            self.put_options = all_options['puts']

        # guard: if no data for CALLs is returned then don't update internal store
        if (not all_options['calls'].empty):
            self.call_options = all_options['calls']


    def getData(self, type: datasource.OptionTypes = datasource.OptionTypes.PUT):

        if (type == datasource.OptionTypes.PUT):
            return self.put_options

        if (type == datasource.OptionTypes.CALL):
            return self.call_options
            
        return self.EMPTY_VALUE
    
    
    def getLivePrice(self, ticker):
        return stocks.get_live_price(ticker=ticker)
