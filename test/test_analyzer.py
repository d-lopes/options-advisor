import unittest
from unittest.mock import MagicMock

from datetime import datetime

from src.analyzer import analyzer as classUnderTest

class analyzer_test(unittest.TestCase):

    TEST_SYMBOL = 'AMZN'

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
        classUnderTest.get_info()

if __name__ == '__main__':
    unittest.main()