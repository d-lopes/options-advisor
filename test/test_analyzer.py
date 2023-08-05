import pandas as pd
from datetime import date

import unittest
from unittest.mock import patch

from src.analyzer import YahooFinanceWrapper as yfw

from src.analyzer import OptionsAnalyzer as ClassUnderTest
from src.utils.filter_opts import FilterOptions

from test.utils.sample_data import SampleData
from test.utils.mock_data import MockData
from test.utils.pd_base_testcase import PandasBaseTestCase


class AnalyzerTest(PandasBaseTestCase):

    mock_data = MockData()

    def setUp(self):
        PandasBaseTestCase.setUp(self)

    def test_filter_string_representation(self):
        expected_value = "Filter(min_puts=1000, min_calls=1000, min_yield=10, max_strike=100000)"

        actual_value = SampleData.FILTER.__repr__()

        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_info_handles_value_error_input(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        with patch.object(yfw, 'get_options_chain') as mocked_method:

            mocked_method.side_effect = ValueError(Exception('symbol does not exist'))

            actual_value = ClassUnderTest.get_info(SampleData.SYMBOL, SampleData.MODE, SampleData.EXP_DATE,
                                                   SampleData.PRICE, SampleData.FILTER, SampleData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(SampleData.SYMBOL, SampleData.EXP_DATE)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_info_handles_incorrect_mode(self):

        expected_value = 'invalid type "incorrect"'
        mocked_data = self.mock_data.EXAMPLE_RESPONSE

        with patch.object(yfw, 'get_options_chain', return_value=mocked_data) as mocked_method:
            with self.assertRaises(ValueError) as context:

                ClassUnderTest.get_info(SampleData.SYMBOL, 'incorrect', SampleData.EXP_DATE,
                                        SampleData.PRICE, SampleData.FILTER, SampleData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(SampleData.SYMBOL, SampleData.EXP_DATE)

            # ensure exception was thrown
            self.assertTrue(expected_value in str(context.exception))

    def test_get_info_transforms_empty_input(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)
        mocked_data = self.mock_data.EMPTY_RESPONSE

        with patch.object(yfw, 'get_options_chain', return_value=mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_info(SampleData.SYMBOL, SampleData.MODE, SampleData.EXP_DATE,
                                                   SampleData.PRICE, SampleData.FILTER, SampleData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(SampleData.SYMBOL, SampleData.EXP_DATE)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_info_4_puts_transforms_example_input(self):

        expected_value = SampleData.EXAMPLE_RESULT
        mocked_data = self.mock_data.EXAMPLE_RESPONSE

        with patch.object(yfw, 'get_options_chain', return_value=mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_info(SampleData.SYMBOL, SampleData.MODE, SampleData.EXP_DATE,
                                                   SampleData.PRICE, SampleData.FILTER, SampleData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(SampleData.SYMBOL, SampleData.EXP_DATE)

            # check results
            self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
            self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_info_4_calls_transforms_example_input(self):

        expected_value = SampleData.EXAMPLE_RESULT.copy()
        expected_value[ClassUnderTest.Fields.TYPE.value] = ClassUnderTest.Types.CALL.value
        expected_value[ClassUnderTest.Fields.YIELD.value] = 27.881944
        expected_value[ClassUnderTest.Fields.PREMIUM.value] = 0.72
        expected_value[ClassUnderTest.Fields.BID.value] = 0.7
        expected_value[ClassUnderTest.Fields.ASK.value] = 0.74
        expected_value[ClassUnderTest.Fields.IMPLIED_VOLATILITY.value] = '20.70%'

        mocked_data = self.mock_data.EXAMPLE_RESPONSE

        with patch.object(yfw, 'get_options_chain', return_value=mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_info(SampleData.SYMBOL, ClassUnderTest.Types.CALL, SampleData.EXP_DATE,
                                                   SampleData.PRICE, SampleData.FILTER, SampleData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(SampleData.SYMBOL, SampleData.EXP_DATE)

            # check results
            self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
            self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')

            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_options_handles_assertion_error(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        with patch.object(yfw, 'get_live_price') as mocked_method:

            mocked_method.side_effect = AssertionError(Exception('symbol does not exist'))

            actual_value = ClassUnderTest.get_options(symbols=[SampleData.SYMBOL], year=2023, start_week=33, end_week=34)

            # ensure mock for get_live_price() was called
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(SampleData.SYMBOL)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_options_skips_too_expensive_underlying(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        mock1 = patch.object(yfw, 'get_live_price', return_value=48.1)
        mock2 = patch.object(yfw, 'get_options_chain', return_value=self.mock_data.EXAMPLE_RESPONSE)

        test_filter = FilterOptions.get_defaults()
        test_filter.max_strike = 40

        with mock1 as get_live_price, mock2 as get_options_chain:

            actual_value = ClassUnderTest.get_options(symbols=[SampleData.SYMBOL], year=2023,
                                                      start_week=33, end_week=34, filter=test_filter)

            # ensure mock for get_live_price() was called
            get_live_price.assert_called_once()
            get_live_price.assert_called_with(SampleData.SYMBOL)

            # ensure mock for get_options_chain() was NOT called
            get_options_chain.assert_not_called()

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_options_computes_correct_expiration_dates(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        mock1 = patch.object(yfw, 'get_live_price', return_value=self.mock_data.EMPTY_RESPONSE)
        mock2 = patch.object(yfw, 'get_options_chain', return_value=self.mock_data.EMPTY_RESPONSE)

        symbols = [SampleData.SYMBOL]

        with mock1, mock2 as get_options_chain:

            actual_value = ClassUnderTest.get_options(symbols=symbols, year=2023, start_week=32, end_week=36)

            # ensure mock was called with corresponding expiration dates
            get_options_chain.assert_any_call(SampleData.SYMBOL, date.fromisoformat("2023-08-11"))
            get_options_chain.assert_any_call(SampleData.SYMBOL, date.fromisoformat("2023-08-18"))
            get_options_chain.assert_any_call(SampleData.SYMBOL, date.fromisoformat("2023-08-25"))
            get_options_chain.assert_any_call(SampleData.SYMBOL, date.fromisoformat("2023-09-01"))

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')


if __name__ == '__main__':
    unittest.main()
