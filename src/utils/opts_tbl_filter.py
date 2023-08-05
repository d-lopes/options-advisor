import pandas as pd

import src.analyzer as analyzer
import src.utils.processor as root


class OptionsTableFilter(root.Processor):

    class FilterOptions:
        min_puts = None
        min_calls = None
        min_yield = None
        max_strike = None

        def __init__(self, min_puts=None, min_calls=None, min_yield=None, max_strike=None):
            self.min_puts = min_puts
            self.min_calls = min_calls
            self.min_yield = min_yield
            self.max_strike = max_strike

        def __repr__(self):
            ret_val = "Filter("
            ret_val += f"min_puts={self.min_puts}, "
            ret_val += f"min_calls={self.min_calls}, "
            ret_val += f"min_yield={self.min_yield}, "
            ret_val += f"max_strike={self.max_strike}"
            ret_val += ")"

            return ret_val

        @staticmethod
        def get_defaults():
            return OptionsTableFilter.FilterOptions(min_puts=1000, min_calls=1000, min_yield=10, max_strike=100000)

    filter = None

    def __init__(self, ordinal: int, filter: FilterOptions):
        root.Processor.__init__(self, ordinal)
        self.filter = filter

    def process(self, data: pd.DataFrame):
        return_value = root.Processor.process(self, data)

        fltr = self.filter
        fields = analyzer.OptionsAnalyzer.Fields

        # filter for minium available puts
        if (fltr.min_puts is not None):
            return_value = return_value.loc[return_value[fields.PUTS_CNT.value] >= fltr.min_puts]

        # filter for minium available calls
        if (fltr.min_calls is not None):
            return_value = return_value.loc[return_value[fields.CALLS_CNT.value] >= fltr.min_calls]

        # filter for minimum acceptable yield
        if (fltr.min_yield is not None):
            return_value = return_value.loc[return_value[fields.YIELD.value] >= fltr.min_yield]

        # filter for maximum acceptable strike
        if (fltr.max_strike is not None):
            return_value = return_value.loc[return_value[fields.STRIKE.value] <= fltr.max_strike]

        return return_value
