import pandas as pd
from datetime import datetime

import src.utils.processor as root


class ExpirationDateExtractor(root.Processor):

    source_col = None
    target_col = None
    ticker = None

    def __init__(self, ordinal: int, ticker: str, source: str, target: str):
        root.Processor.__init__(self, ordinal)
        self.ticker = ticker
        self.source_col = source
        self.target_col = target

    def process(self, data: pd.DataFrame):
        data = root.Processor.process(self, data)

        data[self.target_col] = data[self.source_col].transform(lambda name: self.extract_date(name))

        return data

    def extract_date(self, name: str):
        size = len(name)
        ticker_date_portion = name[:size-9]
        date_str = '20' + ticker_date_portion.replace(self.ticker, '', 1)

        return datetime.strptime(date_str, '%Y%m%d')
