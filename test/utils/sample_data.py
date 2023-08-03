from datetime import date, datetime
import pandas as pd

from src.analyzer import OptionsAnalyzer
from src.utils.filter_opts import FilterOptions


class SampleData:

    CONTRACT_NAME = 'BAC230818P00031000'
    SYMBOL = 'BAC'
    MODE = OptionsAnalyzer.Types.PUT
    EXP_DATE = date.fromisoformat('2023-08-18')
    ORDER_DATE = date.fromisoformat('2023-07-22')
    PRICE = 31.66
    FILTER = FilterOptions.getDefaults()

    EXAMPLE_RESULT = pd.DataFrame([
        [SYMBOL,  MODE.value, datetime.fromisoformat('2023-08-18'), 32.0, 37.175925925925924, PRICE, -1.073911, 0.94,
            0.93, 0.95, 1252, 5575, '21.39%', ['goodYield']],
        [SYMBOL,  MODE.value, datetime.fromisoformat('2023-09-01'), 32.0, 46.8923611111111, PRICE, -1.073911, 1.17,
            1.17, 1.21, 1252, 8574, '23.58%', ['goodYield']]
    ], columns=OptionsAnalyzer.DATA_COLUMNS)
    EXAMPLE_RESULT = EXAMPLE_RESULT.reset_index(drop=True)
