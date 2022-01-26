# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 14:12:34 2022

@author: richa
"""

import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import date
from datetime import datetime
from dateutil import parser
from statsmodels.graphics.tsaplots import plot_acf

tickers = ["EVO","SINCH","LATO_B","KINV_B","NIBE_B","EQT","MIPS","STORY_B","SF","PDX","SBB_B","BALD_B","SAGA_B","INDT","LIFCO_B","LAGR_B"]
stock_returns = {}

for x in tickers:
    data = pd.read_csv('OMXSTO_DLY_'+x+', 15.csv')
    #evo_data = pd.read_csv('OMXSTO_DLY_INDT, 15.csv')
    
    time_offset_removed =  data["time"].str[:-6]
    only_date_part = data["time"].str[:-15]
    only_time_part = time_offset_removed.str[11:]
    
    data.insert(1,"DatePart", only_date_part) 
    data.insert(2,"TimePart", only_time_part)
    
    
    #DAY HIGH and DAY LOWS
    dh = data.groupby('DatePart')["high"].max().to_frame()
    dl = data.groupby('DatePart')["low"].min().to_frame()
    
    #Closing prices for the trading session, full and half session
    full_day_dates = data[data["TimePart"] == "17:15:00"]["DatePart"].to_frame()
    all_dates =  data[data["TimePart"] == "09:00:00"]["DatePart"].to_frame()
    idx = np.where(all_dates.merge(full_day_dates,how="left",indicator=True)["_merge"] == "left_only")
    half_day_dates = all_dates.iloc[idx]["DatePart"].to_frame()
    half_days_data = data[data["DatePart"].isin(half_day_dates["DatePart"])]
    half_days_data["TimePart"] == "12:45:00"
    
    
    #EXIT PRICES for both half and full sessions
    exit_price_half_day = half_days_data[half_days_data["TimePart"] == "12:45:00"]["close"]
    exit_price_full_days = data[data["TimePart"] == "17:15:00"]["close"]
    exit_price = exit_price_full_days.append(exit_price_half_day)
    
    exit_price = exit_price.sort_index()
    exit_price = exit_price.to_frame().astype(float)
    exit_price.insert(1,"DatePart",only_date_part)
    cover_price = exit_price.set_index("DatePart")
    
    #calculate realized variance using 680 (15 min) observations, roughly 20 trading sessions
    returns_squared = data["close"].astype(float).pct_change()**2
    realized_volatility = np.sqrt(returns_squared.rolling(680).sum().astype(float)).to_frame()
    
    #realized_volatility.insert(1,"TimePart",only_time_part)
    #realized_volatility.insert(2,"DatePart", only_date_part)
    #realized_volatility = realized_volatility.set_index("TimePart")
    #realized_volatility_daily = realized_volatility[realized_volatility.index == "17:15:00"]
    
    #avg_realized_vol = realized_volatility.rolling(680).mean().shift(1).to_frame()
    #avg_realized_vol.insert(1,"DatePart",only_date_part)
    #avg_realized_vol = avg_realized_vol.set_index("DatePart")
    
    #OPENING RANGE
    opening_rng_high = data[data["TimePart"] == "09:00:00"]["high"].to_frame()
    #opening_rng_high = opening_rng_high.to_frame()
    opening_rng_high.insert(1,"DatePart",only_date_part)
    opening_rng_high = opening_rng_high.set_index("DatePart")
    
    
    opening_rng_low = data[data["TimePart"] == "09:00:00"]["low"].to_frame()
    #opening_rng_high = opening_rng_high.to_frame()
    opening_rng_low.insert(1,"DatePart",only_date_part)
    opening_rng_low = opening_rng_low.set_index("DatePart")
    
    #OPEN BAR VOLUME
    opening_rng_volume = data[data["TimePart"] == "09:00:00"]["Volume"].to_frame()
    opening_rng_volume.insert(1,"DatePart",only_date_part)
    opening_rng_volume = opening_rng_volume.set_index("DatePart")
    
    #calculate rolling 20 session opening range volume
    avg_rolling_opening_volume = opening_rng_volume.rolling(20).mean().shift(1)
    
    #OPENING GAP 
    open_price = data[data["TimePart"] == "09:00:00"]["open"].to_frame().astype(float)
    open_price.insert(1,"DatePart",only_date_part)
    open_price = open_price.set_index("DatePart")
    opening_gap = open_price["open"]/cover_price["close"].shift(1)-1
    
    opening_rng_pct = (opening_rng_high["high"].astype(float) - opening_rng_low["low"].astype(float))/(opening_rng_high["high"].astype(float) + opening_rng_low["low"].astype(float)).mean()
    
    #short position logic
    dl_below_opening_low = (dl < opening_rng_low)
    high_opening_rng_volume = (opening_rng_volume["Volume"].astype(float) > 1.5*avg_rolling_opening_volume["Volume"]).to_frame()
    
    short_pos_ind = (dl_below_opening_low["low"]) & (opening_gap < 0.0) & (high_opening_rng_volume["Volume"]) & (opening_rng_pct < 0.02)
    
    
    short_sell_price = opening_rng_low[short_pos_ind].astype(float)
    
    #entry_price_no_nan = entry_price[~entry_price["High"].isnull()].astype(float)
    #exit_price_no_nan = exit_price[~entry_price["High"].isnull()].astype(float)
    
    #is stop loss hit?
    #exit_price[exit_price["Close"].astype(float) < opening_rng_low["Low"].astype(float)] =  opening_rng_low
    #TAKE OUT closing prices where we had an trade
    short_buy_price = cover_price[short_pos_ind].astype(float)
    
    #calculate reutrns
    comm = 0.0002
    slippage = 0.25/100
    short_strat_returns = short_sell_price["low"]/short_buy_price["close"]-1-2*comm-2*slippage
    
    #returns =short_strat_returns #pd.concat([long_strat_returns, short_strat_returns],axis=0) #
    #returns = returns.sort_index()
    
    stock_returns.update(short_strat_returns)
    

returns = pd.DataFrame(list(stock_returns.items()),columns=["index", "returns"])
returns = returns.set_index("index")
returns = returns.sort_index()

print("Number of trades " + str(len(returns)))

print("avg return " + str(returns.mean()))
print("volatility " + str(returns.std()))

sharpe = len(returns)*returns.mean()/(returns.std()*math.sqrt(len(returns)))
print("sharpe ratio " + str(sharpe))
kelly_f = returns.mean()/(returns.std()**2)
print("kelly f " + str(kelly_f))
percent_profitable = (returns > 0).sum()/len(returns)
print("Percent profitable " + str(percent_profitable))

############################################
##stats for basic strategy
###########################################
cum_ret =(1 + returns).cumprod()
total_return = cum_ret.tail(1)-1
print("Total return " + str(total_return["returns"][0]))

#maxiumum drawdown
Roll_Max = cum_ret.cummax()
Daily_Drawdown = cum_ret/Roll_Max - 1.0
Max_Daily_Drawdown = Daily_Drawdown.cummin()
print("Max drawdown " + str(Max_Daily_Drawdown.tail(1)["returns"][0]))

##plots
plt.plot(cum_ret)
##plt.plot(cum_long_ret)
##plt.plot(cum_short_ret)
#plt.plot(Daily_Drawdown)
#group by date and save high value it is day high (DH)

#if day high is same as high in first bar of day ie opening range then no trade
#if not then entry is opening range high + slippage

# exit is close of bar with time 17.15



#dates = evo_data.index.str.split(",")
#yourdate = parser.parse(dates)