import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

style.use('ggplot')


#Usage: start time, end time , how long period, stock 1 , stock 2 , stock 3 and so on
#output is [[period 1], [period 2], ...]
def get_data(start_time,end_time,period_length,*stock_names):
    #print(start_time , end_time, period_length)
    dateStart = dt.datetime(int(start_time[0:4]),int(start_time[4:6]),int(start_time[6:8]))
    dateEnd = dt.datetime(int(end_time[0:4]),int(end_time[4:6]),int(end_time[6:8]))
    dataframes = []
    tmp = 1
    for stock_name in stock_names:
        print("stock ",tmp,": ",stock_name,sep='')
        tmp = tmp +1
        df = web.DataReader(stock_name,'yahoo',dateStart,dateEnd); #get dataframe
        dataframes.append(df)
    build_data(dataframes)

def build_data(dataframes):
    print("Daily data: ","1)",dataframes[0].columns.values[0]," 2)",dataframes[0].columns.values[1]," 3)",dataframes[0].columns.values[2],sep='')
    #first lets find the first day with recorded data for each data frame
    firstDay = dt.datetime.strptime(str(dataframes[0].head().index[0]), '%Y-%m-%d %H:%M:%S')
    for df in dataframes: #we have to know what dataframe starts latest
        #print(df.head())
        tmp = dt.datetime.strptime(str(df.head().index[0]),'%Y-%m-%d %H:%M:%S')
        if tmp > firstDay:
            firstDay = tmp;
    #here we will use python dicts
    dictionary = {} #this is our dictionary with {key:value}
    lastDay = dt.datetime(2097,4,12) #arbitrary last day
    for df in dataframes: #iterate different stocks
        dayBefore = dt.datetime.strptime(str(df.head().index[0]),'%Y-%m-%d %H:%M:%S')
        copyWhenNoData = df.head(1).to_numpy()[0][0:3]
        for index, row in df.iterrows(): #iterate days
            day = dt.datetime.strptime(str(index),'%Y-%m-%d %H:%M:%S')
            if (day - dayBefore).days > 1: #check if day is consecutive day
                while (day - dayBefore).days > 1:
                    dayBefore += dt.timedelta(days=1) #increment one day
                    if not dayBefore < firstDay and dayBefore < lastDay:
                        if dayBefore.strftime("%Y-%m-%d") not in dictionary:
                            dictionary[dayBefore.strftime("%Y-%m-%d")] = []
                        dictionary[dayBefore.strftime("%Y-%m-%d")].append(copyWhenNoData)
            if day < firstDay:
                dayBefore = day
                copyWhenNoData = [row[0],row[1],row[2]]
                continue #all stocks don't have recorded data for this day
            if day > lastDay:
                break #we dont want more data than the last day
            if day.strftime("%Y-%m-%d") not in dictionary:
                dictionary[day.strftime("%Y-%m-%d")] = [] #if null then create empty list for the day
            dictionary[day.strftime("%Y-%m-%d")].append([row[0],row[1],row[2]])
            dayBefore = day
            copyWhenNoData = [row[0],row[1],row[2]]
        lastDay = day #the data can end here thank youuuuu

    print("Data was collected from",firstDay.strftime("%Y-%m-%d"),"to",lastDay.strftime("%Y-%m-%d"))
    #NO IT IS DONE! WE CAN RETRIEVE ANY DAY DATA wow !
    print("\nExample data from 2018-08-09:\n",dictionary['2018-08-01'])
    print()
    
    #this below is just a control that there are no gaps in recorded days
    for key in dictionary.keys():
        if len(dictionary[key]) != 4:
            print("wrong1"," ",key)
        for stock in dictionary[key]:
            if len(stock) != 3:
                print("wrong2"," ",key)
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
get_data('20170801','20181231',15,'AAPL','TSLA','OOIL','COPX')
