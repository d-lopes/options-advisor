from src.ingest.datasource import AbstractDataSource

import pandas as pd

class DataSourceAggregator:
    
    
    # map from priority to datasource - the priority influences which value is taken, when a data point occurs twice
    
    dataSources = None
    
    def __init__(self):
        self.dataSources = []
    
    
    def loadData(self, ticker, date=None):
        
        for datasource in self.dataSources:
            datasource.loadData(ticker=ticker, date=date)
        
    
    def getData(self, type: AbstractDataSource.OptionTypes = AbstractDataSource.OptionTypes.PUT):
        
        data = pd.DataFrame([])
        for datasource in self.dataSources:
            tmp = datasource.getData(type)
            data = pd.concat([data, tmp])
            
        return data
    
    def getPrice(self):
        print("noop")
        
    def addDataSource(self, datasource: AbstractDataSource):
        
        self.dataSources.append(datasource)
        
    def getDataSourceCount(self):
        return len(self.dataSources)
