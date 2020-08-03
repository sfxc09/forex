# loop through past historical data
# after each day candle, record how long it takes using 1-5 min candles for 52 TP or 23 SL to hit, long/short
# avoid peak spread times, don't trade over longer than a day, don't forget to record when sl/tp weren't hit

# when either end of day because sl/tp weren't hit or sl/tp was hit:
# plot and save a graph with seperate lines for h/l/o/p, for the past 10-15 candles leading up the day candle trigger, in percentage increase/decrease from the decided first candle in the graph/ record whether tp or sl hit or if neither hit and if so what the pip change was - include on the graph info on the effect of going long or short eg. short: hit SL, long: hit TP 
# once this has been done for a decided period, go through all the recorded graphs to see if there are similar patterns and calculate the profitability


# MUST NOT FORGET TO INCLUDE CANDLES WHOSE OPEN ARE SAME AS CLOSE

import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import time
import matplotlib.pyplot as plt

account_id = '101-004-13127690-001'
client = oandapyV20.API(access_token='871452ee8558e618bf6a16131b964ead-d1ea65c6acff1a7f9e53d7f5948ace17')
instrument = 'GBP_USD'

day_close, day_open, day_high_low, day_time = [],[],[],[]
r = instruments.InstrumentsCandles(instrument=instrument, 
                                    params={'granularity':'D', 'count':'260', 'from':'2017-01-29T00:00:00.000000000Z'}) 
client.request(r) 
for candle in r.response['candles']:
    day_close.append(float(candle['mid']['c']))
    day_open.append(float(candle['mid']['o']))
    day_high_low.append([float(candle['mid']['h']), float(candle['mid']['l'])])
    day_time.append(candle['time'])
    

    
    
# for each day candle, loop through min/sec candles until 23/52 hit or time reaches 8pm
def trade(testing_price, trade_price, position, stop_type):
    if position == 'short':
        if stop_type == 'tp':
            if testing_price <= trade_price:
                print(f'found trade, short - TP, time: {sec_candle["time"]}')
                return True
        elif stop_type == 'sl':
            if testing_price >= trade_price:
                print(f'found trade, short - SL, time: {sec_candle["time"]}')
                return True
        else: # price didn't hit tp or sl
            return False
            
    elif position == 'long':
        if stop_type == 'tp':
            if testing_price >= trade_price:
                print(f'found trade, long - TP, time: {sec_candle["time"]}')
                return True
        elif stop_type == 'sl':
            if testing_price <= trade_price:
                print(f'found trade, long - SL, time: {sec_candle["time"]}')
                return True
        else: # price didn't hit tp or sl
            return False
            
    

