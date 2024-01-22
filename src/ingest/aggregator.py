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
        
        data = pd.DataFrame(columns=AbstractDataSource.DATA_FIELDS)
        for datasource in self.dataSources:
            tmp = datasource.getData(type)
            data = pd.concat([data.astype(tmp.dtypes), tmp.astype(tmp.dtypes)])
            
        return data
    
    def getPrice(self, ticker):
        # for now only the first datasource is used to retrieve the live price of a stock
        # ---
        # better approach: define priorities for data sources. 
        # then it will be possible to process data sources in the order of their priority and take the
        # first value that occurs
        for datasource in self.dataSources:
            return datasource.getLivePrice(ticker)
            
        return -4711
        
    def addDataSource(self, datasource: AbstractDataSource):
        self.dataSources.append(datasource)
        
    def getDataSourceCount(self):
        return len(self.dataSources)
