import datetime as dt
import sklearn
from itertools import combinations
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

style.use('ggplot')


#Usage: start time, end time , how long period, stock 1 , stock 2 , stock 3 and so on
#output is [[period 1], [period 2], ...]

#get_data will only create a list of dataframes. Each dataframe is from one stock
#get_data will call build_data when it has the list of dataframes
def get_data(start_time,end_time,verbose,stock_names):
    #print(start_time , end_time, period_length)
    dateStart = dt.datetime(int(start_time[0:4]),int(start_time[4:6]),int(start_time[6:8]))
    dateEnd = dt.datetime(int(end_time[0:4]),int(end_time[4:6]),int(end_time[6:8]))
    dataframes = []
    tmp = 1
    for stock_name in stock_names:
        if verbose:
            print("stock ",tmp,": ",stock_name,sep='')
        tmp = tmp +1
        df = web.DataReader(stock_name,'yahoo',dateStart,dateEnd); #get dataframe
        dataframes.append(df)
    return build_data(dataframes,verbose)

#build_data will take the list of dataframes and produce a dictionary
#alot of corner cases; where to start, where to end, fill gaps
def build_data(dataframes,verbose=True):
    if verbose:
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
    if verbose:
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
def flatten(list):#helper function to flatten nested list to simple list
    new_list = []
    for vals in list:
        for val in vals:
            new_list.append(val)
    return new_list
#get_features will take the dictionary and create features and labels
#output is a tuple: features , labels
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

#new version of classify
#give me the whole dictionary and which stock (index)
#I will give you the prediction of tomorrow
#It should be called "labeler"
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

    strong_bound_percentage = 0.005 #what is considered strong?

    if (tomorrow_low / today_low) - 1 > strong_bound_percentage:
        return "SB"
    if (tomorrow_low * -1 / today_low) - 1 > strong_bound_percentage:
        return "SS"
    if (tomorrow_low / today_low) - 1 > 0:
        return "WB"
    if (tomorrow_low / today_low) - 1 < 0:
        return "WS"

    return "WB" #We are optimistic
#old version of classify
def classify_old(today,tomorrow,stock_index,dictionary):
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

    strong_bound_percentage = 0.005 #what is considered strong?

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
#
def main(start_time,end_time,period_length,verbose,stock_names):
    if verbose:
        print("Training data with", period_length,"days historical data:")
    our_dictionary = get_data(start_time,end_time,verbose,stock_names) #fetch the consistent dictionary
    our_features, our_labels = get_features(our_dictionary,period_length) #get features and labels
    if verbose:
        print("Test data:")
    formatted_labels = encode_labels(our_labels) #simple encoder and decoder used
    p_MLP, p_RandomForest, p_KNeighbor, p_tree = learn(our_features,formatted_labels)
    #holy shit we have created strong AI now !
    #lets try to predict something L O L
    #Below is test data starting from where we ended when getting training data
    try_start_time = dt.datetime(int(end_time[0:4]),int(end_time[4:6]),int(end_time[6:8]))
    try_end_time = dt.datetime.today() - dt.timedelta(days=1) #yesterday
    try_dictionary = get_data(try_start_time.strftime("%Y%m%d"),try_end_time.strftime("%Y%m%d"),verbose,stock_names)
    try_features, true_labels = get_features(try_dictionary,period_length)

    result = []

    for p in [p_MLP, p_RandomForest, p_KNeighbor, p_tree]:
        if verbose:
            print(type(p))
        correct_prediction_count = 0
        #try_count = 10
        try_count = len(true_labels)
        first = dt.datetime.strptime(next(iter(try_dictionary)),'%Y-%m-%d')
        first = first  + dt.timedelta(days=period_length)

        for i in range(0,try_count):
            predict_val = decode_label(p.predict([try_features[i]]))
            actual_val = true_labels[i]
            #print("predicted:",predict_val,sep="")
            #print("actual:   ",actual_val,sep="")
            if predict_val == actual_val:
                correct_prediction_count+=1
                if verbose:
                    pass#print("hit",first.strftime("%Y-%m-%d"), predict_val,actual_val)
            first = first + dt.timedelta(days=1)
        if verbose:
            print("Predicted",try_count,"days and",correct_prediction_count," were fully accurate")
            print(100*correct_prediction_count/try_count,"% accuracy\n",sep="")
        result.append(100*correct_prediction_count/try_count)

    return result
