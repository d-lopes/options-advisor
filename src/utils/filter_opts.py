

class FilterOptions:
    min_puts = None
    min_calls = None
    min_yield = None
    max_strike = None

    def __init__(self, min_puts=0, min_calls=0, min_yield=0, max_strike=1000):
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
    def getDefaults():
        return FilterOptions(min_puts=1000, min_calls=1000, min_yield=10, max_strike=100000)
