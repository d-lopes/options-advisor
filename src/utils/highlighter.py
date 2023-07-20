
class highlighter:

    @staticmethod
    def determine(row):
        highlights = "["
        if (row['Distance (%)'] >= 10):
            highlights = highlights + "marginOfSafety,"

        if (row['Premium'] * 100 >= row['Strike']):
            highlights = highlights + "goodYield,"

        return highlights + "]"