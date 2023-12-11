import pandas as pd
from datetime import date

import unittest
from unittest.mock import patch

from src.ingest.yahoo_fin import YahooFinanceDataSource as yfds

from src.analyzer import OptionsAnalyzer as ClassUnderTest
from src.utils.opts_tbl_filter import OptionsTableFilter

from test.utils.sample_data import SampleData
from test.utils.mock_data import MockData
from test.utils.pd_base_testcase import PandasBaseTestCase


class AnalyzerTest(PandasBaseTestCase):

    mock_data = MockData()
    classUnderTest = ClassUnderTest()

    def setUp(self):
        PandasBaseTestCase.setUp(self)


    def test_get_info_handles_value_error_input(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        with patch.object(yfds, 'loadData') as mocked_method:

            mocked_method.side_effect = ValueError(Exception('symbol does not exist'))

            actual_value = self.classUnderTest.get_info(SampleData.SYMBOL, SampleData.MODE, SampleData.EXP_DATE,
                                                   SampleData.PRICE, SampleData.FILTER, SampleData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(ticker=SampleData.SYMBOL, date=SampleData.EXP_DATE)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')
            

    def test_get_info_transforms_empty_input(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        mockA = patch.object(yfds, 'loadData')
        mockB = patch.object(yfds, 'getData', side_effect=self.mock_data.get_empty_data) 
        
        with mockB, mockA as mocked_method:

            actual_value = self.classUnderTest.get_info(SampleData.SYMBOL, SampleData.MODE, SampleData.EXP_DATE,
                                                   SampleData.PRICE, SampleData.FILTER, SampleData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(ticker=SampleData.SYMBOL, date=SampleData.EXP_DATE)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')
            

    def test_get_info_4_puts_transforms_example_input(self):

        expected_value = SampleData.EXAMPLE_RESULT
        
        mockA = patch.object(yfds, 'loadData')
        mockB = patch.object(yfds, 'getData', side_effect=self.mock_data.get_example_data) 
        
        with mockB, mockA as mocked_method:

            actual_value = self.classUnderTest.get_info(SampleData.SYMBOL, SampleData.MODE, SampleData.EXP_DATE,
                                                   SampleData.PRICE, SampleData.FILTER, SampleData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(ticker=SampleData.SYMBOL, date=SampleData.EXP_DATE)

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
        expected_value[ClassUnderTest.Fields.VOLUME.value] = 10
        expected_value[ClassUnderTest.Fields.IMPLIED_VOLATILITY.value] = '20.70%'

        mockA = patch.object(yfds, 'loadData')
        mockB = patch.object(yfds, 'getData', side_effect=self.mock_data.get_example_data) 
        
        with mockB, mockA as mocked_method:

            actual_value = self.classUnderTest.get_info(SampleData.SYMBOL, ClassUnderTest.Types.CALL, 
                                                        SampleData.EXP_DATE, SampleData.PRICE,
                                                        SampleData.FILTER, SampleData.ORDER_DATE)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(ticker=SampleData.SYMBOL, date=SampleData.EXP_DATE)

            # check results
            self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
            self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')

            self.assertEqual(expected_value, actual_value, 'unexpected return data')


    def test_get_options_handles_assertion_error(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        with patch.object(yfds, 'getLivePrice') as mocked_method:

            mocked_method.side_effect = AssertionError(Exception('symbol does not exist'))

            actual_value = self.classUnderTest.get_options(symbols=[SampleData.SYMBOL], year=2023, start_week=33, end_week=34)

            # ensure mock for get_live_price() was called
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(SampleData.SYMBOL)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')


    def test_get_options_skips_too_expensive_underlying(self):

        expected_value = pd.DataFrame(columns=ClassUnderTest.DATA_COLUMNS)

        mock1 = patch.object(yfds, 'getLivePrice', return_value=48.1)
        mock2 = patch.object(yfds, 'loadData')

        test_filter = OptionsTableFilter.FilterOptions.get_defaults()
        test_filter.max_strike = 40

        with mock1 as get_live_price, mock2 as get_options_chain:

            actual_value = self.classUnderTest.get_options(symbols=[SampleData.SYMBOL], year=2023,
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

        symbols = [SampleData.SYMBOL]

        mockA = patch.object(yfds, 'getLivePrice', return_value=48.1)
        mockB = patch.object(yfds, 'getData', side_effect=self.mock_data.get_empty_data)
        mockC = patch.object(yfds, 'loadData')
        
        with mockA, mockB, mockC as mocked_method:

            actual_value = self.classUnderTest.get_options(symbols=symbols, year=2023, start_week=32, end_week=36)

            # ensure mock was called with corresponding expiration dates
            mocked_method.assert_any_call(ticker=SampleData.SYMBOL, date=date.fromisoformat("2023-08-11"))
            mocked_method.assert_any_call(ticker=SampleData.SYMBOL, date=date.fromisoformat("2023-08-18"))
            mocked_method.assert_any_call(ticker=SampleData.SYMBOL, date=date.fromisoformat("2023-08-25"))
            mocked_method.assert_any_call(ticker=SampleData.SYMBOL, date=date.fromisoformat("2023-09-01"))

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')


if __name__ == '__main__':
    unittest.main()
