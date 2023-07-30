import pandas as pd


class Processor:

    ordinal = None

    def __init__(self, ordinal: int):
        self.ordinal = ordinal

    def process(self, data: pd.DataFrame):
        return data
