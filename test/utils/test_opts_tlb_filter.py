import pandas as pd
import unittest

from src.utils.opts_tbl_filter import OptionsTableFilter as ClassUnderTest

from test.utils.pd_base_testcase import PandasBaseTestCase


class OptionsTableFilterTest(PandasBaseTestCase):

    TEST_DATA = None

    def setUp(self):
        PandasBaseTestCase.setUp(self)

        base_path = "resources/test"
        self.TEST_DATA = pd.read_csv(f"{base_path}/test_opts_tlb_filter.csv", index_col=0, header=0)

    def test_process_options_above_min_yield_and_below_max_strike(self):

        test_data = self.TEST_DATA
        test_filter = ClassUnderTest.FilterOptions(min_yield=10, max_strike=31.0)

        # only use certain rows from test data as expected result
        expected_value = test_data.copy()
        expected_value = expected_value.iloc[[5, 17, 18]]

        otf = ClassUnderTest(10, test_filter)
        actual_value = otf.process(test_data)

        self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
        self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_process_options_above_min_calls_and_above_min_puts(self):

        test_data = self.TEST_DATA
        test_filter = ClassUnderTest.FilterOptions(min_calls=1000, min_puts=1000)

        # only use certain rows from test data as expected result
        expected_value = test_data.copy()
        expected_value = expected_value.iloc[[6, 19]]

        otf = ClassUnderTest(10, test_filter)
        actual_value = otf.process(test_data)

        self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
        self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_process_options_above_min_yield(self):

        test_data = self.TEST_DATA
        test_filter = ClassUnderTest.FilterOptions(min_yield=20)

        # only use certain rows from test data as expected result
        expected_value = test_data.copy()
        expected_value = expected_value.iloc[[6, 7, 8, 9, 10, 11, 12, 13, 18, 19, 20, 21]]

        otf = ClassUnderTest(10, test_filter)
        actual_value = otf.process(test_data)

        self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
        self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_process_options_above_min_puts(self):

        test_data = self.TEST_DATA
        test_filter = ClassUnderTest.FilterOptions(min_puts=1000)

        # only use certain rows from test data as expected result
        expected_value = test_data.copy()
        expected_value = expected_value.iloc[[0, 1, 2, 3, 4, 5, 6, 7, 14, 19]]

        otf = ClassUnderTest(10, test_filter)
        actual_value = otf.process(test_data)

        self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
        self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_process_options_above_min_calls(self):

        test_data = self.TEST_DATA
        test_filter = ClassUnderTest.FilterOptions(min_calls=1000)

        # only use certain rows from test data as expected result
        expected_value = test_data.copy()
        expected_value = expected_value.iloc[[6, 19]]

        otf = ClassUnderTest(10, test_filter)
        actual_value = otf.process(test_data)

        self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
        self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_process_options_below_max_strike(self):

        test_data = self.TEST_DATA
        test_filter = ClassUnderTest.FilterOptions(max_strike=31.0)

        # only use certain rows from test data as expected result
        expected_value = test_data.copy()
        expected_value = expected_value.iloc[[0, 1, 2, 3, 4, 5, 14, 15, 16, 17, 18]]

        otf = ClassUnderTest(10, test_filter)
        actual_value = otf.process(test_data)

        self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
        self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_filter_string_representation(self):
        expected_value = "Filter(min_puts=1000, min_calls=1000, min_yield=10, max_strike=100000)"

        filter = ClassUnderTest.FilterOptions.get_defaults()
        filter.max_strike = 100000
        actual_value = filter.__repr__()

        self.assertEqual(expected_value, actual_value, 'unexpected return data')


if __name__ == '__main__':
    unittest.main()
