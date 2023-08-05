import pandas as pd
from enum import Enum
from typing import Optional

import src.analyzer as analyzer
import src.utils.processor as root


class OptionsTableFilter(root.Processor):

    class Moneyness(Enum):
        IN = 'ITM'
        AT = 'ATM'
        OUT = 'OTM'

    class FilterOptions:
        min_puts: Optional[int] = None
        min_calls: Optional[int] = None
        min_yield: Optional[float] = None
        max_strike: Optional[float] = None
        moneyness: Optional[str] = None

        def __init__(self, min_puts: int = None, min_calls: int = None, min_yield: float = None,
                     max_strike: float = None, moneyness: str = None):

            self.min_puts = min_puts
            self.min_calls = min_calls
            self.min_yield = min_yield
            self.max_strike = max_strike
            self.moneyness = moneyness

        def __repr__(self):
            if self.moneyness is None:
                moneyness = "None"
            else:
                moneyness = self.moneyness.value

            ret_val = "Filter("
            ret_val += f"min_puts={self.min_puts}, "
            ret_val += f"min_calls={self.min_calls}, "
            ret_val += f"min_yield={self.min_yield}, "
            ret_val += f"max_strike={self.max_strike}, "
            ret_val += f"moneyness={moneyness}"
            ret_val += ")"

            return ret_val

        @staticmethod
        def get_defaults():
            return OptionsTableFilter.FilterOptions(min_puts=1000, min_calls=1000, min_yield=10, max_strike=100000,
                                                    moneyness=OptionsTableFilter.Moneyness.IN)

    filter: FilterOptions = None
    type: str = None

    def __init__(self, ordinal: int, type: str, filter: FilterOptions):
        root.Processor.__init__(self, ordinal)
        self.filter = filter
        self.type = type

    def process(self, data: pd.DataFrame):
        return_value = root.Processor.process(self, data)

        # define aliases for better readability
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

        # filter for moneyness
        return_value = self._handle_moneyness_internal(return_value)

        return return_value

    def _handle_moneyness_internal(self, data: pd.DataFrame):

        # define aliases for better readability
        fltr = self.filter
        fields = analyzer.OptionsAnalyzer.Fields
        moneyness = OptionsTableFilter.Moneyness
        types = analyzer.OptionsAnalyzer.Types

        return_value = data

        # business rules (for market price is ABOVE the strike price):
        #   * A CALL option is in the money (ITM) if the  market price of the underlying is above the strike price.
        #   * A PUT option is OTM if the market price is above the strike price.
        if (((moneyness.IN == fltr.moneyness) & (types.CALL == self.type)) or
                ((moneyness.OUT == fltr.moneyness) & (types.PUT == self.type))):
            return_value = return_value.loc[return_value[fields.DIFFERENCE.value] > 0]

        # business rules (for market price is BELOW the strike price):
        #   * A PUT option is ITM if the market price is below the strike price.
        #   * A CALL option is out of the money (OTM) if the market price of the underlying is below the strike price
        elif (((moneyness.IN == fltr.moneyness) & (types.PUT == self.type)) or
                ((moneyness.OUT == fltr.moneyness) & (types.CALL == self.type))):
            return_value = return_value.loc[return_value[fields.DIFFERENCE.value] < 0]

        # Any option is at the money (ATM) if the market price of the underlying is at or very near to the strike price.
        # this is tested here by checking if the distance of market price of the underlying and strike price is between
        # -1% and 1%
        elif (moneyness.AT == fltr.moneyness):
            return_value = return_value.loc[(-1 < return_value[fields.DISTANCE.value]) &
                                            (return_value[fields.DISTANCE.value] < 1)]

        return return_value
