# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 09:44:53 2021

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

tickers = ["EVO", "SINCH", "LATO_B", "KINV_B", "NIBE_B", "EQT", "MIPS", "STORY_B", "SF", "PDX", "SBB_B", "BALD_B", "SAGA_B", "INDT", "LIFCO_B", "LAGR_B"]

for x in tickers:
    
    data = pd.read_csv('OMXSTO_DLY_'+ x + ', 15.csv')
    #data = data['time,open,high,low,close,VWAP,Upper Band,Lower Band,Volume,Volume MA'].str.split(",",expand=True)
    #data = data.rename(columns={0:"DateTime", 1:"Open", 2:"High", 3:"Low", 4:"Close", 5:"VWAP", 6:"Upper Band", 7:"Lower Band", 8:"Volume", 9:"Volume MA"})
    #data = data[["DateTime","Open","High", "Low", "Close","Volume"]]
    
    time_offset_removed =  data["time"].str[:-6]
    only_date_part = data["time"].str[:-15]
    only_time_part = time_offset_removed.str[11:]
    
    data.insert(1,"DatePart", only_date_part) 
    data.insert(2,"TimePart", only_time_part)
    
    #OPEN BAR VOLUME
    opening_rng_volume = data[data["TimePart"] == "09:00:00"]["Volume"].to_frame()
    opening_rng_volume.insert(1,"DatePart",only_date_part)
    opening_rng_volume = opening_rng_volume.set_index("DatePart")
    
    #calculate rolling 20 session opening range volume
    avg_rolling_opening_volume = opening_rng_volume.rolling(20).mean().shift(1)
    #print(x)
    print(avg_rolling_opening_volume.tail(1)["Volume"][0])
    
