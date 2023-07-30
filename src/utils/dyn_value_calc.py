import pandas as pd
from datetime import date, timedelta

import src.utils.processor as root
import src.analyzer as dfn


class DynamicValueCalculator(root.Processor):

    expiration_date: date = None
    order_date: date = None
    price: float = None

    def __init__(self, ordinal: int,  expiration_date: date, order_date: date, price: float):
        root.Processor.__init__(self, ordinal)
        self.expiration_date = expiration_date
        self.order_date = order_date
        self.price = price

    def process(self, data: pd.DataFrame):
        data = root.Processor.process(self, data)

        data[dfn.OptionsAnalyzer.Fields.DIFFERENCE.value] = self.price - data[dfn.OptionsAnalyzer.Fields.STRIKE.value]
        data[dfn.OptionsAnalyzer.Fields.DISTANCE.value] = data[dfn.OptionsAnalyzer.Fields.DIFFERENCE.value] / self.price * 100
        data[dfn.OptionsAnalyzer.Fields.YIELD.value] = self.calculate_yield(data)

        return data

    def calculate_yield(self, data: pd.DataFrame):

        strike_col_name = dfn.OptionsAnalyzer.Fields.STRIKE.value

        transaction_cost = 2 * 3 / 100  # assumption 3 US$ per transaction (buy and sell of 100 shares)
        days_per_year = 365
        holding_period: timedelta = self.expiration_date - self.order_date

        # yield = [ (premium - transaction costs) / strike ] / holding_period * 365 * 100
        ret_val = (data[dfn.OptionsAnalyzer.Fields.PREMIUM.value] - transaction_cost) / data[strike_col_name]
        ret_val = ret_val / holding_period.days * days_per_year * 100

        return ret_val
