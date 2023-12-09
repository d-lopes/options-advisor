import src.ingest.datasource.AbstractDataSource as datasource

class YOptionDataSource(datasource):

    def __init__(self):
        datasource.__init__(self)
    
        
    def loadData(self, ticker, date=None):
        print("noop")

        
    def getLivePrice(self, ticker):
        print("noop")
