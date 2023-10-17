import src.ingest.datasource.AbstractDataSource as datasource

class DataSourceAggregator:
    
    dataSources = None
    
    def __init__(self):
        
        self.dataSources = []
    
    def getData(self):
        
        print("here is your data")
        
        
    def addDataSource(self, datasource: datasource):
        
        self.dataSources.append(datasource)
