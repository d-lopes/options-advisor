import pandas as pd
from datetime import datetime

import unittest
from unittest.mock import MagicMock

from src.main.analyzer import analyzer as classUnderTest

class analyzer_test(unittest.TestCase):

    TEST_SYMBOL = 'AMZN'
    TEST_FILTER = classUnderTest.Filter.getDefaults()
    TEST_EXP_DATE = expected_value = datetime.fromisoformat('2023-07-21').date()

    # def setUpClass():
    #     # mock API Calls towards Yahoo Finance Website
    #     thing = object()
    #     thing.get_options_chain = MagicMock(return_value=4711)

    def test_get_exp_date_from_contract_name(self):

        test_contract_name = 'AMZN230721P00015000'
        expected_value = datetime.fromisoformat('2023-07-21')

        actual_value = classUnderTest.exp_date_from_contract_name(test_contract_name, analyzer_test.TEST_SYMBOL)

        self.assertEqual(expected_value, actual_value, 'unexpected expiration date')

    def test_get_info(self):
        expected_value = pd.DataFrame()

        actual_value = classUnderTest.get_info(ticker = analyzer_test.TEST_SYMBOL, expiration_date = analyzer_test.TEST_EXP_DATE, filter = analyzer_test.TEST_FILTER)

        self.assertEqual(expected_value.empty, actual_value.empty, 'unexpected return data')

if __name__ == '__main__':
    unittest.main()