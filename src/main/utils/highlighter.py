from enum import Enum

import main.analyzer as root

class highlighter:

    class Tags(Enum):
        MARGIN_OF_SAFETY = 'marginOfSafety'
        GOOD_YIELD = 'goodYield'
        BALANCED_PUT_CALL_RATIO = 'balancedPutCallRatio'

    @staticmethod
    def determineTags(row):
        tags = []

        #1: mark rows with a distance between strike and current price >= 10%
        if (row[root.analyzer.Fields.DISTANCE.value] >= 10):
            tags.append(highlighter.Tags.MARGIN_OF_SAFETY.value)

        #2: mark rows where collected premium is at least 1% of the cash provided as collateral
        if (row[root.analyzer.Fields.PREMIUM.value] * 100 >= row[root.analyzer.Fields.STRIKE.value]):
            tags.append(highlighter.Tags.GOOD_YIELD.value)

        #3: mark rows where ratio between open PUTs and open CALLs is relatively balanced (between 0.8 and 1.2)
        if (0.8 <= row[root.analyzer.Fields.CALLS_CNT.value] / row[root.analyzer.Fields.PUTS_CNT.value] <= 1.2):
            tags.append(highlighter.Tags.BALANCED_PUT_CALL_RATIO.value)

        return tags