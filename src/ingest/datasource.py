from enum import Enum

class AbstractDataSource:
    
    class OptionTypes(Enum):
        PUT = 'PUT'
        CALL = 'CALL'
    
    class Fields(Enum):
        CONTRACT_NAME = 'Contract Name'
        LAST_TRADE_DATE = 'Last Trade Date (EDT)'
        STRIKE = 'Strike'
        LAST_PRICE = 'Last Price'
        BID = 'Bid'
        ASK = 'Ask'
        CHANGE = 'Change'
        CHANGE_PCT = '% Change'
        VOLUME = 'Volume'
        OPEN_INTEREST = 'Open Interest'
        IMPLIED_VOLATILITY = 'Implied Volatility'
            
    DATA_FIELDS = [Fields.CONTRACT_NAME.value, Fields.LAST_TRADE_DATE.value, Fields.STRIKE.value,
                    Fields.LAST_PRICE.value, Fields.BID.value, Fields.ASK.value, 
                    Fields.CHANGE.value, Fields.CHANGE_PCT.value, Fields.VOLUME.value,
                    Fields.OPEN_INTEREST.value, Fields.IMPLIED_VOLATILITY.value]

    
    def __init__(self):
        pass
    
    
    def loadData(self, ticker, date=None):
        print("noop")
    
    
    def getData(self, type: OptionTypes = OptionTypes.PUT):
        print("noop")


    def getLivePrice(self, ticker):
        print("noop")
