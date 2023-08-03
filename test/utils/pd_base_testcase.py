import pandas as pd
import pandas.testing as pd_testing

import unittest


class PandasBaseTestCase(unittest.TestCase):

    def assert_frame_equal(self, a, b, msg):
        try:
            pd_testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def assert_series_equal(self, a, b, msg):
        try:
            pd_testing.assert_series_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        # enable comparison of data frames
        self.addTypeEqualityFunc(pd.DataFrame, self.assert_frame_equal)
        self.addTypeEqualityFunc(pd.Series, self.assert_series_equal)
