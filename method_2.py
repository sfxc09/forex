# plot the values in a graph
# METHOD??
# take a look at current market condtion
# is it a bullish or bearish market
# METHOD on how many occasions does a 5,10,15 pip movement imply a following 5,10,15 pip movement?
# look for a 10 pip movement. when this occurs, count how many times this immediately followed by another movement
# METHOD - on how many occasions is an increase by 10 pips, followed immediately by a decrease in 5-10 pips across the same or similar time frame, and vice versa
# check previous candle data to see, eg. if the market moves up by 10 pips, then in the 10 pips before the market moved up by 10 pips, how did the market move..????
# or if the market moves down by x% from average price of previous hour, what can we expect from the hour to come..?
# make a short or long with stop loss and take profit relative to extent of bullish or bearish market condition
# I have a ~30% winrate for always going long, or always going short, or taking short/long based on coinflip. So now, I just need to increase the current winrate to 50% through a variety of additional methods

# create new file for each new method
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import time
import matplotlib.pyplot as plt

account_id = '101-004-13127690-001'
client = oandapyV20.API(access_token='871452ee8558e618bf6a16131b964ead-d1ea65c6acff1a7f9e53d7f5948ace17')

# the candlesticks start from the minute, so if you want to take a previous candlestick, it must be in the 2 min interval before the 2 min interval right now. eg time is 16:21 - previous candle was 16:18:00-16:19:59 interval, current candle is 16:20:00-16:21:69
# find patterns in historical candlestick variance

candles, high_low = [],[]
'''r = instruments.InstrumentsCandles(instrument='GBP_USD', 
                                   params={'granularity':'M1', 'count':'5000', 'from':'2020-01-23T00:00:00.000000000Z'})
client.request(r)
for candle in r.response['candles']:
    high_low.append([candle['mid']['h'], candle['mid']['l']])
    candles.append(candle['mid']['c'])'''
    
with open('1 min candles close, 201701 - 202001','r') as f:
    for line in f:
        candles.append(line[:-1])

with open('1 min candles highlow, 201701 - 202001','r') as f:
    for line in f:
        high_low.append([line[:7],line[-8:-1]])

print(type(candles[0]))
print(len(candles))
print(type(high_low[0]))

########################################################################################################
#look at average movement of the market for the past 24 hours. Make a swing trade based on it?
#eg. take first 1H candle close price as indicative of 'base' for rest of the day's market movement
#what is average pip movement up or down, for the past ten days
########################################################################################################


# working with this, include probability of outcome occuring overall, for last five years and current year
# if probability is low, maybe provide option where more than 9 candles before current one are included, eg. 'probability of x occuring is increased to x% if xxx candles are present before this sequence'
    

# METHOD
# for each candle close added to sequence, check all before it and if current close is x pips more than any value before, then take the whole list before and including current candle close and add to price_movement
# each sublist in price movement is for one sequence ending where x pip increase from final value to some value in sequence
# discarding the actual price, look instead for price movement from all candles in sequence leading up to 10 pip increase. eg. list of movements in price relative to the final price which was x pip more than the lowest price, [-1,-4,5,2,-5]


# it seems that after a 10 pip increase in price, it is almost guaranteed that a 10 pip drop will follow that can be captured with a 10 pip stop loss and take profit on 1 minute candles

###########################################################################################################
# FAILS BECAUSE PIP SPREAD EATS EVERYTHING :'(
# OTHERWISE 3500 PIP PROFIT A YEAR

