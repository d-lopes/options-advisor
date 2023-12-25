import pandas as pd

from src.ingest.datasource import AbstractDataSource

class MockData:

    EMPTY_RESPONSE = None
    EXAMPLE_RESPONSE = None

    def __init__(self):
        self.EMPTY_RESPONSE = {}
        self.EMPTY_RESPONSE['puts'] = pd.DataFrame(columns=AbstractDataSource.DATA_FIELDS)
        self.EMPTY_RESPONSE['calls'] = pd.DataFrame(columns=AbstractDataSource.DATA_FIELDS)

        self.EXAMPLE_RESPONSE = {}
        base_path = "resources/test"
        put_data = pd.read_csv(f"{base_path}/test_analyzer_1_puts.csv", index_col=0, header=0)
        call_data = pd.read_csv(f"{base_path}/test_analyzer_2_calls.csv", index_col=0, header=0)
        self.EXAMPLE_RESPONSE['puts'] = put_data
        self.EXAMPLE_RESPONSE['calls'] = call_data

    
    def get_empty_data(self, optionType):
        if (optionType == AbstractDataSource.OptionTypes.PUT):
            return self.EMPTY_RESPONSE['puts']
        
        if (optionType == AbstractDataSource.OptionTypes.CALL):
            return self.EMPTY_RESPONSE['calls']
    
    
    def get_example_data(self, optionType):
        if (optionType == AbstractDataSource.OptionTypes.PUT):
            return self.EXAMPLE_RESPONSE['puts']
        
        if (optionType == AbstractDataSource.OptionTypes.CALL):
            return self.EXAMPLE_RESPONSE['calls']
    