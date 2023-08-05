import pandas as pd
from typing import Optional

import unittest

from src.analyzer import OptionsAnalyzer

from src.utils.opts_tbl_filter import OptionsTableFilter as ClassUnderTest
from test.utils.pd_base_testcase import PandasBaseTestCase


class OptionsTableFilterTest(PandasBaseTestCase):

    TEST_DATA: Optional[pd.DataFrame] = None

    def setUp(self):
        PandasBaseTestCase.setUp(self)

        base_path = "resources/test"
        self.TEST_DATA = pd.read_csv(f"{base_path}/test_opts_tlb_filter.csv", index_col=0, header=0)

    def _run_test_internal(self, test_filter: ClassUnderTest.FilterOptions, expected_idx: list,
                           type=OptionsAnalyzer.Types.PUT):

        test_data = self.TEST_DATA

        # only use certain rows from test data as expected result
        expected_value = test_data.copy()
        expected_value = expected_value.iloc[expected_idx]

        otf = ClassUnderTest(ordinal=10, type=type, filter=test_filter)
        actual_value = otf.process(test_data)

        self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
        self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_process_options_above_min_yield_and_below_max_strike(self):

        test_filter = ClassUnderTest.FilterOptions(min_yield=10, max_strike=31.0)
        expected_idx = [5, 17, 18]
        self._run_test_internal(test_filter, expected_idx)

    def test_process_options_above_min_calls_and_above_min_puts(self):

        test_filter = ClassUnderTest.FilterOptions(min_calls=1000, min_puts=1000)
        expected_idx = [6, 19]
        self._run_test_internal(test_filter, expected_idx)

    def test_process_options_above_min_yield(self):

        test_filter = ClassUnderTest.FilterOptions(min_yield=20)
        expected_idx = [6, 7, 8, 9, 10, 11, 12, 13, 18, 19, 20, 21]
        self._run_test_internal(test_filter, expected_idx)

    def test_process_options_above_min_puts(self):

        test_filter = ClassUnderTest.FilterOptions(min_puts=1000)
        expected_idx = [0, 1, 2, 3, 4, 5, 6, 7, 14, 19]
        self._run_test_internal(test_filter, expected_idx)

    def test_process_options_above_min_calls(self):

        test_filter = ClassUnderTest.FilterOptions(min_calls=1000)
        expected_idx = [6, 19]
        self._run_test_internal(test_filter, expected_idx)

    def test_process_options_below_max_strike(self):

        test_filter = ClassUnderTest.FilterOptions(max_strike=31.0)
        expected_idx = [0, 1, 2, 3, 4, 5, 14, 15, 16, 17, 18]
        self._run_test_internal(test_filter, expected_idx)

    def test_process_put_options_in_the_money(self):

        test_filter = ClassUnderTest.FilterOptions(moneyness=ClassUnderTest.Moneyness.IN)
        expected_idx = [6, 7, 8, 9, 10, 11, 12, 13, 19, 20, 21]
        self._run_test_internal(test_filter, expected_idx)

    def test_process_put_options_out_of_money(self):

        test_filter = ClassUnderTest.FilterOptions(moneyness=ClassUnderTest.Moneyness.OUT)
        expected_idx = [0, 1, 2, 3, 4, 5, 14, 15, 16, 17, 18]
        self._run_test_internal(test_filter, expected_idx)

    def test_process_put_options_at_the_money(self):

        test_filter = ClassUnderTest.FilterOptions(moneyness=ClassUnderTest.Moneyness.AT)
        expected_idx = []
        self._run_test_internal(test_filter, expected_idx)

    def test_process_call_options_in_the_money(self):

        test_filter = ClassUnderTest.FilterOptions(moneyness=ClassUnderTest.Moneyness.IN)
        expected_idx = [0, 1, 2, 3, 4, 5, 14, 15, 16, 17, 18]
        self._run_test_internal(test_filter, expected_idx, OptionsAnalyzer.Types.CALL)

    def test_process_call_options_out_of_money(self):

        test_filter = ClassUnderTest.FilterOptions(moneyness=ClassUnderTest.Moneyness.OUT)
        expected_idx = [6, 7, 8, 9, 10, 11, 12, 13, 19, 20, 21]
        self._run_test_internal(test_filter, expected_idx, OptionsAnalyzer.Types.CALL)

    def test_process_call_options_at_the_money(self):

        test_filter = ClassUnderTest.FilterOptions(moneyness=ClassUnderTest.Moneyness.AT)
        expected_idx = []
        self._run_test_internal(test_filter, expected_idx, OptionsAnalyzer.Types.CALL)

    def test_default_filter_string_representation(self):
        expected_value = "Filter(min_puts=1000, min_calls=1000, min_yield=10, max_strike=100000, moneyness=ITM)"

        filter = ClassUnderTest.FilterOptions.get_defaults()
        actual_value = filter.__repr__()

        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_no_filter_string_representation(self):
        expected_value = "Filter(min_puts=None, min_calls=None, min_yield=None, max_strike=None, moneyness=None)"

        filter = ClassUnderTest.FilterOptions()
        actual_value = filter.__repr__()

        self.assertEqual(expected_value, actual_value, 'unexpected return data')


if __name__ == '__main__':
    unittest.main()
