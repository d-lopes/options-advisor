from src.ingest.datasource import AbstractDataSource as datasource

class YOptionDataSource(datasource):

    def __init__(self):
        datasource.__init__(self)
    
        
    def loadData(self, ticker, date=None):
        print("noop")


    def getData(self, type: datasource.OptionTypes = datasource.OptionTypes.PUT):
        print("noop")

        
    def getLivePrice(self, ticker):
        print("noop")
