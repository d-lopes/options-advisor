import pandas as pd
import pandas.testing as pd_testing
from datetime import date, datetime
from logging import Logger

import unittest
from unittest.mock import patch

from src.analyzer import YahooFinanceWrapper as yfw

from src.analyzer import OptionsAnalyzer as ClassUnderTest
from src.utils.filter_opts import FilterOptions


class AnalyzerTest(unittest.TestCase):

    class TestData:

        CONTRACT_NAME = 'BAC230818P00031000'
        SYMBOL = 'BAC'
        MODE = ClassUnderTest.Types.PUT
        EXP_DATE = date.fromisoformat('2023-08-18')
        ORDER_DATE = date.fromisoformat('2023-07-22')
        PRICE = 31.66
        FILTER = FilterOptions.getDefaults()

        EXAMPLE_RESULT = pd.DataFrame([
            [SYMBOL,  MODE.value, datetime.fromisoformat('2023-08-18'), 32.0, 37.175925925925924, PRICE, -1.073911, 0.94,
             0.93, 0.95, 1252, 5575, '21.39%', ['goodYield']],
            [SYMBOL,  MODE.value, datetime.fromisoformat('2023-09-01'), 32.0, 46.8923611111111, PRICE, -1.073911, 1.17,
             1.17, 1.21, 1252, 8574, '23.58%', ['goodYield']]
        ], columns=ClassUnderTest.DATA_COLUMNS)
        EXAMPLE_RESULT = EXAMPLE_RESULT.reset_index(drop=True)

    class MockData:

        # Contract Name, Last Trade Date, Strike, Last Price, Bid, Ask, Change, % Change, Volume, Open Interest, Volatility
        COLUMNS = [ClassUnderTest.Fields.CONTRACT_NAME.value, 'Last Trade Date', ClassUnderTest.Fields.STRIKE.value,
                   'Last Price', ClassUnderTest.Fields.BID.value, ClassUnderTest.Fields.ASK.value, 'Change', '% Change',
                   ClassUnderTest.Fields.VOLUME.value, ClassUnderTest.Fields.OPEN_INTEREST.value,
                   ClassUnderTest.Fields.IMPLIED_VOLATILITY.value]

        EMPTY_RESPONSE = None
        EXAMPLE_RESPONSE = None

    def assert_frame_equal(self, a, b, msg):
        try:
            pd_testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def assert_series_equal(self, a, b, msg):
        try:
            pd_testing.assert_series_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        # enable comparison of data frames
        self.addTypeEqualityFunc(pd.DataFrame, self.assert_frame_equal)
        self.addTypeEqualityFunc(pd.Series, self.assert_series_equal)

        self.MockData.EMPTY_RESPONSE = {}
        self.MockData.EMPTY_RESPONSE['puts'] = pd.DataFrame(columns=self.MockData.COLUMNS)
        self.MockData.EMPTY_RESPONSE['calls'] = pd.DataFrame(columns=self.MockData.COLUMNS)

        base_path = "test/resources"
        put_data = pd.read_csv(f"{base_path}/test_analyzer_1_puts.csv", index_col=0, header=0)
        call_data = pd.read_csv(f"{base_path}/test_analyzer_2_calls.csv", index_col=0, header=0)
        self.MockData.EXAMPLE_RESPONSE = {}
        self.MockData.EXAMPLE_RESPONSE['puts'] = put_data
        self.MockData.EXAMPLE_RESPONSE['calls'] = call_data

    def test_filter_string_representation(self):
        expected_value = "Filter(min_puts=1000, min_calls=1000, min_yield=10, max_strike=100000)"

        actual_value = AnalyzerTest.TestData.FILTER.__repr__()

        self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_info_handles_value_error_input(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        with patch.object(yfw, 'get_options_chain') as mocked_method:

            mocked_method.side_effect = ValueError(Exception('symbol does not exist'))

            actual_value = ClassUnderTest.get_info(self.TestData.SYMBOL, self.TestData.MODE, self.TestData.EXP_DATE,
                                                   self.TestData.PRICE, self.TestData.FILTER, self.TestData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL, self.TestData.EXP_DATE)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_info_handles_incorrect_mode(self):

        expected_value = 'invalid type "incorrect"'
        mocked_data = self.MockData.EXAMPLE_RESPONSE

        with patch.object(yfw, 'get_options_chain', return_value=mocked_data) as mocked_method:
            with self.assertRaises(ValueError) as context:

                ClassUnderTest.get_info(self.TestData.SYMBOL, 'incorrect', self.TestData.EXP_DATE,
                                        self.TestData.PRICE, self.TestData.FILTER, self.TestData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL, self.TestData.EXP_DATE)

            # ensure exception was thrown
            self.assertTrue(expected_value in str(context.exception))

    def test_get_info_transforms_empty_input(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)
        mocked_data = self.MockData.EMPTY_RESPONSE

        with patch.object(yfw, 'get_options_chain', return_value=mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_info(self.TestData.SYMBOL, self.TestData.MODE, self.TestData.EXP_DATE,
                                                   self.TestData.PRICE, self.TestData.FILTER, self.TestData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL, self.TestData.EXP_DATE)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_info_4_puts_transforms_example_input(self):

        expected_value = self.TestData.EXAMPLE_RESULT
        mocked_data = self.MockData.EXAMPLE_RESPONSE

        with patch.object(yfw, 'get_options_chain', return_value=mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_info(self.TestData.SYMBOL, self.TestData.MODE, self.TestData.EXP_DATE,
                                                   self.TestData.PRICE, self.TestData.FILTER, self.TestData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL, self.TestData.EXP_DATE)

            # check results
            self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
            self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_info_4_calls_transforms_example_input(self):

        expected_value = self.TestData.EXAMPLE_RESULT.copy()
        expected_value[ClassUnderTest.Fields.TYPE.value] = ClassUnderTest.Types.CALL.value
        expected_value[ClassUnderTest.Fields.YIELD.value] = 27.881944
        expected_value[ClassUnderTest.Fields.PREMIUM.value] = 0.72
        expected_value[ClassUnderTest.Fields.BID.value] = 0.7
        expected_value[ClassUnderTest.Fields.ASK.value] = 0.74
        expected_value[ClassUnderTest.Fields.IMPLIED_VOLATILITY.value] = '20.70%'

        mocked_data = self.MockData.EXAMPLE_RESPONSE

        with patch.object(yfw, 'get_options_chain', return_value=mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_info(self.TestData.SYMBOL, ClassUnderTest.Types.CALL, self.TestData.EXP_DATE,
                                                   self.TestData.PRICE, self.TestData.FILTER, self.TestData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL, self.TestData.EXP_DATE)

            # check results
            self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
            self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')

            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_options_handles_assertion_error(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        with patch.object(yfw, 'get_live_price') as mocked_method:

            mocked_method.side_effect = AssertionError(Exception('symbol does not exist'))

            actual_value = ClassUnderTest.get_options(symbols=[self.TestData.SYMBOL], year=2023, start_week=33, end_week=34)

            # ensure mock for get_live_price() was called
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_options_skips_too_expensive_underlying(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        mock1 = patch.object(yfw, 'get_live_price', return_value=48.1)
        mock2 = patch.object(yfw, 'get_options_chain', return_value=self.MockData.EXAMPLE_RESPONSE)

        test_filter = FilterOptions.getDefaults()
        test_filter.max_strike = 40

        with mock1 as get_live_price, mock2 as get_options_chain:

            actual_value = ClassUnderTest.get_options(symbols=[self.TestData.SYMBOL], year=2023,
                                                      start_week=33, end_week=34, filter=test_filter)

            # ensure mock for get_live_price() was called
            get_live_price.assert_called_once()
            get_live_price.assert_called_with(self.TestData.SYMBOL)

            # ensure mock for get_options_chain() was NOT called
            get_options_chain.assert_not_called()

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_options_computes_correct_expiration_dates(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        mock1 = patch.object(yfw, 'get_live_price', return_value=self.MockData.EMPTY_RESPONSE)
        mock2 = patch.object(yfw, 'get_options_chain', return_value=self.MockData.EMPTY_RESPONSE)

        symbols = [self.TestData.SYMBOL]

        with mock1, mock2 as get_options_chain:

            actual_value = ClassUnderTest.get_options(symbols=symbols, year=2023, start_week=32, end_week=36)

            # ensure mock was called with corresponding expiration dates
            get_options_chain.assert_any_call(self.TestData.SYMBOL, date.fromisoformat("2023-08-11"))
            get_options_chain.assert_any_call(self.TestData.SYMBOL, date.fromisoformat("2023-08-18"))
            get_options_chain.assert_any_call(self.TestData.SYMBOL, date.fromisoformat("2023-08-25"))
            get_options_chain.assert_any_call(self.TestData.SYMBOL, date.fromisoformat("2023-09-01"))

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')


if __name__ == '__main__':
    unittest.main()
