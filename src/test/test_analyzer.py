import pandas as pd
from datetime import datetime

import unittest
from unittest.mock import patch

from src.main.analyzer import YahooFinanceWrapper

from src.main.analyzer import Analyzer as ClassUnderTest

class AnalyzerTest(unittest.TestCase):

    class TestData:

        SYMBOL = 'AMZN'
        MODE = ClassUnderTest.Types.PUT
        EXP_DATE = expected_value = datetime.fromisoformat('2023-07-21').date()
        PRICE = 130
        FILTER = ClassUnderTest.Filter.getDefaults()


    DATA_COLUMNS = ClassUnderTest.DATA_COLUMNS.copy()
    DATA_COLUMNS.append(ClassUnderTest.Fields.CONTRACT_NAME.value)
    DATA_COLUMNS.append(ClassUnderTest.Fields.OPEN_INTEREST.value)

    def test_get_exp_date_from_contract_name(self):

        test_contract_name = 'AMZN230721P00015000'
        expected_value = datetime.fromisoformat('2023-07-21')

        actual_value = ClassUnderTest.exp_date_from_contract_name(test_contract_name, self.TestData.SYMBOL)

        self.assertEqual(expected_value, actual_value, 'unexpected expiration date')

    def test_get_info_can_return_empty_list(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        mocked_data = {}
        mocked_data['puts'] = pd.DataFrame(columns=self.DATA_COLUMNS)
        mocked_data['calls'] = pd.DataFrame(columns=self.DATA_COLUMNS)

        with patch.object(YahooFinanceWrapper, 'get_options_chain', return_value = mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_info(self.TestData.SYMBOL, self.TestData.MODE,
                                                    self.TestData.EXP_DATE, self.TestData.PRICE,
                                                    self.TestData.FILTER)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL, self.TestData.EXP_DATE)

            # check results
            self.assertEqual(expected_value.empty, actual_value.empty, 'unexpected return data')

    def test_get_options_skips_too_expensive_underlying(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        mocked_data = 140

        with patch.object(YahooFinanceWrapper, 'get_live_price', return_value = mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_options(symbols = [self.TestData.SYMBOL])

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL)

            # check results
            self.assertEqual(expected_value.empty, actual_value.empty, 'unexpected return data')

if __name__ == '__main__':
    unittest.main()