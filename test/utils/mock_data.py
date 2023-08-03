import pandas as pd

from src.analyzer import OptionsAnalyzer


class MockData:

    # Contract Name, Last Trade Date, Strike, Last Price, Bid, Ask, Change, % Change, Volume, Open Interest, Volatility
    COLUMNS = [OptionsAnalyzer.Fields.CONTRACT_NAME.value, 'Last Trade Date', OptionsAnalyzer.Fields.STRIKE.value,
               'Last Price', OptionsAnalyzer.Fields.BID.value, OptionsAnalyzer.Fields.ASK.value, 'Change', '% Change',
               OptionsAnalyzer.Fields.VOLUME.value, OptionsAnalyzer.Fields.OPEN_INTEREST.value,
               OptionsAnalyzer.Fields.IMPLIED_VOLATILITY.value]

    EMPTY_RESPONSE = None
    EXAMPLE_RESPONSE = None

    def __init__(self):
        self.EMPTY_RESPONSE = {}
        self.EMPTY_RESPONSE['puts'] = pd.DataFrame(columns=self.COLUMNS)
        self.EMPTY_RESPONSE['calls'] = pd.DataFrame(columns=self.COLUMNS)

        base_path = "test/resources"
        put_data = pd.read_csv(f"{base_path}/test_analyzer_1_puts.csv", index_col=0, header=0)
        call_data = pd.read_csv(f"{base_path}/test_analyzer_2_calls.csv", index_col=0, header=0)
        self.EXAMPLE_RESPONSE = {}
        self.EXAMPLE_RESPONSE['puts'] = put_data
        self.EXAMPLE_RESPONSE['calls'] = call_data
