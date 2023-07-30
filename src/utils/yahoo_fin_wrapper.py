import types

from yahoo_fin import stock_info as stocks, options as opts


# introduced to being able to mock out the actual calls to Yahoo Finance (done by yahoo_fin module)
class YahooFinanceWrapper:

    @staticmethod
    def get_options_chain(ticker, date=None, raw=True, headers=types.MappingProxyType({'User-agent': 'Mozilla/5.0'})):
        return opts.get_options_chain(ticker=ticker, date=date, raw=raw, headers=headers)

    @staticmethod
    def get_live_price(symbol):
        return stocks.get_live_price(symbol)
