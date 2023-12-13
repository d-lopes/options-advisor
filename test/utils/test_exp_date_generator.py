from datetime import date

import unittest

from src.utils.exp_date_generator import ExpiryDateGenerator as ClassUnderTest

from test.utils.sample_data import SampleData

class ExpirationDateGeneratorTest(unittest.TestCase):

    def test_get_dates_returns_expected_values_for_default_scenario(self):

        expected_value = [date.fromisoformat('2023-08-18')]
        
        # only use certain lines of mock data example response and tweak it to be compatible with method calculate_yield()
        base_date = date.fromisoformat('2023-08-18')
        actual_value = ClassUnderTest.getDates(base_date = base_date)

        # check results
        self.assertEqual(len(expected_value), len(actual_value), 'unexpected number of expiration dates')

        self.assertEqual(expected_value, actual_value, 'unexpected expiration dates')


    def test_get_dates_respects_input_parameters(self):

        expected_value = [
            date.fromisoformat('2023-08-18'), date.fromisoformat('2023-08-25'), date.fromisoformat('2023-09-01')
        ]
        
        # only use certain lines of mock data example response and tweak it to be compatible with method calculate_yield()
        base_date = date.fromisoformat('2023-08-04')
        start_week_offset = 2
        end_week_offset = 5
        actual_value = ClassUnderTest.getDates(base_date, start_week_offset, end_week_offset)

        # check results
        self.assertEqual(len(expected_value), len(actual_value), 'unexpected number of expiration dates')

        self.assertEqual(expected_value, actual_value, 'unexpected expiration dates')


    def test_get_dates_can_handle_week_overflow_at_year_end(self):

        expected_value = [
            date.fromisoformat('2023-12-22'), date.fromisoformat('2023-12-29'), date.fromisoformat('2024-01-05')
        ]
        
        # only use certain lines of mock data example response and tweak it to be compatible with method calculate_yield()
        base_date = date.fromisoformat('2023-12-15')
        start_week_offset = 1
        end_week_offset = 4
        actual_value = ClassUnderTest.getDates(base_date, start_week_offset, end_week_offset)

        # check results
        self.assertEqual(len(expected_value), len(actual_value), 'unexpected number of expiration dates')

        self.assertEqual(expected_value, actual_value, 'unexpected expiration dates')
    
    
    def test_get_dates_can_handle_arbitrary_weekdays_as_base_date(self):

        expected_value = [
            date.fromisoformat('2023-08-18'), date.fromisoformat('2023-08-25'), 
            date.fromisoformat('2023-09-01'), date.fromisoformat('2023-09-08')
        ]
        
        # only use certain lines of mock data example response and tweak it to be compatible with method calculate_yield()
        base_date = date.fromisoformat('2023-08-01')
        start_week_offset = 2
        end_week_offset = 6
        actual_value = ClassUnderTest.getDates(base_date, start_week_offset, end_week_offset)

        # check results
        self.assertEqual(len(expected_value), len(actual_value), 'unexpected number of expiration dates')

        self.assertEqual(expected_value, actual_value, 'unexpected expiration dates')
        
        
if __name__ == '__main__':
    unittest.main()