# Try tHIS WITH MORE THAN M1 so pip spread has less impact!
###########################################################################################################
# if risk is more than profit, for profitable trade -(2(spread)*number of winning trades), or just take 2 away from the regular calculation. eg for five pip profit, take away 2, for five pip loss, add 2
# for fail trade, +(2(spread)*number of losing trades)
###############
# on what occasion does below trade fail?
# if you can identify a pattern which makes the trade fail, just switch to long instead of short or vice versa
# get all sequences that follow from a 5 pip increase, and fail
# find patterns in the one's that win..?
# calculate the average pip price across 5-10 pips before/after the 5 pip price movement
# moving averages???
# see if you can find any correlations-
##############
# use 1 day candle to identify previous days movement
# if market tends to go up the day after a low
# then maybe on that day, keeping going long, or make trades meant to capture large number of pips?
#################
# METHOD
# look for 10-100 pip movement in market
# look 10-20 pips behind, what is the average price movement leading up to the point where the market goes 10-100 pips in some direction. are there any similarities in movement? and on how many occassions does this movement occur, but the market doesnt go 10-100 pips in some direction. make use of moving averages, exponential moving averages and so on
#################
price_movement, sequence = [],[]
TEST = False
count = 0
fails, wins = [],[]
uptrend = downtrend = 0
for c,i in enumerate(candles):
    if not sequence:
        sequence.append(f'sequence starts here')
    sequence.append(i)
    
    if TEST:
        count+=1
        if ((float(high_low[c][0]) - peak) >= 0.0005) : # because pip spread, this is  5+1.5 loss. you buy 1.5 pips below the market, so 5 pip stop loss is actually 6.5 pips
            sequence.append(f'price increased by 5 pips after {count} candles')
            TEST = False
            price_movement.append(sequence)
            fails.append(sequence)
            sequence = []
            count = 0
            uptrend+=1
        elif ((float(high_low[c][1]) - peak) <= -0.005): 
            sequence.append(f'price decreased by 20 pips after {count} candles')
            TEST = False
            price_movement.append(sequence)
            wins.append(sequence)
            sequence = []
            count = 0
            downtrend+=1
        continue
                        
    # if previous values are 4 pips less than current value
    for value in sequence:
        try: 
            
            if ((float(high_low[c][1])-float(value)) <= -0.0005): # TRY THIS METHOD
                # see whether going short/long is more profitable after 5 pip increase/decrease
                # eg. if short is more profitable after 5 pip increase, and vice versa, set up the program so that it behaves exactly in this way. if 5 pip decrease, do this, if 5 pip increase, do this
                # GOING LONG after 5 pip decrease, with 25 pip take-profit and 5 pip stop loss, gives 800 pip profit over 6 months
                # GOING SHORT regardless both with 5 pip increases and decreases gives 800 pips over 6 months
                # GOING LONG after 5 pip increase, with 25 pip take-profit and 5 pip stop loss, gives ~650 pip profit over 6 months
                # GOING SHORT after 5 pip increase, with 50 pip take-profit, 5 pip stop-loss, gives 2800 pips over 1 year, 700 pips over 3 months, 4000 over 2 years
                sequence.append(f'sequence ends here. {i} is 10 pips greater than {value}')
                TEST = True
                peak = float(i) # this implies you are buying immediately as this candle forms completely - aka at its close price
                # take this as the price I bought at. This is where you'd enter your trade, but is this actually the price you'd manage to get? In the actual market, you'd buy as soon as there is a five pip movement from a particular spot, which might not be the high that you presume to be the trade entry here
                # unless, you wait for candle to form, and buy/sell at the candle close
                # this peak should be high_low[c], because i is the candle close, which was not what was used to calculate the 5 pip difference. it's not necessary, but it might help overall
                # x pips higher than lowest point in sequence
                break
        except Exception as e:
            pass
            #print(e) # trying to convert 'sequence starts here' to float

#print(*price_movement, sep='\n')
print(len(price_movement))
print('uptrend: '+str(uptrend), 'downtrend: '+str(downtrend))

avg_price_movement_wins = []
avg_price_movement_fails = []
# calculate average pip increase or decrease leading to pip increase
for trade in fails:
    for c,value in enumerate(trade):
        if 'sequence ends here' in value:
            lowest = value[-7:] # point from which 5 pip increase occurred 
            price_difference = [f'{float(lowest)-float(x):.5f}' for x in trade[1:c]]
            avg_price_movement_fails.append(f'{sum(map(float, price_difference))/len(price_difference):.5f}')
            break
            
for trade in wins:
    for c,value in enumerate(trade):
        if 'sequence ends here' in value:
            lowest = value[-7:] # point from which 5 pip increase occurred 
            price_difference = [f'{float(lowest)-float(x):.5f}' for x in trade[1:c]]
            avg_price_movement_wins.append(f'{sum(map(float, price_difference))/len(price_difference):.5f}')
            
            break
            

# what are the most common averages in fails, that are the least present in wins?
# to start: if there is an average that is present by more than 1 in fails, but not in wins, then print the number of occurrences in fails
# also number of candles before the pip movement up, might bear some relation to the movement after
win_counts = []
gone_over = []
for win in avg_price_movement_wins:
    if win not in gone_over: # avoid counting same value multiple times
        count = 0
        for comparison in avg_price_movement_wins:
            if comparison == win:
                count+=1
        win_counts.append([win, count])
        gone_over.append(win)
        
print(win_counts)
# counting the pip spread, for 50-5 take-profit, stop-loss -> 48-7 with the an average 2 pip spread
# to break-even, must win 15% of the time, or no. of losses must be max 6.66 times higher than no. of wins
# so no. of fails / wins must be more than less 6.66

