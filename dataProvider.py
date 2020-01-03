import datetime as dt
import sklearn
from sklearn import tree
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

style.use('ggplot')


#Usage: start time, end time , how long period, stock 1 , stock 2 , stock 3 and so on
#output is [[period 1], [period 2], ...]
def get_data(start_time,end_time,*stock_names):
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
    return build_data(dataframes)


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
    #NOw IT IS DONE! WE CAN RETRIEVE ANY DAY DATA wow !
    print()

    #this below is just a control that there are no gaps in recorded days
    #for key in dictionary.keys():
    #    if len(dictionary[key]) != 4:
    #        print("wrong1"," ",key)
    #    for stock in dictionary[key]:
    #        if len(stock) != 3:
    #            print("wrong2"," ",key)
    return dictionary
# hur kommer data se ut efter  de här 2? ^^
# svar: jag tänkte använde så kallade "python dictionary" där man har key
# och value precis som en symboltabell. I detta fall är key = dagen
# och value = data för dagen. Datat kan vara en lista med dagens data från
# alla aktier.
# När vi har en dictionary så kan vi enkelt slå upp dagar

#Usage: give me one example training data and I will label it
#output: Label , Buy/Sell.
def flatten(list):#helper function to flatten nested list to simple
    new_list = []
    for vals in list:
        for val in vals:
            new_list.append(val)
    return new_list
def get_features(dictionary,period_length):
    first_day = dt.datetime.strptime(list(dictionary)[0],'%Y-%m-%d')
    #NOTE: start day is first_day + period_length
    stock_count = len(dictionary[first_day.strftime("%Y-%m-%d")])
    features = []
    labels = []
    for day in dictionary.keys():
        date = dt.datetime.strptime(day,'%Y-%m-%d')
        period = flatten(dictionary[day])
        for i in range(1,period_length):
            tmp_date = (date+dt.timedelta(days=i)).strftime("%Y-%m-%d") #increment one day
            if not tmp_date in dictionary:
                return features, labels
            period = period + flatten(dictionary[tmp_date])
        end_date = (date+dt.timedelta(days=period_length-1)).strftime("%Y-%m-%d")
        prediction_date = (date+dt.timedelta(days=period_length)).strftime("%Y-%m-%d")
        if not prediction_date in dictionary:
            return features, labels
        period_label = ""
        for i in range(0,stock_count):
            label = classify(end_date,prediction_date,i,dictionary)
            period_label = period_label + label
        labels.append(period_label)
        features.append(period)


def classify(today,tomorrow,stock_index,dictionary):
    #SB -> StrongBuy
    #WB -> WeakBuy
    #SS -> StrongSell
    #WS -> WeakSell

    today_high = dictionary[today][stock_index][0]
    today_low = dictionary[today][stock_index][1]
    today_Open = dictionary[today][stock_index][2]
    tomorrow_high = dictionary[tomorrow][stock_index][0]
    tomorrow_low = dictionary[tomorrow][stock_index][1]
    tomorrow_Open = dictionary[tomorrow][stock_index][2]

    strong_bound_percentage = 0.008 #what is considered strong?

    if (tomorrow_low / today_high) - 1 > strong_bound_percentage:
        return "SB"
    if (tomorrow_low * -1 / today_high) - 1 > strong_bound_percentage:
        return "SS"
    if (tomorrow_low / today_high) - 1 > 0:
        return "WB"
    if (tomorrow_low / today_high) - 1 < 0:
        return "WS"

    return "WB" #We are optimistic
def simple_classifier():
    pass
def main(start_time,end_time,period_length,*stock_names):
    our_dictionary = get_data(start_time,end_time,*stock_names)
    our_features, our_labels = get_features(our_dictionary,period_length)

    print(len(our_features),len(our_labels))
    formatted_labels = encode_labels(our_labels)
    predictor = learn(our_features,formatted_labels)
    #holy shit we have created strong AI now !
    #lets try to predict something L O L
    try_start_time = dt.datetime(int(end_time[0:4]),int(end_time[4:6]),int(end_time[6:8]))
    try_end_time = dt.datetime.today() - dt.timedelta(days=2) #yesterday
    try_dictionary = get_data(try_start_time.strftime("%Y%m%d"),try_end_time.strftime("%Y%m%d"),*stock_names)
    try_features, true_labels = get_features(try_dictionary,period_length)

    correct_prediction_count = 0
    #try_count = 10
    try_count = len(true_labels)
    for i in range(0,try_count):
        predict_val = decode_label(predictor.predict([try_features[i]]))
        actual_val = true_labels[i]
        #print("predicted:",predict_val)
        #print("actual:   ",actual_val)
        if predict_val == actual_val:
            correct_prediction_count+=1
    print("\nPredicted",try_count,"days and",correct_prediction_count," were fully accurate")
    print(100*correct_prediction_count/try_count,"% accuracy",sep="")

def learn(features,labels):
    our_tree = tree.DecisionTreeClassifier()
    return our_tree.fit(features,labels)
def encode_labels(labels):
    new_labels = []
    for l in labels:
        new_labels.append(encode_label(l))
    return new_labels

def encode_label(labl):
    table = {"SS":0,"WS":1,"WB":2,"SB":3}
    exponent = len(labl) / 2 - 1
    result = 0
    for i in range(0,len(labl)//2):
        result += table[labl[2*i:2+2*i]] * (4**exponent)
        exponent = exponent - 1
    return int(result)

def decode_label(number):
    table = ["SS","WS","WB","SB"];
    rest = number
    label = ""
    max_exponent = 4**10
    while rest // max_exponent < 1:
        max_exponent = max_exponent / 4 #too big
    while rest != 0:
        key = int(rest // max_exponent)
        label += table[key]
        rest = rest - key * max_exponent
        max_exponent = max_exponent / 4
    return label
main('20170803','20181231',20,'OOIL')#,'COPX','TSLA','GOOG')
#main('20190101','20191231',15,'OOIL','COPX','TSLA','GOOG')
#this is an example of how to retrieve some data
