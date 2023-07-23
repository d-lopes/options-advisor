import pandas as pd
from datetime import date, datetime

import unittest

from src.main.utils.highlighter import Highlighter as ClassUnderTest
from src.main.analyzer import OptionsAnalyzer

class HighlighterTest(unittest.TestCase):

    class TestData:

        CURRENT_PRICE = 31.66
        TRANSACTION_COST = 2 * 3 / 100
        DAYS_PER_YEAR = 365

        CONTRACT_NAME = 'BAC230818P00031000'
        STRIKE = 35.0
        PREMIUM = 0.31
        BID = 0.30
        ASK = 0.32
        VOLUME = 1000
        OPEN_INTEREST = 5575
        IMPLIED_VOLATILITY = '21.39%'
        EXPIRATION_DATE = date.fromisoformat('2023-08-18')
        ORDER_DATE = date.fromisoformat('2023-07-21')
        HOLDING_PERIOD = EXPIRATION_DATE - ORDER_DATE

        PUTS_CNT = 5575
        CALLS_CNT = PUTS_CNT * 0.7

        DIFFERENCE = STRIKE - CURRENT_PRICE
        DISTANCE = DIFFERENCE/STRIKE * 100
        YIELD = (PREMIUM - TRANSACTION_COST) / STRIKE / HOLDING_PERIOD.days * DAYS_PER_YEAR * 100
        TICKER = 'BAC'
        TYPE = OptionsAnalyzer.Types.PUT

        EXAMPLES_COLUMNS = [OptionsAnalyzer.Fields.CONTRACT_NAME.value, OptionsAnalyzer.Fields.STRIKE.value, OptionsAnalyzer.Fields.PREMIUM.value, OptionsAnalyzer.Fields.BID.value,
                            OptionsAnalyzer.Fields.ASK.value, OptionsAnalyzer.Fields.VOLUME.value,OptionsAnalyzer.Fields.OPEN_INTEREST.value, OptionsAnalyzer.Fields.IMPLIED_VOLATILITY.value,
                            OptionsAnalyzer.Fields.EXPIRATION_DATE.value, OptionsAnalyzer.Fields.CALLS_CNT.value, OptionsAnalyzer.Fields.PUTS_CNT.value, OptionsAnalyzer.Fields.DIFFERENCE.value,
                            OptionsAnalyzer.Fields.DISTANCE.value, OptionsAnalyzer.Fields.YIELD.value, OptionsAnalyzer.Fields.TICKER.value, OptionsAnalyzer.Fields.TYPE.value,
                            OptionsAnalyzer.Fields.CURRENT_PRICE.value]

        EXAMPLES = pd.DataFrame([

            # nothing to highlight
            [CONTRACT_NAME, STRIKE, PREMIUM, BID, ASK, VOLUME, OPEN_INTEREST, IMPLIED_VOLATILITY, EXPIRATION_DATE, CALLS_CNT, PUTS_CNT, DIFFERENCE, DISTANCE, YIELD, TICKER, TYPE, CURRENT_PRICE],

            # highlight: margin of safety
            #   => distance between strike and current price >= 10%
            [CONTRACT_NAME, 35.5, PREMIUM, BID, ASK, VOLUME, OPEN_INTEREST, IMPLIED_VOLATILITY, EXPIRATION_DATE, CALLS_CNT, PUTS_CNT, 3.84, 10.82, YIELD, TICKER, TYPE, CURRENT_PRICE],

            # highlight: good yield
            #   => premium is at least 1% of the cash provided as collateral (strike * 100)
            [CONTRACT_NAME, STRIKE, 0.35, 0.33, 0.37, VOLUME, OPEN_INTEREST, IMPLIED_VOLATILITY, EXPIRATION_DATE, CALLS_CNT, PUTS_CNT, DIFFERENCE, DISTANCE, 37.18, TICKER, TYPE, CURRENT_PRICE],

            # highlight: balanced PUT/CALL Ratio
            #   => ratio between open PUTs and open CALLs is relatively balanced (between 0.8 and 1.2)
            [CONTRACT_NAME, STRIKE, PREMIUM, BID, ASK, VOLUME, OPEN_INTEREST, IMPLIED_VOLATILITY, EXPIRATION_DATE, 5575, 5575, DIFFERENCE, DISTANCE, YIELD, TICKER, TYPE, CURRENT_PRICE],
            [CONTRACT_NAME, STRIKE, PREMIUM, BID, ASK, VOLUME, OPEN_INTEREST, IMPLIED_VOLATILITY, EXPIRATION_DATE, 5575 * 0.8, 5575, DIFFERENCE, DISTANCE, YIELD, TICKER, TYPE, CURRENT_PRICE],
            [CONTRACT_NAME, STRIKE, PREMIUM, BID, ASK, VOLUME, OPEN_INTEREST, IMPLIED_VOLATILITY, EXPIRATION_DATE, 5575 * 1.2, 5575, DIFFERENCE, DISTANCE, YIELD, TICKER, TYPE, CURRENT_PRICE],
            [CONTRACT_NAME, STRIKE, PREMIUM, BID, ASK, VOLUME, OPEN_INTEREST, IMPLIED_VOLATILITY, EXPIRATION_DATE, 5575, 5575 * 0.8, DIFFERENCE, DISTANCE, YIELD, TICKER, TYPE, CURRENT_PRICE],
            [CONTRACT_NAME, STRIKE, PREMIUM, BID, ASK, VOLUME, OPEN_INTEREST, IMPLIED_VOLATILITY, EXPIRATION_DATE, 5575, 5575 * 1.2, DIFFERENCE, DISTANCE, YIELD, TICKER, TYPE, CURRENT_PRICE],

        ], columns = EXAMPLES_COLUMNS)

        ROW_WITH_NO_HIGHLIGHTS = EXAMPLES.iloc[0]
        ROW_WITH_MARGIN_OF_SAFETY = EXAMPLES.iloc[1]
        ROW_WITH_GOOD_YIELD = EXAMPLES.iloc[2]
        ROWS_WITH_BALANCED_PUT_CALL_RATIO = EXAMPLES.iloc[[3, 4, 5, 6, 7]]

    def test_determine_tags_highlights_nothing(self):

        expected_value = []

        actual_value = ClassUnderTest.determine_tags(self.TestData.ROW_WITH_NO_HIGHLIGHTS)

        self.assertEqual(expected_value, actual_value, 'unexpected tags')

    def test_determine_tags_highlights_margin_of_safety(self):

        expected_value = ['marginOfSafety']

        actual_value = ClassUnderTest.determine_tags(self.TestData.ROW_WITH_MARGIN_OF_SAFETY)

        self.assertEqual(expected_value, actual_value, 'unexpected tags')


    def test_determine_tags_highlights_good_yield(self):

            expected_value = ['goodYield']

            actual_value = ClassUnderTest.determine_tags(self.TestData.ROW_WITH_GOOD_YIELD)

            self.assertEqual(expected_value, actual_value, 'unexpected tags')

    def test_determine_tags_highlights_balanced_put_call_ratio(self):

            expected_value = ['balancedPutCallRatio']

            size = len(self.TestData.ROWS_WITH_BALANCED_PUT_CALL_RATIO.index)
            for index in range(size):
                row = self.TestData.ROWS_WITH_BALANCED_PUT_CALL_RATIO.iloc[index]
                actual_value = ClassUnderTest.determine_tags(row)

            self.assertEqual(expected_value, actual_value, 'unexpected tags for scenario ' + str(index))

if __name__ == '__main__':
    unittest.main()