bad_fails = [] # 0 wins for x losses, or loss rate is more than 6.66x win rate, aka no profitable
profitable_wins = []
fail_counts = []
gone_over = []
for fail in avg_price_movement_fails:
    if fail not in gone_over: # avoid counting same value multiple times
        count = 0
        for comparison in avg_price_movement_fails:
            if comparison == fail:
                count+=1
        for win in win_counts:
            if win[0] == fail:
                if int(count) / int(win[1]) > 6.66: # loss rate is more than 6.66x win rate, aka not profitable for 50/5 short, 48/7 accounting for spread
                    bad_fails.append([fail,count,win[1],f'{int(count) / int(win[1]):.2f}'])
                    fail_counts.append([fail, f'{fail}: fails {count} times, same value {win[0]} in wins list wins {win[1]} times'])
                    gone_over.append(fail)
                else:
                    print([win[0],win[1],count, f'{int(count) / int(win[1]):.2f}'])
                    profitable_wins.append(win[0])
                    fail_counts.append([fail, f'{fail}: fails {count} times, same value {win[0]} in wins list wins {win[1]} times'])
                    gone_over.append(fail)
                break
        else: # didn't find a win that had same pip movement as a fail
            fail_counts.append([fail, f'{fail}: fails {count} times, does not appear in wins list'])
            bad_fails.append([fail, count])
            gone_over.append(fail)
        
print('\n\n')
print(len(fail_counts))
print(len(bad_fails))
print(len(profitable_wins))
print(sum(map(float, profitable_wins)))

