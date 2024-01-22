from src.ingest.datasource import AbstractDataSource as datasource
from datetime import date
import logging

import yoptions as yo

import pandas as pd

class YOptionsDataSource(datasource):

    DLFT_TICKER_SUFFIX = "99999999C000000"
    EMPTY_VALUE = pd.DataFrame(columns=datasource.DATA_FIELDS) 

    put_options = None
    call_options = None

    logger = logging.getLogger('yoptionsDataSource')

    def __init__(self):
        datasource.__init__(self)
    
        
    def loadData(self, ticker, date=None):
        
        # reset internal store    
        self.put_options = self.EMPTY_VALUE
        self.call_options = self.EMPTY_VALUE

        # get options
        try:
            self.put_options = yo.get_plain_chain_date(option_ticker=ticker, option_type='p', expiration_date=date)
            self.call_options = yo.get_plain_chain_date(option_ticker=ticker, option_type='c', expiration_date=date)
        except ValueError as err:
            self.logger.error(f"unable to retrieve data for symbol {ticker}: {err}")


    def getData(self, type: datasource.OptionTypes = datasource.OptionTypes.PUT):

        if (type == datasource.OptionTypes.PUT):
            return self.put_options

        if (type == datasource.OptionTypes.CALL):
            return self.call_options
            
        return self.EMPTY_VALUE
        
        
    def getLivePrice(self, ticker):

        # implementation of yoptions requires a digit to mark the end of the ticker symbol
        input_ticker = f"{ticker}{self.DLFT_TICKER_SUFFIX}" 
        
        return yo.get_underlying_price(option_ticker=input_ticker)
