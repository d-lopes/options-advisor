import pandas as pd
import pandas.testing as pd_testing
from datetime import date, datetime

import unittest
from unittest.mock import patch

from src.main.analyzer import YahooFinanceWrapper

from src.main.analyzer import OptionsAnalyzer as ClassUnderTest

class AnalyzerTest(unittest.TestCase):

    class TestData:

        CONTRACT_NAME = 'BAC230818P00031000'
        SYMBOL = 'BAC'
        MODE = ClassUnderTest.Types.PUT
        EXP_DATE = date.fromisoformat('2023-08-18')
        PRICE = 31.66
        FILTER = ClassUnderTest.Filter.getDefaults()

        EXAMPLE_RESULT = pd.DataFrame([
            [SYMBOL,  MODE.value, datetime.fromisoformat('2023-08-18'), 32.0, 37.175925925925924, PRICE, -1.073911, 0.94, 0.93, 0.95, 1252, 5575, '21.39%', ['goodYield']],
            [SYMBOL,  MODE.value, datetime.fromisoformat('2023-09-01'), 32.0, 46.8923611111111, PRICE, -1.073911, 1.17, 1.17, 1.21, 1252, 8574, '23.58%', ['goodYield']]
        ], columns=ClassUnderTest.DATA_COLUMNS)
        EXAMPLE_RESULT = EXAMPLE_RESULT.reset_index(drop=True)

    class MockData:

        # Contract Name, Last Trade Date, Strike, Last Price, Bid, Ask, Change, % Change, Volume, Open Interest, Implied Volatility
        COLUMNS = [ClassUnderTest.Fields.CONTRACT_NAME.value, 'Last Trade Date', ClassUnderTest.Fields.STRIKE.value, 'Last Price',
                    ClassUnderTest.Fields.BID.value, ClassUnderTest.Fields.ASK.value, 'Change', '% Change', ClassUnderTest.Fields.VOLUME.value,
                    ClassUnderTest.Fields.OPEN_INTEREST.value, ClassUnderTest.Fields.IMPLIED_VOLATILITY.value]

        EMPTY_RESPONSE = None
        EXAMPLE_RESPONSE = None

    def assert_frame_equal(self, a, b, msg):
        try:
            pd_testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        # enable comparison of data frames
        self.addTypeEqualityFunc(pd.DataFrame, self.assert_frame_equal)

        self.MockData.EMPTY_RESPONSE = {}
        self.MockData.EMPTY_RESPONSE['puts'] = pd.DataFrame(columns=self.MockData.COLUMNS)
        self.MockData.EMPTY_RESPONSE['calls'] = pd.DataFrame(columns=self.MockData.COLUMNS)

        put_data = [
            ['BAC230818P00015000', '2023-07-07 3:30PM EDT', 15.0, 0.01, 0.00, 0.01, 0.00, '-', 25, 2258, '96.88%'],
            ['BAC230818P00016000', '2023-07-12 2:01PM EDT', 16.0, 0.01, 0.00, 0.01, 0.00, '-', 150, 1578, '87.50%'],
            ['BAC230818P00021000', '2023-07-20 11:57AM EDT', 21.0, 0.01, 0.01, 0.02, 0.00, '-', 27, 4659, '62.50%'],
            ['BAC230818P00025000', '2023-07-21 9:43AM EDT', 25.0, 0.02, 0.02, 0.03, 0.00, '-', 20, 9986, '42.19%'],
            ['BAC230818P00026000', '2023-07-20 3:52PM EDT', 26.0, 0.04, 0.03, 0.04, 0.00, '-', 104, 23523, '37.89%'],
            ['BAC230818P00027000', '2023-07-21 9:34AM EDT', 27.0, 0.05, 0.04, 0.05, 0.01, '+25.00%', 3, 15689, '33.20%'],
            ['BAC230818P00028000', '2023-07-21 10:00AM EDT', 28.0, 0.07, 0.06, 0.07, 0.00, '-', 18, 28109, '28.91%'],
            ['BAC230818P00029000', '2023-07-21 10:04AM EDT', 29.0, 0.12, 0.11, 0.12, 0.01, '+9.09%', 90, 23504, '25.68%'],
            ['BAC230818P00030000', '2023-07-21 10:04AM EDT', 30.0, 0.23, 0.23, 0.24, 0.01, '+4.55%', 167, 28255, '23.44%'],
            ['BAC230818P00031000', '2023-07-21 9:59AM EDT', 31.0, 0.48, 0.48, 0.49, 0.03, '+6.67%', 54, 4191, '21.97%'],
            ['BAC230818P00032000', '2023-07-21 9:59AM EDT', 32.0, 0.94, 0.93, 0.95, 0.08, '+9.30%', 55, 5575, '21.39%'],
            ['BAC230818P00033000', '2023-07-21 9:30AM EDT', 33.0, 1.49, 1.63, 1.68, -0.09, '-5.70%', 2, 3574, '23.19%'],
            ['BAC230818P00034000', '2023-07-20 2:50PM EDT', 34.0, 2.40, 2.52, 2.58, 0.00, '-', 17, 335, '27.05%'],
            ['BAC230818P00035000', '2023-07-20 9:46AM EDT', 35.0, 3.35, 3.45, 3.55, 0.00, '-', 1, 130, '32.23%'],
            ['BAC230818P00036000', '2023-07-19 11:27AM EDT', 36.0, 4.64, 4.45, 4.60, 0.00, '-', 1, 72, '40.72%'],
            ['BAC230818P00037000', '2023-06-28 3:54PM EDT', 37.0, 8.95, 5.45, 5.55, 0.00, '-', 123, 37, '43.65%'],
            ['BAC230818P00038000', '2023-03-30 9:50AM EDT', 38.0, 9.10, 8.55, 8.95, 0.00, '-', 5, 0, '127.25%'],
            ['BAC230818P00039000', '2023-06-26 12:22PM EDT', 39.0, 10.85, 7.45, 7.55, 0.00, '-', 12, 0, '50.29%'],
            ['BAC230818P00040000', '2023-06-21 1:14PM EDT', 40.0, 11.35, 8.50, 8.60, 0.00, '-', 1, 0, '58.40%'],
            ['BAC230818P00041000', '2023-06-29 1:05PM EDT', 41.0, 12.30, 9.45, 9.55, 0.00, '-', 1, 0, '59.08%'],
            ['BAC230818P00042000', '2023-06-29 1:05PM EDT', 42.0, 13.30, 10.45, 10.55, 0.00, '-', 1, 0, '63.28%'],
            ['BAC230901P00027000', '2023-07-20 3:51PM EDT', 27.0, 0.08, 0.06, 0.09, 0.00, '-', 252, 8007, '30.86%'],
            ['BAC230901P00028000', '2023-07-20 1:12PM EDT', 28.0, 0.14, 0.10, 0.13, 0.00, '-', 7, 191, '27.64%'],
            ['BAC230901P00029000', '2023-07-21 9:46AM EDT', 29.0, 0.21, 0.20, 0.22, 0.00, '-', 1, 199, '25.49%'],
            ['BAC230901P00030000', '2023-07-21 9:42AM EDT', 30.0, 0.38, 0.38, 0.41, -0.01, '-2.56%', 1, 185, '24.51%'],
            ['BAC230901P00031000', '2023-07-21 10:00AM EDT', 31.0, 0.71, 0.68, 0.73, 0.05, '+7.58%', 5, 467, '23.88%'],
            ['BAC230901P00032000', '2023-07-21 9:35AM EDT', 32.0, 1.17, 1.17, 1.21, 0.01, '+0.86%', 3, 8574, '23.58%'],
            ['BAC230901P00034000', '2023-07-17 9:58AM EDT', 34.0, 4.55, 1.81, 2.74, 0.00, '-', 1, 1, '27.34%'],
            ['BAC230901P00035000', '2023-07-18 11:42AM EDT', 35.0, 4.50, 2.78, 3.65, 0.00, '-', '-', 1, '30.23%']
        ]

        call_data = [
            ['BAC230818C00019000', '2023-07-17 9:36AM EDT', 19.0, 10.50, 12.55, 12.65, 0.00, '-',' -', 1, '0.00%'],
            ['BAC230818C00020000', '2023-07-17 10:43AM EDT', 20.0,9.54,11.60,11.65,0.00, '-', 1,61, '0.00%'],
            ['BAC230818C00022000', '2023-07-20 9:37AM EDT', 22.0,9.80,9.55,9.70,0.00, '-', 2,86, '53.91%'],
            ['BAC230818C00025000', '2023-07-19 10:22AM EDT', 25.0,6.50,6.60,6.70,0.00, '-', 5,5, '37.11%'],
            ['BAC230818C00026000', '2023-07-18 9:55AM EDT', 26.0,4.65,5.65,5.75,0.00, '-',' -', 2, '36.91%'],
            ['BAC230818C00027000', '2023-07-19 12:08PM EDT', 27.0,4.85,4.65,4.80,0.00, '-', 3, 12, '34.57%'],
            ['BAC230818C00028000', '2023-07-20 3:39PM EDT', 28.0,3.90,3.65,3.80,0.00, '-', 5, 54, '28.42%'],
            ['BAC230818C00029000', '2023-07-21 10:00AM EDT', 29.0,2.84,2.79,2.86,-0.09, '-3.07%', 1, 297, '24.90%'],
            ['BAC230818C00030000', '2023-07-21 9:55AM EDT', 30.0,2.03,1.94,2.02,-0.07, '-3.33%', 30, 385, '23.15%'],
            ['BAC230818C00031000', '2023-07-21 9:48AM EDT', 31.0,1.30,1.23,1.29,-0.12, '-8.45%', 35, 411, '21.58%'],
            ['BAC230818C00032000', '2023-07-21 9:38AM EDT', 32.0,0.72,0.70,0.74,-0.11, '-13.25%', 10, 1252, '20.70%'],
            ['BAC230818C00033000', '2023-07-21 9:45AM EDT', 33.0,0.37,0.35,0.38,-0.07, '-15.91%', 28, 509, '20.26%'],
            ['BAC230818C00034000', '2023-07-21 9:48AM EDT', 34.0,0.17,0.16,0.19,-0.04, '-19.05%', 23, 117, '20.61%'],
            ['BAC230818C00035000', '2023-07-20 3:49PM EDT', 35.0,0.10,0.07,0.10,0.00, '-', 13, 90, '21.58%'],
            ['BAC230818C00036000', '2023-07-19 12:06PM EDT', 36.0,0.05,0.03,0.07,0.00, '-', 250, 287, '23.93%'],
            ['BAC230818C00037000', '2023-07-20 9:30AM EDT', 37.0,0.05,0.00,0.11,0.00, '-', 2, 3, '30.66%'],
            ['BAC230818C00038000', '2023-07-17 1:22PM EDT', 38.0,0.02,0.00,0.10,0.00, '-',' -', 1, '33.89%'],
            ['BAC230818C00039000', '2023-07-13 3:05PM EDT', 39.0,0.02,0.00,0.10,0.00, '-',' -', 21, '37.50%'],
            ['BAC230901C00019000', '2023-07-17 9:36AM EDT', 19.0,10.50,12.55,12.65,0.00, '-',' -', 1, '0.00%'],
            ['BAC230901C00020000', '2023-07-17 10:43AM EDT', 20.0,9.54,11.60,11.65,0.00, '-', 1, 61, '0.00%'],
            ['BAC230901C00022000', '2023-07-20 9:37AM EDT', 22.0,9.80,9.55,9.70,0.00, '-', 2, 86, '53.91%'],
            ['BAC230901C00025000', '2023-07-19 10:22AM EDT', 25.0,6.50,6.60,6.70,0.00, '-', 5, 5, '37.11%'],
            ['BAC230901C00026000', '2023-07-18 9:55AM EDT', 26.0,4.65,5.65,5.75,0.00, '-',' -', 2, '36.91%'],
            ['BAC230901C00027000', '2023-07-19 12:08PM EDT', 27.0,4.85,4.65,4.80,0.00, '-', 3, 12, '34.57%'],
            ['BAC230901C00028000', '2023-07-20 3:39PM EDT', 28.0,3.90,3.65,3.80,0.00, '-', 5, 54, '28.42%'],
            ['BAC230901C00029000', '2023-07-21 10:00AM EDT', 29.0,2.84,2.79,2.86,-0.09, '-3.07%', 1, 297, '24.90%'],
            ['BAC230901C00030000', '2023-07-21 9:55AM EDT', 30.0,2.03,1.94,2.02,-0.07, '-3.33%', 30, 385, '23.15%'],
            ['BAC230901C00031000', '2023-07-21 9:48AM EDT', 31.0,1.30,1.23,1.29,-0.12, '-8.45%', 35, 411, '21.58%'],
            ['BAC230901C00032000', '2023-07-21 9:38AM EDT', 32.0,0.72,0.70,0.74,-0.11, '-13.25%', 10, 1252, '20.70%'],
            ['BAC230901C00033000', '2023-07-21 9:45AM EDT', 33.0,0.37,0.35,0.38,-0.07, '-15.91%', 28, 509, '20.26%'],
            ['BAC230901C00034000', '2023-07-21 9:48AM EDT', 34.0,0.17,0.16,0.19,-0.04, '-19.05%', 23, 117, '20.61%'],
            ['BAC230901C00035000', '2023-07-20 3:49PM EDT', 35.0,0.10,0.07,0.10,0.00, '-', 13, 90, '21.58%'],
            ['BAC230901C00036000', '2023-07-19 12:06PM EDT', 36.0,0.05,0.03,0.07,0.00, '-', 250, 287, '23.93%'],
            ['BAC230901C00037000', '2023-07-20 9:30AM EDT', 37.0,0.05,0.00,0.11,0.00, '-', 2, 3, '30.66%'],
            ['BAC230901C00038000', '2023-07-17 1:22PM EDT', 38.0,0.02,0.00,0.10,0.00, '-',' -', 1, '33.89%'],
            ['BAC230901C00039000', '2023-07-13 3:05PM EDT', 39.0,0.02,0.00,0.10,0.00, '-',' -', 21, '37.50%'],
        ]

        self.MockData.EXAMPLE_RESPONSE = {}
        self.MockData.EXAMPLE_RESPONSE['puts'] = pd.DataFrame(put_data, columns=self.MockData.COLUMNS)
        self.MockData.EXAMPLE_RESPONSE['calls'] = pd.DataFrame(call_data, columns=self.MockData.COLUMNS)

    def test_get_exp_date_from_contract_name(self):

        expected_value = datetime.fromisoformat('2023-08-18')

        actual_value = ClassUnderTest.exp_date_from_contract_name(self.TestData.CONTRACT_NAME, self.TestData.SYMBOL)

        self.assertEqual(expected_value, actual_value, 'unexpected expiration date')

    def test_get_info_transforms_empty_input(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)
        mocked_data = self.MockData.EMPTY_RESPONSE

        with patch.object(YahooFinanceWrapper, 'get_options_chain', return_value = mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_info(self.TestData.SYMBOL, self.TestData.MODE,
                self.TestData.EXP_DATE, self.TestData.PRICE,
                self.TestData.FILTER)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL, self.TestData.EXP_DATE)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_info_transforms_example_input(self):

        expected_value = self.TestData.EXAMPLE_RESULT
        mocked_data = self.MockData.EXAMPLE_RESPONSE

        with patch.object(YahooFinanceWrapper, 'get_options_chain', return_value = mocked_data) as mocked_method:

            actual_value = ClassUnderTest.get_info(self.TestData.SYMBOL, self.TestData.MODE,
                self.TestData.EXP_DATE, self.TestData.PRICE, self.TestData.FILTER)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(self.TestData.SYMBOL, self.TestData.EXP_DATE)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_options_skips_too_expensive_underlying(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)
        mocked_data = 40
        mocked_data_2 = self.MockData.EMPTY_RESPONSE

        with patch.object(YahooFinanceWrapper, 'get_live_price', return_value = mocked_data) as mocked_get_live_price:
            with patch.object(YahooFinanceWrapper, 'get_options_chain', return_value = mocked_data_2) as mocked_get_options_chain:

                actual_value = ClassUnderTest.get_options(symbols = [self.TestData.SYMBOL])

                # ensure mock for get_live_price() was called
                mocked_get_live_price.assert_called_once()
                mocked_get_live_price.assert_called_with(self.TestData.SYMBOL)

                # ensure mock for get_options_chain() was NOT called
                mocked_get_options_chain.assert_not_called()

                # check results
                self.assertEqual(expected_value, actual_value, 'unexpected return data')

    def test_get_options_computes_correct_expiration_dates(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)
        mocked_data = self.MockData.EMPTY_RESPONSE

        with patch.object(YahooFinanceWrapper, 'get_live_price', return_value = mocked_data):
            with patch.object(YahooFinanceWrapper, 'get_options_chain', return_value = mocked_data) as mocked_method:

                actual_value = ClassUnderTest.get_options(symbols = [self.TestData.SYMBOL], year = 2023, start_week = 32, end_week = 36)

                # ensure mock was called with corresponding expiration dates
                mocked_method.assert_any_call(self.TestData.SYMBOL, date.fromisoformat("2023-08-11"))
                mocked_method.assert_any_call(self.TestData.SYMBOL, date.fromisoformat("2023-08-18"))
                mocked_method.assert_any_call(self.TestData.SYMBOL, date.fromisoformat("2023-08-25"))
                mocked_method.assert_any_call(self.TestData.SYMBOL, date.fromisoformat("2023-09-01"))

                # check results
                self.assertEqual(expected_value, actual_value, 'unexpected return data')

if __name__ == '__main__':
    unittest.main()