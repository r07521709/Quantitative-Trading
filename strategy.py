# Class name must be Strategy
class Strategy():
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, '')

    def __init__(self):
        # strategy property
        self.subscribedBooks = {
            'Binance': {
                'pairs': ['BTC-USDT'],
            },
        }
        self.period = 5* 60
        self.options = {}

        # user defined class attribute
        self.close_price_trace = np.array([])
        self.ma_long = 20
        self.ma_short = 10
        self.UP = 1
        self.DOWN = 2
        self.close_price = 0.0

        # holding
        self.amount = 1.0
        self.lowerbound = 0.0
        self.buy_price = np.array()
       


    def get_current_ma_cross(self):
        s_ma = talib.SMA(self.close_price_trace, self.ma_short)[-1]
        l_ma = talib.SMA(self.close_price_trace, self.ma_long)[-1]
        if np.isnan(s_ma) or np.isnan(l_ma):
            return None

        ma = s_ma
        if self.close_price < ma*0.99:
            self.lowerbound = self.close_price
        elif self.close_price > self.lowerbound or self.close_price > ma*1.01:
            self.lowerbound = 0
            return self.UP
        return None


    # called every self.period
    def trade(self, information):

        exchange = list(information['candles'])[0]
        pair = list(information['candles'][exchange])[0]
        close_price = information['candles'][exchange][pair][0]['close']
        
        self.close_price = close_price

        # add latest price into trace
        self.close_price_trace = np.append(self.close_price_trace, [float(close_price)])
        # only keep max length of ma_long count elements
        self.close_price_trace = self.close_price_trace[-self.ma_long:]
        # calculate current ma cross status
        cur_cross = self.get_current_ma_cross()

        Log('info: ' + str(information['candles'][exchange][pair][0]['time']) + ', ' + str(information['candles'][exchange][pair][0]['open']) + ', assets' + str(self['assets'][exchange]['BTC']))

        if cur_cross is None:
            return []

        # cross up
        if cur_cross == self.UP and self.amount >= 0.1:
            self.buy_price.append(close_price)
            amount = amount - 0.1
            Log('buying, opt1:' + self['opt1'])
            return [
                {
                    'exchange': exchange,
                    'amount': 0.1,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                }
            ]
        # cross down
        for i in range(self.buy_price):
            if self.buy_price[i] > 0 and close_price >= self.buy_price[i]*1.05:
                self.buy_price[i] = 0
                amount = amount + 0.1
                Log('selling, ' + exchange + ':' + pair)
                return [
                {
                    'exchange': exchange,
                    'amount': -0.1,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                }
            ]
        return []