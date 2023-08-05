import pandas as pd


class MockData:

    COLUMNS = ['Contract Name', 'Last Trade Date', 'Strike', 'Last Price', 'Bid', 'Ask', 'Change', '% Change', 'Volume',
               'Open Interest', 'Implied Volatility']

    EMPTY_RESPONSE = None
    EXAMPLE_RESPONSE = None

    def __init__(self):
        self.EMPTY_RESPONSE = {}
        self.EMPTY_RESPONSE['puts'] = pd.DataFrame(columns=self.COLUMNS)
        self.EMPTY_RESPONSE['calls'] = pd.DataFrame(columns=self.COLUMNS)

        self.EXAMPLE_RESPONSE = {}
        base_path = "resources/test"
        put_data = pd.read_csv(f"{base_path}/test_analyzer_1_puts.csv", index_col=0, header=0)
        call_data = pd.read_csv(f"{base_path}/test_analyzer_2_calls.csv", index_col=0, header=0)
        self.EXAMPLE_RESPONSE['puts'] = put_data
        self.EXAMPLE_RESPONSE['calls'] = call_data
