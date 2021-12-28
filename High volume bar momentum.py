# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:27:47 2021

@author: Richard
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
from collections import Counter

data = pd.read_csv('OMXSTO_DLY_STORY_B, 15.csv')

time_offset_removed =  data["time"].str[:-6]
only_date_part = data["time"].str[:-15]
only_time_part = time_offset_removed.str[11:]
    
data.insert(1,"DatePart", only_date_part) 
data.insert(2,"TimePart", only_time_part)

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
exit_price = exit_price.set_index("DatePart")


volume = data.groupby(["DatePart"]).sum()["Volume"]
adv = volume.rolling(20).mean().shift(1)

high_volume_bar = data["Volume"] > 7*data["Volume"].rolling(170).mean().shift(1)
bar_return = data["close"]/data["open"]-1
not_open = (data["TimePart"] != "09:00:00") & (data["TimePart"] != "09:15:00") 
not_close = (data["TimePart"] != "17:15:00") & (data["TimePart"] != "17:00:00")

long_pos_ind = (bar_return > 0) & high_volume_bar & not_open & not_close
short_pos_ind = (bar_return < 0) & high_volume_bar & not_open & not_close

long_exit_ind = long_pos_ind.shift(2).fillna(False)
short_exit_ind = short_pos_ind.shift(2).fillna(False)


# long_pos_ind = long_pos_ind.to_frame()
# long_pos_ind.insert(1,"DatePart",only_date_part)
# long_pos_ind = long_pos_ind.set_index("DatePart")
# long_pos_ind.columns = ["pos indicator"]

# short_pos_ind = short_pos_ind.to_frame()
# short_pos_ind.insert(1,"DatePart",only_date_part)
# short_pos_ind = short_pos_ind.set_index("DatePart")
# short_pos_ind.columns = ["pos indicator"]

long_entry_price = data[long_pos_ind]["close"].astype(float).to_frame()
short_entry_price = data[short_pos_ind]["close"].astype(float).to_frame()


# long_dates = data.iloc[long_entry_price.index]["DatePart"]
# long_exit_idx = exit_price.index.isin(long_dates)
# long_exit_price = exit_price[long_exit_idx].astype(float)

# short_dates = data.iloc[short_entry_price.index]["DatePart"]
# short_exit_idx = exit_price.index.isin(short_dates)
# short_exit_price = exit_price[short_exit_idx]
long_exit_price = data[long_exit_ind]["close"].astype(float).to_frame()
short_exit_price = data[short_exit_ind]["close"].astype(float).to_frame()

#calculate reutrns
comm = 0.0002
slippage = 0.05/100
long_strat_returns = long_exit_price["close"].div(long_entry_price["close"].values)-1-comm*2-slippage
short_strat_returns =  -(short_exit_price["close"].div(short_entry_price["close"].values)-1)-comm*2-slippage

long_short_returns =pd.concat([long_strat_returns, short_strat_returns],axis=0) #
long_short_returns = long_short_returns.sort_index()

print("avg return " + str(long_short_returns.mean()))
print("volatility " + str(long_short_returns.std()))

kelly_f = long_short_returns.mean()/(long_short_returns.std()**2)
print("kelly f " + str(kelly_f))
percent_profitable = (long_short_returns > 0).sum()/len(long_short_returns)
print("Percent profitable " + str(percent_profitable))

#plot_acf(short_strat_returns)

############################################
##stats for basic strategy
###########################################
cum_ret =(1 + long_short_returns).cumprod()
total_return = cum_ret.tail(1)-1
print("Total return " + str(total_return))
print("Number of trades " + str(len(long_short_returns)))


long_kelly_f = long_strat_returns.mean()/long_strat_returns.std()**2
short_kelly_f = short_strat_returns.mean()/short_strat_returns.std()**2

print("Long kelly " + str(long_kelly_f))
print("Short kelly " + str(short_kelly_f))

#print("Average realized volatility " + str(realized_volatility.mean()))

#print("   ")
#print('Opening range break out')
#mean_ret = cum_ret.tail(1)**(1/7)-1
##print("CAGR " + str(mean_ret[0]))

#vol = (strat_returns.std()*math.sqrt(252))
#sharpe = mean_ret/vol
#kelly_f = mean_ret/vol**2
#print("Volatility " + str(vol))
#print("Sharpe " + str(sharpe[0]))
#print("Kelly fraction " + str(kelly_f[0]))
##maxiumum drawdown
#Roll_Max = cum_ret.cummax()
#Daily_Drawdown = cum_ret/Roll_Max - 1.0
#Max_Daily_Drawdown = Daily_Drawdown.cummin()
#print("Max drawdown " + str(Max_Daily_Drawdown.tail(1)[0]))
#
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