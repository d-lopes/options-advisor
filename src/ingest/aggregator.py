import src.ingest.datasource as types

import pandas as pd

class DataSourceAggregator:
    
    dataSources = None
    
    def __init__(self):
        
        self.dataSources = []
    
    def getData(self):
        
        data = pd.DataFrame([])
        for datasource in self.dataSources:
            tmp = datasource.load_data()
            data = pd.concat([data, tmp])
            
        return data
    
        
    def addDataSource(self, datasource: types.AbstractDataSource):
        
        self.dataSources.append(datasource)
        
    def getDataSourceCount(self):
        
        return len(self.dataSources)
