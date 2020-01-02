import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

style.use('ggplot')


#Usage: start time, end time , how long period, stock 1 , stock 2 , stock 3 and so on
#output is [[period 1], [period 2], ...]
def get_data(start_time,end_time,period_length,*stock_names):
    print(start_time , end_time, period_length)
    dateStart = dt.datetime(int(start_time[0:4]),int(start_time[4:6]),int(start_time[6:8]))
    dateEnd = dt.datetime(int(end_time[0:4]),int(end_time[4:6]),int(end_time[6:8]))
    dataframes = []
    for stock_name in stock_names:
        print(stock_name)
        df = web.DataReader(stock_name,'yahoo',dateStart,dateEnd); #get dataframe
        dataframes.append(df)
    build_data(dataframes)

def build_data(dataframes):
    #first lets find the first day with recorded data for each data frame
    firstDay = dt.datetime.strptime(str(dataframes[0].head().index[0]), '%Y-%m-%d %H:%M:%S')
    print(firstDay)
    for df in dataframes: #we have to know what dataframe starts latest
        tmp = dt.datetime.strptime(str(df.head().index[0]),'%Y-%m-%d %H:%M:%S');
        if tmp > firstDay:
            firstDay = tmp;
    #here we will use python dicts
    for df in dataframes:
        for index, row in df.iterrows():
            print(index)
            print(row[0],row[1])
            break

# hur kommer data se ut efter  de här 2? ^^
# svar: jag tänkte använde så kallade "python dictionary" där man har key
# och value precis som en symboltabell. I detta fall är key = dagen
# och value = data för dagen. Datat kan vara en lista med dagens data från
# alla aktier.
# När vi har en dictionary så kan vi enkelt slå upp dagar

#Usage: give me one example training data and I will label it
#output: Label , Buy/Sell.
def simple_classifier():
    pass

#this is an example of how to retrieve some data
get_data('20170101','20181231',15,'AAPL','TSLA','OOIL','COPX')
