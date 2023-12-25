import unittest
from unittest.mock import MagicMock

import pandas as pd

from src.ingest.aggregator import DataSourceAggregator as ClassUnderTest
from src.ingest.datasource import AbstractDataSource

from test.utils.sample_data import SampleData
from test.utils.mock_data import MockData
from test.utils.pd_base_testcase import PandasBaseTestCase

class DataSourceAggregatorTest(PandasBaseTestCase):

    mock_data = MockData()
    
    def setUp(self):
        PandasBaseTestCase.setUp(self)


    def test_empty_aggregator_has_zero_datasources(self):
    
        expected_value = 0

        instance = ClassUnderTest()
        actual_value = instance.getDataSourceCount()

        self.assertEqual(expected_value, actual_value, 'unexpected return value')


    def test_empty_aggregator_return_no_data(self):
    
        expected_value = pd.DataFrame(columns=AbstractDataSource.DATA_FIELDS)

        instance = ClassUnderTest()
        instance.loadData(ticker=SampleData.SYMBOL, date=SampleData.EXP_DATE)
        actual_value = instance.getData()
        
        self.assertEqual(expected_value, actual_value, 'unexpected return value')


    def test_aggregator_combines_data_of_all_datasources(self):
        
        empty_value = self.mock_data.get_empty_data(AbstractDataSource.OptionTypes.PUT)
        expected_value = pd.concat([empty_value, empty_value, empty_value])
        
        test_double_1 = AbstractDataSource()
        test_double_1.loadData = MagicMock()
        test_double_1.getData = MagicMock(side_effect=self.mock_data.get_empty_data)
        
        test_double_2 = AbstractDataSource()
        test_double_2.loadData = MagicMock()
        test_double_2.getData = MagicMock(side_effect=self.mock_data.get_empty_data)
 
        test_double_3 = AbstractDataSource()
        test_double_3.loadData = MagicMock()
        test_double_3.getData = MagicMock(side_effect=self.mock_data.get_empty_data)
        
        instance = ClassUnderTest()
        instance.addDataSource(test_double_1)
        instance.addDataSource(test_double_2)
        instance.addDataSource(test_double_3)
        
        instance.loadData(ticker=SampleData.SYMBOL, date=SampleData.EXP_DATE)
        actual_value = instance.getData()
        
        test_double_1.loadData.assert_called_once()
        test_double_2.loadData.assert_called_once()
        test_double_3.loadData.assert_called_once()
        
        self.assertEqual(expected_value, actual_value, 'unexpected return value')
            

if __name__ == '__main__':
    unittest.main()
