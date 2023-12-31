from datetime import date, datetime
import pandas as pd

from src.analyzer import OptionsAnalyzer
from src.utils.opts_tbl_filter import OptionsTableFilter


class SampleData:

    CONTRACT_NAME = 'BAC230818P00031000'
    SYMBOL = 'BAC'
    MODE = OptionsAnalyzer.Types.PUT
    EXP_DATE = date.fromisoformat('2023-08-18')
    ORDER_DATE = date.fromisoformat('2023-07-22')
    PRICE = 31.66
    FILTER = OptionsTableFilter.FilterOptions.get_defaults()
    FILTER.moneyness = None

    EXAMPLE_RESULT = pd.DataFrame([
        [SYMBOL,  MODE.value, datetime.fromisoformat('2023-08-18'), 32.0, 37.175925925925924, PRICE, -1.073911, 0.94,
            0.93, 0.95, 1252, 5575, 55, '21.39%', ['goodYield']],
        [SYMBOL,  MODE.value, datetime.fromisoformat('2023-09-01'), 32.0, 46.8923611111111, PRICE, -1.073911, 1.17,
            1.17, 1.21, 1252, 8574, 3, '23.58%', ['goodYield']]
    ], columns=OptionsAnalyzer.DATA_COLUMNS)
    EXAMPLE_RESULT = EXAMPLE_RESULT.reset_index(drop=True)