#return all the classifier
def learn(features,labels):
    return learn_MLP(features,labels),learn_RandomForest(features,labels),learn_KNeighbors(features,labels),learn_tree(features,labels)
def learn_MLP(features,labels):
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(5, 2), random_state=1)
    return clf.fit(features,labels)

def learn_RandomForest(features,labels):
    clf = RandomForestClassifier(max_depth=2, random_state=0)
    return clf.fit(features, labels)

def learn_KNeighbors(features,labels): #KNeighborsClassifier
    neigh = KNeighborsClassifier(n_neighbors=3)
    return neigh.fit(features, labels)

def learn_tree(features,labels):
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
#main('20150803','20181231',16,'OOIL','COPX','GOLD','AG','UEC')
#main('20150803','20181231',7,True,['GOLD'])#,'COPX','TSLA','GOOG')

#main('20190101','20191231',15,'OOIL','COPX','TSLA','GOOG')
#this is an example of how to retrieve some data
def test(tmp):
    print("Welcome to MarketGenie v0.1")
    print("1) Run massive test (Automated)")
    print("2) Run massive test (Manually)")
    print("3) Get a prediction for tomorrow")

    choice = "1"#input()

    if choice == "1":
        #1 , 2 , 3, 4 , 5 ,6 , 7, 8 , 9 , 10 ,11 , 12 ,15 , 20 ,30 , 60, 90
        #0 , 1, 2 , 3, 4 , 5,  6 ,7,  8,  9 , 10 , 11 ,12 , 13 ,14  ,15 ,16
        x_labels = [1 , 2 , 3, 4 , 5 ,6 , 7, 8 , 9 , 10 ,11 , 12 ,15 , 20 ,30 , 60, 90]
        #stocks = {'O':'OOIL','C':'COPX','G':'GOLD','A':'AG','U':'UEC'}
        stocks = ['OOIL','COPX','GOLD','AG','UEC']
        #stocks = ['OOIL']
        y_labels = list(combinations(stocks,1)) #all combinations of length = 1
        y_labels+=(list(combinations(stocks,2)))
        #y_labels+=(list(combinations(stocks,3)))
        #y_labels+=(list(combinations(stocks,4)))
        #y_labels+=(list(combinations(stocks,5)))
        classifier_dict = {0:'red',1:'blue',2:'green',3:'yellow'}
        #x_labels = [4,5,6,7]
        x_values = []
        y_values = []
        s_values = []
        bubble_colors = []
        global_highest = 0
        perm = ['OOIL']
        period_len = 0
        classifier_id = 0
        print(len(y_labels))

        for period_length in x_labels:
            print("Calculating for period length", period_length)
            for comb_stocks in y_labels:
                local_highest = {'model_id':-1,'res':0}
                res = main('20150803','20181231',period_length,False,list(comb_stocks))
                print(comb_stocks," ",max(res),"%",)
                for x in range(0,len(res)):
                    x_values.append(period_length)
                    y_values.append(comb_stocks)
                    s_values.append(res[x])
                    bubble_colors.append(x)
                    if res[x] > local_highest['res']:
                        local_highest['model_id'] = x
                        local_highest['res'] = res[x]
                    if res[x] > global_highest:
                        global_highest = res[x]
                        perm = comb_stocks
                        period_len = period_length
                        classifier_id = x
                comb_stocks = ''.join(comb_stocks)
                plt.scatter(comb_stocks,str(period_length),alpha=0.5,s=local_highest['res']*tmp, c=classifier_dict[local_highest['model_id']])
                #plt.scatter(comb_stocks,str(period_length),s=100*40, edgecolors='black',facecolors='none')
        print(global_highest,perm,period_len,classifier_id)
        res = main('20150803','20181231',15,False,list(y_labels[0]))
        #plt.scatter(list(x_values),list(y_values),s = s_values*1000)#,c = bubble_colors)
        plt.ylabel('Period length', fontsize=16)
        plt.xlabel('Stocks', fontsize=16)
        plt.savefig('fig'+str(tmp)+'.png')
        #plt.show()
        #print(res[0])


test(15)
test(12)
test(10)
test(9)
test(8)
test(7)
test(6)
test(5)
test(3)