wins, fails = 0,0
patterns = []
for c,day_candle in enumerate(day_open):
    if c > 8: # need to take previous 10 candles for pattern
        r = instruments.InstrumentsCandles(instrument=instrument, 
                                        params={'granularity':'S30', 'count':'2500', 'from':day_time[c]}) 
        client.request(r) 
        
        
        long, short = False, False
        long_tp, long_sl, short_tp, short_sl = False, False, False, False
        for i,sec_candle in enumerate(r.response['candles']):
            if i == 330: # wait until ~3 hours have passed to avoid the 7 pip spread around 21-00
                trade_price = float(sec_candle['mid']['o'])
                print(f'\nopened trade at {sec_candle["time"]}, day candle: {day_time[c]}')

            elif i > 330:   
                if not long: # haven't hit long sl or tp
                    if trade(float(sec_candle['mid']['h'])-0.0052, trade_price, 'long','tp'): # long tp
                        long = True
                        long_tp = True
                    elif trade(float(sec_candle['mid']['l'])+0.0023 , trade_price, 'long', 'sl'): # long sl
                        long = True
                        long_sl = True
                
                if not short: # haven't hit short sl or tp
                    if trade(float(sec_candle['mid']['l'])+0.0052, trade_price, 'short', 'tp'): # short tp
                        short = True
                        short_tp = True
                    elif trade(float(sec_candle['mid']['h'])-0.0023, trade_price, 'short', 'sl'): # short sl
                        short = True
                        short_sl = True
                        
                
            if i == len(r.response['candles'])-1:
                # take the previous day candles, excluding current one
                pattern = []
                for z in range(1,10): # the current candle shouldn't be included, hence '1', as the trade is entered during it. the previous candle then would be the trigger for the trade
                    h = day_high_low[c-z][0]
                    l = day_high_low[c-z][1]
                    o = day_open[c-z]
                    close = day_close[c-z]
                    
                    if z == 1: # referring to trigger candle
                        if close < o: # red candle
                            if long_tp:
                                wins+=1
                            elif long_sl:
                                fails+=1
                        elif close > o: # green candle
                            if short_tp:
                                wins+=1
                            elif short_sl:
                                fails+=1
                    
                    #hloc.append([day_high_low[c-x][0], day_high_low[c-x][1], day_open[c-x], day_close[c-x]])
                    if close > o: # green candle
                        pattern.insert(0,'1')
                        plt.vlines(x=15-z, ymin=close, ymax=h) # upper wick
                        plt.vlines(x=15-z, ymin=o, ymax=close, color='green', linewidth=10) # body
                        plt.vlines(x=15-z, ymin=l, ymax=o) # lower wick
                    elif close < o: # red candle
                        pattern.insert(0,'0')
                        plt.vlines(x=15-z, ymin=o, ymax=h) # upper wick
                        plt.vlines(x=15-z, ymin=close, ymax=o, color='red', linewidth=10) # body
                        plt.vlines(x=15-z, ymin=l, ymax=close) # lower wick
                
                # negative if price is lower than trade price
                if not long: # tp/sl weren't triggered for long
                    pl = float(f"{float(sec_candle['mid']['c']) - trade_price:.5f}")
                    print(f"long - sl/tp not hit, p/l: {(float(sec_candle['mid']['c']) - trade_price)*10000:.1f} pips (spread not factored in)")
                    plt.ylabel(f"long - sl/tp not hit, p/l: {(float(sec_candle['mid']['c']) - trade_price)*10000:.1f} pips (spread not factored in)")
                else: 
                    plt.xlabel(f'short: tp {short_tp}, sl {short_sl} - long: tp {long_tp}, sl {long_sl}')
                    
                if not short: # tp/sl weren't triggered for long
                    pl = float(f"{trade_price - float(sec_candle['mid']['c']):.5f}")
                    print(f'short - sl/tp not hit, p/l: {(trade_price - float(sec_candle["mid"]["c"]))*10000:.1f} pips (spread not factored in)')
                    plt.ylabel(f'short - sl/tp not hit, p/l: {(trade_price - float(sec_candle["mid"]["c"]))*10000:.1f} pips (spread not factored in)')
                else:
                    plt.xlabel(f'short: tp {short_tp}, sl {short_sl} - long: tp {long_tp}, sl {long_sl}')
                
                #plt.savefig(f'C:\\Users\\Admin\\Documents\\Code\\forex\\candle_graphs\\{c}.png')
                plt.clf()
                patterns.append([''.join(pattern), short_tp, short_sl, long_tp, long_sl]) # must include p/l when sl/tp aren't hit
                print(patterns[-1])
                
                    
                
                    
print(*patterns, sep='\n')   
done = []
refined_patterns = []
for pattern in patterns:
    if pattern[0] not in done: # avoid counting same patterns multiple times
        ssl,stp,lsl,ltp = 0,0,0,0
        for comparison in patterns:
            if pattern[0] == comparison[0]: # five candles including trigger candle
                if comparison[1]: # short tp
                    stp+=1
                elif comparison[2]: # short sl
                    ssl+=1
                
                if comparison[3]: # long tp
                    ltp+=1
                elif comparison[4]: # long sl
                    lsl+=1
        
        done.append(pattern[0])
        refined_patterns.append([pattern[0], stp, ssl, ltp, lsl])
        
print(*refined_patterns, sep='\n')


##########################################################
# test year after using above created patterns
##########################################################

sequence,patterns = [],[]
day_close, day_open, day_high_low, day_time = [],[],[],[]
r = instruments.InstrumentsCandles(instrument=instrument, 
                                    params={'granularity':'D', 'count':'260', 'from':'2018-01-29T00:00:00.000000000Z'}) 
client.request(r) 
for candle in r.response['candles']:
    day_close.append(float(candle['mid']['c']))
    day_open.append(float(candle['mid']['o']))
    day_high_low.append([float(candle['mid']['h']), float(candle['mid']['l'])])
    day_time.append(candle['time'])
    


