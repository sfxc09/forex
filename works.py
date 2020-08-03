import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import time

account_id = '101-004-13127690-001'
client = oandapyV20.API(access_token='')

# the candlesticks start from the minute, so if you want to take a previous candlestick, it must be in the 2 min interval before the 2 min interval right now. eg time is 16:21 - previous candle was 16:18:00-16:19:59 interval, current candle is 16:20:00-16:21:69

# based on the total body size of the previous 9 candles, see on how many occasions the following candle is red or green: aka if previous is -20, what candle color follows, if previous is +30, what candle color follows, and so on


# don't use a take profit as it limits the profits, but what about just using a stop loss?
# main issue with using a stop loss is if the broker partakes in stop loss hunting
# only take trades that have 1 win, 0 loss and take the 0 trade? and vice versa

# instead of recreating the whole self.categorisations with each new trade taken, meaning the count always stays at 3000.. why not instead just keep adding to the list? surely more data is better?

class Main:
    def __init__(self):
        self.instrument = 'GBP_USD'
        print(self.instrument)
        self.update_rules()
        
    def update_rules(self, dt='2013-12-29T00:00:00.000000000Z'):   
        
        self.categorisations = [[f'{i} to {i+1}', 'green ->', 0, 'red ->', 0,] for i in range(-2000,2000)]
        
        candles_close, candles_open, high_low, candles_time = [],[],[],[]
        r = instruments.InstrumentsCandles(instrument=self.instrument, 
                                           params={'granularity':'D', 'count':'3000', 'to':dt}) 
        client.request(r) 
        for candle in r.response['candles']:
            candles_close.append(float(candle['mid']['c']))
            candles_open.append(float(candle['mid']['o']))
            high_low.append([float(candle['mid']['h']), float(candle['mid']['l'])])
            candles_time.append(candle['time'])
            
        print(dt)
        print(candles_time[-1])
        # loop through 14 candles, calculate overall pip increase/decrease
        # add the next candle color and the combined 14 candle size to list
        candle_sizes, data = [],[]
        for c,item in enumerate(candles_close):
            if c > 13:
                if c == 14:
                    combined_candles = int(f'{sum(candle_sizes)*10000:.0f}') # last 14 candles 0-13 inclusive
                else:
                    combined_candles = int(f'{sum(candle_sizes[-14:])*10000:.0f}') # last 14 candles 
                
                if candles_close[c] > candles_open[c]: # current candle closed green
                    #print(f'previous 14 candles size: {combined_candles}, adding to {self.categorisations[combined_candles+2000][0]}')
                    self.categorisations[combined_candles+2000][2]+=1 # add 2000 to get right index for self.categorisations
                elif candles_close[c] < candles_open[c]: # current candle closed red
                    self.categorisations[combined_candles+2000][4]+=1
                            
                '''if c > 29:
                    data[-1].append(f'sum of past 20 day candles:     {sum(candle_sizes[-20:])*10000:.1f}')'''

                # negative if red, positive if green
                candle_sizes.append(float(f'{candles_close[c] - candles_open[c]:.5f}'))     

        print(f'\n\nfrom {candles_time[0]} to {candles_time[-1]}')

    
    ###############################################################################################
    # using data from previous year, trade coming year 
    ###############################################################################################
    def run_backtest(self):
        candles_close, candles_open, high_low, candles_time = [],[],[],[]
        r = instruments.InstrumentsCandles(instrument=self.instrument, 
                                           params={'granularity':'D', 'count':'230', 'from':'2018-01-01T00:00:00.000000000Z'}) 
        client.request(r) 
        for candle in r.response['candles']:
            candles_close.append(float(candle['mid']['c']))
            candles_open.append(float(candle['mid']['o']))
            high_low.append([float(candle['mid']['h']), float(candle['mid']['l'])])
            candles_time.append(candle['time'])
        print(candles_time[-1])

        # loop through 9 candles, calculate overall pip increase/decrease
        # add the next candle color and the combined 9 candle size to list
        candle_sizes = []
        data = []
        for c,item in enumerate(candles_close):
            if c > 13:
                if c == 14:
                    combined_candles = sum(candle_sizes) # last 9 candles 0-8 inclusive
                else:
                    combined_candles = sum(candle_sizes[-14:]) # last 9 candles 
                
                data.append([f'{combined_candles*10000:.1f}', 'green' if candles_close[c] > candles_open[c] else 'red', float(f'{abs(candles_close[c] - candles_open[c]):.5f}')]) # this would consider candle with same open/close as red

                if c > 29:
                    data[-1].append(f'sum of past 20 day candles:     {sum(candle_sizes[-20:])*10000:.1f}')
                else:
                    data[-1].append('0')

                for item in ['long (success,fail) ->',0,0,'short (success,fail) ->',0,0,0,0]:
                    data[-1].append(item)

                # negative if red, positive if green
                candle_sizes.append(float(f'{candles_close[c] - candles_open[c]:.5f}'))

                # get price info of current candle
                # take both long and short tp and sl, because could predict as red or green
                # even if the prediction turns out wrong, I would have nonetheless taken it
                r = instruments.InstrumentsCandles(instrument=self.instrument, 
                                                   params={'granularity':'S30', 'count':'2500', 'from':candles_time[c]}) 
                client.request(r) 
                print(f'current day candle dt: {candles_time[c]}')
                print('testing long')
                for i,sec_candle in enumerate(r.response['candles']):
                    if i == 330: # wait until ~3 hours have passed to avoid the 7 pip spread around 21-00
                        trade_price = float(sec_candle['mid']['o'])
                        print(f'opened trade long at {sec_candle["time"]}')
                    elif i > 330:    
                        '''# problem with this is if the high >= tp AND the same candle low <= sl
                        # this would consider the tp first, so if the above happens, only the tp would be considered, and I wouldn't know which really was first, the high or the low.. meaning the success/fail is up in the air
                        
                        # going long
                        # don't forget pip spread
                        # sl: trade_price - 0.0012
                        # tp: trade_price + 0.0022
                        if float(sec_candle['mid']['h'])-0.0102 >= trade_price:
                            data[-1][5]+=1 # success
                            print(f'found trade, long - success, time: {sec_candle["time"]}')
                            break'''
                        if float(sec_candle['mid']['l'])+0.0048 <= trade_price:
                            data[-1][6]+=1 # fail
                            print(f'found trade, long - fail, time: {sec_candle["time"]}')
                            break
                    
                    if i == len(r.response['candles'])-1:
                        # negative if price is lower than trade price
                        data[-1][10]+=(float(f"{float(sec_candle['mid']['c']) - trade_price:.5f}"))
                        print(f'trade ended at {sec_candle["time"]}')
                        break
                            
                            
                print('testing short')        
                for i,sec_candle in enumerate(r.response['candles']):
                    if i == 330: # wait until ~3 hours have passed to avoid the 7 pip spread around 21-00
                        trade_price = float(sec_candle['mid']['o'])
                        print(f'opened trade short at {sec_candle["time"]}')
                    elif i > 330:    
                        '''# problem with this is if the high >= tp AND the same candle low <= sl
                        # this would consider the tp first, so if the above happens, only the tp would be considered, and I wouldn't know which really was first, the high or the low.. meaning the success/fail is up in the air
                        
                        # going short
                        # don't forget pip spread
                        # sl: trade_price + 0.0010
                        # tp: trade_price - 0.0020
                        if float(sec_candle['mid']['l'])+0.0102 <= trade_price:
                            data[-1][8]+=1 # success
                            print(f'found trade, short - success, time: {sec_candle["time"]}')
                            break'''
                        if float(sec_candle['mid']['h'])-0.0048 >= trade_price:
                            data[-1][9]+=1 # fail
                            print(f'found trade, short - fail, time: {sec_candle["time"]}')
                            break
                            
                    if i == len(r.response['candles'])-1:
                        # negative if price is lower than trade price
                        data[-1][11]+=(float(f"{trade_price - float(sec_candle['mid']['c']):.5f}"))    
                        print(f'trade ended at {sec_candle["time"]}')
                        break
                        
                data[-1].append(candles_time[c])
                
        print(len(candles_close), len(data))
        print(*self.categorisations, sep='\n') 
        print(*data, sep='\n') 
        no_wins, no_fails = 0,0
        trades,total,trades_not_taken = 0,0,0
        for c,item in enumerate(data):
            
            print(f'time of current candle: {item[-1]}')
            
            for i in range(-2000,2040):
                if float(item[0]) >= i and float(item[0]) < i+1:
                    if self.categorisations[i+2000][2] > self.categorisations[i+2000][4]:
                        if item[1] == 'green':
                            no_wins+=item[5]
                        elif item[1] == 'red':
                            no_fails+=item[6]

                        total+=item[10]
                        trades+=1

                    elif self.categorisations[i+2000][2] < self.categorisations[i+2000][4]:
                        if item[1] == 'red':
                            no_wins+=item[8]
                        elif item[1] == 'green':
                            no_fails+=item[9]

                        total+=item[11]
                        trades+=1
                    
                    else:
                        trades_not_taken+=1
                        
            self.update_rules(dt=item[-1])

        print(no_wins, no_fails, total, trades, trades_not_taken)
        
Main().run_backtest()
