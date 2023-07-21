from enum import Enum

import src.main.analyzer as root

class Highlighter:

    class Tags(Enum):
        MARGIN_OF_SAFETY = 'marginOfSafety'
        GOOD_YIELD = 'goodYield'
        BALANCED_PUT_CALL_RATIO = 'balancedPutCallRatio'

    @staticmethod
    def determineTags(row):
        tags = []

        #1: mark rows with a distance between strike and current price >= 10%
        if (row[root.Analyzer.Fields.DISTANCE.value] >= 10):
            tags.append(Highlighter.Tags.MARGIN_OF_SAFETY.value)

        #2: mark rows where collected premium is at least 1% of the cash provided as collateral
        if (row[root.Analyzer.Fields.PREMIUM.value] * 100 >= row[root.Analyzer.Fields.STRIKE.value]):
            tags.append(Highlighter.Tags.GOOD_YIELD.value)

        #3: mark rows where ratio between open PUTs and open CALLs is relatively balanced (between 0.8 and 1.2)
        if (0.8 <= row[root.Analyzer.Fields.CALLS_CNT.value] / row[root.Analyzer.Fields.PUTS_CNT.value] <= 1.2):
            tags.append(Highlighter.Tags.BALANCED_PUT_CALL_RATIO.value)

        return tags