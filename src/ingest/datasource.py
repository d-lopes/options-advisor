from enum import Enum

class AbstractDataSource:
    
    class OptionTypes(Enum):
        PUT = 'PUT'
        CALL = 'CALL'
    
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

    DATA_FIELDS = [Fields.TICKER.value, Fields.TYPE.value, Fields.EXPIRATION_DATE.value, Fields.STRIKE.value,
                    Fields.YIELD.value, Fields.CURRENT_PRICE.value, Fields.DISTANCE.value, Fields.PREMIUM.value,
                    Fields.BID.value, Fields.ASK.value, Fields.CALLS_CNT.value, Fields.PUTS_CNT.value, Fields.VOLUME.value,
                    Fields.IMPLIED_VOLATILITY.value, Fields.TAGS.value]

    
    def __init__(self):
        pass
    
    
    def loadData(self, ticker, date=None):
        print("noop")
    
    
    def getData(self, type: OptionTypes = OptionTypes.PUT):
        print("noop")


    def getLivePrice(self, ticker):
        print("noop")