patterns = []
for c,day_candle in enumerate(day_open):
    if c > 10: # need to take previous 10 candles for pattern
        r = instruments.InstrumentsCandles(instrument=instrument, 
                                        params={'granularity':'S30', 'count':'2500', 'from':day_time[c]}) 
        client.request(r) 
        
        long, short = False, False
        long_tp, long_sl, short_tp, short_sl = False, False, False, False
        for i,sec_candle in enumerate(r.response['candles']):
            if i == 330: # wait until ~3 hours have passed to avoid the 7 pip spread around 21-00
                trade_price = float(sec_candle['mid']['o'])
                print(f'\nopened trade at {sec_candle["time"]}, day candle: {day_time[c]}')

            elif i > 330:   
                if not long: # haven't hit long sl or tp
                    if trade(float(sec_candle['mid']['h'])-0.0052, trade_price, 'long','tp'): # long tp
                        long = True
                        long_tp = True
                    elif trade(float(sec_candle['mid']['l'])+0.0023 , trade_price, 'long', 'sl'): # long sl
                        long = True
                        long_sl = True
                
                if not short: # haven't hit short sl or tp
                    if trade(float(sec_candle['mid']['l'])+0.0052, trade_price, 'short', 'tp'): # short tp
                        short = True
                        short_tp = True
                    elif trade(float(sec_candle['mid']['h'])-0.0023, trade_price, 'short', 'sl'): # short sl
                        short = True
                        short_sl = True
                        
            if i == len(r.response['candles'])-1:
                # take the previous day candles, excluding current one
                pattern = []
                for z in range(1,10): # the current candle shouldn't be included, hence '1', as the trade is entered during it. the previous candle then would be the trigger for the trade
                    h = day_high_low[c-z][0]
                    l = day_high_low[c-z][1]
                    o = day_open[c-z]
                    close = day_close[c-z]
                    
                    
                    #hloc.append([day_high_low[c-x][0], day_high_low[c-x][1], day_open[c-x], day_close[c-x]])
                    if close > o: # green candle
                        pattern.insert(0,'1')
                    elif close < o: # red candle
                        pattern.insert(0,'0')
                
                # negative if price is lower than trade price
                if not long: # tp/sl weren't triggered for long
                    pl = float(f"{float(sec_candle['mid']['c']) - trade_price:.5f}")
                    print(f"long - sl/tp not hit, p/l: {(float(sec_candle['mid']['c']) - trade_price)*10000:.1f} pips (spread not factored in)")
                    plt.ylabel(f"long - sl/tp not hit, p/l: {(float(sec_candle['mid']['c']) - trade_price)*10000:.1f} pips (spread not factored in)")
                else: 
                    plt.xlabel(f'short: tp {short_tp}, sl {short_sl} - long: tp {long_tp}, sl {long_sl}')
                    
                if not short: # tp/sl weren't triggered for long
                    pl = float(f"{trade_price - float(sec_candle['mid']['c']):.5f}")
                    print(f'short - sl/tp not hit, p/l: {(trade_price - float(sec_candle["mid"]["c"]))*10000:.1f} pips (spread not factored in)')
                    plt.ylabel(f'short - sl/tp not hit, p/l: {(trade_price - float(sec_candle["mid"]["c"]))*10000:.1f} pips (spread not factored in)')
                else:
                    plt.xlabel(f'short: tp {short_tp}, sl {short_sl} - long: tp {long_tp}, sl {long_sl}')
                
                #plt.savefig(f'C:\\Users\\Admin\\Documents\\Code\\forex\\candle_graphs\\{c}.png')
                plt.clf()
                patterns.append([''.join(pattern), short_tp, short_sl, long_tp, long_sl]) # must include p/l when sl/tp aren't hit
                print(patterns[-1])
                        
done = []
result_refined_patterns = []
for pattern in patterns:
    if pattern[0] not in done: # avoid counting same patterns multiple times
        ssl,stp,lsl,ltp = 0,0,0,0
        for comparison in patterns:
            if pattern[0] == comparison[0]: # candles including trigger candle
                if comparison[1]: # short tp
                    stp+=1
                elif comparison[2]: # short sl
                    ssl+=1
                
                if comparison[3]: # long tp
                    ltp+=1
                elif comparison[4]: # long sl
                    lsl+=1
        
        done.append(pattern[0])
        result_refined_patterns.append([pattern[0], stp, ssl, ltp, lsl])

done = []
win, fail = 0,0
for pattern in refined_patterns:
    if pattern[0] not in done:
        for comparison in result_refined_patterns:
            if pattern[0] == comparison[0]:
                if (pattern[1] > pattern[2]): # going short 
                    win+=comparison[1]
                    fail+=comparison[2]
                elif (pattern[3] > pattern[4]): # going long
                    win+=comparison[3]
                    fail+=comparison[4]
        done.append(patterns[0])
        
print(win,fail)
