import types

import unittest
from unittest.mock import patch

import pandas as pd
 
from src.ingest.yahoo_fin import YahooFinanceDataSource as ClassUnderTest

from yahoo_fin import stock_info as stocks, options as opts

from test.utils.sample_data import SampleData
from test.utils.mock_data import MockData
from test.utils.pd_base_testcase import PandasBaseTestCase

class YahooFinDataSourceTest(PandasBaseTestCase):

    mock_data = MockData()


    def setUp(self):
        PandasBaseTestCase.setUp(self)


    def test_get_live_price_returns_result_from_yahoo_fin(self):
    
        instance = ClassUnderTest()
    
        expected_value = SampleData.PRICE
        mocked_data = SampleData.PRICE

        with patch.object(stocks, 'get_live_price', return_value=mocked_data) as mocked_method:

            actual_value = instance.getLivePrice(ticker=SampleData.SYMBOL)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(ticker=SampleData.SYMBOL)

            # check results
            self.assertEqual(expected_value, actual_value, 'unexpected return data')


    def test_load_data_returns_options_from_yahoo_fin(self):
    
        instance = ClassUnderTest()
    
        expected_value = self.mock_data.EXAMPLE_RESPONSE.get('puts')
        mocked_data = self.mock_data.EXAMPLE_RESPONSE

        with patch.object(opts, 'get_options_chain', return_value=mocked_data) as mocked_method:

            instance.loadData(ticker=SampleData.SYMBOL, date=SampleData.EXP_DATE)
            actual_value = instance.getData(instance.OptionTypes.PUT)

            # ensure mock was called (instead of real yahoo_fin module implementation)
            mocked_method.assert_called_once()
            mocked_method.assert_called_with(ticker=SampleData.SYMBOL, date=SampleData.EXP_DATE, 
                                             raw=True, headers=types.MappingProxyType({'User-agent': 'Mozilla/5.0'}))

            # check results
            self.assertEqual(expected_value.empty, actual_value.empty, 'returned data frame is empty')
            self.assertEqual(len(expected_value.index), len(actual_value.index), 'unexpected size of data frame')
            self.assertEqual(expected_value, actual_value, 'unexpected return data')


if __name__ == '__main__':
    unittest.main()
