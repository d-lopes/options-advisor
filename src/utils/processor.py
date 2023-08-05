import pandas as pd
from typing import Optional


class Processor:

    ordinal: Optional[int] = None

    def __init__(self, ordinal: int):
        self.ordinal = ordinal

    def process(self, data: pd.DataFrame):
        return data
