import pandas as pd
from datetime import datetime
import unittest

from src.analyzer import OptionsAnalyzer
from src.utils.exp_date_extractor import ExpirationDateExtractor as ClassUnderTest

from test.utils.sample_data import SampleData
from test.utils.mock_data import MockData


class ExpirationDateExtractorTest(unittest.TestCase):

    mock_data = MockData()

    def test_process(self):

        expected_value = datetime.fromisoformat('2023-08-18')

        # only use certain lines of mock data example response and tweak it to be compatible with method calculate_yield()
        test_options: pd.DataFrame = self.mock_data.EXAMPLE_RESPONSE['puts'].copy()
        test_options = test_options.rename(columns={'Last Price': OptionsAnalyzer.Fields.PREMIUM.value})
        test_options = test_options.iloc[[0]]

        col_name1 = OptionsAnalyzer.Fields.CONTRACT_NAME.value
        col_name2 = OptionsAnalyzer.Fields.EXPIRATION_DATE.value
        ede = ClassUnderTest(ordinal=10, ticker=SampleData.SYMBOL, source=col_name1, target=col_name2)
        actual_value = ede.process(test_options)

        # check results
        expected_columns = actual_value.columns
        self.assertTrue(expected_columns.__contains__(OptionsAnalyzer.Fields.EXPIRATION_DATE.value), 'EXPIRATION_DATE missing')

        actual_date = actual_value[OptionsAnalyzer.Fields.EXPIRATION_DATE.value][0]
        self.assertEqual(expected_value, actual_date, 'unexpected expiration date')


if __name__ == '__main__':
    unittest.main()
