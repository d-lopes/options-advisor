import unittest
from unittest.mock import MagicMock

import pandas as pd

from src.ingest.aggregator import DataSourceAggregator as ClassUnderTest
from src.ingest.datasource import AbstractDataSource as abstractDataSource

from test.utils.sample_data import SampleData
from test.utils.pd_base_testcase import PandasBaseTestCase

class DataSourceAggregatorTest(PandasBaseTestCase):

    def setUp(self):
        PandasBaseTestCase.setUp(self)


    def test_empty_aggregator_has_zero_datasources(self):
    
        instance = ClassUnderTest()
    
        expected_value = 0

        actual_value = instance.getDataSourceCount()

        self.assertEqual(expected_value, actual_value, 'unexpected return value')


    def test_empty_aggregator_return_no_data(self):
    
        instance = ClassUnderTest()
    
        expected_value = pd.DataFrame([])

        actual_value = instance.getData()

        self.assertEqual(expected_value, actual_value, 'unexpected return value')


    def test_aggregator_combines_data_of_all_datasources(self):
        
        sample_value = SampleData.EXAMPLE_RESULT
        
        expected_value = pd.concat([sample_value, sample_value, sample_value])
        
        instance = ClassUnderTest()
        
        test_double_1 = abstractDataSource()
        test_double_1.load_data = MagicMock(return_value=sample_value)
        test_double_2 = abstractDataSource()
        test_double_2.load_data = MagicMock(return_value=sample_value)
        test_double_3 = abstractDataSource()
        test_double_3.load_data = MagicMock(return_value=sample_value)
        
        instance.addDataSource(test_double_1)
        instance.addDataSource(test_double_2)
        instance.addDataSource(test_double_3)
        
        actual_value = instance.getData()
        
        test_double_1.load_data.assert_called_once()
        test_double_2.load_data.assert_called_once()
        test_double_3.load_data.assert_called_once()
        
        self.assertEqual(expected_value, actual_value, 'unexpected return value')
            

if __name__ == '__main__':
    unittest.main()
