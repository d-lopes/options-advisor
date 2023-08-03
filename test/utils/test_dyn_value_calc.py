import pandas as pd
from datetime import date

import unittest

from src.analyzer import OptionsAnalyzer
from src.utils.dyn_value_calc import DynamicValueCalculator as ClassUnderTest

from test.test_analyzer import AnalyzerTest
from src.utils.filter_opts import FilterOptions


class DynamicValueCalculatorTest(unittest.TestCase):

    class TestData:

        CONTRACT_NAME = 'BAC230818P00031000'
        SYMBOL = 'BAC'
        MODE = OptionsAnalyzer.Types.PUT
        EXP_DATE = date.fromisoformat('2023-08-18')
        ORDER_DATE = date.fromisoformat('2023-07-22')
        PRICE = 31.66
        FILTER = FilterOptions.getDefaults()

    def test_process(self):

        # only use certain lines of mock data example response and tweak it to be compatible with method calculate_yield()
        test_options: pd.DataFrame = AnalyzerTest.MockData.EXAMPLE_RESPONSE['puts'].copy()
        test_options = test_options.rename(columns={'Last Price': OptionsAnalyzer.Fields.PREMIUM.value})
        test_options = test_options.iloc[[0]]
        # test_options = test_options.reset_index(drop=True)

        expected_difference = 16.66
        expected_distance = 52.62160454832596
        expected_yield = -4.506172839506172

        dvc = ClassUnderTest(ordinal=20, expiration_date=self.TestData.EXP_DATE, order_date=self.TestData.ORDER_DATE,
                             price=self.TestData.PRICE)
        actual_value = dvc.process(test_options)

        # check results
        expected_columns = actual_value.columns
        self.assertTrue(expected_columns.__contains__(OptionsAnalyzer.Fields.DIFFERENCE.value), 'DIFFERENCE missing')
        self.assertTrue(expected_columns.__contains__(OptionsAnalyzer.Fields.DISTANCE.value), 'DISTANCE missing')
        self.assertTrue(expected_columns.__contains__(OptionsAnalyzer.Fields.YIELD.value), 'YIELD missing')

        actual_difference = actual_value[OptionsAnalyzer.Fields.DIFFERENCE.value][0]
        self.assertEqual(expected_difference, actual_difference, 'unexpected value for DIFFERENCE')

        actual_distance = actual_value[OptionsAnalyzer.Fields.DISTANCE.value][0]
        self.assertEqual(expected_distance, actual_distance, 'unexpected value for DISTANCE')

        actual_yield = actual_value[OptionsAnalyzer.Fields.YIELD.value][0]
        self.assertEqual(expected_yield, actual_yield, 'unexpected value for YIELD')


if __name__ == '__main__':
    unittest.main()
