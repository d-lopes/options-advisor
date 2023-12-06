import src.ingest.datasource.AbstractDataSource as datasource

class YOptionDataSource(datasource):

    def __init__(self):
        datasource.__init__(self)
        
    def loadData(self):
        
        print("noop")