# now run the above process but below and modified:
# if there is an increase in 5 pips from the lowest point
# get the average of all points saved before the lowest point
# if the average is in the profitable_wins list, then go ahead with the trade
# if it's not, then skip until it is
# to improve profit, would allowing fails up to 3.3x work, if they balanced each other out somehow?
'''
######################################################################################################
price_movement, sequence = [],[]
TEST = False
count = 0
fails, wins = [],[]
uptrend = downtrend = 0
for c,i in enumerate(candles):
    if not sequence:
        sequence.append(f'sequence starts here')
    sequence.append(i)
    
    if TEST:
        count+=1
        if ((float(high_low[c][0]) - peak) >= 0.0005) : # because pip spread, this is  5+ 1.5-2 loss. you buy 1.5 pips below the market, so 5 pip stop loss is actually 6.5-7 pips
            sequence.append(f'price increased by 5 pips after {count} candles')
            TEST = False
            price_movement.append(sequence)
            fails.append(sequence)
            sequence = []
            count = 0
            uptrend+=1
        elif ((float(high_low[c][1]) - peak) <= -0.005): # because pip spread, this is 50- 1.5-2 win. you buy 1.5 pips below the market, so profit for you really started developing after 1.5-2 pips
            sequence.append(f'price decreased by 20 pips after {count} candles')
            TEST = False
            price_movement.append(sequence)
            wins.append(sequence)
            sequence = []
            count = 0
            downtrend+=1
        continue
                        
    # if previous values are 4 pips less than current value
    for x,value in enumerate(sequence):
        try: 
            if ((float(high_low[c][1])-float(value)) <= -0.0005) and len(sequence[1:-1]) in profitable_wins: 
                print('success '+len(sequence[1:-1]))
                sequence.append(f'sequence ends here. {high_low[c][1]} is 10 pips lower/greater than {value}')
                TEST = True 
                peak = float(high_low[c][1]) # x pips higher/lower than lowest/highest point in sequence
                break
        except Exception as e:
            pass
            #print(e) # trying to convert 'sequence starts here' to float

#print(*price_movement, sep='\n')
print(len(price_movement))
print('uptrend: '+str(uptrend), 'downtrend: '+str(downtrend))
######################################################################################################

''' '''

# taking x number of values directly before the lowest point from which a 10 pip increase occurs
# calculating the percentage +/- based on that lowest point

percentage_price_movement, percentages = [],[]
for count,sequence in enumerate(price_movement):
    comparison = lowest[count]
    for value in sequence:
        if value == comparison:
            percentage_price_movement.append(percentages)
            percentages = []
            break
        percentages.append(f'{(float(value)/float(comparison)):.3f}%')
# matplotlib
for c,x in enumerate(rounded_price_movement):
    #print([float(item) for item in x])
    if c % 15 == 0:
        plt.show()

    plt.plot([float(item) for item in x])

# use python random coin flipper
# heads go long, tails go short - 0 tails, 1 heads
# decide on stop-loss and take-profit - eg. 3,6 respectively - can fine tweak this according to market, market conditions?
# loop through candle lows and highs
# if candle low =< stop-loss, mark as 'fail'
# if candle high >= take=profit, mark as 'success'
# wait one min, then repeat the above
# store success and fails (add details of trade?) to list and compare number of wins to losses
# take note this is only across a four day period
####################################################################################
#                             BACKTESTING ALGORITHM BELOW                          #
####################################################################################
# when price moves up by 100 pips
import random

count = len(high_low)   
long_stop_loss = -0.005
long_take_profit = 0.003
short_stop_loss = 0.005
short_take_profit = -0.003
trade_end,new_entry = False,False
fail = success = coin = 0
trade_history = []
entering_price = float(candles[0]) # enter at closing price

for count,candle in enumerate(high_low):
    if new_entry: # go to the next iteration (simulate waiting one minute), then enter trade on the minute candle after that
        minutes_passed += 1
        if minutes_passed == 2:
            new_entry = False
            entering_price = float(candles[count])
            #coin = random.randint(0,1) # 0 -> tails, 1 -> heads
            print('going short' if not coin else 'going long')
        else:
            continue # wait for the next minute
    if coin: # heads, going long
        if (float(candle[0]) - entering_price) >= long_take_profit: # take-profit?
            print(f'trade ended. opening price of {entering_price}, close price of {candle[0]}. pip gain was {float(candle[0]) - entering_price:.5f}')
            success+=1
            trade_end = True
        elif (float(candle[1]) - entering_price) <= long_stop_loss: # stop-loss?
            print(f'trade ended. opening price of {entering_price}, close price of {candle[1]}. pip loss was {float(candle[1]) - entering_price:.5f}')
            fail+=1
            trade_end = True
    
    if not coin: # tails, going short
        if (float(candle[1]) - entering_price) <= short_take_profit: # take-profit?
            print(f'trade ended. opening price of {entering_price}, close price of {candle[0]}. pip gain was {entering_price - float(candle[1]):.5f}')
            success+=1
            trade_end = True
        elif (float(candle[0]) - entering_price) >= short_stop_loss: # stop-loss?
            print(f'trade ended. opening price of {entering_price}, close price of {candle[1]}. pip loss was {entering_price - float(candle[0]):.5f}')
            fail+=1
            trade_end = True
        
    
    if trade_end:
        minutes_passed = 0
        trade_end = False
        new_entry = True # to be able to wait one minute

print(fail, success)
###################################################################################################################
###################################################################################################################
###################################################################################################################


# TODO read from file to get candle_history to save startup time
with open('candle_history','w') as f:
    f.write(''.join(map(str, candle_history)))

# looking for candles that are green, taking it and 9 candles before
potential_pattern = []
prev_values = candle_history[:9] # sequences ending in green candlestick
for value in candle_history[9:]:
    if (int(value) == 1): #            
        prev_values.append(value)
        potential_pattern.append(''.join(list(map(str, prev_values[-10:]))))
        print(''.join(list(map(str, prev_values[-10:]))))
    else:
        prev_values.append(value)
        
# looking for instances where patterns that end in green candle develop, but end up forming red or same candle instead
# add each found instance to 'fails' list
prev_values = candle_history[:9]  
wins = potential_pattern[:]
fails = []
done = []
for c,pattern in enumerate(wins): 
    if pattern not in done:
        for value in candle_history[9:]:
            prev_values.append(value)
            sequence = ''.join(list(map(str, prev_values[-10:]))) # take last 10 values from prev_values and make into string
            if (sequence[:9] == pattern[:9]) and (sequence[-1] != pattern[-1]):
                print(pattern, pattern[:9], pattern[-1], sequence, sequence[:9], sequence[-1])
                fails.append(sequence) # add the failed sequence
        done.append(pattern) # avoid counting this item again
        prev_values = candle_history[:10]

# takes each sequence which ends in green, counts how many times this sequence ends not in green by comparing itself to each fail in 'fails' list
patterns = []
for pattern in wins:
    if pattern not in patterns: # avoid counting same appearances multiple times
        fail, success=0,0
        for comparison in fails:
            if (pattern[:9] == comparison[:9]):
                fail+=1
                failed=comparison
            
        patterns.append(pattern)
        try:
            patterns.append(failed)
            patterns.append('<- fails: '+str(fail))
        except:
            patterns.append('0 fails')

print(patterns)

# finds number of occurrences of same sequences that end in green
# TODO no need to include sequences which appear only once, as that cannot be used for any prediction
# TODO reorganise the code so that it makes sense, this algorithm should be above the one which checks for number of fails, not after it. very untidy rough code right now
done = []
for x in wins:
    if x not in done: 
        count=0
        for c,match in enumerate(wins):
            if x == match:
                print(match)
                count+=1
        done.append(x)
        #if count > 2: # if trend only appears once no reason to expect it to appear again
        index = patterns.index(x)
        patterns.insert(index, 'success: '+str(count)+' ->')

print(patterns)

########################################################################
########################################################################

# take the 9 most recent 1H candles in the market to use as the base for building a sequence
# 

########################################################################
########################################################################
class BuildPattern:
    def __init__(self):
        # first time running setup
        self.sequence, self.closes = [], []
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        
        if int(current_time[14:16]) % 2 == 1:
            current_time = current_time[:14]+str(int(current_time[14:16])-1)+current_time[16:]
        
        previous_candle = current_time[:10]+'T'+current_time[11:14]+str(int(current_time[14:16])-2)+':00'+'.000000000Z'
        # ensure you are getting previous not current value, which changes with each call
        r = instruments.InstrumentsCandles(instrument='EUR_USD', 
                                           params={'granularity':'M2', 'count':1, 'from':previous_candle})
        client.request(r) # what if we start at 00-03 seconds and 'time is in future' error occurs, or if too close to 00 point and the candle hasn't been updated yet so you get no candle as response??
        # maybe just wait until time passed since last minute is 10-30 seconds before making request
        if len(r.response) == 0:
            print('failed')
        for i in r.response['candles']:
            print('first candle: '+i['mid']['c']+' for '+current_time[11:14]+str(int(current_time[14:16])-2))
            self.closes.append(float(i['mid']['c']))
        print(r.response)
        time.sleep(0.5) # in case mm:ss is mm:00 - could be less than a second until main loop starts which might mean having same first and second values
        
    def build_sequence(self, candle_close):
        if candle_close > self.closes[-1]:
            self.sequence.append(1)
        elif candle_close < self.closes[-1]:
            self.sequence.append(0)
        else:
            self.sequence.append(2)
        
        self.closes.append(candle_close)
        print(''.join(map(str, self.sequence)))
        
        
sequencer = BuildPattern()     
time.sleep(1) # why?

# check every 0.5 seconds to see if immediate previous 5 min candle has been formed
# from then on keep trying every second to see if that previous candle is shown on oanda, use try except to avoid time error 
# this might not be necessary anymore as the code was built around mistakenly getting the current developing candle in the code below as opposed to the previous one. shouldn't be any errors getting the past one..?
# records the minute mark that is a multiple of 2 and use it for the 'from' parameter until that candle appears in oanda command output. should instead be getting the candle that was BEFORE the 2 minute mark, because previous candle end at mm:59, and current candle begins at mm:00
# once the candle is found, break out of loop and wait to re enter until current time is again a multiple of 2

# keep track of x number of candles to see if potential pattern may develop 
# looking for candlestick pattern that could be imported from file as list, keep comparing every candle sequence built to previous pattern basically

while True: 
    # wait for minutes to be multiple of 2
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    previous_candle_time = int(current_time[14:16])
    
    #debugging
    if int(current_time[17:]) % 30 == 0:
        print(current_time[17:])
    
    if (previous_candle_time % 2 == 0) and (int(current_time[17:]) == 0): # looking for 2 min candlesticks
        trade_time = current_time[:10]+'T'+current_time[11:14]+str(int(current_time[14:16])-2)+':00'+'.000000000Z'
        print(trade_time)
        
        # stay in this loop until we get an output for this command, implying previous candlestick formed
        # we are getting the current changing candle with this, see above and above for more info
        try:
            r = instruments.InstrumentsCandles(instrument="EUR_USD", params={'granularity':'M2', 'count':1, 'from':trade_time})
            client.request(r)
            if len(r.response['candles']) == 0: # 'time in future' error means this clause only reached if we have a candle response
                candle_found = False
            else:
                candle_found = True 
        except Exception as e: # time is ahead of oanda server, error so no candlestick response
            print(e)
            candle_found = False
            
        while not candle_found:
            print('candlestick retrieval failed, trying again..')
            time.sleep(1)
            try:
                client.request(r)
                if len(r.response['candles']) == 1:
                    candle_found = True
            except Exception as e: # time in future error
                print(e)
                
        print(r.response)
        for i in r.response['candles']:
            close_value = i['mid']['c']
            print('candle from '+current_time[11:14]+str(int(current_time[14:16])-4)+' to '+current_time[11:14]+str(int(current_time[14:16])-2)+' closed at '+close_value)
            sequencer.build_sequence(float(close_value))
            
    time.sleep(0.5)'''
    
